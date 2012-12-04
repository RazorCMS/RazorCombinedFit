#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
from array import *

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "\nRun the script as follows:\n"
        print "python scripts/runToys DatasetName BoxName FitRegion FitMode"
        print "with:"
        print "   DatasetName = name of the sample (TTJets, WJets, SMCocktail, MuHad-Run2012AB, ElectronHad-Run2012AB)"
        print "   BoxName = name of the Box (MuMu, MuEle, etc)"
        print "   FitRegion = name of the fit region (FULL, Sideband)"
        print "   FitMode = 2D or 3D"
        print ""
        print "After the inputs you can specify the following options"
        print " --newFR    this is the new fit region"
        sys.exit()
    
    datasetName = sys.argv[1]
    box = sys.argv[2]
    sideband = sys.argv[3]
    fitmode = sys.argv[4]
    
    newFR = False
    tagFR = ""
    fit3D = False
    tag3D = ""
    for i in range(4,len(sys.argv)):
        if sys.argv[i] == "--newFR":
            newFR = True
            tagFR = "--newFR"
    if fitmode == "3D":
        fit3D = True
        tag3D = "--3D"
        
    fitResultsDir = "FitResults_%s"%fitmode
    config = "config_summer2012/RazorInclusive2012_%s_btag.config"%fitmode

    if newFR:
        fitResultsDir = "FitResults_%s_newFR"%fitmode
        config = "config_summer2012/RazorInclusive2012_%s_newFR_btag.config"%fitmode
        
    queue = "1nd"
    nToys = 3225
    pwd = os.environ['PWD']
    submitDir = "submit"
    fitResultMap = {'WJets':'%s/razor_output_WJets_%s_%s.root'%(fitResultsDir,sideband,box),
                    'TTJets':'%s/razor_output_TTJets_%s_%s.root'%(fitResultsDir,sideband,box),
                    'SMCocktail':'%s/razor_output_SMCocktail_%s_%s.root'%(fitResultsDir,sideband,box),
                    'MuHad-Run2012AB':'%s/razor_output_MuHad-Run2012AB_%s_%s.root'%(fitResultsDir,sideband,box),
                    'ElectronHad-Run2012AB':'%s/razor_output_ElectronHad-Run2012AB_%s_%s.root'%(fitResultsDir,sideband,box)}
    if box == "TauTauJet" or box=="Jet" or box=="MultiJet":
        mRmin = 400.
        rMin = 0.424264068712
    else:
        mRmin = 350.
        rMin = 0.331662479036
    if newFR:
        mRmin = 250.
        rMin = 0.316227766017
    label = "MR"+str(mRmin)+"_R"+str(rMin)
    datasetMap = {'WJets':'MC/WJetsToLNu_%s_BTAG_PF_%s.root'%(label,box),
                  'TTJets':'MC/TTJets_%s_BTAG_PF_%s.root'%(label,box),
                  'SMCocktail':'MC/SMCocktail_GENTOY_%s_%s.root'%(label,box),
                  'MuHad-Run2012AB':'DATA/MuHad-Run2012AB_%s_BTAG_PF_%s.root'%(label,box),
                  'ElectronHad-Run2012AB':'DATA/ElectronHad-Run2012AB_%s_BTAG_PF_%s.root'%(label,box)}
    resultDir = "toys_%s_%s"%(datasetName,fitmode)
    toyDir = resultDir+"/%s_%s"%(sideband,box)
    ffDir = toyDir+"_FF"


    os.system("mkdir -p %s"%(submitDir)) 
    # prepare the script to run
    outputname = submitDir+"/submit_"+datasetName+"_"+fitmode+"_"+sideband+"_"+box+".src"
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('cd %s \n'%pwd)
    outputfile.write('echo $PWD \n')
    outputfile.write('eval `scramv1 runtime -sh` \n')
    outputfile.write("mkdir -p %s; mkdir -p %s; mkdir -p %s \n"%(resultDir,toyDir,ffDir));
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s --fit-region %s -i %s --save-toys-from-fit %s -t %i -b \n"%(config,datasetMap[datasetName],sideband,fitResultMap[datasetName],toyDir,nToys))
    outputfile.write("python scripts/convertToyToROOT.py %s/frtoydata_%s -b \n" %(toyDir, box))
    outputfile.write("rm %s.txt \n" %(toyDir))
    outputfile.write("ls %s/frtoydata_*.root > %s.txt \n" %(toyDir, toyDir))
    outputfile.write("python scripts/expectedYield_sigbin.py 1 %s/expected_sigbin_%s.root %s %s.txt %s %s -b \n"%(ffDir, box, box, toyDir,tagFR,tag3D))
    outputfile.write("python scripts/makeToyPVALUE_sigbin.py %s %s/expected_sigbin_%s.root %s %s %s %s -b \n"%(box, ffDir, box, datasetMap[datasetName], ffDir,tagFR,tag3D))
    if datasetName.find("Run") != -1:
        outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s %s %s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,tagFR,tag3D))
    else:
        outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s -MC=%s %s %s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,datasetName,tagFR,tag3D))
    
    outputfile.close
    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)
    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)
