#! /usr/bin/env python
import os
import sys
import ROOT as rt

## assumes you have the config file SingleBoxFit_Prompt_MR300.0_R0.3_B123hC123_new.cfg in your directory
## 
queue= sys.argv[1]
signalfilename = sys.argv[2]
ngen = sys.argv[3]

pwd = os.environ['PWD']
boxes = ['Had','Mu','Ele','MuMu','EleEle','MuEle']

signal = signalfilename.split('.root')[0]

M0 = int(signal.split('_')[-2])
M12 = int(signal.split('_')[-1])

xsecfilename = signal.split('_')[0]+'_'+signal.split('_')[1]+'_xsec.root'

xsecfile = rt.TFile(xsecfilename)
xsechist = xsecfile.Get('xsec')

xsec = xsechist.GetBinContent(xsechist.FindBin(M0,M12))
afile = 'config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_SignalTemplate.cfg'
destination= open('config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_Signal.cfg', 'w' )
source= open( afile, 'r' )
for line in source:
    newline = line.replace('0.3104','%f' %xsec).replace('220000',ngen)
    if newline == '': destination.write( line )
    else: destination.write( newline )
source.close()
destination.close()



for box in boxes:
    if box=='Had':
        MR='400.0'
        R='0.4'
    else:
        MR='300.0'
        R='0.3'
    # prepare the script to run box-by-box
    outputname = "%s_%s.src" %(signal,box)
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('cd '+pwd+'\n')
    outputfile.write("eval `scramv1 run -sh`\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("cp %s /tmp/woodson/ \n" %signalfilename)
    # convert original signal file to box-by-box datasets
    outputfile.write("python scripts/Chris2Dataset.py  -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_Signal.cfg -d /tmp/woodson /tmp/woodson/%s\n" %signalfilename)
    # fit on a single box dataset 
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_Signal.cfg -o /tmp/woodson/SingleBoxFit_Prompt_MR%s_R%s_fR1fR2fR3fR4_%s.root /afs/cern.ch/user/m/mpierini/public/RAZOR2011_FitSamples/*_%s.root -b >& /tmp/woodson/fitoutput_%s_%s.txt \n" %(MR,R,box,box,signal,box))
    # perform limit toys(signal + bkgd) setting fits
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_Signal.cfg -o /tmp/woodson/SingleBoxFit_Prompt_MR%s_R%s_fR1fR2fR3fR4_%s_%s.root -i /tmp/woodson/SingleBoxFit_Prompt_MR%s_R%s_fR1fR2fR3fR4_%s.root /tmp/woodson/%s_MR%s_R%s_%s.root -b --limit >& /tmp/woodson/output_%s_%s.txt \n" %(MR,R,signal,box,MR,R,box,signal,MR,R,box,signal,box))
    # perform limit toys(bkgd only) setting fits
    outputfile.write("scp /tmp/woodson/SingleBoxFit_Prompt_MR%s_R%s_fR1fR2fR3fR4_%s_%s.root woodson@lxcms133:/data/woodson/SIGNALMODELTOYS/\n" %(MR,R,signal,box))
    outputfile.write("scp /tmp/woodson/output_%s_%s.txt woodson@lxcms133:/data/woodson/SIGNALMODELTOYS/\n" %(signal,box))
    outputfile.write("rm /tmp/woodson/SingleBoxFit_Prompt_MR%s_R%s_fR1fR2fR3fR4_%s.root\n" %(MR,R,box))
    outputfile.write("rm /tmp/woodson/SingleBoxFit_Prompt_MR%s_R%s_fR1fR2fR3fR4_%s_%s.root\n" %(MR,R,signal,box))
    outputfile.write("rm /tmp/woodson/fitoutput_%s_%s.txt \n" %(signal,box))
    outputfile.write("rm /tmp/woodson/output_%s_%s.txt" %(signal,box))
    outputfile.close
    # submit to batch
    os.system("echo bsub -q "+queue+" -o log_"+signal+"_"+box+".log source "+pwd+"/"+outputname)
    #os.system("bsub -q "+queue+" -o log_"+signal+"_"+box+".log source "+pwd+"/"+outputname)
    continue
