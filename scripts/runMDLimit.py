#! /usr/bin/env python
import os
import sys
import ROOT as rt

## assumes you have the config file config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_SignalTemplate.cfg
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


for i in range(100,150):

    for box in boxes:
        
        pid = os.getpid()
        now = rt.TDatime()
        today = now.GetDate()
        clock = now.GetTime()
        seed = today+clock+pid+i
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
        outputfile.write("python scripts/Chris2Dataset.py -c config_summer11/SingleBoxFit_Prompt_fR1fR2fR3fR4_Signal.cfg -x %s -d %s %s/%s\n" %(box,mydir, mydir, signalfilename))
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
