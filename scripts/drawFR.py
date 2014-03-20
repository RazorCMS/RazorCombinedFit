from optparse import OptionParser
import ROOT as rt
from array import *
import sys
import makeBluePlot

def set2DStyle(h) :
    h.GetXaxis().SetTitle("M_{R}[GeV]")
    h.GetYaxis().SetTitle("R^{2}")
    h.GetXaxis().SetTitleSize(0.055)
    h.GetXaxis().SetLabelSize(0.055)
    h.GetYaxis().SetTitleSize(0.055)
    h.GetYaxis().SetLabelSize(0.055)

def setCanvasStyle(c):
    c.SetLeftMargin(0.1127232)
    c.SetBottomMargin(0.1311189)
    rt.gStyle.SetOptStat(0)

def HadFR(MR, Rsq):
    FR = False
    if Rsq<0.24: FR = True
    if MR<500: FR = True
    return FR

def Rebin(h):
    myhisto = rt.TH1D("%s_REBIN" %h.GetName(), "%s_REBIN" %h.GetName(), 5000, 0., 5000.)
    for i in range(1,1001):
        myhisto.SetBinContent(i, h.GetBinContent(int(i/10)))
    return myhisto

def WriteArrowsLep():
    arrow = rt.TArrow(583.1752,0.42951,583.1752,0.4908057,0.04,">")
    arrow.SetFillColor(1)
    arrow.SetFillStyle(1001)
    arrow.SetLineWidth(2)
    arrow.SetAngle(44)

    arrow2 = rt.TArrow(896.2333,0.2805274,893.8616,0.3443771,0.05,">")
    arrow2.SetFillColor(1)
    arrow2.SetFillStyle(1001)
    arrow2.SetLineWidth(2)
    arrow2.SetAngle(39)
    return arrow, arrow2

def WriteArrowsDiLep():
    arrow = rt.TArrow(988.7277,0.3613024,538.1138,0.3604065,0.04,">")
    arrow.SetFillColor(1)
    arrow.SetFillStyle(1001)
    arrow.SetLineWidth(2)
    arrow.SetAngle(44)

    arrow2 = rt.TArrow(395.8147,0.1937544,398.1864,0.3998295,0.05,">")
    arrow2.SetFillColor(1)
    arrow2.SetFillStyle(1001)
    arrow2.SetLineWidth(2)
    arrow2.SetAngle(39)
    return arrow, arrow2

def WriteText(pt, result):

    pt.SetFillColor(0)
    pt.SetFillStyle(0)
    pt.SetLineColor(0)
    pt.SetTextAlign(13)
    pt.SetTextSize(0.022)
    pt.SetFillColor(0)
    pt.SetBorderSize(0)
    pt.SetTextAlign(13)
    pt.SetTextFont(42)
    pt.SetTextSize(0.0282392)
    pt.AddText("%s %s box" %(result[0],result[1]))
    pt.AddText("68%% range [%3.1f,%3.1f]" %(result[3], result[4]))
    pt.AddText("Mode %3.1f" %result[6])
    pt.AddText("Median %3.1f" %result[7])
    pt.AddText("observed %i" %result[2])
    pt.AddText("p-value %4.2f" %result[5])    
    pt.Draw()

    
if __name__ == '__main__':

    Box = sys.argv[1]
    noBtag = False
    MRbins, Rsqbins, nBtagbins = makeBluePlot.Binning(Box, noBtag)
    print MRbins
    print Rsqbins
    x = array("d",MRbins)
    y = array("d",Rsqbins)
    
    hNS =  rt.TH2D("hNS","", len(MRbins)-1, x, len(Rsqbins)-1, y)
    set2DStyle(hNS)
    
    # the gray lines
    xLines = []
    yLines = []

    lastX = len(x)-1
    lastY = len(y)-1

    for i in range(1,lastY):
        xLines.append(rt.TLine(x[0], y[i], x[lastX], y[i]))
        xLines[i-1].SetLineStyle(2);
        xLines[i-1].SetLineColor(rt.kGray);
        
    for i in range(1,lastX):
        yLines.append(rt.TLine(x[i], y[0], x[i], y[lastY]))
        yLines[i-1].SetLineStyle(2)
        yLines[i-1].SetLineColor(rt.kGray)

    # the fit region in green
    frLines = []


    frLines.append(rt.TLine(x[0],y[0],x[-1],y[0]))
    frLines.append(rt.TLine(x[2],y[1],x[-1],y[1]))
    frLines.append(rt.TLine(x[2],y[1],x[2],y[-1]))
    frLines.append(rt.TLine(x[0],y[0],x[0],y[-1]))
    frLines.append(rt.TLine(x[0],y[-1],x[2],y[-1]))
    frLines.append(rt.TLine(x[-1],y[0],x[-1],y[0]))


    fGrayGraphs = []
    fGray = rt.TGraph(5)

    fGray.SetPoint(0,x[0],y[0])
    fGray.SetPoint(1,x[0],y[1])
    fGray.SetPoint(2,x[1],y[1])
    fGray.SetPoint(3,x[1],y[0])
    fGray.SetPoint(4,x[0],y[0])
    fGray.SetFillColor(rt.kGray+1)
    fGrayGraphs.append(fGray)
    

    fGray1 = rt.TGraph(5)
    cit = rt.gROOT.GetColor(rt.kBlue)
    cit.SetAlpha(0.3)
    fGray1.SetPoint(0,x[0],y[1])
    fGray1.SetPoint(1,x[2],y[1])
    fGray1.SetPoint(2,x[2],y[-1])
    fGray1.SetPoint(3,x[0],y[-1])
    fGray1.SetPoint(4,x[0],y[1])
    fGray1.SetFillColor(rt.kBlue)
    fGrayGraphs.append(fGray1)

    fGray2 = rt.TGraph(5)
    cit2 = rt.gROOT.GetColor(rt.kRed)
    cit2.SetAlpha(0.3)
    fGray2.SetPoint(0,x[1],y[0])
    fGray2.SetPoint(1,x[-1],y[0])
    fGray2.SetPoint(2,x[-1],y[1])
    fGray2.SetPoint(3,x[1],y[1])
    fGray2.SetPoint(4,x[1],y[0])
    fGray2.SetFillColor(rt.kRed)
    fGrayGraphs.append(fGray2)
    
    fGray3 = rt.TGraph(5)
    cit3 = rt.gROOT.GetColor(rt.kWhite)
    cit3.SetAlpha(0.0)
    fGray3.SetPoint(0,x[2],y[1])
    fGray3.SetPoint(1,x[-1],y[1])
    fGray3.SetPoint(2,x[-1],y[-1])
    fGray3.SetPoint(3,x[2],y[-1])
    fGray3.SetPoint(4,x[2],y[1])
    fGray3.SetFillColor(rt.kWhite)
    fGrayGraphs.append(fGray3)


    
        
    c2 = rt.TCanvas("c2","c2", 900, 600)
    setCanvasStyle(c2)
    # French flag Palette
    Red = array('d',[0.00, 1.00, 1.00])
    Green = array('d',[1.00, 1.00, 0.00])
    Blue = array('d',[1.00, 1.00, 0.00])
    Length = array('d',[0.00, 0.50, 1.00])
    rt.TColor.CreateGradientColorTable(3,Length,Red,Green,Blue,3)
    hNS.SetMaximum(5.1)
    hNS.SetMinimum(-5.1)
    hNS.SetContour(3)
    
    hNS.GetXaxis().SetMoreLogLabels()
    #hNS.GetYaxis().SetMoreLogLabels()
    hNS.GetXaxis().SetNoExponent()
    hNS.GetYaxis().SetNoExponent()
    hNS.Draw("colz")
    c2.Update()
    palette = hNS.GetListOfFunctions().FindObject("palette")
    #for i in range(0,11):
    #    print -5.+i
    #    hNS.SetContourLevel(i,-5. +i)
    
    for i in range(0,len(xLines)): xLines[i].Draw()
    for i in range(0,len(yLines)): yLines[i].Draw()
    for fGray in fGrayGraphs: fGray.Draw("F")
        
    for frLine in frLines:
        frLine.SetLineColor(rt.kBlack)
        frLine.SetLineWidth(2)
        frLine.Draw()
    #c2.SaveAs("nSigma_%s.C" %(Box))
    
    c2.SetLogx()
    c2.SetLogy()
    tlabels = []
    if Box=="Jet1b":
        tlabels.append(rt.TLatex(330,0.485, "0.5"))
        tlabels.append(rt.TLatex(330,0.39, "0.4"))
        tlabels.append(rt.TLatex(330,0.295, "0.3"))
    elif Box=="MultiJet" or Box=="TauTauJet" or Box=="Jet2b":
        tlabels.append(rt.TLatex(330,0.76, "0.8"))
        tlabels.append(rt.TLatex(330,0.47, "0.5"))
        tlabels.append(rt.TLatex(330,0.285, "0.3"))
    else:
        tlabels.append(rt.TLatex(240,0.75, "0.8"))
        tlabels.append(rt.TLatex(240,0.375, "0.4"))
        tlabels.append(rt.TLatex(240,0.19, "0.2"))
        
    for tlabel in tlabels:
        tlabel.SetTextSize(0.065)
        tlabel.SetTextFont(42)
        tlabel.Draw()
        

    tleg = rt.TLegend(0.25,0.5,0.9,0.9,)
    tleg.AddEntry(fGray1,"Low M_{R} sideband: M_{R}<%i GeV and R^{2}>%.1f"%(x[2],y[1]),"F")
    tleg.AddEntry(fGray2,"Low R^{2} sideband: M_{R}>%i GeV and R^{2}<%.1f"%(x[2],y[1]),"F")
    #PAS 8 TeV:
    #tleg.AddEntry(fGray3,"Extrapolation region: M_{R}>%i GeV and R^{2}>%.1f"%(x[2],y[1]),"F")
    #Paper 8 TeV:
    tleg.AddEntry(fGray3,"Signal-sensitive region: M_{R}>%i GeV and R^{2}>%.1f"%(x[2],y[1]),"F")
    tleg.SetFillColor(rt.kWhite)
    tleg.SetLineColor(rt.kWhite)
    tleg.Draw()
        
    c2.SaveAs("SidebandL_%s.pdf" %(Box))
    c2.SaveAs("SidebandL_%s.C" %(Box))
