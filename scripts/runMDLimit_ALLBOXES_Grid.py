#! /usr/bin/env python
import os
import sys
import ROOT as rt
from optparse import OptionParser

pwd = os.environ['PWD']
#boxes = ['Had','Mu','Ele','MuMu','EleEle','MuEle']
if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-t','--toys',dest="toys",type="int",default="40", help="Number of toys per job")
    parser.add_option('-i','--index',dest="iJob",type="int",default="5", help="Integer index (to label outputs)")
    parser.add_option('-n','--number',dest="numJobs",type="int",default="100", help="number of jobs")
    parser.add_option('-f','--fill-by-box',dest="fillByProcess",default=True, action='store_false', help="Fill boxes by Box")
    parser.add_option("--input",dest="input",default="razor_output.root", help="input file containing the bkg fits") 
    parser.add_option('--xsec',dest="xsec",type="float",default="-99", help="Signal cross section (in pb) for SMSs limit setting")

    (options,args) = parser.parse_args()
    
    print 'Input files are %s' % ', '.join(args)

    toys = options.toys
    xsec = options.xsec
    input = options.input
    if options.fillByProcess: script = "Chris2BinnedDataset_ALLBOXES_BYPROCESS.py"
    else: script = "Chris2BinnedDataset_ALLBOXES.py"

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

        # prepare the script to run           
        if xsec >0: outputname = "%s_xsec_%f.src" %(signal, xsec)
        else: outputname = "%s.src" %(signal)
        outputfile = open(outputname,'w')
        outputfile.write('#!/bin/bash\n')
        outputfile.write("eval `scramv1 run -sh`\n")
        outputfile.write("tar zxvf everything.tgz\n")
        if xsec > 0: outputfile.write("tar zxvf files_%i_%i_xsec_%f.tgz\n" %(M0,M12,xsec))
        else: outputfile.write("tar zxvf files_%i_%i.tgz\n" %(M0,M12))
        outputfile.write("cd RazorCombinedFit\n")
        outputfile.write("source setup.sh\n")
        outputfile.write("export PYTHONPATH=$PYTHONPATH:$PWD/python\n")
        outputfile.write("mkdir lib\n")
        outputfile.write("make\n") 
        
        # convert original signal file to box-by-box datasets
        seed = -1
        if xsec > 0.:
            # run SMS
            outputfile.write("python scripts/%s -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg --sms -t %i -d $PWD $PWD/../%s/%s\n" %(script, toys, signalfiledir, signalfilename))
            # perform limit toys(signal + bkgd) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit --xsec %f -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o $PWD/../LimitBkgSigToys_%s_xsec_%f.root -i $PWD/../%s $PWD/%s_MR*.root -b --limit -t %i >& /dev/null\n" %(xsec,seed,signal,xsec,input,signal,toys))
            # perform limit toys(bkgd only) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit --xsec %f -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o $PWD/../LimitBkgToys_%s_xsec_%f.root -i $PWD/../%s $PWD/%s_MR*.root -b --limit -e -t %i >& /dev/null\n" %(xsec,seed,signal,xsec,input,signal,toys))
        else:
            # run CMSSM
            outputfile.write("python scripts/%s -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -t %i -d $PWD $PWD/../%s/%s\n" %(script, toys, signalfiledir, signalfilename))
            # perform limit toys(signal + bkgd) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o $PWD/../LimitBkgSigToys_%s.root -i $PWD/../%s $PWD/%s_MR*.root -b --limit -t %i >& /dev/null\n" %(seed,signal,input,signal,toys))
            # perform limit toys(bkgd only) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o $PWD/../LimitBkgToys_%s.root -i $PWD/../%s $PWD/%s_MR*.root -b --limit -e -t %i >& /dev/null\n" %(seed,signal,input,signal,toys))

        # prepare the CRAB script
        if xsec>0: outputname2 = "crab_%s_xsec_%f.cfg" %(signal,xsec)
        else: outputname2 = "crab_%s.cfg" %(signal)
        outputfile2 = open(outputname2,'w')
        outputfile2.write('[CRAB]\n')
        outputfile2.write('jobtype = cmssw\n')
        outputfile2.write('scheduler = glite\n')
        outputfile2.write('[CMSSW]\n')
        outputfile2.write('### The output files (comma separated list)\n')
        if xsec > 0.:
            #SMS
            outputfile2.write('output_file = LimitBkgSigToys_%s_xsec_%f.root, LimitBkgToys_%s_xsec_%f.root\n' %(signal,xsec,signal,xsec))
        else:
            # CMSSM
            outputfile2.write('output_file = LimitBkgSigToys_%s.root, LimitBkgToys_%s.root\n' %(signal,signal))
        outputfile2.write('datasetpath=None\n')
        outputfile2.write('pset=None\n')
        outputfile2.write('number_of_jobs=%i\n' %options.numJobs)
        outputfile2.write('[USER]\n')
        outputfile2.write('debug_wrapper=1\n')
        outputfile2.write('script_exe = %s\n' %outputname)
        outputfile2.write('### OUTPUT files Management\n')
        outputfile2.write('##  output back into UI\n')
        outputfile2.write('return_data = 1\n')
        outputfile2.write('ui_working_dir = %s\n' %(outputname2.split(".cfg")[0]))
        if xsec > 0: outputfile2.write('additional_input_files = everything.tgz, files_%i_%i_xsec_%f.tgz\n' %(M0,M12,xsec))
        else: outputfile2.write('additional_input_files = everything.tgz, files_%i_%i.tgz\n' %(M0,M12))
        outputfile2.write('[GRID]\n')
        outputfile2.write('ce_white_list=T2_US_Caltech\n')
        outputfile2.close
        
        # prepare the tarball
        if xsec > 0: outputname3 = "source_me_%s_xsec_%f.src" %(signal,xsec)
        else: outputname3 = "source_me_%s.src" %(signal)
        outputfile3 = open(outputname3,'w')
        if xsec > 0: outputfile3.write('tar czf files_%i_%i_xsec_%f.tgz %s %s/%s\n' %(M0, M12, xsec, outputname, signalfiledir, signalfilename))
        else: outputfile3.write('tar czf files_%i_%i.tgz %s %s/%s\n' %(M0, M12, outputname, signalfiledir, signalfilename))
        outputfile3.write('crab -create -cfg %s\n' %outputname2)
        outputfile3.write('crab -submit -c  %s\n' %(outputname2.split(".cfg")[0]))
        outputfile3.close
        
        # submit the job [TO UNCOMMENT]
        #os.system("source %s" %outputname3)
