#! /usr/bin/env python
import os
import sys
import ROOT as rt
from optparse import OptionParser

pwd = os.environ['PWD']
boxes = ['Had','Mu','Ele','MuMu','EleEle','MuEle']
if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-q','--queue',dest="queue",type="string",default="1nh",
                  help="Name of queue to use")
    
    (options,args) = parser.parse_args()
    
    print 'Input files are %s' % ', '.join(args)

    queue= options.queue

    for signalfilename in args:
        signal = signalfilename.split('.root')[0]

        M0 = int(signal.split('_')[-2].split('-')[-1])
        M12 = int(signal.split('_')[-1].split('-')[-1])

        print "\nNow scanning mSUGRA (M0,M12)=("+str(M0)+","+str(M12)+")\n"

        for i in range(200,202):

            for box in boxes:
        
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
                # prepare the script to run box-by-box
                outputname = "%s_%s_%i.src" %(signal,box,i)
                outputfile = open(outputname,'w')
                outputfile.write('#!/bin/bash\n')
                outputfile.write('cd '+pwd+'\n')
                outputfile.write("eval `scramv1 run -sh`\n")
                outputfile.write("source setup.sh\n")
                mydir = "/tmp/woodson/%s_%s_%i" %(signal,box,i)
                outputfile.write("rm /tmp/woodson/*\n")
                outputfile.write("mkdir %s\n" % mydir)
                outputfile.write("cp %s %s \n" %(signalfilename, mydir))
                # convert original signal file to box-by-box datasets
                outputfile.write("python scripts/Chris2BinnedDataset.py -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_Signal.cfg -x %s -d %s %s/%s\n" %(box,mydir, mydir, signalfilename))
                # perform limit toys(signal + bkgd) setting fits
                outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_Signal.cfg -o %s/LimitBkgSigToys_MR%s_R%s_%s_%s_%i.root -i /afs/cern.ch/user/w/woodson/public/RAZORFITS/SingleBoxFit_Prompt_MR%s_R%s_fR1fR2fR3fR4_%s.root %s/%s_MR%s_R%s_%s.root -b --limit >& %s/LimitBkgSigToys_output_%s_%s_%i.txt \n" %(seed,mydir,MR,R,signal,box,i,MR,R,box,mydir,signal,MR,R,box,mydir,signal,box,i))
                # perform limit toys(bkgd only) setting fits
                outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -s %i -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_Signal.cfg -o %s/LimitBkgToys_MR%s_R%s_%s_%s_%i.root -i /afs/cern.ch/user/w/woodson/public/RAZORFITS/SingleBoxFit_Prompt_MR%s_R%s_fR1fR2fR3fR4_%s.root %s/%s_MR%s_R%s_%s.root -b --limit -e >& %s/LimitBkgToys_output_%s_%s_%i.txt \n" %(seed,mydir,MR,R,signal,box,i,MR,R,box,mydir,signal,MR,R,box,mydir,signal,box,i))
                # copy output files
                outputfile.write("scp %s/LimitBkgSigToys_MR%s_R%s_%s_%s_%i.root woodson@lxcms132:/data/woodson/SIGNALMODELTOYS/\n" %(mydir,MR,R,signal,box,i))
                outputfile.write("scp %s/LimitBkgToys_MR%s_R%s_%s_%s_%i.root woodson@lxcms132:/data/woodson/SIGNALMODELTOYS/\n" %(mydir,MR,R,signal,box,i))
                outputfile.write("scp %s/LimitBkgSigToys_output_%s_%s_%i.txt woodson@lxcms132:/data/woodson/SIGNALMODELTOYS/\n" %(mydir,signal,box,i))
                outputfile.write("scp %s/LimitBkgToys_output_%s_%s_%i.txt woodson@lxcms132:/data/woodson/SIGNALMODELTOYS/\n" %(mydir,signal,box,i))
                # remove output files
                outputfile.write("rm -r %s\n" %(mydir))
                outputfile.close
                # submit to batch
                os.system("echo bsub -q "+queue+" -o log_"+signal+"_"+box+".log source "+pwd+"/"+outputname)
                os.system("bsub -q "+queue+" -o log_"+signal+"_"+box+".log source "+pwd+"/"+outputname)
                continue
