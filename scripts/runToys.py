#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
from array import *

if __name__ == '__main__':
    datasetName = sys.argv[1]
    box = sys.argv[2]
    sideband = sys.argv[3]
    if sideband == "SidebandL": showSidebandL = "--SidebandL"
    else: showSidebandL = ""
    config = "config_summer2012/RazorInclusive2012_2D_btag.config"
    queue = "1nd"
    nToys = 2000
    pwd = os.environ['PWD']
    submitDir = "submit"
    fitResultMap = {'WJets':'FitResults/razor_output_WJets_%s_%s.root'%(sideband,box),
                    'TTJets':'FitResults/razor_output_TTJets_%s_%s.root'%(sideband,box),
                    'SMCocktail':'FitResults/razor_output_SMCocktail_%s_%s.root'%(sideband,box),
                    'MuHad-Run2012AB':'FitResults/razor_output_MuHad-Run2012AB_%s_%s.root'%(sideband,box),
                    'ElectronHad-Run2012AB':'FitResults/razor_output_ElectronHad-Run2012AB_%s_%s.root'%(sideband,box)}
    if box == "TauTauJet" or box=="Jet" or box=="MultiJet":
        mRmin = 400.
        rMin = 0.424264068712
    else:
        mRmin = 350.
        rMin = 0.331662479036
    label = "MR"+str(mRmin)+"_R"+str(rMin)
    datasetMap = {'WJets':'MC/WJetsToLNu_%s_BTAG_PF_%s.root'%(label,box),
                  'TTJets':'MC/TTJets_%s_BTAG_PF_%s.root'%(label,box),
                  'SMCocktail':'MC/SMCocktail_GENTOY_%s_%s.root'%(label,box),
                  'MuHad-Run2012AB':'DATA/MuHad-Run2012AB_%s_BTAG_PF_%s.root'%(label,box),
                  'ElectronHad-Run2012AB':'DATA/ElectronHad-Run2012AB_%s_BTAG_PF_%s.root'%(label,box)}
    resultDir = "toys_%s"%datasetName
    toyDir = "toys_%s/%s_%s"%(datasetName,sideband,box)
    ffDir = toyDir+"_FF"


    os.system("mkdir -p %s"%(submitDir)) 
    # prepare the script to run
    outputname = submitDir+"/submit_"+datasetName+"_"+sideband+"_"+box+".src"
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
    outputfile.write("python scripts/expectedYield_sigbin.py 1 %s/expected_sigbin_%s.root %s %s.txt -b \n"%(ffDir, box, box, toyDir))
    outputfile.write("python scripts/makeToyPVALUE_sigbin.py %s %s/expected_sigbin_%s.root %s %s %s -b \n"%(box, ffDir, box, datasetMap[datasetName], ffDir,showSidebandL))
    if datasetName.find("Run") != -1:
        outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir))
    else:
        outputfile.write("python scripts/make1DProj.py %s %s/expected_sigbin_%s.root %s %s -MC=%s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,datasetName))
    
    outputfile.close
    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)
    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)
