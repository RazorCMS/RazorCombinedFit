#! /usr/bin/env python
import os.path
import sys
import time, datetime
from array import *

def getXsecRange(box,neutralinopoint,gluinopoint):
    massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)

    if gluinopoint < 500 :
        return [0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
    if gluinopoint == 500 :
        return [0.01, 0.05, 0.1, 0.2, 0.3]
    elif gluinopoint == 525 :
        return [0.01, 0.05, 0.1, 0.2]
    elif gluinopoint == 550 :
        return [0.01, 0.05, 0.1, 0.2, 0.3]
    elif gluinopoint == 575 :
        return [0.01, 0.05, 0.1, 0.2, 0.3]
    elif gluinopoint == 600 :
        return [0.01, 0.05, 0.1, 0.2]
    elif gluinopoint == 625 :
        return [0.01, 0.05, 0.1]
    elif gluinopoint > 625 :
        return [0.001, 0.005, 0.01, 0.05, 0.1]


    
def writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    nToys = 50 ## instead of 500 for the 2011 hybrid

    if box == 'Mu' or box == 'Ele':
        name = "SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR350.0_R0.22360679775"
    else : #assume bjetHS or bjetLS
        name = "SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR500.0_R0.22360679775"
    
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
    outputfile.write("scramv1 project CMSSW CMSSW_6_1_1\n")
    outputfile.write("cd CMSSW_6_1_1/src\n")
    outputfile.write("eval `scramv1 run -sh`\n")

    outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW\n")
   # outputfile.write("cvs co -r wreece_101212_2011_style_fits -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
    outputfile.write("cvs co -r lucieg_Ap25 -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("mkdir lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.34.05/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")
    outputfile.write("make\n")
    
    outputfile.write("export NAME=\"T2tt\"\n")
    outputfile.write("export LABEL=\"MR500.0_R0.22360679775\"\n")

    if box == 'had' or box == 'BJetHS' or box == 'BJetLS':
        outputfile.write("cp /afs/cern.ch/user/w/wreece/public/Razor2012/500_0_05/FullRegion/Run2012ABCD_Full_Search-280113.root $PWD\n")
        #outputfile.write("cp /afs/cern.ch/user/w/wreece/public/Razor2012/500_0_05/FitRegion/Run2012ABCD_Fit_Had-280113.root $PWD\n")
    elif box == 'Ele':
        outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/350_0_05/FitRegion/Run2012ABCD_Fit_Ele-120313.root $PWD\n")
    elif box == 'Mu':
        outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/350_0_05/FitRegion/Run2012ABCD_Fit_Mu-120313.root $PWD\n")
      

    outputfile.write("cp /afs/cern.ch/work/l/lucieg/public/forRazorStop/SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY/%s_%s_%s.root $PWD\n"%(name,massPoint,box))
                
    if box == 'had':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'BJetHS':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'BJetLS':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'lep':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Ele.root %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Had-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Ele.root %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'Ele':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Ele-120313.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Ele.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Ele-120313.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Ele.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'Mu':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Mu-120313.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Mu-120313.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_Mu.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        

    # the output directory must be changed
    outputfile.write("cp $WD/CMSSW_6_1_1/src/RazorCombinedFit/*.root /afs/cern.ch/work/l/lucieg/private/workspace"+timestamp+"/RazorStops/ScanHybrid"+box+"/\n")
    outputfile.write("rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir
if __name__ == '__main__':
    box = sys.argv[1]
    nJobs = 30 # do 100=50+50 toys each job => 5000 toys
    timestamp = str(datetime.date.today())
    print box
    
    gluinopoints = [ 150 , 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625, 650, 675, 700, 725, 750, 775, 800]
    neutralinopoints = [0]
    queue = "1nd"
    
    pwd = os.environ['PWD']

    submitDir = "submit"
    outputDir = "output"+timestamp+"_"+box
   
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p /afs/cern.ch/work/l/lucieg/private/workspace"+timestamp+"/RazorStops/ScanHybrid"+box)
    os.system("mkdir -p /afs/cern.ch/work/l/lucieg/private/"+outputDir)
    os.system("ln -s /afs/cern.ch/work/l/lucieg/private/"+outputDir)
    
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
                        
