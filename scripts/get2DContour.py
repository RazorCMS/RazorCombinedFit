import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os
from array import *
import numpy as np
from scipy.interpolate import Rbf

def interpolate2D(hist,epsilon=1,smooth=0):
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
            xLow = hist.GetXaxis().GetBinLowEdge(i)
            yLow = hist.GetYaxis().GetBinLowEdge(j)
            if xLow >= yLow+diagonalOffset:
                hist.SetBinContent(i,j,rt.TMath.Exp(myZI[j-1][i-1]))
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
    rt.gStyle.SetLabelSize(0.05,"xyz")
    rt.gStyle.SetLabelColor(1,"xyz")
    rt.gStyle.SetTextFont(42)
    rt.gStyle.SetTextSize(0.08)
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
    #rt.gStyle.SetOptFit(11111111)
    rt.gStyle.SetOptFit(0)
    
    # put tick marks on top and RHS of plots
    rt.gStyle.SetPadTickX(1)
    rt.gStyle.SetPadTickY(1)
    if name == "gray" or name == "grayscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.95, 0.95, 0.65, 0.15]
        green = [1.00, 0.85, 0.7, 0.5, 0.3]
        blue  = [0.95, 0.6, 0.3, 0.45, 0.65]
    elif name == "chris":
	stops = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
	red =   [ 1.0,   0.95,  0.95,  0.65,   0.15 ]
	green = [ 1.0,  0.85, 0.7, 0.5,  0.3 ]
	blue =  [ 0.95, 0.6 , 0.3,  0.45, 0.65 ]
    elif name == "blue":
	stops = [ 0.0, 0.5, 1.0]
	red =   [ 0.0, 1.0, 0.0]
	green = [ 0.0, 0.0, 0.0]
	blue =  [ 1.0, 0.0, 0.0]
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

def getLogHist(hist):
    logHist = hist.Clone("log"+hist.GetName())
    for i in xrange(1,hist.GetNbinsX()+1):
        for j in xrange(1,hist.GetNbinsY()+1):
            if hist.GetBinContent(i,j) > 0.: logHist.SetBinContent(i,j,rt.TMath.Log(hist.GetBinContent(i,j)))
    return logHist

def getExpHist(logHist):
    hist = logHist.Clone("exp"+logHist.GetName())
    for i in xrange(1,hist.GetNbinsX()+1):
        for j in xrange(1,hist.GetNbinsY()+1):
            if logHist.GetBinContent(i,j) != 0.: hist.SetBinContent(i,j,rt.TMath.Exp(logHist.GetBinContent(i,j)))
    return hist

if __name__ == '__main__':
    box = sys.argv[1]
    model = sys.argv[2]
    directory = sys.argv[3]
    #set_palette("blue",2)

    
    set_palette("rainbow",999)
    rt.gStyle.SetOptStat(0)
    rt.gROOT.ProcessLine(".L macros/swissCrossInterpolate.h+")
    rt.gSystem.Load("macros/swissCrossInterpolate_h.so")
    
    xsecFile = rt.TFile.Open("%s/xsecUL_%s.root"%(directory,box))


    if model=="T1bbbb":
        mgMin = 400
        mgMax = 1425
        mchiMin = 0
        mchiMax = 1400
        binWidth = 25.
        nRebins = 0
        xsecMin = 1.e-3
        xsecMax = 1.
        diagonalOffset = 25
        smooth = 50
    elif model=="T1tttt":
        mgMin = 400
        mgMax = 1425
        mchiMin = 0
        mchiMax = 1200
        binWidth = 25.
        nRebins = 0
        xsecMin = 1.e-3
        xsecMax = 10.
        diagonalOffset = 200.
        smooth = 50
    elif model=="T2tt":
        mgMin = 150
        mgMax = 800
        mchiMin = 0
        mchiMax = 700
        binWidth = 25.
        nRebins = 2
        xsecMin = 1.e-3
        xsecMax = 10.
        diagonalOffset = 400.
        smooth = 50
    elif model=="T2bb":
        mgMin = 100
        mgMax = 825
        mchiMin = 0
        mchiMax = 800
        binWidth = 25.
        nRebins = 0
        xsecMin = 1.e-3
        xsecMax = 10.
        diagonalOffset = 25
        smooth = 50
    elif model=="T6bbHH":
        mgMin = 300
        mgMax = 750
        mchiMin = 0
        mchiMax = 425
        binWidth = 25.
        nRebins = 0
        xsecMin = 9.e-3
        xsecMax = 1.
        diagonalOffset = 325.
        smooth = 50
    
    xsecTree = xsecFile.Get("xsecTree")
    xsecGluino =  rt.TH2D("xsecGluino","xsecGluino",int((mgMax-mgMin)/binWidth),mgMin, mgMax,int((mchiMax-mchiMin)/binWidth), mchiMin, mchiMax)
    xsecGluinoPlus =  rt.TH2D("xsecGluinoPlus","xsecGluinoPlus",int((mgMax-mgMin)/binWidth),mgMin, mgMax,int((mchiMax-mchiMin)/binWidth), mchiMin, mchiMax)
    xsecGluinoMinus =  rt.TH2D("xsecGluinoMinus","xsecGluinoMinus",int((mgMax-mgMin)/binWidth),mgMin, mgMax,int((mchiMax-mchiMin)/binWidth), mchiMin, mchiMax)
    
    clsTypes = ["Exp","ExpMinus","ExpPlus","ObsMinus","ObsPlus","Obs"]
    
    titleMap = {"Exp":"Expected","ExpMinus":"Expected-1#sigma","ExpPlus":"Expected+1#sigma",
                "ObsMinus":"Observed-1#sigma", "ObsPlus":"Observed+1#sigma","Obs":"Observed"}
    whichCLsVar = {"Obs":"xsecULObs_%s"%(box),"ObsPlus":"xsecULObs_%s"%(box),"ObsMinus":"xsecULObs_%s"%(box),
                   "Exp":"xsecULExp_%s"%(box),"ExpPlus":"xsecULExpMinus_%s"%(box),"ExpMinus":"xsecULExpPlus_%s"%(box)}
    xsecUL = {}
    logXsecUL = {}
    rebinXsecUL = {}
    subXsecUL = {}

    contourFinal = {}
    
    for clsType in clsTypes:
        xsecUL[clsType] = rt.TH2D("xsecUL_%s"%clsType,"xsecUL_%s"%clsType,int((mgMax-mgMin)/binWidth),mgMin, mgMax,int((mchiMax-mchiMin)/binWidth), mchiMin, mchiMax)
        xsecTree.Project("xsecUL_%s"%clsType,"mchi:mg",whichCLsVar[clsType])

        # Change xsecUL for T2bb for (mg,mchi) = (100,50), (100,1):
        if model=="T2bb":
            if clsType.find("Plus"):
                xsecUL[clsType].SetBinContent(1,1,1.e4)
                xsecUL[clsType].SetBinContent(1,3,1.e4)
            elif clsType.find("Minus"):
                xsecUL[clsType].SetBinContent(1,1,3.e4)
                xsecUL[clsType].SetBinContent(1,3,3.e4)
            else:
                xsecUL[clsType].SetBinContent(1,1,2.e4)
                xsecUL[clsType].SetBinContent(1,3,2.e4)
        if model=="T6bbHH":
            xsecUL[clsType].SetBinContent(5,1,xsecUL[clsType].GetBinContent(6,2))
            xsecUL[clsType].SetBinContent(4,1,xsecUL[clsType].GetBinContent(5,2))
            xsecUL[clsType].SetBinContent(3,1,xsecUL[clsType].GetBinContent(4,2))
            xsecUL[clsType].SetBinContent(2,1,xsecUL[clsType].GetBinContent(3,2))
            xsecUL[clsType].SetBinContent(1,1,xsecUL[clsType].GetBinContent(2,2))
            
        print "INFO: doing interpolation for %s"%(clsType)

        # do swiss cross average in log domain
        #logXsecUL[clsType] = getLogHist(xsecUL[clsType])
        #logXsecUL[clsType] = rt.swissCrossInterpolate(logXsecUL[clsType],"NE")
        #rebinXsecUL[clsType] = getExpHist(logXsecUL[clsType])
        
        # do swiss cross average in real domain
        rebinXsecUL[clsType] = rt.swissCrossInterpolate(xsecUL[clsType],"NE")

        # do scipy multi-quadratic interpolation in log domain
        rebinXsecUL[clsType] = interpolate2D(rebinXsecUL[clsType],epsilon=1,smooth=smooth)

        # do swiss cross rebin + average in real domain (should be log??)
        for i in xrange(0,nRebins):
            rebinXsecUL[clsType] = rt.swissCrossRebin(rebinXsecUL[clsType],"NE")

        # only for display purposes of underlying heat map: do swiss cross average then scipy interpolation 
        xsecUL[clsType] = rt.swissCrossInterpolate(xsecUL[clsType],"NE")
        xsecUL[clsType] = interpolate2D(xsecUL[clsType], epsilon=1,smooth=smooth)
       
        
    if model in ["T2bb","T2tt","T6bbHH"]:
        gluinoFile =  rt.TFile.Open("%s/stop.root"%(directory))
        gluinoHist = gluinoFile.Get("stop")
    else:
        gluinoFile =  rt.TFile.Open("%s/gluino.root"%(directory))
        gluinoHist = gluinoFile.Get("gluino")
    

    # now rebin xsecGluino the correct number of times
    for i in xrange(0,nRebins):
        xsecGluino = rt.swissCrossRebin(xsecGluino,"NE")
        xsecGluinoPlus = rt.swissCrossRebin(xsecGluinoPlus,"NE")
        xsecGluinoMinus = rt.swissCrossRebin(xsecGluinoMinus,"NE")
    
    
    for i in xrange(1,xsecGluino.GetNbinsX()+1):
        xLow = xsecGluino.GetXaxis().GetBinLowEdge(i)
        xsecVal =  gluinoHist.GetBinContent(gluinoHist.FindBin(xLow))
        xsecErr =  gluinoHist.GetBinError(gluinoHist.FindBin(xLow))
        for j in xrange(1,xsecGluino.GetNbinsY()+1):
            yLow = xsecGluino.GetYaxis().GetBinLowEdge(j)
            if xLow >= yLow+diagonalOffset and xLow <= mgMax-binWidth:
                xsecGluino.SetBinContent(i,j,xsecVal)
                xsecGluinoPlus.SetBinContent(i,j,xsecVal+xsecErr)
                xsecGluinoMinus.SetBinContent(i,j,xsecVal-xsecErr)
                
    c = rt.TCanvas("c","c",500,500)
    
    for clsType in clsTypes:
        xsecUL[clsType].SetTitle("%s %s, %s #sigma #times Branching Fraction"%(model,box.replace("_","+"),titleMap[clsType]))
        xsecUL[clsType].SetTitleOffset(1.5)
        xsecUL[clsType].SetXTitle("gluino Mass [GeV]")
        xsecUL[clsType].GetXaxis().SetTitleOffset(0.95)
        xsecUL[clsType].SetYTitle("LSP Mass [GeV]")
        xsecUL[clsType].GetYaxis().SetTitleOffset(1.25)

        # subtract the predicted xsec
        subXsecUL[clsType] = rebinXsecUL[clsType].Clone()
        if clsType=="ObsMinus":
            subXsecUL[clsType].Add(xsecGluinoMinus,-1)
        elif clsType=="ObsPlus":
            subXsecUL[clsType].Add(xsecGluinoPlus,-1)
        else:
            subXsecUL[clsType].Add(xsecGluino,-1)

        contours = array('d',[0.0])
        subXsecUL[clsType].SetContour(1,contours)
        
        xsecUL[clsType].SetMinimum(xsecMin)
        xsecUL[clsType].SetMaximum(xsecMax)
        rebinXsecUL[clsType].SetMinimum(xsecMin)
        rebinXsecUL[clsType].SetMaximum(xsecMax)
        subXsecUL[clsType].SetMaximum(1.)
        subXsecUL[clsType].SetMinimum(-1.)

        
        # fGrayGraphs = []
        # for iBinX in range(1,subXsecUL[clsType].GetNbinsX()+1):
        #     for iBinY in range(1,subXsecUL[clsType].GetNbinsY()+1):
        #         if subXsecUL[clsType].GetBinContent(iBinX,iBinY)>0: color = rt.kRed
        #         elif subXsecUL[clsType].GetBinContent(iBinX,iBinY)<0: color = rt.kBlue
        #         elif subXsecUL[clsType].GetBinContent(iBinX,iBinY)==0: color = rt.kWhite

        #         xBinLow = subXsecUL[clsType].GetXaxis().GetBinLowEdge(iBinX)
        #         xBinHigh = xBinLow+subXsecUL[clsType].GetXaxis().GetBinWidth(iBinX)
        #         yBinLow = subXsecUL[clsType].GetYaxis().GetBinLowEdge(iBinY)
        #         yBinHigh = yBinLow+subXsecUL[clsType].GetYaxis().GetBinWidth(iBinY)
        #         fGray = rt.TGraph(5)
        #         fGray.SetPoint(0,xBinLow-2,yBinLow-2)
        #         fGray.SetPoint(1,xBinLow-2,yBinHigh+2)
        #         fGray.SetPoint(2,xBinHigh+2,yBinHigh+2)
        #         fGray.SetPoint(3,xBinHigh+2,yBinLow-2)
        #         fGray.SetPoint(4,xBinLow-2,yBinLow-2)
        #         fGray.SetFillColor(color)
        #         fGrayGraphs.append(fGray)

        
        c.SetLogz(0)
        subXsecUL[clsType].Draw("CONT Z LIST")
        c.Update()
        
        conts = rt.gROOT.GetListOfSpecials().FindObject("contours")

        
        xsecUL[clsType].Draw("COLZ")
        #for testing:
        #rebinXsecUL[clsType].Draw("COLZ")
        #subXsecUL[clsType].Draw("COLZ")
        
        contour0 = conts.At(0)
        curv = contour0.First()
        curv.SetLineWidth(3)
        curv.SetLineColor(rt.kBlack)
        curv.Draw("lsame")
        finalcurv = curv.Clone()
        maxN = curv.GetN()
        
        for i in xrange(1, contour0.GetSize()):
            curv = contour0.After(curv)
            curv.SetLineWidth(3)
            curv.SetLineColor(rt.kBlack)
            curv.Draw("lsame")
            if curv.GetN()>maxN:
                maxN = curv.GetN()
                finalcurv = curv.Clone()

        
        contourFinal[clsType] = finalcurv.Clone(clsType+"Final")
        
        #for fGray in fGrayGraphs: fGray.Draw("F")
        
        c.SetLogz(1)
        c.Print("%s_INTERP_%s_%s.pdf"%(model,box,clsType))

    #outFile = rt.TFile.Open("PlotsSMS/config/SUS13004/%s_results.root"%model,"recreate")
    outFile = rt.TFile.Open("%s/%s_results.root"%(directory,model),"recreate")
    for clsType in clsTypes:
        contourFinal[clsType].Write()
        xsecUL[clsType].Write()
