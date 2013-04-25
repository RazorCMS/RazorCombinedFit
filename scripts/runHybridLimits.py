#! /usr/bin/env python
import os.path
import sys
import time
from array import *

def getXsecRange(box,neutralinopoint,gluinopoint):
    massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)

    if gluinopoint == 200:
        return [0.05, 0.1, 0.2, 0.4, 0.8]
    elif gluinopoint == 300:
        return [0.05, 0.1, 0.2, 0.4, 0.8]
    elif gluinopoint == 400:
        return [0.005, 0.02, 0.05, 0.2, 0.4]
    elif gluinopoint == 500:
        return [0.005, 0.02, 0.05, 0.2, 0.4]
    elif gluinopoint == 550:
        return [0.005, 0.02, 0.05, 0.2, 0.4]
    elif gluinopoint == 600:
        return [0.001, 0.005, 0.02, 0.05, 0.08]
    elif gluinopoint == 650:
        return [0.001, 0.005, 0.02, 0.05, 0.08]
    elif gluinopoint == 700:
        return [0.001, 0.005, 0.02, 0.05, 0.08]
    elif gluinopoint == 800:
        return [0.001, 0.005, 0.02, 0.05, 0.08]
    else:
        return []



    
def writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    nToys = 50 ## instead of 500 for the 2011 hybrid

    name = "SMS_T2tt_mLSP50_apr3_MR350.0_R0.22360679775"
    massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)
    #massPoint = "%.1f_0.0"%gluinopoint
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
    outputfile.write("cvs co -r wreece_101212_2011_style_fits -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
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
        #outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/500_0_05/FitRegion/Run2012ABCD_Fit_Lep-280113.root $PWD\n")


    if box == 'BJetHS':
        outputfile.write("cp /afs/cern.ch/user/s/ssekmen/public/RzrMJ/SMS/T2tt_mLSP50_apr3/%s_%s_BJetHS.root $PWD\n"%(name,massPoint))
    elif box == 'BJetLS':
        outputfile.write("cp /afs/cern.ch/user/s/ssekmen/public/RzrMJ/SMS/T2tt_mLSP50_apr3/%s_%s_BJetLS.root $PWD\n"%(name,massPoint))
    elif box == 'Ele':
        outputfile.write("cp /afs/cern.ch/user/s/ssekmen/public/RzrMJ/SMS/T2tt_mLSP50_apr3/%s_%s_Ele.root $PWD\n"%(name,massPoint))
    elif box == 'Mu':
        outputfile.write("cp /afs/cern.ch/user/s/ssekmen/public/RzrMJ/SMS/T2tt_mLSP50_apr3/%s_%s_Mu.root $PWD\n"%(name,massPoint))

                
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
    outputfile.write("cp $WD/CMSSW_6_1_1/src/RazorCombinedFit/*.root /afs/cern.ch/work/l/lucieg/private/workspace/RazorStops/ScanHybridEle_mLSP_50/\n")
    outputfile.write("rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir
if __name__ == '__main__':
    box = sys.argv[1]
    nJobs = 50 # do 100=50+50 toys each job => 5000 toys
    
    print box
    
    #gluinopoints = [200,250, 300, 350, 400,450, 500, 550, 600, 650, 700, 750, 800]
    gluinopoints = [200, 300, 400, 500, 550, 600, 650, 700, 800]
    neutralinopoints = [50]
    queue = "1nd"
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "/afs/cern.ch/work/l/lucieg/private/output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))
    os.system("mkdir -p /afs/cern.ch/work/l/lucieg/private/workspace/RazorStops/ScanHybridEle_mLSP_50/")
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
                        
