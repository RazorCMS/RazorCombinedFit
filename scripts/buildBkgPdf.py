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
for i in range(1,10):
    # prepare the script to run
    outputname = "%s/%s_%i.src" %(label, label, i)
    outputfile = open(outputname,'w')
    #outputfile.write('#!/bin/bash\n')
    #outputfile.write("cd /afs/cern.ch/user/m/mpierini/scratch0/CMSSW_4_2_0/src; eval `scramv1 run -sh`\n")
    #outputfile.write('cd '+pwd+'\n')
    #outputfile.write("source setup.sh\n")
    outputfile.write("mkdir /Users/maurizio/TMPTOY/toy%s_%i\n" %(box,i))
    outputfile.write("python scripts/runAnalysis.py -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4.cfg -a SingleBoxFit %s -i %s --save-toys-from-fit /Users/maurizio/TMPTOY/toy%s_%i --scale-lumi 1 -t 1000 \n" %(inputFile, inputFit, box, i))
    outputfile.write("python scripts/convertToyToROOT.py /Users/maurizio/TMPTOY/toy%s_%i/toys%s_ /Users/maurizio/TMPTOY/toy%s_%i/fr*txt\n" %(box, i, box, box, i)) 
    outputfile.write("rm /Users/maurizio/TMPTOY/toy%s_%i/fr*txt\n" %(box, i))
    #outputfile.write("python scripts/expectedYield.py 1 /Users/maurizio/TMPTOY/expectedYield_%s_%i.root %s /Users/maurizio/TMPTOY/toy%s_%i/*root\n" %(box, i, box, box, i))
    #outputfile.write("scp /Users/maurizio/TMPTOY/expectedYield_%s_%i.root mpierini@lxcms132:/data1/mpierini/TOY/\n" %(box, i))
    #outputfile.write("rm -r /Users/maurizio/TMPTOY/toy%s_%i\n" %(box,i))
    #outputfile.write("rm /Users/maurizio/TMPTOY/expectedYield_%s_%i.root\n" %(box,i))
    outputfile.close
    os.system("echo source "+pwd+"/"+outputname)
    #os.system("bsub -q "+queue+" -o log_"+str(i)+".log source "+pwd+"/"+outputname)
    #os.system("source "+pwd+"/"+outputname)
    continue
