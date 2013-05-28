#! /usr/bin/env python
import os.path
import sys
import time, datetime

def getXsecRange(box,gluinopoint):

    if gluinopoint == 150 :
        return [0.01, 0.05, 0.07]
    elif gluinopoint ==175  :
        return [0.01, 0.05, 0.07]
    elif gluinopoint == 200 :
        return [0.01, 0.05, 0.07]
    elif gluinopoint == 225 :
        return [0.01, 0.05, 0.1, 0.2]
    elif gluinopoint < 300 :
        return [0.01, 0.05, 0.1, 0.5]
    elif gluinopoint <= 300 :
        return [0.01, 0.05, 0.1, 0.5]
    elif gluinopoint < 400 :
        return [0.01, 0.05, 0.1, 0.5]
    elif gluinopoint == 400 :
        return [ 0.1, 0.5, 1.0]
    elif gluinopoint <= 500 :
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
        return [ 0.01, 0.05, 0.1, 0.2]
    elif gluinopoint > 625 :
        return [  0.01, 0.05, 0.1, 0.2]


    
def writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint):
    if box == 'Mu' or box == 'Ele':
        name = "SMS-T2tt_mStop-Combo_mLSP_50.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR350.0_R0.22360679775"
    else : #assume bjetHS or bjetLS
        name = "SMS-T2tt_mStop-Combo_mLSP_50.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR500.0_R0.22360679775"
    
    massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)

    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+massPoint+"_"+box+"_xsec"+xsecstring+".src"
    outputfile = open(outputname,'w')
            
    logFile = logDir+"/logs_"+massPoint+"_"+xsecstring+".log"

    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write("export WD=/tmp/${USER}/Razor2012_%s_%s_%s\n"%(massPoint,box,xsecstring))
    outputfile.write("mkdir -p $WD\n")
    outputfile.write("cd $WD\n")
    outputfile.write("scramv1 project CMSSW CMSSW_6_1_2\n")
    outputfile.write("cd CMSSW_6_1_2/src\n")
    outputfile.write("eval `scramv1 run -sh`\n")

    outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW\n")
    outputfile.write("cvs co -r salvati_May28 -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("mkdir lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.34.07/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")
    outputfile.write("make\n")
    
    outputfile.write("export NAME=\"T2tt\"\n")

    if box == 'had' or box == 'BJetHS' or box == 'BJetLS':
        outputfile.write("cp /afs/cern.ch/user/w/wreece/public/Razor2012/500_0_05/FullRegion/Run2012ABCD_Full_Search-280113.root $PWD\n")
    elif box == 'Ele':
        outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/350_0_05/FitRegion/Run2012ABCD_Fit_Ele-120313.root $PWD\n")
    elif box == 'Mu':
        outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/350_0_05/FitRegion/Run2012ABCD_Fit_Mu-120313.root $PWD\n")
      

    outputfile.write("cp /afs/cern.ch/work/l/lucieg/public/forRazorStop/SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY/Datasets/mLSP50/%s_%s_%s.root $PWD\n"%(name,massPoint,box))
                
    if box == 'BJetHS':
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --run-cls --nosave-workspace -o ${NAME}_%s_%s_%s.root %s_%s_BJetHS.root --xsec %f --multijet --massPoint %s_%s\n"%(massPoint,box,xsecstring,name,massPoint,xsecpoint,massPoint,xsecstring))

    elif box == 'BJetLS':
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --run-cls --nosave-workspace -o ${NAME}_%s_%s_%s.root %s_%s_BJetLS.root --xsec %f --multijet --massPoint %s_%s\n"%(massPoint,box,xsecstring,name,massPoint,xsecpoint,massPoint,xsecstring))

    elif box == 'Ele':
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Ele-120313.root -l --run-cls --nosave-workspace -o ${NAME}_%s_%s_%s.root %s_%s_Ele.root --xsec %f --multijet --massPoint %s_%s\n"%(massPoint,box,xsecstring,name,massPoint,xsecpoint,massPoint,xsecstring))

    elif box == 'Mu':
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Fit_Mu-120313.root -l --run-cls --nosave-workspace -o ${NAME}_%s_%s_%s.root %s_%s_Mu.root --xsec %f --multijet --massPoint %s_%s\n"%(massPoint,box,xsecstring,name,massPoint,xsecpoint,massPoint,xsecstring))
        

    # the output directory must be changed
    outputfile.write("cp $WD/CMSSW_6_1_2/src/RazorCombinedFit/*.root /afs/cern.ch/work/s/salvati/private/" + outputDir +"/\n")
    outputfile.write("rm -rf $WD\n")
    
    outputfile.close
    return outputname,logFile

if __name__ == '__main__':
    box = sys.argv[1]
    timestamp = str(datetime.date.today())
    print box
    
    gluinopoints = [150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625, 650, 675, 700, 725, 750, 775, 800]
    neutralinopoints = [50]

    queue = "1nd"
    
    pwd = os.environ['PWD']

    submitDir = "submit"
    outputDir = "output"+timestamp+"_"+box
    logDir = outputDir + "/logs"

    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p /afs/cern.ch/work/s/salvati/private/"+outputDir)
    os.system("ln -s /afs/cern.ch/work/s/salvati/private/"+outputDir)
    os.system("mkdir -p /afs/cern.ch/work/s/salvati/private/"+logDir)
    
    for neutralinopoint in neutralinopoints:
        for gluinopoint in gluinopoints:
            massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)
            xsecRange = getXsecRange(box,gluinopoint)
            for xsecpoint in xsecRange:
                print "Now scanning xsec = %f"%xsecpoint
                outputname,log = writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint)
                time.sleep(3)
                os.system("echo bsub -q "+queue+" -o "+pwd+"/"+log+" source "+pwd+"/"+outputname)
                os.system("bsub -q "+queue+" -o "+pwd+"/"+log+" source "+pwd+"/"+outputname)
                        
