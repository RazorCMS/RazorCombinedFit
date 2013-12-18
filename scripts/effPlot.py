#! /usr/bin/env python
import os
import os.path
import sys
import time
from array import *
import glob
import ROOT as rt

if __name__ == '__main__':
    
    model = sys.argv[1]
    rt.gStyle.SetPaintTextFormat("4.4f")
    rt.gStyle.SetOptStat(0)
    
    if model in ["T2tt","T1tttt","T2tb","T1tttb","T1tbbb","T1ttbb"]:
        boxes = ["MultiJet","Jet1b","Jet2b","EleJet", "EleMultiJet","EleEle","MuEle","MuMu","MuJet","MuMultiJet"]
    elif model in ["T2bb","T6bbHH","T1bbbb"]:
        boxes = ["MultiJet","Jet1b","Jet2b"]
    effHistos = {}
    for box in boxes:
        if box in ["MultiJet","Jet1b","Jet2b"]:
            label = "MR400.0_R0.5"
        else:
            label = "MR300.0_R0.387298334621"
        
        if model in ["T1tttt"]:
            effHistos[box] = rt.TH2D(model+"_"+box,model+"_"+box, 41, 400, 1425, 56, 0, 1400)
        elif model in ["T1bbbb"]:
            effHistos[box] = rt.TH2D(model+"_"+box,model+"_"+box, 49, 400, 1625, 64, 0, 1600)
        elif model in ["T1tttb","T1ttbb","T1tbbb"]:
            effHistos[box] = rt.TH2D(model+"_"+box,model+"_"+box, 25, 400, 1650, 32, 0, 1600)
        elif model in ["T2tt"]:
            effHistos[box] = rt.TH2D(model+"_"+box,model+"_"+box, 27, 150, 825, 29, 0, 725)
        elif model=="T6bbHH":
            effHistos[box] = rt.TH2D(model+"_"+box,model+"_"+box, 17, 300, 725, 17, 0, 425)
        elif model in ["T2bb"]:
            effHistos[box] = rt.TH2D(model+"_"+box,model+"_"+box, 37, 100, 1025, 40, 0, 1000)
        elif model in ["T2tb"]:
            effHistos[box] = rt.TH2D(model+"_"+box,model+"_"+box, 37, 100, 1025, 40, 0, 1000)
        for mg in xrange(100, 1625, 25):
            for mchi in [1]+range(25, 1625, 25):
                fileName = "/afs/cern.ch/user/w/woodson/public/Razor2013/Signal/%s/%s_MG_%f_MCHI_%f_%s_%s.root"%(model,model,mg,mchi,label,box)
                #fileName = "/data/woodson/NTUPLE_SMS_MISSING//%s_MG_%f_MCHI_%f_%s_%s.root"%(model,mg,mchi,"MR300.0_R0.387298334621",box)
                #destName = "/afs/cern.ch/user/w/woodson/public/Razor2013/Signal/%s/%s_MG_%f_MCHI_%f_%s_%s.root"%(model,model,mg,mchi,"MR300.0_R0.387298334621",box)
                
                if glob.glob(fileName):
                    #os.system("cp %s %s"%(fileName,destName))
                    print fileName
                    tFile  = rt.TFile.Open(fileName)
                    wHisto = tFile.Get("wHisto_pdferr_nom")
                    binX = effHistos[box].GetXaxis().FindBin(mg)
                    binY = effHistos[box].GetYaxis().FindBin(mchi)
                    effHistos[box].SetBinContent(binX,binY,wHisto.GetSumOfWeights())
                    wHisto.Delete()
                    tFile.Close()
                    tFile.Delete()

    outputFile = rt.TFile.Open(model+"_EffHistos.root","recreate")
    for box in boxes:
        effHistos[box].Write()
    outputFile.Close()
        #c = rt.TCanvas("c","c",500,400)
        #effHistos[box].Draw("colzTEXT45")
        #c.Print("effHisto.pdf")
