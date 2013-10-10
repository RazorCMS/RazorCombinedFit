#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys
import time
from math import *
from array import *

def getGChiPairs(model):
    if model=="T1bbbb":
        gchipairs = [(400, 50), (400, 200), (400, 300),
                     (450, 50), (450, 200), (450, 300), (450, 400),
                     (500, 50), (500, 200), (500, 300), (500, 400), (500, 450), 
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
                     (925, 50), (925, 200), (925, 300), (925, 400), (925, 450), (925, 500), (925, 525), (925, 550), (925, 600), (925, 625), (925, 650), (925, 700), (925, 750), (925, 800), (925, 850), (925, 875), (925, 900),
                     (950, 525), (950, 550), (950, 600), (950, 625), (950, 650), (950, 700), (950, 750), (950, 800), (950, 850), (950, 900), (950, 925),
                     (1000, 525), (1000, 550), (1000, 600), (1000, 625), (1000, 650), (1000, 700), (1000, 750), (1000, 800), (1000, 850),  (1000, 900), (1000, 950), (1000, 975),
                     (1025, 50), (1025, 200), (1025, 300), (1025, 400), (1025, 450), (1025, 500), (1025, 525), (1025, 550), (1025, 600), (1025, 625), (1025, 650), (1025, 700), (1025, 750), (1025, 800), (1025, 850), (1025, 900), (1025, 950), (1025, 1000),
                     (1050, 550), (1050, 600), (1050, 650), (1050, 700), (1050, 750), (1050, 800), (1050, 825), (1050, 850), (1050, 900), (1050, 950), (1050, 1000), (1050, 1025),
                     (1075, 50), (1075, 200), (1075, 300), (1075, 400), (1075, 450), (1075, 500), (1075, 525), (1075, 550), (1075, 600), (1075, 625), (1075, 650), (1075, 700), (1075, 750), (1075, 800), (1075, 850), (1075, 900), (1075, 950),  (1075, 1000),  (1075, 1050),
                     (1100, 550), (1100, 600), (1100, 650), (1100, 700), (1100, 750), (1100, 800), (1100, 850), (1100, 900), (1100, 950), (1100, 1000), (1100, 1050), (1100, 1075),
                     (1125, 50), (1125, 200), (1125, 300), (1125, 400), (1125, 450), (1125, 500), (1125, 525), (1125, 550), (1125, 600), (1125, 625), (1125, 650), (1125, 700), (1125, 750), (1125, 800), (1125, 850), (1125, 900), (1125, 950), (1125, 1000), (1125, 1050), (1125, 1100),
                     (1150, 550), (1150, 600), (1150, 650), (1150, 700), (1150, 750), (1150, 800), (1150, 850),
                     (1225, 50), (1225, 200), (1225, 300), (1225, 400), (1225, 450), (1225, 500), (1225, 525), (1225, 550), (1225, 600), (1225, 625), (1225, 650), (1225, 700), (1225, 750), (1225, 800), (1225, 850), (1225, 900), (1225, 950), (1225, 1000), (1225, 1050), (1225, 1100), (1225, 1150), (1225, 1200), 
                     (1275, 50), (1275, 200), (1275, 300), (1275, 400), (1275, 450), (1275, 500), (1275, 525), (1275, 550), (1275, 600), (1275, 625), (1275, 650), (1275, 700), (1275, 750), (1275, 800), (1275, 850), (1275, 900), (1275, 950), (1275, 1000), (1275, 1050), (1275, 1100), (1275, 1150), (1275, 1200), (1275, 1250),
                     (1325, 50), (1325, 200), (1325, 300), (1325, 400), (1325, 450), (1325, 500), (1325, 525), (1325, 550), (1325, 600), (1325, 625), (1325, 650), (1325, 700), (1325, 750), (1325, 800), (1325, 850), (1325, 900), (1325, 950), (1325, 1000), (1325, 1050), (1325, 1100), (1325, 1150), (1325, 1200), (1325, 1250), (1325, 1300),
                     (1375, 50), (1375, 200), (1375, 300), (1375, 400), (1375, 450), (1375, 500), (1375, 525), (1375, 550), (1375, 600), (1375, 625), (1375, 650), (1375, 700), (1375, 750), (1375, 800), (1375, 850), (1375, 900), (1375, 950), (1375, 1000), (1375, 1050), (1375, 1100), (1375, 1150), (1375, 1200), (1375, 1250), (1375, 1300), (1375, 1350)]


    if model=="T2tt":
        gchipairs = [(150, 25), (150, 50),
                     (200, 25), (200, 50), (200, 100),
                     (250, 25), (250, 50), (250, 100), (250, 150),
                     (300, 25), (300, 50), (300, 100), (300, 150), (300, 200),
                     (350, 25), (350, 50), (350, 100), (350, 150), (350, 200), (350, 250),
                     (400, 25), (400, 50), (400, 100), (400, 150), (400, 200), (400, 250), (400, 300),
                     (450, 25), (450, 50), (450, 100), (450, 150), (450, 200), (450, 250), (450, 300), (450, 350),
                     (500, 25), (500, 50), (500, 100), (500, 150), (500, 200), (500, 250), (500, 300), (500, 350), (500, 400),
                     (550, 25), (550, 50), (550, 100), (550, 150), (550, 200), (550, 250), (550, 300), (550, 350), (550, 400), (550, 450),
                     (600, 25), (600, 50), (600, 100), (600, 150), (600, 200), (600, 250), (600, 300), (600, 350), (600, 400), (600, 450), (600, 500),
                     (650, 25), (650, 50), (650, 100), (650, 150), (650, 200), (650, 250), (650, 300), (650, 350), (650, 400), (650, 450), (650, 500), (650, 550),
                     (700, 25), (700, 50), (700, 100), (700, 150), (700, 200), (700, 250), (700, 300), (700, 350), (700, 400), (700, 450), (700, 500), (700, 550), (700, 600),
                     (750, 25), (750, 50), (750, 100), (750, 150), (750, 200), (750, 250), (750, 300), (750, 350), (750, 400), (750, 450), (750, 500), (750, 550), (750, 600), (750, 650),
                     (800, 25), (800, 50), (800, 100), (800, 150), (800, 200), (800, 250), (800, 300), (800, 350), (800, 400), (800, 450), (800, 500), (800, 550), (800, 600), (800, 650), (800, 700)]
        
    if model=="T1tttt":
        gchipairs = [(400, 1), (400, 25), (400, 75), (400, 125), (400, 175),
                     (450, 1), (450, 25), (450, 75), (450, 125), (450, 175), (450, 225),
                     (500, 1), (500, 25), (500, 75), (500, 125), (500, 175), (500, 225), (500, 275),
                     (550, 1), (550, 25), (550, 75), (550, 125), (550, 175), (550, 225), (550, 275), (550, 325),
                     (600, 1), (600, 25), (600, 75), (600, 125), (600, 175), (600, 225), (600, 275), (600, 325), (600, 375),
                     (650, 1), (650, 25), (650, 75), (650, 125), (650, 175), (650, 225), (650, 275), (650, 325), (650, 375), (650, 425),
                     (700, 1), (700, 25), (700, 75), (700, 125), (700, 175), (700, 225), (700, 275), (700, 325), (700, 375), (700, 425), (700, 475),
                     (750, 1), (750, 25), (750, 75), (750, 125), (750, 175), (750, 225), (750, 275), (750, 325), (750, 375), (750, 425), (750, 475), (750, 525),
                     (775, 25), (775, 75), (775, 125), (775, 175), (775, 225), (775, 275), (775, 325), (775, 375), (775, 425), (775, 475), (775, 525), (775, 575),
                     (800, 1),
                     (825, 75), (825, 125), (825, 175), (825, 225), (825, 275), (825, 325), (825, 375), (825, 425), (825, 475), (825, 525), (825, 575), (825, 625),
                     (850, 1), (875, 25), (875, 75), (875, 125), (875, 175), (875, 225), (875, 275), (875, 325), (875, 375), (875, 425), (875, 475), (875, 525), (875, 575), (875, 625), (875, 675),
                     (900, 1),
                     (925, 75), (925, 125), (925, 175), (925, 225), (925, 275), (925, 325), (925, 375), (925, 425), (925, 475), (925, 525), (925, 575), (925, 625), (925, 675), (925, 725),
                     (950, 1),
                     (975, 75), (975, 125), (975, 175), (975, 225), (975, 275), (975, 325), (975, 375), (975, 425), (975, 475), (975, 525), (975, 575), (975, 625), (975, 675), (975, 725), (975, 775),
                     (1000, 1),
                     (1025, 75), (1025, 125), (1025, 175), (1025, 225), (1025, 275), (1025, 325), (1025, 375), (1025, 425), (1025, 475), (1025, 525), (1025, 575), (1025, 625), (1025, 675), (1025, 725), (1025, 775), (1025, 825),
                     (1050, 1),
                     (1075, 75), (1075, 125), (1075, 175), (1075, 225), (1075, 275), (1075, 325), (1075, 375), (1075, 425), (1075, 475), (1075, 525), (1075, 575), (1075, 625), (1075, 675), (1075, 725), (1075, 775), (1075, 825), (1075, 875),
                     (1100, 1), (1100, 75), (1100, 125), (1100, 175), (1100, 225), (1100, 275), (1100, 325), (1100, 375), (1100, 425), (1100, 475), (1100, 525), (1100, 575), (1100, 625), (1100, 675), (1100, 725), (1100, 775), (1100, 825), (1100, 875), (1100, 900),
                     (1150, 1), (1150, 75), (1150, 125), (1150, 175), (1150, 225), (1150, 275), (1150, 325), (1150, 375), (1150, 425), (1150, 475), (1150, 525), (1150, 575), (1150, 625), (1150, 675), (1150, 725), (1150, 775), (1150, 825), (1150, 875), (1150, 925), (1150, 950),
                     (1200, 1), (1200, 25), (1200, 75), (1200, 125), (1200, 175), (1200, 225), (1200, 275), (1200, 325), (1200, 375), (1200, 425), (1200, 475), (1200, 525), (1200, 575), (1200, 625), (1200, 675), (1200, 725), (1200, 775), (1200, 825), (1200, 875), (1200, 925), (1200, 975), (1200, 1000),
                     (1250, 1), (1250, 75), (1250, 125), (1250, 175), (1250, 225), (1250, 275), (1250, 325), (1250, 375), (1250, 425), (1250, 475), (1250, 525), (1250, 575), (1250, 625),(1250, 675), (1250, 725), (1250, 775), (1250, 825), (1250, 875), (1250, 925), (1250, 975), (1250, 1025),
                     (1300, 1), (1300, 75), (1300, 125), (1300, 175), (1300, 225), (1300, 275), (1300, 325), (1300, 375), (1300, 425), (1300, 475), (1300, 525), (1300, 575), (1300, 625), (1300, 675), (1300, 725), (1300, 775), (1300, 825), (1300, 875), (1300, 925), (1300, 975), (1300, 1025), (1300, 1075),
                     (1350, 1), (1350, 75), (1350, 125), (1350, 175), (1350, 225), (1350, 275), (1350, 325), (1350, 375), (1350, 425), (1350, 475), (1350, 525), (1350, 575), (1350, 625), (1350, 675), (1350, 725), (1350, 775), (1350, 825), (1350, 875), (1350, 925), (1350, 975), (1350, 1025), (1350, 1075), (1350, 1125),
                     (1400, 1), (1400, 75), (1400, 125), (1400, 175), (1400, 225), (1400, 275), (1400, 325), (1400, 375), (1400, 425), (1400, 475), (1400, 525), (1400, 575), (1400, 625), (1400, 675), (1400, 725), (1400, 775), (1400, 825), (1400, 875), (1400, 925), (1400, 975), (1400, 1025), (1400, 1075), (1400, 1125), (1400, 1175)]

        
    if model=="T6bbHH":
        gchipairs = [(325, 25),
                     (350, 25), (350, 50),
                     (375, 25), (375, 50), (375, 75),
                     (400, 25), (400, 50), (400, 75), (400, 100),
                     (425, 25), (425, 50), (425, 75), (425, 100), (425, 125),
                     (450, 25), (450, 50), (450, 75), (450, 100), (450, 125), (450, 150),
                     (475, 25), (475, 50), (475, 75), (475, 100), (475, 125), (475, 150), (475, 175),
                     (500, 25), (500, 50), (500, 75), (500, 100), (500, 125), (500, 150), (500, 175), (500, 200),
                     (525, 25), (525, 50), (525, 75), (525, 100), (525, 125), (525, 150), (525, 175), (525, 200), (525, 225),
                     (550, 25), (550, 50), (550, 75), (550, 100), (550, 125), (550, 150), (550, 175), (550, 200), (550, 225), (550, 250),
                     (575, 25), (575, 50), (575, 75), (575, 100), (575, 125), (575, 150), (575, 175), (575, 200), (575, 225), (575, 250), (575, 275),
                     (600, 25), (600, 50), (600, 75), (600, 100), (600, 125), (600, 150), (600, 175), (600, 200), (600, 225), (600, 250), (600, 275), (600, 300),
                     (625, 25), (625, 50), (625, 75), (625, 100), (625, 125), (625, 150), (625, 175), (625, 200), (625, 225), (625, 250), (625, 275), (625, 300), (625, 325),
                     (650, 25), (650, 50), (650, 75), (650, 100), (650, 125), (650, 150), (650, 175), (650, 200), (650, 225), (650, 250), (650, 275), (650, 300), (650, 325), (650, 350),
                     (675, 25), (675, 50), (675, 75), (675, 100), (675, 150), (675, 225), (675, 250), (675, 275), (675, 300), (675, 325), (675, 350), (675, 375),
                     (700, 25), (700, 50), (700, 75), (700, 100), (700, 125), (700, 150), (700, 175), (700, 200), (700, 225), (700, 250), (700, 275), (700, 300), (700, 325), (700, 350), (700, 375), (700, 400)]
        
    
    if model=="T2bb":
        gchipairs = [(100, 1), (100, 50),
                     (150, 1), (150, 50), (150, 100),
                     (200, 1), (200, 50), (200, 100), (200, 150),
                     (250, 1), (250, 50), (250, 100), (250, 150), (250, 200),
                     (300, 1), (300, 50), (300, 100), (300, 150), (300, 200), (300, 250),
                     (350, 1), (350, 50), (350, 100), (350, 150), (350, 200), (350, 250), (350, 300),
                     (400, 1), (400, 50), (400, 100), (400, 150), (400, 200), (400, 250), (400, 300), (400, 350),
                     (450, 1), (450, 50), (450, 100), (450, 150), (450, 200), (450, 250), (450, 300), (450, 350), (450, 400),
                     (500, 1), (500, 50), (500, 100), (500, 150), (500, 200), (500, 250), (500, 300), (500, 350), (500, 400), (500, 450),
                     (550, 1), (550, 50), (550, 100), (550, 150), (550, 200), (550, 250), (550, 300), (550, 350), (550, 400), (550, 450), (550, 500),
                     (600, 1), (600, 50), (600, 100), (600, 150), (600, 200), (600, 250), (600, 300), (600, 350), (600, 400), (600, 450), (600, 500), (600, 550),
                     (650, 1), (650, 50), (650, 100), (650, 150), (650, 200), (650, 250), (650, 300), (650, 350), (650, 400), (650, 450), (650, 500), (650, 550), (650, 600),
                     (700, 1), (700, 50), (700, 100), (700, 150), (700, 200), (700, 250), (700, 300), (700, 350), (700, 400), (700, 450), (700, 500), (700, 550), (700, 600), (700, 650),
                     (750, 1), (750, 50), (750, 100), (750, 150), (750, 200), (750, 250), (750, 300), (750, 350), (750, 400), (750, 450), (750, 500), (750, 550), (750, 600), (750, 650), (750, 700),
                     (775, 1), (775, 50), (775, 100), (775, 150), (775, 200), (775, 250), (775, 300), (775, 350), (775, 400), (775, 450), (775, 500), (775, 550), (775, 600), (775, 650), (775, 700), (775, 725)]
        
    return gchipairs

    
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
    
    combineDir = "/afs/cern.ch/work/%s/%s/RAZORLIMITS/Combine/"%(user[0],user)
    
    outputfile.write('#!/usr/bin/env bash -x\n')
    outputfile.write("export TWD=/tmp/${USER}/Razor2013_%s_%s_%s_%s_%i\n"%(model,massPoint,box,xsecstring,t))
    outputfile.write("mkdir -p $TWD\n")
    outputfile.write("cd $TWD\n")
    outputfile.write("export SCRAM_ARCH=slc5_amd64_gcc472\n")
    outputfile.write("scram project CMSSW_6_2_0\n")
    outputfile.write("cd CMSSW_6_2_0/src\n")
    outputfile.write("eval `scram runtime -sh`\n")
    outputfile.write("export WD=/tmp/${USER}/Razor2013_%s_%s_%s_%s_%i/CMSSW_6_2_0/src\n"%(model,massPoint,box,xsecstring,t))
    outputfile.write("git clone git@github.com:RazorCMS/RazorCombinedFit.git\n")
    outputfile.write("cd RazorCombinedFit\n")
    outputfile.write("mkdir -p lib\n")
    outputfile.write("source setup.sh\n")
    outputfile.write("make clean; make -j 4\n")
    
    outputfile.write("export NAME=\"%s\"\n"%model)
    outputfile.write("export LABEL=\"%s\"\n"%label)
    
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/FULLFits2012ABCD.root $PWD\n")
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}/${NAME}_%s_${LABEL}*.root $PWD\n"%massPoint)
    outputfile.write("cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/NuisanceTreeISR.root $PWD\n")
        
    outputfile.write("python scripts/prepareCombine.py %s ${NAME} FULLFits2012ABCD.root ${NAME}_%s_${LABEL}_%s.root"%(box,massPoint,box))
    
    outputfile.write("cp $WD/RazorCombinedFit/*.root %s \n"%combineDir)
    outputfile.write("cd; rm -rf $WD\n")
    
    outputfile.close

    return outputname,ffDir

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "\nRun the script as follows:\n"
        print "python scripts/runCombineLimits.py Box Model Queue CompletedOutputTextFile"
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
    mg_lower = 0
    mg_upper = 2025
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--t3")!=-1: t3 = True
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--mchi-lt")!=-1: mchi_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mchi-geq")!=-1: mchi_lower = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-lt")!=-1: mg_upper = float(sys.argv[i+1])
        if sys.argv[i].find("--mg-geq")!=-1: mg_lower = float(sys.argv[i+1])
    
    nJobs = 1 # do 1 toy each job => 1 toy
    
    print box, model, queue

    gchipairs = getGChiPairs(model)

    gchipairs = reversed(gchipairs)
    
    pwd = os.environ['PWD']
    
    submitDir = "submit"
    outputDir = "output"+box
    
    os.system("mkdir -p %s"%(submitDir))
    os.system("mkdir -p %s"%(outputDir))

    hypotheses = ["SpB"]

    # for compting what jobs are left:
    doneFile = open(done)
    outFileList = [outFile.replace("Razor2013CombineLimit_","").replace(".root\n","") for outFile in doneFile.readlines()]

    # dictionary of src file to output file names
    nToys = 1 # toys per command
    srcDict = {}
    for i in xrange(0,nJobs):
        srcDict[i] = ["0-0"]
        
    totalJobs = 0
    missingFiles = 0
    for gluinopoint, neutralinopoint in gchipairs:
        if neutralinopoint < mchi_lower or neutralinopoint >= mchi_upper: continue
        if gluinopoint < mg_lower or gluinopoint >= mg_upper: continue
        xsecRange = getXsecRange(model,neutralinopoint,gluinopoint)
        for xsecpoint in xsecRange:
            print "Now scanning mg = %.0f, mchi = %.0f, xsec = %.4f"%(gluinopoint, neutralinopoint,xsecpoint)
            for hypo in hypotheses:
                for t in xrange(0,nJobs):
                    xsecstring = str(xsecpoint).replace(".","p")
                    massPoint = "MG_%f_MCHI_%f"%(gluinopoint, neutralinopoint)
                    outputname = submitDir+"/submit_"+model+"_"+massPoint+"_"+box+"_xsec"+xsecstring+"_"+hypo+"_"+str(t)+".src"
                    output0 = str(outputname.replace("submit/submit_","").replace("xsec",""))
                    for i in xrange(0,nJobs):
                        output0 = output0.replace("SpB_%i.src"%i,"SpB_%s"%srcDict[i][0])
                    runJob = False
                    if output0 not in outFileList: 
                        missingFiles+=1
                        runJob = True
                    if not runJob: continue
                    outputname,ffDir = writeBashScript(box,model,submitDir,neutralinopoint,gluinopoint,xsecpoint,hypo,t)
                    os.system("mkdir -p %s/%s"%(pwd,ffDir))
                    totalJobs+=1
                    time.sleep(3)
                    os.system("echo bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
                    os.system("bsub -q "+queue+" -o "+pwd+"/"+ffDir+"/log_"+str(t)+".log source "+pwd+"/"+outputname)
    print "Missing files = ", missingFiles
    print "Total jobs = ", totalJobs
