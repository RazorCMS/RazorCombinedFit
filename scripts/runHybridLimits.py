#! /usr/bin/env python
import os.path
import sys
import datetime, time
from getXsecRange import getXsecRange

def getStopMassPoints(neutralinopoint):

    stopMassDict = {
        25: range(150, 825, 25),
        50: range(150, 825, 25),
        75: range(175, 825, 25),
        100: range(200, 825, 25),
        125: range(225, 825, 25),
        150: range(250, 825, 25),
        175: range(275, 825, 25),
        200: range(300, 825, 25),
        225: range(325, 825, 25),
        250: range(350, 825, 25),
        275: range(375, 825, 25),
        300: range(400, 825, 25),
        325: range(425, 825, 25),
        350: range(450, 825, 25),
        375: range(475, 825, 25),
        400: range(500, 825, 25),
        425: range(525, 825, 25),
        450: range(550, 825, 25),
        475: range(575, 825, 25),
        500: range(600, 825, 25),
        525: range(625, 825, 25),
        550: range(650, 825, 25),
        575: range(675, 825, 25),
        600: range(700, 825, 25),
        625: range(725, 825, 25),
        650: range(750, 825, 25),
        675: range(775, 825, 25),
        700: 800,
       }
    return stopMassDict[neutralinopoint]

def writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t, outputDir):
    nToys = 30 ## instead of 500 for the 2011 hybrid

    if box == 'Mu' or box == 'Ele':
        name = "SMS-T2tt_mStop-Combo_mLSP_"+str(neutralinopoint)+".0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR350.0_R0.22360679775"
    else : #assume bjetHS or bjetLS
        name = "SMS-T2tt_mStop-Combo_mLSP_" + str(neutralinopoint) + ".0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR500.0_R0.22360679775"
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
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write("scram project CMSSW_6_2_0\n")
    outputfile.write("cd CMSSW_6_2_0/src\n")
    outputfile.write("eval `scram runtime -sh`\n")
    outputfile.write("git clone -b signal_injection_Lucie git@github.com:RazorCMS/RazorCombinedFit.git\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("mkdir -p lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("make clean; make -j 4\n")

    
    outputfile.write("export NAME=\"T2tt\"\n")
    if box == "BJetHS" or box == "BJetLS" :
        outputfile.write("export LABEL=\"MR500.0_R0.22360679775\"\n")
    else :
        outputfile.write("export LABEL=\"MR350.0_R0.22360679775\"\n")

    if box == 'had' or box == 'BJetHS' or box == 'BJetLS':
        outputfile.write("cp /afs/cern.ch/user/w/wreece/public/Razor2012/500_0_05/FullRegion/Run2012ABCD_Full_Search-280113.root $PWD\n")
        outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/FullFit_BJetHS.root $PWD\n")
    elif box == 'Ele':
        outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/350_0_05/FitRegion/Run2012ABCD_Fit_Ele-120313.root $PWD\n")
    elif box == 'Mu':
        outputfile.write("cp /afs/cern.ch/user/l/lucieg/public/Razor2012/350_0_05/FitRegion/Run2012ABCD_Fit_Mu-120313.root $PWD\n")
      

    outputfile.write("cp /afs/cern.ch/work/l/lucieg/public/forRazorStop/SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY/Datasets/mLSP%s.0/%s_%s_%s.root $PWD\n"%(neutralinopoint,name,massPoint,box))
                
    if box == 'had':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root %s_%s_BJetLS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

    elif box == 'BJetHS':
        nToyOffset = nToys*(2*t)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i FullFit_BJetHS.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))
        nToyOffset = nToys*(2*t+1)
        outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i FullFit_BJetHS.root -l --nuisance-file NuisanceTree_multijet.root --nosave-workspace %s_%s_BJetHS.root -o Razor2012HybridLimit_${NAME}_%s_%s_%s_%s_%i-%i.root %s --xsec %f --toy-offset %i -t %i --multijet\n"%(name,massPoint,massPoint,box,xsecstring,hypo,nToyOffset,nToyOffset+nToys-1,tagHypo,xsecpoint,nToyOffset,nToys))

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
        

    outputfile.write("cp $WD/CMSSW_6_2_0/src/RazorCombinedFit/*.root %s/\n" %outputDir)
    outputfile.write("rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "\nRun the script as follows:\n"
        print "python scripts/runHybridLimits.py Box mLSP OutputTextFile"
        print "with:"
        print "- Box = name of the Box (BJetHS, Mu, etc.)"
        print "- mLSP = LSP mass integer (25, 50, etc.)"
        print "- CompletedOutputTextFile = text file containing all completed output files"
        print ""
        sys.exit()
    box = sys.argv[1]
    neutralinopoint = int(sys.argv[2])
    done = sys.argv[3]
    mg_lower = 150
    mg_upper = 800

    for i in xrange(4,len(sys.argv)):
        if sys.argv[i].find('--mg-lt') != -1: mg_upper = int(sys.argv[i+1])
        if sys.argv[i].find('--mg-geq') != -1: mg_lower = int(sys.argv[i+1])

    nJobs = 50
    nToys = 30 # do 60=30+30 toys each job => 3000 toys
    timestamp = str(datetime.date.today())
    print box
    
    gluinopoints = getStopMassPoints(neutralinopoint)
    gluinopoints = [200,25]
    queue = "8nh"
    
    pwd = os.environ['PWD']

    submitDir = "submit"
    # the output directory must be changed
    outputDir = "~/work/RAZORSTOPLIMITS/Hybrid/"
    print outputDir
   
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s" %outputDir)
    #os.system("ln -s %s" %outputDir)

    hypotheses = ["B","SpB"]

    os.system("touch %s" %done)
    doneFile = open(done)
    outFileList = [outFile.replace(".root\n","") for outFile in doneFile.readlines()]

    # dictionary of src file to output file names
    srcDict = {}
    for i in xrange(0,50):
        srcDict[i] = ["%i-%i"%(2*i*nToys,(2*i+1)*nToys-1), "%i-%i"%((2*i+1)*nToys, (2*i+2)*nToys-1)]

    totalJobs = 0
    missingFiles = 0

    for gluinopoint in gluinopoints:
        if gluinopoint < mg_lower or gluinopoint > mg_upper: continue
        gluinopoint = float(gluinopoint)
        xsecRange = getXsecRange(neutralinopoint,gluinopoint)
        xsecRange = [0.05, 1., 5., 10., 15., 20., 25.]
        for xsecpoint in xsecRange:
            for hypo in hypotheses:
                for t in xrange(0,nJobs):
                    massPoint = "%.1f_%.1f"%(gluinopoint, neutralinopoint)

                    fileNameToCheck = outputDir + "/Razor2012HybridLimit_T2tt_" + massPoint + "_" + box + "_" + str(xsecpoint).replace(".","p")  + "_" + hypo + "_" + str(t)
                    output0 = fileNameToCheck.replace("B_%i"%t, "B_%s"%srcDict[t][0])
                    output1 = fileNameToCheck.replace("B_%i"%t, "B_%s"%srcDict[t][1])
                    
                    runJob = False
                    if output0 not in outFileList:
                        missingFiles += 1
                        print output0
                        runJob = True
                    if output1 not in outFileList:
                        missingFiles += 1
                        runJob = True
                        print output1

                    if not runJob: continue

                    print "Now scanning xsec = %f"%xsecpoint
                    outputname,ffDir = writeBashScript(box,neutralinopoint,gluinopoint,xsecpoint,hypo,t,outputDir)
                    os.system("mkdir -p %s" %ffDir)
                    totalJobs += 1
                    time.sleep(3)
                    os.system("echo bsub -q "+queue+" -o " + ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("bsub -q "+queue+" -o " + ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                        
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs

