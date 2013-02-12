#! /usr/bin/env python

#from optparse import OptionParser

#import ROOT as rt
#import RootTools
#from RazorCombinedFit.Framework import Config
import os.path
import sys
import time
from array import *

def getXsecRange(box,neutralinopoint,gluinopoint):
    lumi = 19300
    name = "T2tt"
    label = "MR500.0_R0.22360679775"
    massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)

    mDelta = (gluinopoint*gluinopoint - neutralinopoint*neutralinopoint)/gluinopoint
    print "mDelta = %f"%mDelta
    if mDelta < 800:
        xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
    elif mDelta < 1400:
        xsecRange = [0.0005, 0.001, 0.005, 0.01, 0.05, 0.1]
    else:
        xsecRange = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.1]
        

    #return xsecRange
    return [0.001, 0.005, 0.01, 0.05]

    
def writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    nToys = 500

    name = "SMS_T2tt_jan30_MR500.0_R0.22360679775"    
    massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)
    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
    outputfile = open(outputname,'w')
    
    tagHypo = ""
    if hypo == "B":
        tagHypo = "-e"
        
    ffDir = outputDir+"/logs_"+massPoint+"_"+xsecstring+"_"+hypo
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write("export WD=/tmp/${USER}/Razor2012_%s_%s_%s_%i\n"%(massPoint,box,xsecstring,t))
    outputfile.write("mkdir -p $WD\n")
    outputfile.write("cd $WD\n")
    outputfile.write("scramv1 project CMSSW CMSSW_5_3_7_patch4\n")
    outputfile.write("cd CMSSW_5_3_7_patch4/src\n")
    outputfile.write("eval `scramv1 run -sh`\n")
    
    outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW\n")
    outputfile.write("cvs co -r wreece_101212_2011_style_fits -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("mkdir lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")
    outputfile.write("make\n")
    
    outputfile.write("export NAME=\"T2tt\"\n")
    outputfile.write("export LABEL=\"MR500.0_R0.22360679775\"\n")
    
    if box == 'had' or box == 'BJetHS' or box == 'BJetLS':
        outputfile.write("cp /afs/cern.ch/user/w/wreece/public/Razor2012/500_0_05/FitRegion/Run2012ABCD_Fit_Had-280113.root $PWD\n")
        outputfile.write("cp /afs/cern.ch/user/s/ssekmen/public/forWill/RzrMJSMS/%s_%s_BJet*.root $PWD\n"%(name,massPoint))
    else:
        outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/500_0_05/FitRegion/Run2012ABCD_Fit_Lep-280113.root $PWD\n")
        outputfile.write("cp /afs/cern.ch/user/s/ssekmen/public/forWill/RzrMJSMS/%s_%s_Ele*.root $PWD\n"%(name,massPoint))
        outputfile.write("cp /afs/cern.ch/user/s/ssekmen/public/forWill/RzrMJSMS/%s_%s_Mu*.root $PWD\n"%(name,massPoint))
        


    if box == 'had':
        nToyOffset = nToys*t #(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_BJetHS.root %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        #nToyOffset = nToys*(2*t+1)
        #outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_BJetHS.root %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'BJetHS':
        nToyOffset = nToys*t #(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_BJetHS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        #nToyOffset = nToys*(2*t+1)
        #outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_BJetHS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'BJetLS':
        nToyOffset = nToys*t #(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        #nToyOffset = nToys*(2*t+1)
        #outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'lep':
        nToyOffset = nToys*t#(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_Ele.root %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        #nToyOffset = nToys*(2*t+1)
        #outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_Ele.root %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'Ele':
        nToyOffset = nToys*t#(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_Ele.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        #nToyOffset = nToys*(2*t+1)
        #outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_Ele.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'Mu':
        nToyOffset = nToys*t#(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        #nToyOffset = nToys*(2*t+1)
        #outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nosave-workspace %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        

    # the output directory must be changed
    outputfile.write("cp $WD/CMSSW_5_3_7_patch4/src/RazorCombinedFit/*.root $HOME/workspace/RazorStops/ScanHybrid/\n")
    outputfile.write("rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir
if __name__ == '__main__':
    box = sys.argv[1]
    nJobs = 3 # do 1000=500+500 toys each job
    
    print box
    
    gluinopoints = range(200,850,50)
    neutralinopoints = [0]
    queue = "1nd"
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))

    hypotheses = ["B","SpB"]

    for neutralinopoint in neutralinopoints:
        for gluinopoint in gluinopoints:
            xsecRange = getXsecRange(box,neutralinopoint,gluinopoint)
            for xsecpoint in xsecRange:
                for hypo in hypotheses:
                    for t in xrange(0,nJobs):
                        print "Now scanning xsec = %f"%xsecpoint
                        outputname,ffDir = writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t)
                        os.system("mkdir -p %s/%s"%(pwd,ffDir))
                        time.sleep(3)
                        os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        
