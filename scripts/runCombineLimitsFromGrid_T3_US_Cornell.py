#! /usr/bin/env python
import ROOT as rt
# import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys, re
# import time
from math import *
from array import *
from getGChiPairs import *


def xsecs_to_scan(mglu, asymfile=None, refxsecfile=None):
    """For a given (mg, mchi) point, returns the xsecs to scan"""

    xsec_range = []

    exp_xsec = exp.GetBinContent(exp.FindBin(mglu))
    susy = refxsecfile.Get("stop")

    if asymfile is not None:
        exp_xsec = exp.GetBinContent(exp.FindBin(mglu))
        print "We are using the asymptotic file"
        # for i in range(-2, 4):
        for i in range(-2, 2):
            for j in range(1, 10, 3):
                xsec_range.append(exp_xsec * pow(10, int(i)) * int(j))

    elif refxsecfile is not None:
        susy = refxsecfile.Get("stop")
        print "We are not using the asymptotic file"
        susy_xsec = susy.GetBinContent(susy.FindBin(mglu))
        for i in range(-2, 1):
            for j in [1] + range(2, 5, 2):
                if i == 1 and mglu >= 300.:
                    continue
                elif i == -2 and mglu >= 500.:
                    continue
                xsec_range.append(susy_xsec * pow(10, i) * j)

    else:
        xsec_range = [0, 1]
    return xsec_range


def ref_xsec(mglu, gluino_hist=None):
    """Returns the value in pb of the SUSY xsec for a given mass point"""
    if gluino_hist is not None:
        ref_sec = gluino_hist.GetBinContent(gluino_hist.FindBin(mglu))
        print "INFO: ref xsec taken to be: %s mass %d, ref xsec = %f fb" %\
            (gluino_hist.GetName(), mglu, ref_sec)
    else:
        ref_sec = 1.
    return ref_sec


def writeStep2BashScript(box, model, submitDir, neutralinoPoint, gluinoPoint, fitRegion, xsec):
    """This is for step2"""
    massPoint = "%0.1f_%0.1f" % (gluinoPoint, neutralinoPoint)
    mLSP = int(float(re.split('_', massPoint)[-1]))
    SMS = ('SMS-T2tt_mStop-Combo_mLSP_%s.0_8TeV-Pythia6Z-Summer12-START52_V9_'
           'FSIM-v1-SUSY_MR350.0_R0.387298334621') % mLSP
    xsecString = str(xsec).replace(".", "p")

    t = 0
    # prepare the script to run
    outputname = submitDir + "/submit_" + model + "_" + massPoint + "_" +\
        fitRegion + "_" + box + "_" + str(t) + ".src"
    outputfile = open(outputname, 'w')

    ffDir = outputDir + "/logs_" + model + "_" + massPoint + "_" + fitRegion\
        + "_" + box

    user = os.environ['USER']
    current_dir = os.environ['PWD']
    smsdir = 'Leptonic/Dec2014/T2ttMu0p15/'

    temp_dir = ('/home/%s/cms/CMSSW_6_1_2/src/RazorCombinedFit_lucieg_May29/'
                'temp_dir_step1/%s_%s_%s_%s_%i' %
                (user, model, massPoint, box, xsecString, t))
    if not os.path.exists(temp_dir):
        os.system('mkdir -p %s' % temp_dir)

    combine_dir = ('/home/%s/cms/CMSSW_6_1_2/src/'
                   'RazorCombinedFit_lucieg_May29/'
                   'CombineToys/%s/step1/mLSP%s') %\
        (user, model, neutralinoPoint)
    step2_dir = ('/home/%s/cms/CMSSW_6_1_2/src/RazorCombinedFit_lucieg_May29/'
                 'CombineToys/%s/step2/mLSP%s') %\
        (user, model, neutralinoPoint)

    outputfile.write('#$ -S /bin/sh\n')
    outputfile.write('#$ -l arch=lx24-amd64\n')
    outputfile.write('#PBS -m ea\n')
    outputfile.write('#PBS -M es575@cornell.edu\n')
    outputfile.write('#PBS -j oe\n\n')
    outputfile.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    outputfile.write('export SCRAM_ARCH=slc5_amd64_gcc462\n\n')

    if not os.path.exists(step2_dir):
        outputfile.write('mkdir -p %s\n' % step2_dir)

    outputfile.write('cd %s\n' % current_dir)
    outputfile.write('eval `scramv1 runtime -sh`\n')
    outputfile.write('source setup.sh\n\n')

    outputfile.write("export NAME=\"%s\"\n" % model)
    boxes = box.split("_")
    seed = -1

    outputfile.write('cd %s\n\n' % temp_dir)

    # Create data card with reference cross section
    # outputfile.write("python %s/scripts/prepareCombineSimple.py --box %s "
    #                  "--model %s -i %s/fit_results/fit_result_%s_%s.root "
    #                  "-c %s/config_summer2012/RazorMultiJet2013_3D_hybrid.config "
    #                  "--xsec %f %s/Datasets/%s/mLSP%s/%s_%s_%s.root\n\n"\
    #                  % (current_dir, box, model, current_dir, fitRegion, box,
    #                     current_dir, xsec, current_dir, model,
    #                     neutralinoPoint, SMS, massPoint, box))
    outputfile.write("python %s/scripts/prepareCombineSimple.py --box %s -i "
                     "%s/fit_results/razor_output_Rsq_gte0.15_%s.root "
                     "--refXsec=%s "
                     "--fitmode=3D --pdfmode=split --leptonic "
                     "%s/%s/%s_%s_%s.root %s\n\n"
                     % (current_dir, box,
                        current_dir, box,
                        xsec,
                        current_dir, smsdir, SMS, massPoint, box, model))

    outputfile.write("hadd -f %s/higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew."
                     "mH120.root %s/higgsCombineGrid${NAME}_%s_xsec*_%s_%s_*."
                     "HybridNew.mH120.*.root\n\n" %
                     (combine_dir, massPoint, fitRegion, box, t, combine_dir,
                      massPoint, fitRegion, box))

    # Varying the expectedFromGrid parameter, i.e. 1sigma and 2sigma edges
    outputfile.write("/home/%s/cms/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine "
                     "-M HybridNew --frequentist --grid="
                     "%s/higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root "
                     "--expectedFromGrid 0.025 -n Expected025${NAME}_%s_%s_%s_%i "
                     "%s/razor_combine_%s_${NAME}_%s.txt --rMax 100000.\n" %
                     (user, combine_dir, massPoint, fitRegion, box, t, massPoint,
                      fitRegion, box, t, temp_dir, box, massPoint))
    outputfile.write("/home/%s/cms/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine "
                     "-M HybridNew --frequentist --grid="
                     "%s/higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root "
                     "--expectedFromGrid 0.16 -n Expected160${NAME}_%s_%s_%s_%i "
                     "%s/razor_combine_%s_${NAME}_%s.txt --rMax 100000.\n" %
                     (user, combine_dir, massPoint, fitRegion, box, t, massPoint,
                      fitRegion, box, t, temp_dir, box, massPoint))
    outputfile.write("/home/%s/cms/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine "
                     "-M HybridNew --frequentist --grid="
                     "%s/higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root "
                     "--expectedFromGrid 0.50 -n Expected500${NAME}_%s_%s_%s_%i "
                     "%s/razor_combine_%s_${NAME}_%s.txt --rMax 100000.\n" %
                     (user, combine_dir, massPoint, fitRegion, box, t, massPoint,
                      fitRegion, box, t, temp_dir, box, massPoint))
    outputfile.write("/home/%s/cms/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine "
                     "-M HybridNew --frequentist --grid="
                     "%s/higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root "
                     "--expectedFromGrid 0.84 -n Expected840${NAME}_%s_%s_%s_%i "
                     "%s/razor_combine_%s_${NAME}_%s.txt --rMax 100000.\n" %
                     (user, combine_dir, massPoint, fitRegion, box, t, massPoint,
                      fitRegion, box, t, temp_dir, box, massPoint))
    outputfile.write("/home/%s/cms/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine "
                     "-M HybridNew --frequentist --grid="
                     "%s/higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root "
                     "--expectedFromGrid 0.975 -n Expected975${NAME}_%s_%s_%s_%i "
                     "%s/razor_combine_%s_${NAME}_%s.txt --rMax 100000.\n" %
                     (user, combine_dir, massPoint, fitRegion, box, t, massPoint,
                      fitRegion, box, t, temp_dir, box, massPoint))
    outputfile.write("/home/%s/cms/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine "
                     "-M HybridNew --frequentist --grid="
                     "%s/higgsCombineGrid${NAME}_%s_%s_%s_%i.HybridNew.mH120.root "
                     "-n Observed${NAME}_%s_%s_%s_%i %s/razor_combine_%s_"
                     "${NAME}_%s.txt --rMax 100000.\n\n" %
                     (user, combine_dir, massPoint, fitRegion, box, t, massPoint,
                      fitRegion, box, t, temp_dir, box, massPoint))

    outputfile.write("hadd -f %s/higgsCombineToys${NAME}_%s_%s_%s_%i.HybridNew."
                     "mH120.root "
                     "%s/higgsCombineExpected025*.root "
                     "%s/higgsCombineExpected160*.root "
                     "%s/higgsCombineExpected500*.root "
                     "%s/higgsCombineExpected840*.root "
                     "%s/higgsCombineExpected975*.root "
                     "%s/higgsCombineObserved*.root\n\n" %
                     (step2_dir, massPoint, fitRegion, box, t, temp_dir,
                      temp_dir, temp_dir, temp_dir, temp_dir, temp_dir))
    outputfile.write("rm -f %s/roostats*\n" % temp_dir)
    outputfile.write("mv -f %s/higgsCombineExpect* %s/\n" %
                     (temp_dir, step2_dir))
    outputfile.write("mv -f %s/higgsCombineObserv* %s/\n\n" %
                     (temp_dir, step2_dir))
    outputfile.write('exit')
    outputfile.close

    return outputname, ffDir


def writeStep1BashScript(box, model, submitDir, neutralinoPoint, gluinoPoint,
                         xsecPoint, refXsec, fitRegion, signalRegion, t,
                         nToysPerJob, iterations):

    massPoint = "%0.1f_%0.1f" % (gluinoPoint, neutralinoPoint)
    # workspaceString = ""
    # if workspaceFlag:
    #     workspaceString = "Workspace"
    # penaltyString = ""
    # if penalty:
    #     penaltyString = "--penalty"

    # prepare the script to run
    xsecString = str(xsecPoint).replace(".", "p")
    outputname = submitDir + "/submit_" + model + "_" + massPoint +\
        "_xsec" + xsecString + "_" + fitRegion + "_" + box + "_" + str(t) +\
        ".src"
    outputfile = open(outputname, 'w')

    ffDir = outputDir + "/logs_" + model + "_" + massPoint +\
        "_xsec" + xsecString + "_" + fitRegion + "_" + box
    user = os.environ['USER']
    current_dir = os.environ['PWD']
    smsdir = 'Leptonic/Dec2014/T2ttMu0p15/'

    combine_dir = ('/home/%s/cms/CMSSW_6_1_2/src/'
                   'RazorCombinedFit_lucieg_May29/'
                   'CombineToys/%s/step1/mLSP%s') %\
        (user, model, neutralinoPoint)
    temp_dir = ('/home/%s/cms/CMSSW_6_1_2/src/RazorCombinedFit_lucieg_May29/'
                'temp_dir_step1/%s_%s_%s_%s_%i' %
                (user, model, massPoint, box, xsecString, t))

    if not os.path.exists(combine_dir):
        os.system('mkdir -p %s' % combine_dir)
    if not os.path.exists(temp_dir):
        os.system('mkdir -p %s' % temp_dir)

    outputfile.write('#$ -S /bin/sh\n')
    outputfile.write('#$ -l arch=lx24-amd64\n')
    outputfile.write('#PBS -m ea\n')
    outputfile.write('#PBS -M es575@cornell.edu\n')
    outputfile.write('#PBS -j oe\n\n')
    outputfile.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    outputfile.write('export SCRAM_ARCH=slc5_amd64_gcc472\n\n')

    outputfile.write('cd %s\n' % current_dir)
    outputfile.write('eval `scramv1 runtime -sh`\n')
    outputfile.write('source setup.sh\n\n')
    outputfile.write('cd %s\n' % temp_dir)

    outputfile.write("export NAME=\"%s\"\n" % model)
    boxes = box.split("_")
    sparticle = "stop"
    if model.find("T1") != -1:
        sparticle = "gluino"
    seed = -1
    rSignal = float(xsecPoint)/refXsec
    print "This is the signal strength we are testing now:", rSignal

    mLSP = int(float(re.split('_', massPoint)[-1]))
    SMS = ('SMS-T2tt_mStop-Combo_mLSP_%s.0_8TeV-Pythia6Z-Summer12-START52_V9_'
           'FSIM-v1-SUSY_MR350.0_R0.387298334621') % mLSP

    outputfile.write("python %s/scripts/prepareCombineSimple.py --box %s -i "
                     "%s/fit_results/razor_output_Rsq_gte0.15_%s.root "
                     "--refXsec=%s "
                     "--fitmode=3D --pdfmode=split --leptonic "
                     "%s/%s/%s_%s_%s.root %s\n\n"
                     % (current_dir, box,
                        current_dir, box,
                        xsecPoint,
                        current_dir, smsdir, SMS, massPoint, box, model))

    # outputfile.write("cp -f ./razor_combine_* %s/\n" % temp_dir)
    outputfile.write("/home/%s/cms/CMSSW_6_1_2/bin/slc5_amd64_gcc472/combine "
                     "-M HybridNew -s %i --singlePoint %f --frequentist"
                     " --saveHybridResult --saveToys --testStat LHC --fork 4 "
                     "-T %i --fullBToys -n Grid${NAME}_%s_xsec%s_%s_%s_%i "
                     "--clsAcc 0 --iterations %i "
                     "%s/razor_combine_%s_${NAME}_%s.txt "
                     "--rMax 100000.\n\n" %
                     (user,
                      seed, rSignal,
                      nToysPerJob, massPoint, xsecString, fitRegion, box, t,
                      iterations,
                      temp_dir, box, massPoint))

    outputfile.write("mv higgsCombine*.root %s/ \n" % combine_dir)
    outputfile.write("rm -f roostats-*\n\n")
    outputfile.write("exit")

    outputfile.close

    return outputname, ffDir

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "\nRun the script as follows:\n"
        print "python scripts/runCombineLimits.py Box Model"\
            "CompletedOutputTextFile"
        print "with:"
        print "- Box = name of the Box (MuMu, MuEle, BJetHS_gt6, etc.)"
        print "- Model = T1bbbb, T1tttt, T2tt, etc. "
        print "- CompletedOutputTextFile = text file containing all completed"\
            "output files"
        print ""
        sys.exit()
    box = sys.argv[1]
    name = re.split('_', box)
    box = name[0]

    model = sys.argv[2]
    done = sys.argv[3]
    mchi_lower = 0
    mchi_upper = 2025
    mg_lower = 0
    mg_upper = 2025

    refXsecFile = None
    fitRegion = "FULL"  # Sideband
    signalRegion = "FULL"
    asymptoticFile = None
    nToys = 3000  # do 3000 total toys
    nJobs = 1  # split the toys over 1 jobs
    iterations = 1
    step2 = False
    workspaceFlag = True
    noSub = False
    penalty = False
    for i in xrange(4, len(sys.argv)):
        if sys.argv[i].find("--no-sub") != -1:
            noSub = True
        if sys.argv[i].find("--step2") != -1:
            step2 = True
        if sys.argv[i].find("--mchi-lt") != -1:
            mchi_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mchi-geq") != -1:
            mchi_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-lt") != -1:
            mg_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-geq") != -1:
            mg_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--iterations") != -1:
            iterations = int(sys.argv[i+1])
        if sys.argv[i].find("--xsec") != -1:
            if sys.argv[i].find("--xsec-file") != -1:
                refXsecFile = sys.argv[i+1]
            else:
                refXsec = float(sys.argv[i+1])
        if sys.argv[i].find("--asymptotic-file") != -1:
            asymptoticFile = sys.argv[i+1]
        if sys.argv[i].find("--fit-region") != -1:
            fitRegion = sys.argv[i+1]
        if sys.argv[i].find("--signal-region") != -1:
            signalRegion = sys.argv[i+1]
        if sys.argv[i].find("--toys") != -1:
            nToys = int(sys.argv[i+1])
        if sys.argv[i].find("--jobs") != -1:
            nJobs = int(sys.argv[i+1])
        if sys.argv[i].find("--work") != -1:
            workspaceFlag = True
        if sys.argv[i].find("--no-work") != -1:
            workspaceFlag = False
        if sys.argv[i].find("--penalty") != -1:
            penalty = True

    if refXsecFile is not None:
        print "INFO: Input ref xsec file!", refXsecFile
        gluinoFile = rt.TFile.Open(refXsecFile, "READ")
        gluinoHistName = refXsecFile.split("/")[-1].split(".")[0]
        gluinoHist = gluinoFile.Get(gluinoHistName)

    nToysPerJob = int(nToys/nJobs)
    nXsec = 5

    # Getting asymptotic limits as input
    if asymptoticFile is not None:
        print "INFO: Input ref xsec file!"
        asymptoticRootFile = rt.TFile.Open(asymptoticFile, "READ")
        expMinus2 = asymptoticRootFile.Get("xsecUL_ExpMinus2_%s_%s" %
                                           (model, box))
        expPlus2 = asymptoticRootFile.Get("xsecUL_ExpPlus2_%s_%s" %
                                          (model, box))
        expMinus = asymptoticRootFile.Get("xsecUL_ExpMinus_%s_%s" %
                                          (model, box))
        expPlus = asymptoticRootFile.Get("xsecUL_ExpPlus_%s_%s" %
                                         (model, box))
        exp = asymptoticRootFile.Get("xsecUL_Exp_%s_%s" % (model, box))

    print box, model

    gchipairs = getGChiPairs(model)

    gchipairs = reversed(gchipairs)

    pwd = os.environ['PWD']

    if step2:
        outputDir = "output" + model + fitRegion + box + '/step2'
        submitDir = "submit" + model + fitRegion + box + '/step2'
    else:
        outputDir = "output" + model + fitRegion + box + '/step1'
        submitDir = "submit" + model + fitRegion + box + '/step1'

    os.system("mkdir -p %s" % (submitDir))
    os.system("mkdir -p %s" % (outputDir))

    # for computing what jobs are left:
    doneFile = open(done)
    outFileList = []
    if step2:
        for outFile in doneFile.readlines():
            if outFile.find("higgsCombineObserved%s" % model) != -1:
                outItem = outFile.replace("higgsCombineObserved", "")\
                    .replace(".HybridNew.mH120", "").replace(".root\n", "")
                outFileList.append(outItem)
    else:
        for outFile in doneFile.readlines():
            if outFile.find("higgsCombineGrid%s" % model) != -1:
                outItem = outFile.replace("higgsCombineGrid", "").\
                    replace(".HybridNew.mH120", "").replace(".root\n", "")
                outItem = outItem.split(".")[:-1]
                outItem = ".".join(outItem)
                outFileList.append(outItem)

    totalJobs = 0
    missingFiles = 0

    for gluinoPoint, neutralinoPoint in gchipairs:

        if neutralinoPoint < mchi_lower or neutralinoPoint >= mchi_upper:
            continue
        if gluinoPoint < mg_lower or gluinoPoint >= mg_upper:
            continue
        if not neutralinoPoint == 25:
            continue

        massPoint = "%.1f_%.1f" % (gluinoPoint, neutralinoPoint)

        # Get nominal SUSY cross section and cross section range to scan
        refXsec = ref_xsec(gluinoPoint, gluinoHist)
        xsecRange = xsecs_to_scan(gluinoPoint, asymptoticFile)
        # xsecRange = xsecs_to_scan(gluinoPoint, None, gluinoFile)
        print "This is the range to scan", xsecRange

        if step2:
            t = 0
            print "Now scanning mg = %.0f, mchi = %.0f" % (gluinoPoint, neutralinoPoint)
            output0 = model+"_"+massPoint+"_"+fitRegion+"_"+box+"_"+str(t)
            runJob = False
            if output0 not in outFileList:
                    missingFiles += 1
                    runJob = True
            if not runJob:
                continue
            outputname, ffDir = writeStep2BashScript(box, model, submitDir, neutralinoPoint, gluinoPoint, fitRegion, refXsec)
            os.system("mkdir -p %s/%s" % (pwd, ffDir))
            totalJobs += 1
            os.system("echo qsub -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log "+outputname)
            if not noSub:
                # time.sleep(1)
                os.system("qsub -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log "+outputname)
        else:
            for xsecPoint in xsecRange:
                if xsecPoint <= 0:
                    continue
                xsecString = str(xsecPoint).replace(".", "p")
                print "Now scanning mg = %.0f, mchi = %.0f, xsec = %.4f" %\
                    (gluinoPoint, neutralinoPoint, xsecPoint)
                for t in xrange(0, nJobs):
                    output0 = model + "_" + massPoint + "_xsec" + xsecString +\
                        "_" + fitRegion + "_" + box + "_" + str(t)
                    runJob = False
                    if output0 not in outFileList:
                        missingFiles += 1
                        runJob = True
                    if not runJob:
                        continue
                    outputname, ffDir =\
                        writeStep1BashScript(box, model, submitDir,
                                             neutralinoPoint, gluinoPoint,
                                             xsecPoint, refXsec, fitRegion,
                                             signalRegion, t, nToysPerJob,
                                             iterations)
                    os.system("mkdir -p %s/%s" % (pwd, ffDir))
                    totalJobs += 1
                    os.system("echo qsub -o "+ffDir+"/log_"+str(t)+".log " +
                              outputname)
                    if not noSub:
                        # time.sleep(1)
                        os.system("qsub -o "+ffDir+"/log_"+str(t)+".log "+
                                  outputname)
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs
