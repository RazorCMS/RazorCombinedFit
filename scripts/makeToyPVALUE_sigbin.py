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

def HadFR(MR, Rsq):
    FR = False
    if Rsq<0.18: FR = True
    if Rsq<0.20 and MR<1000: FR = True
    if Rsq<0.30 and MR < 650: FR = True
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

def findMedian(myHisto):
    prob = 0
    median = 0
    for i in range(1, myHisto.GetNbinsX()+1):
        if prob <= 0.5 and prob+myHisto.GetBinContent(i) > 0.5:
            median = myHisto.GetBinCenter(i)
        prob = prob + myHisto.GetBinContent(i)
    return median
    
def find68ProbRange(hToy, probVal=0.68):
    minVal = 0.
    maxVal = 100000.
    if hToy.Integral()<=0: return hToy.GetBinCenter(hToy.GetMaximumBin()),max(minVal,0.),maxVal
    # get the bin contents
    probsList = []
    for  i in range(1, hToy.GetNbinsX()+1):
        probsList.append(hToy.GetBinContent(i)/hToy.Integral())
    probsList.sort()
    #probsList.reverse()
    prob = 0
    prob68 = 0
    found = False
    for i in range(0,len(probsList)):
        if prob+probsList[i] >= 1-probVal and not found:
            frac = (1-probVal-prob)/probsList[i]
            prob68 = probsList[i-1]+frac*(probsList[i]-probsList[i-1])
            found = True
        prob = prob + probsList[i]

    foundMin = False
    foundMax = False
    for  i in range(0, hToy.GetNbinsX()):
        if not foundMin and hToy.GetBinContent(i+1) >= prob68:
            #minVal = 0.
            #if i == 0: 
            #else:
            fraction = (prob68-hToy.GetBinContent(i))/(hToy.GetBinContent(i+1)-hToy.GetBinContent(i))
            #print fraction
            minVal = hToy.GetBinLowEdge(i)+hToy.GetBinWidth(i)*fraction
            foundMin = True
        if not foundMax and hToy.GetBinContent(hToy.GetNbinsX()-i) >= prob68:
            fraction = (prob68-hToy.GetBinContent(hToy.GetNbinsX()-i+1))/(hToy.GetBinContent(hToy.GetNbinsX()-i)-hToy.GetBinContent(hToy.GetNbinsX()-i+1))
            maxVal = hToy.GetBinLowEdge(hToy.GetNbinsX()-i)+hToy.GetBinWidth(hToy.GetNbinsX()-i)*(1-fraction)
            foundMax = True
    return hToy.GetBinCenter(hToy.GetMaximumBin()),max(minVal,0.),maxVal

def getSigma(n, hToy):
    if hToy.GetMaximumBin() == hToy.FindBin(n): return 0.
    # find the probability of the bin corresponding to the observed n
    binN = hToy.FindBin(n)
    Prob_n = hToy.GetBinContent(binN)
    Prob = 0
    for i in range(1, binN+1): Prob += hToy.GetBinContent(i)
    if hToy.Integral() == 0.: return 0.
    if Prob ==0. : Prob = 1./hToy.GetEntries()
    elif Prob >= hToy.Integral(): Prob = 1.-1./hToy.GetEntries()
    else: Prob = Prob/hToy.Integral()
     # convert the one-sided p-value in a number of sigmas
    print rt.TMath.NormQuantile(Prob)
    return rt.TMath.NormQuantile(Prob)

def getPValue(n, hToy):
    Prob_n = hToy.GetBinContent(hToy.FindBin(n+0.1))
    Prob = 0
    for i in range(1, hToy.GetNbinsX()+1):
        if hToy.GetBinContent(i)<= Prob_n: Prob += hToy.GetBinContent(i)
    if hToy.Integral() <= 0.: return 0.
    Prob = Prob/hToy.Integral()
    return Prob
    
if __name__ == '__main__':
    Box = sys.argv[1]
    fileName = sys.argv[2]
    datafileName = sys.argv[3]
    noBtag = False
    for i in range(4,len(sys.argv)):
        if sys.argv[i] == "--noBtag": noBtag = True

    MRbins, Rsqbins = makeBluePlot.Binning(Box, noBtag)

    #MRbins = [400.0, 450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 800, 900, 1000, 1200, 1600, 2000, 2600, 4500.0]
    #Rsqbins = [0.18, 0.21, 0.24, 0.27, 0.3, 0.35, 0.4, 0.5, 0.65, 0.80, 1.5]

    x = array("d",MRbins)
    y = array("d",Rsqbins)
    h =  rt.TH2D("h","", len(MRbins)-1, x, len(Rsqbins)-1, y)
    hOBS =  rt.TH2D("hOBS","hOBS", len(MRbins)-1, x, len(Rsqbins)-1, y)
    hEXP =  rt.TH2D("hEXP","hEXP", len(MRbins)-1, x, len(Rsqbins)-1, y)    
    set2DStyle(h)
    h.SetMaximum(1.)
    h.SetMinimum(0.)

    hNS =  rt.TH2D("hNS","", len(MRbins)-1, x, len(Rsqbins)-1, y)
    set2DStyle(hNS)
    
    fileIn = rt.TFile.Open(fileName)
    myTree = fileIn.Get("myTree")
    dataFile = rt.TFile.Open(datafileName)
    alldata = dataFile.Get("RMRTree")
    fileOUT = rt.TFile.Open("pvalue_%s.root" %Box, "recreate")

    # p-values 1D plot
    pValHist = rt.TH1D("pVal%s" %Box, "pVal%s" %Box, 20, 0., 1.)

    #prepare the latex table
    table = open("table_%s.tex" %Box,"w")
    table.write("\\errorcontextlines=9\n")
    table.write("\\documentclass[12pt]{article}\n")
    table.write("\\begin{document}\n")
    table.write("\\begin{table}[!ht]\n")
    table.write("\\begin{tiny}\n")
    table.write("\\begin{center}\n")
    table.write("\\begin{tabular}{|c|c|c|c|c|c|c|}\n")
    table.write("\\hline\n")
    table.write("$M_R$ Range & $R^2$ Range & Observed & Predicted Mode & Predicted Median & Predicted 68 Prob. Range & p-value \\\\\n")
    table.write("\\hline\n")
    # loop over regions
    result = []
    for i in range(0,len(MRbins)-1):
        for j in range(0,len(Rsqbins)-1):
            varName = "b%i_%i" %(i,j)
            histoName = "Histo_%s" %varName
            # make an histogram of the expected yield                                                                                                                                                 
            myTree.Draw(varName)
            htemp = rt.gPad.GetPrimitive("htemp");
            mean = htemp.GetMean()
            rms = htemp.GetRMS()            
            # make an histogram of the expected yield
            myhisto = rt.TH1D(histoName, histoName, 20, int(max(0.,mean-5.*rms)), int(mean+5.*rms))
            if myhisto.GetXaxis().GetBinWidth(2) <1:
                maxX = int(myhisto.GetXaxis().GetXmax())+10
                del myhisto
                myhisto = rt.TH1D(histoName, histoName, maxX, 0., maxX)
            myTree.Project(histoName, varName)
            if myhisto.GetEntries() != 0: 
                if myhisto.Integral()>0: myhisto.Scale(1./myhisto.Integral())
                # get the observed number of events
                data = alldata.reduce("MR>= %f && MR < %f && Rsq >= %f && Rsq < %f" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1]))
                nObs = data.numEntries()
                modeVal,rangeMin,rangeMax = find68ProbRange(myhisto)
                medianVal = findMedian(myhisto)
                pval = getPValue(nObs, myhisto)
                h.SetBinContent(i+1, j+1, pval)
                nsigma = getSigma(nObs, myhisto)
                # the p-value cannot be one... And we have a limited number of toys
                pvalmax = 1.-1./myhisto.GetEntries()
                if pval >pvalmax: pval = pvalmax 
                # these are those bins where we see 0 and we expect 0
                if pval == pvalmax and myhisto.GetMaximumBin() == 1: nsigma = 0.
                hNS.SetBinContent(i+1, j+1, nsigma)
                #if not HadFR(MRbins[i], Rsqbins[j]):
                hOBS.SetBinContent(i+1, j+1, nObs)
                hEXP.SetBinContent(i+1, j+1, (rangeMax+rangeMin)/2)
                hEXP.SetBinError(i+1, j+1, (rangeMax-rangeMin)/2)
                if (rangeMax+rangeMin)/2 == 50000.: continue
                print "$[%4.0f,%4.0f]$ & $[%5.4f,%5.4f]$ & %i & %3.1f & %3.1f & $%3.1f \\pm %3.1f$ & %4.2f \\\\ \n" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], nObs, modeVal, medianVal, (rangeMax+rangeMin)/2, (rangeMax-rangeMin)/2, pval)
                if pval<0.15: table.write("$[%4.0f,%4.0f]$ & $[%5.4f,%5.4f]$ & %i & %3.1f & %3.1f & $%3.1f \\pm %3.1f$ & %4.2f \\\\ \n" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], nObs, modeVal, medianVal, (rangeMax+rangeMin)/2, (rangeMax-rangeMin)/2, pval))

                # fill the pvalue plot for non-empty bins with expected 0.5 (spikes at 0)
                if not (pval ==0.99 and modeVal == 0.5): pValHist.Fill(pval)
                #else:
                #    hEXP.SetBinContent(i+1, j+1, 0)
                #    hEXP.SetBinError(i+1, j+1, 0)
                BoxName = ""
                if Box == "Had": BoxName = "HAD"
                if Box == "Mu": BoxName = "MU"
                if Box == "Ele": BoxName = "ELE"
                if Box == "MuMu": BoxName = "MU-MU"
                if Box == "EleEle": BoxName = "ELE-ELE"
                if Box == "MuEle": BoxName = "MU-ELE"
                result.append([varName, BoxName, nObs, rangeMin, rangeMax, pval, modeVal, medianVal])
                #myhisto.GetXaxis().SetRangeUser(0., rangeMax*2.)
                myhisto.Write()
                del data
    h.Write()
    pValHist.Write()
    fileOUT.Close()

    # finish writing the table and close the tex file
    table.write("\\hline\n")
    table.write("\\end{tabular}\n")
    table.write("\\end{center}\n")
    table.write("\\end{tiny}\n")
    table.write("\\end{table}\n")
    table.write("\\end{document}\n")
    table.close()

    fileOUTint = rt.TFile.Open("ExpectedObserved_RazorHad_Winter2012.root", "recreate")
    hOBS.Write()
    hEXP.Write()
    fileOUTint.Close()

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

    # Has has a tighter baseline
    #if Box == "Had":
    #    for i in range(1,len(MRbins)): h.SetBinContent(i,1, 0.)
    #    for i in range(1,len(Rsqbins)): h.SetBinContent(1,i, 0.)
                      
    c1 = rt.TCanvas("c1","c1", 900, 600)
    c1.SetLogz()
    setCanvasStyle(c1)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetPalette(900)
    h.Draw("colz")

    for i in range(0,len(xLines)): xLines[i].Draw()
    for i in range(0,len(yLines)): yLines[i].Draw()

    # the fit region in green
    frLines = []
    minRsq = 0.11
    minMR = 300.
    if Box == "Had":
        frLines.append(rt.TLine(400,0.18,800,0.18))
        frLines.append(rt.TLine(800,0.18,800,0.2))
        frLines.append(rt.TLine(650,0.2,800,0.2))
        frLines.append(rt.TLine(650,0.2,650,0.3))
        frLines.append(rt.TLine(450,0.3,650,0.3))
        frLines.append(rt.TLine(450,0.3,450,0.5))
        frLines.append(rt.TLine(450,0.5,400,0.5))
        frLines.append(rt.TLine(400,0.18,400,0.5))

    if Box == "Mu" or Box == "Ele":
        frLines.append(rt.TLine(800,0.11,800,0.2))
        frLines.append(rt.TLine(650,0.2,800,0.2))
        frLines.append(rt.TLine(650,0.2,650,0.3))
        frLines.append(rt.TLine(450,0.3,650,0.3))
        frLines.append(rt.TLine(450,0.3,450,0.5))
        frLines.append(rt.TLine(450,0.5,300,0.5))

    if Box == "MuMu" or Box == "EleEle" or Box == "MuEle":
        frLines.append(rt.TLine(1000,0.15,1000,0.2))
        frLines.append(rt.TLine(1000,0.2,650,0.2))
        frLines.append(rt.TLine(650,0.2,650,0.3))
        frLines.append(rt.TLine(650,0.3,500,0.3))
        frLines.append(rt.TLine(500,0.3,500,0.5))

    ci = rt.TColor.GetColor("#006600");
    #for frLine in frLines:
    #    frLine.SetLineColor(ci)
    #    frLine.SetLineWidth(2)
    #    frLine.Draw()

    c1.SaveAs("pvalue_sigbin_%s.C" %Box)
    c1.SaveAs("pvalue_sigbin_%s.pdf" %Box)

    c2 = rt.TCanvas("c2","c2", 900, 600)
    setCanvasStyle(c2)
    # French flag Palette
    Red = array('d',[0.00, 1.00, 1.00])
    Green = array('d',[0.00, 1.00, 0.00])
    Blue = array('d',[1.00, 1.00, 0.00])
    Length = array('d',[0.00, 0.50, 1.00])
    rt.TColor.CreateGradientColorTable(3,Length,Red,Green,Blue,11)
    hNS.SetMaximum(5.5)
    hNS.SetMinimum(-5.5)
    hNS.SetContour(11);
    hNS.Draw("colz")
    #for i in range(0,11):
    #    print -5.+i
    #    hNS.SetContourLevel(i,-5. +i)
    for i in range(0,len(xLines)): xLines[i].Draw()
    for i in range(0,len(yLines)): yLines[i].Draw()
    c2.SaveAs("nSigma_%s.C" %Box)
    c2.SaveAs("nSigma_%s.pdf" %Box)
