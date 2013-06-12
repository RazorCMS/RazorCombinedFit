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
        mDelta = math.sqrt(pow( (pow(gluinoMass,2) - pow(neutralinoMass,2) + pow(topMass,2) )/gluinoMass , 2) - pow(topMass,2))
        if mDelta < 300:
            xsecRange = [0.1, 0.5, 1., 5., 10., 50., 100.]
        elif mDelta < 400:
            xsecRange = [0.05, 0.1, 0.5, 1., 5., 10., 50.]
        elif mDelta < 500:
            xsecRange = [0.005,0.01, 0.05, 0.1, 0.5, 1., 5.]
        else:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
    elif model=="T1tttt":
        topMass = 175.
        mDelta = math.sqrt(pow( (pow(gluinoMass,2) - pow(neutralinoMass,2) + pow(2*topMass,2) )/gluinoMass , 2) - pow(2*topMass,2))
        if mDelta < 700:
            xsecRange = [0.05, 0.1, 0.5, 1., 5., 10.]
        elif mDelta < 800:
            xsecRange = [0.01, 0.05, 0.1, 0.5, 1.0]
        else:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1]
          
    return xsecRange

    
def writeSgeScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    nToys = 125 # toys per command
    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".sge"
    outputfile = open(outputname,'w')
    
    label = "MR300.0_R0.387298334621"

    tagHypo = ""
    if hypo == "B":
        tagHypo = "-e"
        
    ffDir = outputDir+"/logs_"+model+"_"+massPoint+"_"+xsecstring+"_"+hypo
    user = os.environ['USER']
    
    hybridDir = "/home/%s/work/RAZORLIMITS/Hybrid/"%(user)
    
    
    outputfile.write('#$ -S /bin/sh\n')
    outputfile.write('#$ -cwd\n')
    outputfile.write("export WD=/wntmp/${USER}/Razor2013_%s_%s_%s_%s_%i\n"%(model,massPoint,box,xsecstring,t))
    outputfile.write("mkdir -p $WD\n")
    outputfile.write("cd $WD\n")
    
    outputfile.write("source /home/jduarte/.bashrc\n")
    outputfile.write("cp /home/jduarte/work/RAZORLIMITS/RazorCombinedFit.tar.gz .\n")
    outputfile.write("tar -xvzf RazorCombinedFit.tar.gz\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("mkdir lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("make clean; make\n")
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    outputfile.write("export LABEL=\"%s\"\n"%label)
    
    outputfile.write("cp /home/jduarte/work/RAZORLIMITS/Razor2013/Background/FULLFits2012ABCD.root $PWD\n")
    outputfile.write("cp /home/jduarte/work/RAZORLIMITS/Razor2013/Signal/${NAME}/${NAME}_%s_${LABEL}*.root $PWD\n"%massPoint)
    outputfile.write("cp /home/jduarte/work/RAZORLIMITS/Razor2013/Signal/NuisanceTreeISR.root $PWD\n")
    
    nToyOffset = nToys*(2*t)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_hybrid.config -i FULLFits2012ABCD.root -l --nuisance-file NuisanceTreeISR.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2013HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
    
    nToyOffset = nToys*(2*t+1)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_hybrid.config -i FULLFits2012ABCD.root -l --nuisance-file NuisanceTreeISR.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2013HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    outputfile.write("cp $WD/RazorCombinedFit/*.root %s \n"%hybridDir)
    outputfile.write("cd; rm -rf $WD\n")
    
    return outputname,ffDir
    
def writeBashScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,hypo,t):
    nToys = 125 # toys per command
    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
    # prepare the script to run
    xsecstring = str(xsecpoint).replace(".","p")
    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
    outputfile = open(outputname,'w')

    label = "MR300.0_R0.387298334621"
    
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
    outputfile.write('export PATH=\"/afs/cern.ch/sw/lcg/external/Python/2.6.5/x86_64-slc5-gcc43-opt/bin:${PATH}\" \n')
    outputfile.write('export LD_LIBRARY_PATH=\"/afs/cern.ch/sw/lcg/external/Python/2.6.5/x86_64-slc5-gcc43-opt/lib:${LD_LIBRARY_PATH}\" \n')
    outputfile.write('. /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh \n')
    outputfile.write('cd /afs/cern.ch/sw/lcg/app/releases/ROOT/5.34.07/x86_64-slc5-gcc43-opt/root;. ./bin/thisroot.sh; cd -\n')
    #outputfile.write("scramv1 project CMSSW CMSSW_6_1_1\n")
    #outputfile.write("cd CMSSW_6_1_1/src\n")
    #outputfile.write("eval `scramv1 run -sh`\n")
    #outputfile.write("source /afs/cern.ch/sw/lcg/external/gcc/4.3.2/x86_64-slc5/setup.sh\n")
    #outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.34.05/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")
    outputfile.write("export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW\n")
    outputfile.write("cvs co -r woodson_110613 -d RazorCombinedFit UserCode/wreece/RazorCombinedFit\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("mkdir lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("make clean; make -j 4\n")
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    outputfile.write("export LABEL=\"%s\"\n"%label)
    
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/FULLFits2012ABCD.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}/${NAME}_%s_${LABEL}*.root $PWD\n"%massPoint)
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/NuisanceTreeISR.root $PWD\n")
        
    nToyOffset = nToys*(2*t)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_hybrid.config -i FULLFits2012ABCD.root -l --nuisance-file NuisanceTreeISR.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2013HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
    
    nToyOffset = nToys*(2*t+1)
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_hybrid.config -i FULLFits2012ABCD.root -l --nuisance-file NuisanceTreeISR.root --nosave-workspace ${NAME}_%s_${LABEL}_%s.root -o Razor2013HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i\n"%(massPoint,box,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    #outputfile.write("cp $WD/CMSSW_6_1_1/src/RazorCombinedFit/*.root %s \n"%hybridDir)
    outputfile.write("cp $WD/RazorCombinedFit/*.root %s \n"%hybridDir)
    outputfile.write("cd; rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir
if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "\nRun the script as follows:\n"
        print "python scripts/runHybridLimits.py Box Model Queue CompletedOutputTextFile"
        print "with:"
        print "- Box = name of the Box (MuMu, MuEle, etc.)"
        print "- Model = T1bbbb, T1tttt, T2tt, etc. "
        print "- Queue = 1nh, 8nh, 1nd, etc."
        print "- CompletedOutputTextFile = text file containing all completed output files"
        print ""
        sys.exit()
    box = sys.argv[1]
    model = sys.argv[2]
    queue = sys.argv[3]
    done  = sys.argv[4]
    t3 = False
    mchi_lower = 0
    mchi_upper = 2025
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--t3")!=-1: t3 = True
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--mchi-lt")!=-1: mchi_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mchi-geq")!=-1: mchi_lower = float(sys.argv[i+1])
    
    nJobs = 12 # do 250 toys each job => 3000 toys
    
    print box, model, queue

    if model=="T1bbbb":
        gchipairs = [(400, 50), (400, 200), (400, 300),
                     (450, 50), (450, 200), (450, 300), (450, 400),
                     (500, 50), (500, 200), (500, 300), (500, 400), (500, 450), (500, 500),
                     (550, 50), (550, 200), (550, 300), (550, 400), (550, 450), (550, 500),
                     (600, 50), (600, 200), (600, 300), (600, 400), (600, 450), (600, 500), (600, 550),
                     (650, 50), (650, 200), (650, 300), (650, 400), (650, 450), (650, 500), (650, 550), (650, 600),
                     (700, 50), (700, 200), (700, 300), (700, 400), (700, 450), (700, 500), (700, 550), (700, 600), (700, 650),
                     (750, 200), (750, 300), (750, 400), (750, 450), (750, 500), (750, 550), (750, 600), (750, 650), (750, 700),
                     (775, 50), (775, 200), (775, 300), (775, 400), (775, 450), (775, 500), (775, 525), (775, 550), (775, 600), (775, 625), (775, 650), (775, 700), (775, 750),
                     (800, 550), (800, 600), (800, 650), (800, 700),
                     (825, 50), (825, 200), (825, 300), (825, 400), (825, 450), (825, 500), (825, 525), (825, 550), (825, 600), (825, 625), (825, 650), (825, 700), (825, 750), (825, 800),
                     (850, 550), (850, 600), (850, 650), (850, 700),
                     (875, 50), (875, 200), (875, 300), (875, 400), (875, 450), (875, 500), (875, 525), (875, 550), (875, 600), (875, 625), (875, 650), (875, 700), (875, 750), (875, 800), (875, 850),
                     (900, 550), (900, 600), (900, 650),
                     (925, 50), (925, 200), (925, 300), (925, 400), (925, 450), (925, 500), (925, 525), (925, 550), (925, 600), (925, 625), (925, 650), (925, 700), (925, 750), (925, 800), (925, 850),
                     (950, 525), (950, 550), (950, 600), (950, 625), (950, 650), (950, 700), (950, 750), (950, 800), (950, 850),
                     (1000, 525), (1000, 550), (1000, 600), (1000, 625), (1000, 650), (1000, 700), (1000, 750), (1000, 800), (1000, 850),
                     (1025, 50), (1025, 200), (1025, 300), (1025, 400), (1025, 450), (1025, 500), (1025, 525), (1025, 550), (1025, 600), (1025, 625), (1025, 650), (1025, 700), (1025, 750), (1025, 800), (1025, 850),
                     (1050, 550), (1050, 600), (1050, 650), (1050, 700),
                     (1075, 50), (1075, 200), (1075, 300), (1075, 400), (1075, 450), (1075, 500), (1075, 525), (1075, 550), (1075, 600), (1075, 625), (1075, 650), (1075, 700), (1075, 750), (1075, 800), (1075, 850),
                     (1100, 550), (1100, 600), (1100, 650), (1100, 700),
                     (1125, 50), (1125, 200), (1125, 300), (1125, 400), (1125, 450), (1125, 500), (1125, 525), (1125, 550), (1125, 600), (1125, 625), (1125, 650), (1125, 700), (1125, 750), (1125, 800), (1125, 850),
                     (1150, 550), (1150, 600), (1150, 650), (1150, 700),
                     (1225, 50), (1225, 200), (1225, 300), (1225, 400), (1225, 450), (1225, 500), (1225, 525), (1225, 550), (1225, 600), (1225, 625), (1225, 650), (1225, 700), (1225, 750), (1225, 800), (1225, 850),
                     (1325, 50), (1325, 200), (1325, 300), (1325, 400), (1325, 450), (1325, 500), (1325, 525), (1325, 550), (1325, 600), (1325, 625), (1325, 650), (1325, 700), (1325, 750), (1325, 800), (1325, 850),
                     (1375, 50), (1375, 200), (1375, 300), (1375, 400), (1375, 450), (1375, 500), (1375, 525), (1375, 550), (1375, 600), (1375, 625), (1375, 650), (1375, 700), (1375, 750), (1375, 800), (1375, 850)]
        
    if model=="T2tt":
        gchipairs = [(150, 50),
                     (200, 50),
                     (250, 50), (250, 150),
                     (300, 50), (300, 150),
                     (350, 50), (350, 150), (350, 250),
                     (400, 50), (400, 150), (400, 250),
                     (450, 50), (450, 150), (450, 250), (450, 350),
                     (500, 50), (500, 150), (500, 250), (500, 350),
                     (550, 50), (550, 150), (550, 250), (550, 350), (550, 450),
                     (600, 50), (600, 150), (600, 250), (600, 350), (600, 450),
                     (650, 50), (650, 150), (650, 250), (650, 350), (650, 450), (650, 550),
                     (700, 50), (700, 150), (700, 250), (700, 350), (700, 450), (700, 550),
                     (750, 50), (750, 150), (750, 250), (750, 350), (750, 450), (750, 550), (750, 650),
                     (800, 50), (800, 150), (800, 250), (800, 350), (800, 450), (800, 550), (800, 650)]
        
    if model=="T1tttt":
        gchipairs = [(400, 1), (400, 25), (400, 125),
                     (450, 1), (450, 25), (450, 125), (450, 225),
                     (500, 1), (500, 25), (500, 125), (500, 225),
                     (550, 1), (550, 25), (550, 125), (550, 225), (550, 325),
                     (600, 1), (600, 25), (600, 125), (600, 225), (600, 325),
                     (650, 1), (650, 25), (650, 125), (650, 225), (650, 325), (650, 425),
                     (700, 1), (700, 25), (700, 125), (700, 225), (700, 325), (700, 425),
                     (750, 1), (750, 25), (750, 125), (750, 225), (750, 325), (750, 425), (750, 525),
                     (800, 1), (800, 525),
                     (850, 1), (850, 525), (850, 625),
                     (900, 1), (950, 1),
                     (1000, 1), (1000, 525), (1000, 625), (1000, 725),
                     (1050, 1), (1050, 525), (1050, 625), (1050, 725), (1050, 825),
                     (1100, 1), (1100, 125), (1100, 225), (1100, 325), (1100, 425), (1100, 525), (1100, 625), (1100, 725), (1100, 825),
                     (1150, 1), (1150, 125), (1150, 225), (1150, 325), (1150, 425), (1150, 525), (1150, 625), (1150, 725), (1150, 825), (1150, 925),
                     (1200, 1), (1200, 125), (1200, 225), (1200, 325), (1200, 425), (1200, 525), (1200, 625), (1200, 725), (1200, 825), (1200, 925),
                     (1250, 1), (1250, 125), (1250, 225), (1250, 325), (1250, 425), (1250, 525), (1250, 625), (1250, 725), (1250, 825), (1250, 925), (1250, 1025),
                     (1300, 1), (1300, 125), (1300, 225), (1300, 325), (1300, 425), (1300, 525), (1300, 625), (1300, 725), (1300, 825), (1300, 925), (1300, 1025),
                     (1350, 1), (1350, 125), (1350, 225), (1350, 325), (1350, 425), (1350, 525), (1350, 625), (1350, 725), (1350, 825), (1350, 925), (1350, 1025), (1350, 1125),
                     (1400, 1)]
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))

    hypotheses = ["B","SpB"]

    # for compting what jobs are left:
    doneFile = open(done)
    outFileList = [outFile.replace("Razor2013HybridLimit_","").replace(".root\n","") for outFile in doneFile.readlines()]

    # dictionary of src file to output file names
    nToys = 125 # toys per command
    srcDict = {}
    for i in xrange(0,12):
        srcDict[i] = ["%i-%i"%(2*i*nToys,(2*i+1)*nToys-1), "%i-%i"%((2*i+1)*nToys, (2*i+2)*nToys-1)]
        
    totalJobs = 0
    missingFiles = 0
    for gluinopoint, neutralinopoint in gchipairs:
        if neutralinopoint < mchi_lower or neutralinopoint >= mchi_upper: continue
        xsecRange = getXsecRange(box,model,neutralinopoint,gluinopoint)
        for xsecpoint in xsecRange:
            print "Now scanning mg = %.0f, mchi = %.0f, xsec = %.4f"%(gluinopoint, neutralinopoint,xsecpoint)
            for hypo in hypotheses:
                for t in xrange(0,nJobs):
                    xsecstring = str(xsecpoint).replace(".","p")
                    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
                    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
                    output0 = str(outputname.replace("submit/submit_","").replace("xsec",""))
                    output1 = str(outputname.replace("submit/submit_","").replace("xsec",""))
                    for i in xrange(0,12):
                        output0 = output0.replace("B_%i.src"%i,"B_%s"%srcDict[i][0])
                        output1 = output1.replace("B_%i.src"%i,"B_%s"%srcDict[i][1])
                    runJob = False
                    if output0 not in outFileList: 
                        missingFiles+=1
                        runJob = True
                    if output1 not in outFileList:
                        missingFiles+=1
                        runJob = True
                    if not runJob: continue
                    if t3:
                        outputname,ffDir = writeSgeScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,hypo,t)
                        os.system("mkdir -p %s/%s"%(pwd,ffDir))
                        totalJobs+=1
                        time.sleep(3)
                        #queues = "all.q@compute-2-2.local,all.q@compute-2-4.local,all.q@compute-3-10.local,all.q@compute-3-11.local,all.q@compute-3-12.local,all.q@compute-3-2.local,all.q@compute-3-3.local,all.q@compute-3-4.local,all.q@compute-3-5.local,all.q@compute-3-6.local,all.q@compute-3-7.local,all.q@compute-3-8.local,all.q@compute-3-9.local"
                        queues = "all.q@compute-2-2.local"
                        os.system("echo qsub -j y -q "+queues+" -o /dev/null source "+pwd+"/"+outputname)
                        os.system("qsub -j y -q "+queues+" -o /dev/null source "+pwd+"/"+outputname)
                        #os.system("source "+pwd+"/"+outputname)
                    else:    
                        outputname,ffDir = writeBashScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,hypo,t)
                        os.system("mkdir -p %s/%s"%(pwd,ffDir))
                        totalJobs+=1
                        time.sleep(3)
                        #os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        #os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        os.system("echo bsub -q "+queue+" -o /dev/null source "+pwd+"/"+outputname)
                        os.system("bsub -q "+queue+" -o /dev/null source "+pwd+"/"+outputname)
                        #os.system("source "+pwd+"/"+outputname)
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs
