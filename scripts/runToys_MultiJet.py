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
    fitregion = ""
    sideband = ""
    for i in range(1,len(sys.argv)):
        if sys.argv[i] == "FULL":
            fitregion = "--full-region"
            sideband = "FULL"
        else:
            fitregion = ""
            sideband = "Sideband"

    showSidebandL = ""
    config = "config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg"
    queue = "1nd"
    nToys = 2000
    pwd = os.environ['PWD']
    submitDir = "submit"
    fitResultMap = {'TTJets':'FitResults/TTJets_FullRegion.root',
                    'SMCocktail':'FitResults/razor_output_SMCocktail_%s_%s.root'%(sideband,box),
                    'BJetHS_FullRegion':'FitResults/BJetHS_FullRegion.root',
                    'BJetHS_FitRegion':'FitResults/BJetHS_FitRegion_newBinning.root',
                    'BJetLS_FullRegion':'FitResults/BJetLS_FullRegion.root',
                    'BJetLS_FitRegion':'FitResults/BJetLS_FitRegion.root',
                   # 'SingleEle': 'FitResults/SingleEle_Ele_Sideband_Aug13.root'
                    'SingleEle': 'FitResults/SignalInjection_200_25_0p0.root'
                    
                    }
    if box=="BJet":
        mRmin = 500.0
        rMin =  0.22360679775
    else:
        mRmin = 350.
        rMin = 0.22360679775
    label = "MR"+str(mRmin)+"_R"+str(rMin)
    datasetMap = {'WJets':'MC/WJetsToLNu_%s_BTAG_PF_%s.root'%(label,box),
                  'TTJets':'Datasets/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola-Summer12_DR53X-PU_S10_START53_V7A-v1-wreece_231112-Combo_NODUPLICATE_%s_%s.root'%(label,box),
                  'SMCocktail':'MC/SMCocktail_GENTOY_%s_%s.root'%(label,box),
                  'BJetHS_FullRegion':'Datasets/MultiJet-Run2012AB-wreece_231112-Combo_%s_BJetHS.root'%label,
                  'BJetHS_FitRegion':'Datasets/MultiJet-Run2012AB-wreece_231112-Combo_%s_BJetHS.root'%label,
                  'BJetLS_FullRegion':'Datasets/MultiJet-Run2012AB-wreece_231112-Combo_%s_BJetLS.root'%label,
                  'BJetLS_FitRegion':'Datasets/MultiJet-Run2012AB-wreece_231112-Combo_%s_BJetLS.root'%label,
                  'SingleEle':'Datasets/SingleElectron-Run2012ABCD-wreece_220113-Combo_MR350.0_R0.22360679775_Ele.root'
                  }
    resultDir = "/afs/cern.ch/work/l/lucieg/private/toys_0p0_%s"%datasetName
    toyDir = "/afs/cern.ch/work/l/lucieg/private/toys_0p0_%s/%s_%s"%(datasetName,sideband,box)
   # resultDir = "/afs/cern.ch/work/l/lucieg/private/toys_%s"%datasetName
   # toyDir = "/afs/cern.ch/work/l/lucieg/private/toys_%s/%s_%s"%(datasetName,sideband,box)
    ffDir = toyDir+"_FF"


    os.system("mkdir -p %s"%(submitDir)) 
    # prepare the script to run
    outputname = submitDir+"/submit_"+datasetName+"_"+sideband+"_"+box+"_0p0.src"
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('cd %s \n'%pwd)
    outputfile.write('echo $PWD \n')
    outputfile.write('eval `scramv1 runtime -sh` \n')
    outputfile.write("mkdir -p %s; mkdir -p %s; mkdir -p %s \n"%(resultDir,toyDir,ffDir));
    #outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s %s -i %s --save-toys-from-fit %s -t %i --multijet -b \n"%(config,datasetMap[datasetName],fitregion,fitResultMap[datasetName],toyDir,nToys))
    outputfile.write("python scripts/runAnalysis.py -a SingleBoxFit -c %s %s %s -i %s --save-toys-from-fit %s -t %i --multijet -b --signal-injection \n"%(config,datasetMap[datasetName],fitregion,fitResultMap[datasetName],toyDir,nToys))
    outputfile.write("python scripts/convertToyToROOT.py %s/frtoydata_%s -b \n" %(toyDir, box))
    outputfile.write("rm %s.txt \n" %(toyDir))
    outputfile.write("ls %s/frtoydata_*.root > %s.txt \n" %(toyDir, toyDir))
    outputfile.write("python scripts/expectedYield_multijet.py 1 %s/expected_sigbin_%s.root %s %s.txt -b \n"%(ffDir, box, box, toyDir))
    #outputfile.write("python scripts/makeToyPVALUE_multijet.py %s %s/expected_sigbin_%s.root %s %s %s -b \n"%(box, ffDir, box, datasetMap[datasetName], ffDir,showSidebandL))
    outputfile.write("python scripts/makeToyPVALUE_multijet.py %s %s/expected_sigbin_%s.root %s %s %s -b \n"%(box, ffDir, box, fitResultMap[datasetName], ffDir,showSidebandL))
  
    if datasetName.find("Run") != -1:
        outputfile.write("python scripts/make1DProj_MultiJet.py %s %s/expected_sigbin_%s.root %s %s %s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,showSidebandL))
    else:
        outputfile.write("python scripts/make1DProj_MultiJet.py %s %s/expected_sigbin_%s.root %s %s -MC=%s %s -b \n"%(box,ffDir,box,fitResultMap[datasetName],ffDir,datasetName,showSidebandL))
    
    outputfile.close
    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)
    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log.log source "+pwd+"/"+outputname)
