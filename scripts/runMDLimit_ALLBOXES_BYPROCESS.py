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
        signal = signalfilename.split('.root')[0]

        M0 = int(signal.split('_')[-2].split('-')[-1])
        M12 = int(signal.split('_')[-1].split('-')[-1])

        print "\nNow scanning mSUGRA (M0,M12)=("+str(M0)+","+str(M12)+")\n"

        for i in range(options.iJob,options.iJob+options.numJobs):
            outputFileName = "%s_nbinx_%i_nbiny_%i" %(signal,nbinx, nbiny)
            # prepare the script to run
            outputname = "%s_%i.src" %(outputFileName,i)
            outputfile = open(outputname,'w')
            outputfile.write('#!/bin/bash\n')
            outputfile.write('cd '+pwd+'\n')
            outputfile.write("eval `scramv1 run -sh`\n")
            mydir = "/tmp/smaria/%s_%i" %(signal,i)
            outputfile.write("mkdir %s\n" %mydir)
            outputfile.write("cd %s\n" %mydir)
            outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/cvs/CMSSW\n")
            outputfile.write("cvs co -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
            outputfile.write("cd RazorCombinedFit\n")
            outputfile.write("source setup.sh\n")
            outputfile.write("make\n") 
            outputfile.write("cp -r %s/RAZORFITS %s \n" %(pwd, mydir))
            outputfile.write("cp %s/%s %s \n" %(pwd,signalpath, mydir))

            #outputname = "%s_%s_%i.src" %(signal,options.box,i)
            #outputfile = open(outputname,'w')
            #outputfile.write('#!/bin/bash\n')
            #outputfile.write('cd '+pwd+'\n')
            #outputfile.write("eval `scramv1 run -sh`\n")
            #outputfile.write("source setup.sh\n")
            #mydir = "/tmp/smaria/%s_%i" %(signal,i)
            #outputfile.write("rm /tmp/smaria/*\n")
            #outputfile.write("mkdir %s\n" % mydir)
            #outputfile.write("cp %s %s \n" %(signalpath, mydir))
            
            # convert original signal file to box-by-box datasets

            pid = os.getpid()
            now = rt.TDatime()
            today = now.GetDate()
            clock = now.GetTime()
            seed = today+clock+pid+137*i
            print str(seed)
            outputfile.write("python scripts/Chris2BinnedDataset_ALLBOXES_BYPROCESS.py -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -t %i -d %s -x %i -y %i %s/%s\n" %(toys,mydir, nbinx, nbiny,mydir, signalfilename))
            # perform limit toys(signal + bkgd) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o %s/LimitBkgSigToys_%s_%i.root -i %s/RAZORFITS/all_cleaned.root %s/%s_MR*.root -b --limit -t %i >& /dev/null\n" %(seed,mydir,outputFileName,i,mydir,mydir,signal,toys))
            # perform limit toys(bkgd only) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o %s/LimitBkgToys_%s_%i.root -i %s/RAZORFITS/all_cleaned.root %s/%s_MR*.root -b --limit -e -t %i >& /dev/null\n" %(seed,mydir,outputFileName,i,mydir,mydir,signal,toys))
            # copy output files
            outputfile.write("scp %s/LimitBkgSigToys_%s_%i.root smaria@lxcms132:/data1/smaria/SIGNALMODELTOYS_BYPROCESS_LARGEBIN_PLUSSYS_50/\n" %(mydir,outputFileName,i))
            outputfile.write("scp %s/LimitBkgToys_%s_%i.root smaria@lxcms132:/data1/smaria/SIGNALMODELTOYS_BYPROCESS_LARGEBIN_PLUSSYS_50/\n" %(mydir,outputFileName,i))
            # remove output files
            outputfile.write("cd /tmp; rm -r %s\n" %(mydir))
            outputfile.close
            # submit to batch
            os.system("echo bsub -q "+queue+" -o log_"+signal+"_"+str(i)+".log source "+pwd+"/"+outputname)
            os.system("bsub -q "+queue+" -o log_"+signal+"_"+str(i)+".log source "+pwd+"/"+outputname)
            continue
