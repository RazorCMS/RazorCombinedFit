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
    parser.add_option('-b','--box',dest="box",type="string",default="Had", help="Box To Run ON")
    parser.add_option('-t','--toys',dest="toys",type="int",default="1000", help="Number of toys per job")
    parser.add_option('-i','--index',dest="iJob",type="int",default="5", help="Integer index (to label outputs)")
    parser.add_option('-n','--number',dest="numJobs",type="int",default="1", help="number of total jobs")
    
    (options,args) = parser.parse_args()
    
    print 'Input files are %s' % ', '.join(args)

    queue = options.queue
    toys = options.toys


    for signalpath in args:
        signalfilename = signalpath.split('/')[-1]
        signal = signalfilename.split('.root')[0]

        M0 = int(signal.split('_')[-2].split('-')[-1])
        M12 = int(signal.split('_')[-1].split('-')[-1])

        print "\nNow scanning mSUGRA (M0,M12)=("+str(M0)+","+str(M12)+")\n"

        for i in range(options.iJob,options.iJob+options.numJobs):

            # prepare the script to run           
            outputname = "%s_%s_%i.src" %(signal,options.box,i)
            outputfile = open(outputname,'w')
            outputfile.write('#!/bin/bash\n')
            outputfile.write('cd '+pwd+'\n')
            outputfile.write("eval `scramv1 run -sh`\n")
            mydir = "/tmp/woodson/%s_%i" %(signal,i)
            outputfile.write("mkdir %s\n" %mydir)
            outputfile.write("cd %s\n" %mydir)
            outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/cvs/CMSSW\n")
            outputfile.write("cvs co -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
            outputfile.write("cd RazorCombinedFit\n")
            outputfile.write("source setup.sh\n")
            outputfile.write("make\n") 
            outputfile.write("cp %s/%s %s \n" %(pwd,signalpath, mydir))

            #outputname = "%s_%s_%i.src" %(signal,options.box,i)
            #outputfile = open(outputname,'w')
            #outputfile.write('#!/bin/bash\n')
            #outputfile.write('cd '+pwd+'\n')
            #outputfile.write("eval `scramv1 run -sh`\n")
            #outputfile.write("source setup.sh\n")
            #mydir = "/tmp/woodson/%s_%i" %(signal,i)
            #outputfile.write("rm /tmp/woodson/*\n")
            #outputfile.write("mkdir %s\n" % mydir)
            #outputfile.write("cp %s %s \n" %(signalpath, mydir))
            
            # convert original signal file to box-by-box datasets

            box = options.box
        
            pid = os.getpid()
            now = rt.TDatime()
            today = now.GetDate()
            clock = now.GetTime()
            seed = today+clock+pid+137*i
            print str(seed)
            
            if box=='Had':
                MR='400.0'
                R='0.4'
            else:
                MR='300.0'
                R='0.3'
            outputfile.write("python scripts/Chris2BinnedDataset.py -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -x %s -t %i -d %s %s/%s\n" %(box,toys,mydir, mydir, signalfilename))
            # perform limit toys(signal + bkgd) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o %s/LimitBkgSigToys_MR%s_R%s_%s_%s_%i.root -i /afs/cern.ch/user/w/woodson/public/RAZORFITS/%s_cleaned.root %s/%s_MR%s_R%s_%s.root -b --limit -t %i >& /dev/null\n" %(seed,mydir,MR,R,signal,box,i,box,mydir,signal,MR,R,box,toys))
            # perform limit toys(bkgd only) setting fits
            outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -o %s/LimitBkgToys_MR%s_R%s_%s_%s_%i.root -i /afs/cern.ch/user/w/woodson/public/RAZORFITS/%s_cleaned.root %s/%s_MR%s_R%s_%s.root -b --limit -e -t %i >& /dev/null \n" %(seed,mydir,MR,R,signal,box,i,box,mydir,signal,MR,R,box,toys))
            # copy output files
            outputfile.write("scp %s/LimitBkgSigToys_MR%s_R%s_%s_%s_%i.root woodson@lxcms132:/data1/woodson/SIGNALMODELTOYS/\n" %(mydir,MR,R,signal,box,i))
            outputfile.write("scp %s/LimitBkgToys_MR%s_R%s_%s_%s_%i.root woodson@lxcms132:/data1/woodson/SIGNALMODELTOYS/\n" %(mydir,MR,R,signal,box,i))
            # remove output files
            outputfile.write("cd /tmp; rm -r %s\n" %(mydir))
            outputfile.close
            # submit to batch
            os.system("echo bsub -q "+queue+" -o log_"+signal+"_"+box+"_"+str(i)+".log source "+pwd+"/"+outputname)
            #os.system("bsub -q "+queue+" -o log_"+signal+"_"+box+"_"+str(i)+".log source "+pwd+"/"+outputname)
            continue
