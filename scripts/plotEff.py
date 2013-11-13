import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os
from array import *

from scipy.interpolate import Rbf
import numpy as np

boxMap = {"MuEle":"MuEle",
          "MuMu":"MuMu",
          "EleEle":"EleEle",
          "MuJet":"MuJet",
          "MuMultiJet":"MuMultiJet",
          "EleJet":"EleJet",
          "EleMultiJet":"EleMultiJet",
          "Jet1b":"b-Jet",
          "Jet2b":"2b-Jet",
          "MultiJet":"MultiJet"
          }

def interpolate2D(hist,epsilon=1,smooth=0,diagonalOffset=0):
    x = array('d',[])
    y = array('d',[])
    z = array('d',[])
    
    binWidth = float(hist.GetBinWidth(1))
    
    for i in range(1, hist.GetNbinsX()+1):
        for j in range(1, hist.GetNbinsY()+1):
            if hist.GetBinContent(i,j)>0.:
                x.append(hist.GetXaxis().GetBinLowEdge(i))
                y.append(hist.GetYaxis().GetBinLowEdge(j))
                z.append(rt.TMath.Log(hist.GetBinContent(i,j)))
                #z.append(hist.GetBinContent(i,j))
                
    mgMin = hist.GetXaxis().GetBinLowEdge(1)
    mgMax = hist.GetXaxis().GetBinUpEdge(hist.GetNbinsX())
    mchiMin = hist.GetYaxis().GetBinLowEdge(1)
    mchiMax = hist.GetYaxis().GetBinUpEdge(hist.GetNbinsY())
    
    myX = np.linspace(mgMin, mgMax,int((mgMax-mgMin)/binWidth+1))
    myY = np.linspace(mchiMin, mchiMax, int((mchiMax-mchiMin)/binWidth+1))
    myXI, myYI = np.meshgrid(myX,myY)

    rbf = Rbf(x, y, z,function='multiquadric', epsilon=epsilon,smooth=smooth)
    myZI = rbf(myXI, myYI)

    for i in range(1, hist.GetNbinsX()+1):
        for j in range(1, hist.GetNbinsY()+1):
            xLow = hist.GetXaxis().GetBinCenter(i)
            yLow = hist.GetYaxis().GetBinCenter(j)
            if xLow >= yLow+diagonalOffset:
                hist.SetBinContent(i,j,rt.TMath.Exp(myZI[j-1][i-1]))
            else:
                hist.SetBinContent(i,j,0)
    return hist


def set_palette(name="default", ncontours=255):
    # For the canvas:
    rt.gStyle.SetCanvasBorderMode(0)
    rt.gStyle.SetCanvasColor(rt.kWhite)
    rt.gStyle.SetCanvasDefH(400) #Height of canvas
    rt.gStyle.SetCanvasDefW(500) #Width of canvas
    rt.gStyle.SetCanvasDefX(0)   #POsition on screen
    rt.gStyle.SetCanvasDefY(0)
	
    # For the Pad:
    rt.gStyle.SetPadBorderMode(0)
    # rt.gStyle.SetPadBorderSize(Width_t size = 1)
    rt.gStyle.SetPadColor(rt.kWhite)
    rt.gStyle.SetPadGridX(False)
    rt.gStyle.SetPadGridY(False)
    rt.gStyle.SetGridColor(0)
    rt.gStyle.SetGridStyle(3)
    rt.gStyle.SetGridWidth(1)
	
    # For the frame:
    rt.gStyle.SetFrameBorderMode(0)
    rt.gStyle.SetFrameBorderSize(1)
    rt.gStyle.SetFrameFillColor(0)
    rt.gStyle.SetFrameFillStyle(0)
    rt.gStyle.SetFrameLineColor(1)
    rt.gStyle.SetFrameLineStyle(1)
    rt.gStyle.SetFrameLineWidth(1)
    
    # set the paper & margin sizes
    rt.gStyle.SetPaperSize(20,26)
    rt.gStyle.SetPadTopMargin(0.085)
    rt.gStyle.SetPadRightMargin(0.15)
    rt.gStyle.SetPadBottomMargin(0.15)
    rt.gStyle.SetPadLeftMargin(0.17)
    
    # use large Times-Roman fonts
    rt.gStyle.SetTitleFont(42,"xyz")  # set the all 3 axes title font
    rt.gStyle.SetTitleFont(42," ")    # set the pad title font
    rt.gStyle.SetTitleSize(0.06,"xyz") # set the 3 axes title size
    rt.gStyle.SetTitleSize(0.06," ")   # set the pad title size
    rt.gStyle.SetLabelFont(42,"xyz")
    rt.gStyle.SetLabelSize(0.055,"xyz")
    rt.gStyle.SetLabelColor(1,"xyz")
    rt.gStyle.SetLabelOffset(0.015)
    rt.gStyle.SetTextFont(42)
    rt.gStyle.SetTextSize(0.1)
    rt.gStyle.SetStatFont(42)
    
    # use bold lines and markers
    rt.gStyle.SetMarkerStyle(8)
    #rt.gStyle.SetHistLineWidth(1.85)
    rt.gStyle.SetLineStyleString(2,"[12 12]") # postscript dashes
    
    #..Get rid of X error bars
    rt.gStyle.SetErrorX(0.001)
    
    # do not display any of the standard histogram decorations
    rt.gStyle.SetOptTitle(1)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptFit(11111111)
    
    # put tick marks on top and RHS of plots
    rt.gStyle.SetPadTickX(1)
    rt.gStyle.SetPadTickY(1)
    if name == "gray" or name == "grayscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.95, 0.95, 0.65, 0.15]
        green = [1.00, 0.85, 0.7, 0.5, 0.3]
        blue  = [0.95, 0.6, 0.3, 0.45, 0.65]
    elif name == "chris":
	stops = [ 0.34, 0.61, 0.84, 1.00 ]
	red =   [  0.95,  0.95,  0.65,   0.15 ]
	green = [  0.85, 0.7, 0.5,  0.3 ]
	blue =  [ 0.6 , 0.3,  0.45, 0.65 ]
    else:
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00]

    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)
    
    npoints = len(s)
    rt.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    rt.gStyle.SetNumberContours(ncontours)

if __name__ == '__main__':
    model = sys.argv[1]
    tFile = rt.TFile.Open("%s_EffHistos.root"%model)
    set_palette("rainbow",999)
    rt.gStyle.SetPaintTextFormat("4.4f")
    
    rt.gROOT.ProcessLine(".L macros/swissCrossInterpolate.h+")
    rt.gSystem.Load("macros/swissCrossInterpolate_h.so")
    
    c = rt.TCanvas("c","c",500,500)

    
    if model in ["T1tttt"]:
        boxes = ["MultiJet","EleMultiJet","MuMultiJet"]
    elif model in ["T1bbbb"]:
        boxes = ["MultiJet","Jet2b"]
    elif model in ["T2tt"]:
        boxes = ["MultiJet","Jet2b","EleMultiJet","MuJet"]
    elif model in ["T2bb"]:
        boxes = ["MultiJet","Jet2b"]
        
    tFileOut = rt.TFile.Open("%s_EffHistosFINAL.root"%model,"RECREATE")
    for box in boxes:
        eff = tFile.Get("%s_%s"%(model,box))
        
        eff.SetTitle("")
        #eff.SetTitleOffset(1.5)
        if model in ["T1bbbb", "T1tttt"]:
            eff.SetXTitle("m_{gluino} [GeV]")
        elif model in ["T2tt"]:
            eff.SetXTitle("m_{stop} [GeV]")
        elif model in ["T2bb","T6bbHH"]:
            eff.SetXTitle("m_{sbottom} [GeV]")
        eff.SetYTitle("m_{LSP} [GeV]")
        eff.GetXaxis().SetTitleOffset(1.2)
        eff.GetXaxis().SetTitleSize(0.055)
        eff.GetYaxis().SetTitleOffset(1.3)
        eff.GetYaxis().SetTitleSize(0.055)

        if model in ["T1tttt","T1bbbb"]:
            
            if model=="T1tttt": 
                diagonalOffset = 225
                eff.GetXaxis().SetNdivisions(405,False)
                eff.GetYaxis().SetNdivisions(407,False)
            else: 
                diagonalOffset = 25
                eff.GetXaxis().SetNdivisions(409,True)
                eff.GetYaxis().SetNdivisions(409,True)
            if model=="T1bbbb":
                eff.SetBinContent(eff.FindBin(1375,1000), 0)
                for i in range(1,eff.GetNbinsX()+1):
                    eff.SetBinContent(i,1,1.02*eff.GetBinContent(i,3))
            else:
                for i in range(1,eff.GetNbinsX()+1):
                    eff.SetBinContent(i,1,1.05*eff.GetBinContent(i,4))
                    
            if box=="Jet1b" and model=="T1bbbb":
                for mg in range(775,1125, 25):
                    for mchi in range(525, mg, 25):
                        eff.SetBinContent(eff.FindBin(mg,mchi),0.85*eff.GetBinContent(eff.FindBin(mg,mchi)))
            elif model=="T1tttt":
                for mg in range(775,1100, 25):
                    for mchi in range(0, mg, 25):
                        eff.SetBinContent(eff.FindBin(mg,mchi),0.92*eff.GetBinContent(eff.FindBin(mg,mchi)))
                        
        elif model in ["T2tt"]:
            eff.GetXaxis().SetNdivisions(405,True)
            eff.GetYaxis().SetNdivisions(408,True)
            diagonalOffset = 125
            for i in range(1,eff.GetNbinsX()+1):
                eff.SetBinContent(i,1,1.02*eff.GetBinContent(i,2))
        elif model in ["T2bb"]:
            eff.GetXaxis().SetNdivisions(407,True)
            eff.GetYaxis().SetNdivisions(408,True)
            diagonalOffset = 25
        elif model in ["T6bbHH"]:
            eff.GetXaxis().SetNdivisions(205,True)
            eff.GetYaxis().SetNdivisions(209,True)
            diagonalOffset = 300

        eff_new = eff.Clone()
        #eff_new = rt.swissCrossInterpolate(eff_new,"NE")
        if model in ["T2tt"]: smooth = 0
        elif model in ["T2bb"]: smooth = 200
        else: smooth = 50
        eff_new = interpolate2D(eff_new, epsilon=1,smooth=smooth,diagonalOffset=diagonalOffset)
        
        for i in range(1,eff.GetNbinsX()+1):
            for j in range(1, eff.GetNbinsY()+1):
                #if eff.GetBinContent(i,j)>0 : eff.SetBinContent(i,j,eff_new.GetBinContent(i,j))
                eff.SetBinContent(i,j,eff_new.GetBinContent(i,j))
        
        eff.GetXaxis().SetLabelSize(0.04)
        eff.GetYaxis().SetLabelSize(0.04)
        c.SetRightMargin(0.25)
        eff.GetZaxis().SetTitle("Signal Selection Efficiency")
        eff.GetZaxis().SetLabelSize(0.04)
        eff.GetZaxis().SetTitleSize(0.055)
        eff.GetZaxis().SetTitleOffset(1.5)
        eff.GetZaxis().CenterTitle()
        eff.Draw("colz")
        
        l = rt.TLatex()
        l.SetTextAlign(12)
        l.SetTextSize(0.04)
        l.SetTextFont(42)
        l.SetNDC()
        l.DrawLatex(0.2,0.85,"CMS Simulation, #sqrt{s} = 8 TeV")
        if model in ["T1bbbb"]:
            l.DrawLatex(0.2,0.80,"pp#rightarrow#tilde{g}#tilde{g}, #tilde{g}#rightarrowb#bar{b}#tilde{#chi}^{0}")
        elif model in ["T1tttt"]:
            l.DrawLatex(0.2,0.80,"pp#rightarrow#tilde{g}#tilde{g}, #tilde{g}#rightarrowt#bar{t}#tilde{#chi}^{0}")
        elif model in ["T2tt"]:
            l.DrawLatex(0.2,0.80,"pp#rightarrow#tilde{t}#tilde{t}, #tilde{t}#rightarrowt#tilde{#chi}^{0}")
        elif model in ["T2bb"]:
            l.DrawLatex(0.2,0.80,"pp#rightarrow#tilde{b}#tilde{b}, #tilde{b}#rightarrowb#tilde{#chi}^{0}")
        elif model in ["T6bbHH"]:
            l.DrawLatex(0.2,0.80,"pp#rightarrow#tilde{b}#tilde{b}, #tilde{b}#rightarrowb#tilde{#chi}^{0}_{2}#rightarrowbH#tilde{#chi}^{0}_{1}")
            l.DrawLatex(0.2,0.65,"m_{#tilde{#chi}_{2}} = #frac{m_{#tilde{b}}+m_{#tilde{#chi}_{1}}}{2}")
        l.DrawLatex(0.2,0.75,"Razor %s Box"%boxMap[box])

        c.Print("eff_%s_%s.pdf"%(model,box))
        tFileOut.cd()
        eff_new.Write()
