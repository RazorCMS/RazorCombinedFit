#! /usr/bin/env python
import os
import sys
label = sys.argv[1]
queue= sys.argv[2]
box = sys.argv[3]
inputFile = sys.argv[4]
inputFit = sys.argv[5]

os.system("mkdir %s" %label)
pwd = os.environ['PWD']
for i in range(1,1000):
    # prepare the script to run
    outputname = "%s/%s_%i.src" %(label, label, i)
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write("cd /afs/cern.ch/user/m/mpierini/scratch0/CMSSW_4_2_0/src; eval `scramv1 run -sh`\n")
    outputfile.write('cd '+pwd+'\n')
    outputfile.write("source setup.sh\n")
    outputfile.write("mkdir /tmp/mpierini/toy%s_%i\n" %(box,i))
    outputfile.write("python scripts/runAnalysis.py -c SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_NOTE.cfg -a SingleBoxFit %s -i %s --save-toys-from-fit /tmp/mpierini/toy%s_%i -t 1000 >& /dev/null \n" %(inputFile, inputFit, box, i))
    outputfile.write("python scripts/convertToyToROOT.py /tmp/mpierini/toy%s_%i/toys%s_ /tmp/mpierini/toy%s_%i/fr*txt\n" %(box, i, box, box, i)) 
    outputfile.write("rm /tmp/mpierini/toy%s_%i/fr*txt\n" %(box, i))
    outputfile.write("python scripts/expectedYield.py /tmp/mpierini/expectedYield_%s_%i.root %s /tmp/mpierini/toy%s_%i/*root\n" %(box, i, box, box, i))
    outputfile.write("scp /tmp/mpierini/expectedYield_%s_%i.root mpierini@lxcms132:/data1/mpierini/TOY/\n" %(box, i))
    outputfile.write("rm -r /tmp/mpierini/toy%s_%i\n" %(box,i))
    outputfile.write("rm /tmp/mpierini/expectedYield_%s_%i.root\n" %(box,i))
    outputfile.close
    os.system("echo bsub -q "+queue+" -o log_"+str(i)+".log source "+pwd+"/"+outputname)
    #os.system("bsub -q "+queue+" -o log_"+str(i)+".log source "+pwd+"/"+outputname)
    continue
