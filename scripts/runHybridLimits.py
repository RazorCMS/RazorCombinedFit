#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
import time
import math
from array import *


def getXsecRange(box,model,neutralinoMass,gluinoMass):

    if model=="T1bbbb":
        mDelta = (pow(gluinoMass,2) - pow(neutralinoMass,2))/gluinoMass
        if mDelta < 400:
            xsecRange = [0.005, 0.01, 0.05, 0.1, 0.5, 1.]
        elif mDelta < 800:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
        else:
            xsecRange = [0.0005, 0.001, 0.005, 0.01, 0.05]
    elif model=="T2tt":
        topMass = 175.
        mDelta = math.sqrt(max(pow( (pow(gluinoMass,2) - pow(neutralinoMass,2) + pow(topMass,2) )/gluinoMass , 2) - pow(topMass,2),0))
        if gluinoMass < 2*topMass:
            xsecRange = [0.5, 1., 5., 10., 50., 100., 500.]
        elif mDelta < 200:
            xsecRange = [0.5, 1., 5., 10., 50., 100., 500.]
        elif mDelta < 300:
            xsecRange = [0.1, 0.5, 1., 5., 10., 50., 100.]
        elif mDelta < 400:
            xsecRange = [0.05, 0.1, 0.5, 1., 5., 10., 50.]
        elif mDelta < 500:
            xsecRange = [0.005,0.01, 0.05, 0.1, 0.5, 1., 5.]
        else:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
    elif model=="T1tttt":
        topMass = 175.
        mDelta = math.sqrt(max(pow( (pow(gluinoMass,2) - pow(neutralinoMass,2) + pow(2*topMass,2) )/gluinoMass , 2) - pow(2*topMass,2),0))
        if gluinoMass < 2*topMass:
            xsecRange = [0.005, 0.01, 0.05, 0.1, 0.5, 1., 5.]
        elif mDelta < 600:
            xsecRange = [0.005, 0.01, 0.05, 0.1, 0.5, 1.]
        elif mDelta < 800:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
        else:
            xsecRange = [0.0005, 0.001, 0.005, 0.01, 0.05, 0.1]
          
    return xsecRange

    
def writeBashScript(box,model,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    nToys = 125 # toys per command

    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
    outputfile = open(outputname,'w')

    label = ""

    if box in ["Ele", "EleTau","EleEle","MuEle","MuMu","Mu","MuTau"]:
       label = "MR300.0_R0.387298334621"
    else:
       label = "MR400.0_R0.5"
        
    
    tagHypo = ""
    if hypo == "B":
        tagHypo = "-e"
        
    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_"+xsecstring+"_"+hypo
    user = os.environ['USER']
    
    hybridDir = "/afs/cern.ch/work/%s/%s/RAZORLIMITS/Hybrid/"%(user[0],user)
    
    outputfile.write('#!/usr/bin/env bash -x\n')
    
    outputfile.write("export WD=/tmp/${USER}/Razor2013_%s_%s_%s_%s_%i\n"%(model,massPoint,box,xsecstring,t))
    outputfile.write("mkdir -p $WD\n")
    outputfile.write("cd $WD\n")
    outputfile.write("scramv1 project CMSSW CMSSW_6_1_1\n")
    outputfile.write("cd CMSSW_6_1_1/src\n")
    outputfile.write("eval `scramv1 run -sh`\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh\n")
    outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.34.05/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")
    outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW\n")
    outputfile.write("cvs co -r woodson_110413 -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("mkdir lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("make clean; make\n")
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    outputfile.write("export LABEL=\"%s\"\n"%label)
    
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/FullFits2012ABCD.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}_%s_${LABEL}*.root $PWD\n"%massPoint)
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/NuisanceTreeISR.root $PWD\n")
        
    nToyOffset = nToys*(2*t)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_hybrid.config -i FullFits2012ABCD.root -l --nuisance-file NuisanceTreeISR.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2013HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
    
    nToyOffset = nToys*(2*t+1)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_hybrid.config -i FullFits2012ABCD.root -l --nuisance-file NuisanceTreeISR.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2013HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    outputfile.write("cp $WD/CMSSW_6_1_1/src/RazorCombinedFit/*.root %s \n"%hybridDir)
    outputfile.write("cd; rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir
if __name__ == '__main__':
    box = sys.argv[1]
    model = sys.argv[2]
    queue = sys.argv[3]
    
    nJobs = 12 # do 250 toys each job => 3000 toys
    
    print box, model, queue

    if model=="T1bbbb":
        gchipairs = []
        histoFileName = sys.argv[4]
        histoFile = rt.TFile.Open(histoFileName)
        histo = histoFile.Get("T1bbbb_MultiJet")
        for mg in xrange(450, 1200, 50):
            for mchi in xrange(450, 750, 50):
                if histo.GetBinContent(histo.FindBin(mg,mchi)):
                    if mchi!=0:
                        gchipairs.append((mg,mchi))

        print gchipairs
        print len(gchipairs)

        
        gchipairs.extend([( 400,  50), ( 550,  50), ( 600,  50), ( 700,  50), ( 775,  50), ( 825,  50), ( 925,  50),              (1025,  50), (1075,  50), (1125,  50), (1225,  50), (1325,  50), (1375,  50),
                          ( 400, 200), ( 550, 200), ( 600, 200), ( 700, 200), ( 775, 200), ( 825, 200), ( 925, 200),              (1025, 200), (1075, 200), (1125, 200), (1225, 200), (1325, 200), (1375, 200),
                          ( 400, 300), ( 550, 300), ( 600, 300), ( 700, 300), ( 775, 300), ( 825, 300), ( 925, 300),              (1025, 300), (1075, 300), (1125, 300), (1225, 300), (1325, 300), (1375, 300),
                          ( 550, 400), ( 600, 400), ( 700, 400), ( 775, 400), ( 825, 400), ( 925, 400),              (1025, 400), (1075, 400), (1125, 400), (1225, 400), (1325, 400), (1375, 400),
                          ( 775, 525), ( 825, 525), ( 925, 525), ( 950, 525), (1025, 525), (1075, 525), (1125, 525), (1225, 525), (1325, 525), (1375, 525),
                          ( 700, 600), ( 775, 600), ( 825, 600), ( 925, 600), ( 950, 600), (1025, 600), (1075, 600), (1125, 600), (1225, 600), (1325, 600), (1375, 600),
                          ( 700, 650), ( 775, 650), ( 825, 650), ( 925, 650), ( 950, 650), (1025, 650), (1075, 650), (1125, 650), (1225, 650), (1325, 650), (1375, 650),
                          ( 775, 700), ( 825, 700), ( 925, 700), ( 950, 700), (1025, 700), (1075, 700), (1125, 700), (1225, 700), (1325, 700), (1375, 700),
                          ( 825, 800), ( 925, 800), ( 950, 800), (1025, 800), (1075, 800), (1125, 800), (1225, 800), (1325, 800), (1375, 800)])
        
    #    gchipairs = [(400,  50), (450,  50), (500,  50), (550,  50), (600,  50), (650,  50), (700,  50), (750, 200), (775,  50), (825,  50), (875,  50), (925,  50),                          (1025,  50), (1075,  50), (1125,  50), (1225,  50), (1325,  50), (1375,  50),
    #                  (400, 200), (450, 200), (500, 200), (550, 200), (600, 200), (650, 200), (700, 200), (750, 200), (775, 200), (825, 200), (875, 200), (925, 200),                          (1025, 200), (1075, 200), (1125, 200), (1225, 200), (1325, 200), (1375, 200),
    #                  (400, 300), (450, 300), (500, 300), (550, 300), (600, 300), (650, 300), (700, 300), (750, 300), (775, 300), (825, 300), (875, 300), (925, 300),                          (1025, 300), (1075, 300), (1125, 300), (1225, 300), (1325, 300), (1375, 300),
    #                              (450, 400), (500, 400), (550, 400), (600, 400), (650, 400), (700, 400), (750, 400), (775, 400), (825, 400), (875, 400), (925, 400),                          (1025, 400), (1075, 400), (1125, 400), (1225, 400), (1325, 400), (1375, 400),
    #                                          (500, 450), (550, 450), (600, 450), (650, 450), (700, 450), (750, 450), (775, 450), (825, 450), (875, 450), (925, 450),                          (1025, 450), (1075, 450), (1125, 450), (1225, 450), (1325, 450), (1375, 450),
    #                                          (500, 500), (550, 500), (600, 500), (650, 500), (700, 500), (750, 500), (775, 500), (825, 500), (875, 500), (925, 500),                          (1025, 500), (1075, 500), (1125, 500), (1225, 500), (1325, 500), (1375, 500),
    #                                                                                                                  (775, 525), (825, 525), (875, 525), (925, 525), (950, 525), (1000, 525), (1025, 525), (1075, 525), (1125, 525), (1225, 525), (1325, 525), (1375, 525),
    #                                                                  (600, 550), (650, 550), (700, 550), (750, 550), (775, 550), (825, 550), (875, 550), (925, 550), (950, 550), (1000, 550), (1025, 550), (1075, 550), (1125, 550), (1225, 550), (1325, 550), (1375, 550),
    #                                                                              (650, 600), (700, 600), (750, 600), (775, 600), (825, 600), (875, 600), (925, 600), (950, 600), (1000, 600), (1025, 600), (1075, 600), (1125, 600), (1225, 600), (1325, 600), (1375, 600),
    #                                                                                                                  (775, 625), (825, 625), (875, 625), (925, 625), (950, 625), (1000, 625), (1025, 625), (1075, 625), (1125, 625), (1225, 625), (1325, 625), (1375, 625),
    #                                                                                          (700, 650), (750, 650), (775, 650), (825, 650), (875, 650), (925, 650), (950, 650), (1000, 650), (1025, 650), (1075, 650), (1125, 650), (1225, 650), (1325, 650), (1375, 650),
    #                                                                                                      (750, 700), (775, 700), (825, 700), (875, 700), (925, 700), (950, 700), (1000, 700), (1025, 700), (1075, 700), (1125, 700), (1225, 700), (1325, 700), (1375, 700),
    #                                                                                                                  (775, 750), (825, 750), (875, 750), (925, 750), (950, 750), (1000, 750), (1025, 750), (1075, 750), (1125, 750), (1225, 750), (1325, 750), (1375, 750),
    #                                                                                                                              (825, 800), (875, 800), (925, 800), (950, 800), (1000, 800), (1025, 800), (1075, 800), (1125, 800), (1225, 800), (1325, 800), (1375, 800),
    #                                                                                                                                          (875, 850), (925, 850), (950, 850), (1000, 850), (1025, 850), (1075, 850), (1125, 850), (1225, 850), (1325, 850), (1375, 850)]
    # 
    if model=="T2tt":
        gchipairs = [(150, 50), (200, 50), (250, 50), (300, 50), (350, 50), (400, 50), (450, 50),
                     (500, 50), (550, 50), (600, 50), (650, 50), (700, 50), (750, 50), (800, 50)]
    if model=="T1tttt":
        gchipairs = [(400, 1), (450, 1), (500, 1), (550, 1), (600, 1), (650, 1), (700, 1), (750, 1),
                     (800, 1), (850, 1), (900, 1), (950, 1), (1000, 1), (1050, 1), (1100,1),(1150,1),
                     (1200,1), (1250,1), (1300,1), (1350,1), (1400,1)]
        
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))

    hypotheses = ["B","SpB"]

    totalJobs = 0
    for gluinopoint, neutralinopoint in gchipairs:
        xsecRange = getXsecRange(box,model,neutralinopoint,gluinopoint)
        for xsecpoint in xsecRange:
            print "Now scanning mg = %.0f, mchi = %.0f, xsec = %.4f"%(gluinopoint, neutralinopoint,xsecpoint)
            for hypo in hypotheses:
                for t in xrange(0,nJobs):
                    outputname,ffDir = writeBashScript(box,model,neutralinopoint,gluinopoint,xsecpoint,hypo,t)
                    os.system("mkdir -p %s/%s"%(pwd,ffDir))
                    totalJobs+=1
                    time.sleep(3)
                    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("source "+pwd+"/"+outputname)
                        
    print "Total jobs = ", totalJobs
