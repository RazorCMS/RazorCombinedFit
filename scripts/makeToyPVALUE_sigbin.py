from optparse import OptionParser
import ROOT as rt
from array import *
import sys

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
        if prob < 0.5 and prob+myHisto.GetBinContent(i) > 0.5:
            median = myHisto.GetBinCenter(i)
        prob = prob + myHisto.GetBinContent(i)
    return median
    
def find68ProbRange(hToy, probVal=0.68):
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
            #if i == 0: minVal = 0.
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

def getPValue(n, hToy):
    oldToy = hToy
    #if hToy.GetMaximumBin() >4:
    #    hToy = Rebin(hToy)
    #    hToy.Smooth()
    # find the probability of the bin corresponding to the observed n
    Prob_n = hToy.GetBinContent(hToy.FindBin(n+0.1))
    Prob = 0
    for i in range(1, hToy.GetNbinsX()+1):
        if hToy.GetBinContent(i)<= Prob_n: Prob += hToy.GetBinContent(i)
    Prob = Prob/hToy.Integral()
    return Prob,hToy,oldToy
    
if __name__ == '__main__':
    Box = sys.argv[1]
    fileName = sys.argv[2]
    datafileName = sys.argv[3]

    # bins in mR
    MRbins = [300, 350, 400, 450, 500, 550, 600, 650, 700, 800, 900, 1000, 1200, 1600, 2000, 2800, 3500]
    # bins in R^2
    Rsqbins =  [0.09, 0.16, 0.20, 0.30, 0.40, 0.50]
    x = array("d",MRbins)
    y = array("d",Rsqbins)
    h =  rt.TH2D("h","", len(MRbins)-1, x, len(Rsqbins)-1, y)
    
    h.GetXaxis().SetTitle("M_{R}[GeV]")
    h.GetYaxis().SetTitle("R^{2}")
    h.SetMaximum(1.)
    h.SetMinimum(0.)
    
    fileIn = rt.TFile.Open(fileName)
    myTree = fileIn.Get("myTree")
    dataFile = rt.TFile.Open(datafileName)
    alldata = dataFile.Get("RMRTree")
    fileOUT = rt.TFile.Open("pvalue_%s.root" %Box, "recreate")

    # translate from upper to lower case
    boxName = [["HAD","Had"], ["MU", "Mu"], ["ELE", "Ele"], ["MUMU", "MuMu"], ["MUELE", "MuEle"], ["ELEELE", "EleEle"]]
    thisBoxName = ""
    for bn in boxName:
        if bn[0] == Box: thisBoxName = bn[1]

    # p-values 1D plot
    pValHist = rt.TH1D("pVal%s" %Box, "pVal%s" %Box, 20, 0., 1.)

    print "%s Box & Observed & Predicted Mode & Predicted Median & Predicted 68 Prob. Range & p-value \\\\" %Box
    # loop over regions
    result = []
    for i in range(0,len(MRbins)-1):
        for j in range(0,len(Rsqbins)-1):
            varName = "b%s_%i_%i" %(Box,i,j)
            histoName = "Histo_%s" %varName
            # make an histogram of the expected yield
            myhisto = rt.TH1D(histoName, histoName, 5000, 0., 5000.)
            myTree.Project(histoName, varName)
            if myhisto.GetEntries() != 0: 
                myhisto.Scale(1./myhisto.Integral())
                # get the observed number of events
                data = alldata.reduce("MR>= %f && MR < %f && Rsq >= %f && Rsq < %f" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1]))
                nObs = data.numEntries()
                modeVal,rangeMin,rangeMax = find68ProbRange(myhisto)
                medianVal = findMedian(myhisto)
                pval,myhisto,oldhisto = getPValue(nObs, myhisto)
                h.SetBinContent(i+1, j+1, pval)
                if pval >0.99: pval = 0.99 
                print "%s & %i & %f & %f & $[%f, %f]$ & %f \\\\" %(varName, nObs, modeVal, medianVal, rangeMin, rangeMax, pval)
                # fill the pvalue plot for non-empty bins with expected 0.5 (spikes at 0)
                if pval !=-99 or modeVal != 0.5 : pValHist.Fill(pval)
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
                oldhisto.Write()
                del data
    h.Write()
    pValHist.Write()
    fileOUT.Close()

    # the gray lines
    xLines = []
    yLines = []

    for i in range(1,5):
        xLines.append(rt.TLine(x[0], y[i], x[16], y[i]))
        xLines[i-1].SetLineStyle(2);
        xLines[i-1].SetLineColor(rt.kGray);
        
    for i in range(1,16):
        yLines.append(rt.TLine(x[i], y[0], x[i], y[5]))
        yLines[i-1].SetLineStyle(2)
        yLines[i-1].SetLineColor(rt.kGray)
                      
    c1 = rt.TCanvas("c1","c1", 900, 600)
    c1.SetLogz()
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetPalette(900)
    h.Draw("colz")

    for i in range(0,4): xLines[i].Draw()
    for i in range(0,15): yLines[i].Draw()

    # the fit region in green
    frLines = []
    minRsq = 0.09
    minMR = 300.
    if Box == "Had":
        frLines.append(rt.TLine(400,0.16,800,0.16))
        frLines.append(rt.TLine(800,0.16,800,0.2))
        frLines.append(rt.TLine(650,0.2,800,0.2))
        frLines.append(rt.TLine(650,0.2,650,0.3))
        frLines.append(rt.TLine(450,0.3,650,0.3))
        frLines.append(rt.TLine(450,0.3,450,0.5))
        frLines.append(rt.TLine(450,0.5,400,0.5))
        frLines.append(rt.TLine(400,0.16,400,0.5))

    if Box == "Mu" or Box == "Ele":
        frLines.append(rt.TLine(800,0.09,800,0.2))
        frLines.append(rt.TLine(650,0.2,800,0.2))
        frLines.append(rt.TLine(650,0.2,650,0.3))
        frLines.append(rt.TLine(450,0.3,650,0.3))
        frLines.append(rt.TLine(450,0.3,450,0.5))
        frLines.append(rt.TLine(450,0.5,300,0.5))

    if Box == "MuMu" or Box == "EleEle" or Box == "MuEle":
        frLines.append(rt.TLine(650,0.09,650,0.2))
        frLines.append(rt.TLine(650,0.2,450,0.2))
        frLines.append(rt.TLine(450,0.2,450,0.3))
        frLines.append(rt.TLine(400,0.3,450,0.3))
        frLines.append(rt.TLine(400,0.3,400,0.5))

    ci = rt.TColor.GetColor("#006600");
    for frLine in frLines:
        frLine.SetLineColor(ci)
        frLine.SetLineStyle(2)
        frLine.SetLineWidth(2)
        frLine.Draw()

    c1.SaveAs("pvalue_sigbin_%s.C" %Box)
    c1.SaveAs("pvalue_sigbin_%s.pdf" %Box)
