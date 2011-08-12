#! /usr/bin/env python
import os
import sys
import ROOT as rt

queue= sys.argv[1]
signalfilename = sys.argv[2]
ngen = sys.argv[3]

pwd = os.environ['PWD']
boxes = ['Had','Mu','Ele','MuMu','EleEle','MuEle']

signal = signalfilename.split('.root')[0]

M0 = int(signalpath.split('_')[-2])
M12 = int(signalpath.split('_')[-1])

xsecfilename = signal.split('_')[0]+'_'+signal.split('_')[1]+'_xsec.root'

xsecfile = rt.TFile(xsecfilename)
xsechist = xsecfile.Get('xsec')

xsec = xsechist.GetBinContent(xsechist.FindBin(M0,M12))
afile = 'SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_new.cfg'
destination= open('SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_new2.cfg', 'w' )
source= open( afile, 'r' )
for line in source:
    newline = line.replace('0.3104','%f' %xsec).replace('220000',ngen)
    if newline == '': destination.write( line )
    else: destination.write( newline )
source.close()
destination.close()



for box in boxes:
    # prepare the script to run
    outputname = "%s_%s.src" %(signal,box)
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('cd '+pwd+'\n')
    outputfile.write("eval `scramv1 run -sh`\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("python scripts/Chris2Dataset.py  -c SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_new2.cfg %s" %signalfilename)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_new2.cfg -o SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_%s.root /afs/cern.ch/user/w/wreece/public/RazorResults/PromptDatasets/*_%s.root -b >& /tmp/woodson/fitoutput_%s_%s.txt \n" %(box,box,signal,box))
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_new2.cfg -o SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_%s_%s.root -i SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_%s.root %s_MR300.0_R0.3_%s.root -b --limit >& /tmp/woodson/output_%s_%s.txt \n" %(signal,box,box,signal,box,signal,box))
    outputfile.write("scp /tmp/woodson/output_%s_%s.txt woodson@lxcms132:/data/woodson/\n" %(signal,box))
    outputfile.write("rm /tmp/woodson/fitoutput_%s_%s.txt \n" %(signal,box))
    outputfile.write("rm /tmp/woodson/output_%s_%s.txt" %(signal,box))
    outputfile.close
    os.system("echo bsub -q "+queue+" -o log_"+signal+"_"+box+".log source "+pwd+"/"+outputname)
    #os.system("bsub -q "+queue+" -o log_"+signal+"_"+box+".log source "+pwd+"/"+outputname)
    continue
