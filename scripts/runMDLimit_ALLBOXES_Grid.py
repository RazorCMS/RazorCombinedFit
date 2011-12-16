#! /usr/bin/env python
import os
import sys
import ROOT as rt
from optparse import OptionParser

pwd = os.environ['PWD']
#boxes = ['Had','Mu','Ele','MuMu','EleEle','MuEle']
if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-q','--queue',dest="queue",type="string",default="1nh", help="Name of queue to use")
    parser.add_option('-t','--toys',dest="toys",type="int",default="1000", help="Number of toys per job")
    parser.add_option('-i','--index',dest="iJob",type="int",default="5", help="Integer index (to label outputs)")
    parser.add_option('-n','--number',dest="numJobs",type="int",default="1", help="number of total jobs")
    parser.add_option('-x','--nbinx',dest="nbinx",type="int",default="100", help="number of binx on X axis")
    parser.add_option('-y','--nbiny',dest="nbiny",type="int",default="100", help="number of binx on Y axis")
    
    (options,args) = parser.parse_args()
    
    print 'Input files are %s' % ', '.join(args)

    queue = options.queue
    toys = options.toys
    nbinx = options.nbinx
    nbiny = options.nbiny

    for signalpath in args:
        signalfilename = signalpath.split('/')[-1]
        if len(signalpath.split('/')) > 1: 
            signalfiledir = signalpath.split('/')[-2]
        else:
            signalfiledir = "./"

        signal = signalfilename.split('.root')[0]
        M0 = int(signal.split('_')[-2].split('-')[-1])
        M12 = int(signal.split('_')[-1].split('-')[-1])

        print "\nNow scanning mSUGRA (M0,M12)=("+str(M0)+","+str(M12)+")\n"

        for i in range(options.iJob,options.iJob+options.numJobs):

            # prepare the script to run           
            outputname = "%s.src" %(signal)
            outputfile = open(outputname,'w')
            outputfile.write('#!/bin/bash\n')
            outputfile.write("eval `scramv1 run -sh`\n")
            outputfile.write("tar zxvf everything.tgz\n")
            outputfile.write("cd RazorCombinedFit\n")
            outputfile.write("source setup.sh\n")
            outputfile.write("export PYTHONPATH=$PYTHONPATH:$PWD/python\n")
            outputfile.write("mkdir lib\n")
            outputfile.write("make\n") 

            # convert original signal file to box-by-box datasets

            pid = os.getpid()
            now = rt.TDatime()
            today = now.GetDate()
            clock = now.GetTime()
            seed = today+clock+pid+137*i
            print str(seed)
            outputfile.write("python scripts/Chris2BinnedDataset_ALLBOXES_BYPROCESS.py -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -t %i -d $PWD -x %i -y %i $PWD/../%s/%s\n" %(toys, nbinx, nbiny, signalfiledir, signalfilename))
            # perform limit toys(signal + bkgd) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o $PWD/../LimitBkgSigToys_%s.root -i $PWD/../RAZORFITS/all_cleaned.root $PWD/%s_MR*.root -b --limit -t %i >& /dev/null\n" %(seed,signal,signal,toys))
            # perform limit toys(bkgd only) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o $PWD/../LimitBkgToys_%s.root -i $PWD/../RAZORFITS/all_cleaned.root $PWD/%s_MR*.root -b --limit -e -t %i >& /dev/null\n" %(seed,signal,signal,toys))

            # prepare the CRAB script
            outputname2 = "crab_%s.cfg" %(signal)
            outputfile2 = open(outputname2,'w')
            outputfile2.write('[CRAB]\n')
            outputfile2.write('jobtype = cmssw\n')
            outputfile2.write('scheduler = glite\n')
            outputfile2.write('[CMSSW]\n')
            outputfile2.write('### The output files (comma separated list)\n')
            outputfile2.write('output_file = LimitBkgSigToys_%s.root, LimitBkgToys_%s.root\n' %(signal,signal))
            outputfile2.write('datasetpath=None\n')
            outputfile2.write('pset=None\n')
            outputfile2.write('number_of_jobs=100\n')
            outputfile2.write('[USER]\n')
            outputfile2.write('debug_wrapper=1\n')
            outputfile2.write('script_exe = %s\n' %outputname)
            outputfile2.write('### OUTPUT files Management\n')
            outputfile2.write('##  output back into UI\n')
            outputfile2.write('return_data = 1\n')
            outputfile2.write('ui_working_dir = crab_%s\n' %(signal))
            outputfile2.write('additional_input_files = everything.tgz\n')
            outputfile2.write('[GRID]\n')
            outputfile2.write('ce_white_list=T2_US_Caltech\n')
            outputfile2.close

            # prepare the tarball
            outputname3 = "source_me_%s.src" %(signal)
            outputfile3 = open(outputname3,'w')
            outputfile3.write('tar czf everything.tgz %s RAZORFITS/all_cleaned.root RazorCombinedFit/ rootplot/ %s/%s\n' %(outputname, signalfiledir, signalfilename))
            outputfile3.write('crab -create -cfg %s\n' %outputname2)
            outputfile3.write('crab -submit -c  crab_%s\n' %(signal))
            outputfile3.close
            
            continue
