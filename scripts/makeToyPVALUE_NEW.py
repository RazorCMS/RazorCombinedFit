from optparse import OptionParser
import ROOT as rt
from array import *
import sys

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

    minRsq = 0.11
    minMR = 300.
    firstmR = 450
    if Box == "Had":
        minRsq = 0.18
        minMR = 400.
        firstmR = 500
    if Box == "BJet":
        minRsq = 0.16

    # bins in mR
    MRbins = [300, 350, 400, 450, 500, 550, 600, 650, 700, 800, 900, 1000, 1200, 1600, 2000, 2800, 3500]
    # bins in R^2
    Rsqbins =  [0.11, 0.18, 0.20, 0.30, 0.40, 0.50]
    x = array("d",MRbins)
    y = array("d",Rsqbins)
       
     # bins in mR
    MRbinsGL = [400, 450, 500, 550, 600, 650, 700, 800, 900, 1000, 1200, 1600, 2000, 2800, 3500]
    # bins in R^2
    RsqbinsGL =  [minRsq, 0.20, 0.30, 0.40, 0.50]

    MRbins2 = [minMR, firstmR, 650, 1000, 2000, 3500]
    Rsqbins2 =  [minRsq, 0.20, 0.30, 0.50]

    x2 = array("d",MRbins2)
    y2 = array("d",Rsqbins2)
    h =  rt.TH2D("h","", len(MRbins2)-1, x2, len(Rsqbins2)-1, y2)
    
    h.GetXaxis().SetTitle("M_{R}[GeV]")
    h.GetYaxis().SetTitle("R^{2}")
    h.SetMaximum(1.)
    h.SetMinimum(0.)
    
    fileIn = rt.TFile.Open(fileName)
    myTree = fileIn.Get("myTree")
    dataFile = rt.TFile.Open(datafileName)
    alldata = dataFile.Get("RMRTree")
    fileOUT = rt.TFile.Open("pvalue_%s_new.root" %Box, "recreate")

    # translate from upper to lower case
    boxName = [["HAD","Had"], ["MU", "Mu"], ["ELE", "Ele"], ["MUMU", "MuMu"], ["MUELE", "MuEle"], ["ELEELE", "EleEle"],["BJET","BJet"]]
    thisBoxName = ""
    for bn in boxName:
        if bn[0] == Box: thisBoxName = bn[1]

    # p-values 1D plot
    pValHist = rt.TH1D("pVal%s" %Box, "pVal%s" %Box, 20, 0., 1.)

    #define the SRs
    S1sel = ""
    S2sel = ""
    for i in range(14,16):
        for j in range(0,3):
            S1sel = S1sel+"b%i_%i+" %(i,j)
        for j in range(3,5):
            S2sel = S2sel+"b%i_%i+" %(i,j)
    S1 = ["S1", S1sel[:-1], "MR>=2000.&&Rsq<0.3&&Rsq>=%f" %minRsq]
    S2 = ["S2", S2sel[:-1], "MR>=2000.&&Rsq>=0.3"]
    #define the SRs
    S3sel = ""
    S4sel = ""
    for i in range(11,14):
        for j in range(0,3):
            S3sel = S3sel+"b%i_%i+" %(i,j)
        for j in range(3,5):
            S4sel = S4sel+"b%i_%i+" %(i,j)
    S3 = ["S3", S3sel[:-1], "MR>=1000.&&MR<2000.&&Rsq<0.3&&Rsq>=%f" %minRsq]
    S4 = ["S4", S4sel[:-1], "MR>=1000.&&MR<2000.&&Rsq>=0.3"]
    #define the SRs
    S5sel = ""
    for i in range(7,11): S5sel = S5sel+"b%i_%i+" %(i,2)
    S5 = ["S5", S5sel[:-1], "(MR>=650.&&MR<1000.&&Rsq<0.3&&Rsq>=0.2)"]
    #define the SRs
    S6sel = ""
    if Box != "Had":
        for i in range(3,11):
            for j in range(3,5):
                S6sel = S6sel+"b%i_%i+" %(i,j)
        S6 = ["S6", S6sel[:-1], "MR>=450.&&MR<1000.&&Rsq>=0.3"]
    else:
        for i in range(4,11):
            for j in range(3,5):
                S6sel = S6sel+"b%i_%i+" %(i,j)
        S6 = ["S6", S6sel[:-1], "MR>=500.&&MR<1000.&&Rsq>=0.3"]

    SR = [S1, S2, S3, S4, S5, S6]

    print "%s Box & Observed & Predicted Mode & Predicted Median & Predicted 68 Prob. Range & p-value \\\\" %Box
    # loop over regions
    result = []
    for S in SR:
            histoName = "Histo_%s" %S[0]
            # make an histogram of the expected yield
            myhisto = rt.TH1D(histoName, histoName, 5000, 0., 5000.)
            myTree.Project(histoName, S[1])
            if myhisto.GetEntries() != 0: 
                myhisto.Scale(1./myhisto.Integral())
                # get the observed number of events
                data = alldata.reduce(S[2])
                nObs = data.numEntries()
                modeVal,rangeMin,rangeMax = find68ProbRange(myhisto)
                medianVal = findMedian(myhisto)
                if medianVal <= 100 and medianVal > 50: myhisto.Rebin(2)
                if medianVal > 100: myhisto.Rebin(5)
                pval,myhisto,oldhisto = getPValue(nObs, myhisto)
                # fill the bins of 2D blue plot
                if S[0] == "S1":
                    h.SetBinContent(5, 1, pval)
                    h.SetBinContent(5, 2, pval)
                if S[0] == "S2":
                    h.SetBinContent(5, 3, pval)
                if S[0] == "S3":
                    h.SetBinContent(4, 1, pval)
                    h.SetBinContent(4, 2, pval)
                if S[0] == "S4":
                    h.SetBinContent(4, 3, pval)
                if S[0] == "S5":
                    h.SetBinContent(3, 2, pval)
                if S[0] == "S6":
                    h.SetBinContent(3, 3, pval)
                    h.SetBinContent(2, 3, pval)

                if pval >0.99: pval = 0.99 
                print "%s & %i & %f & %f & $[%f, %f]$ & %f \\\\" %(S[0], nObs, modeVal, medianVal, rangeMin, rangeMax, pval)
                # fill the pvalue plot for non-empty bins with expected 0.5 (spikes at 0)
                if pval !=-99 or modeVal != 0.5 : pValHist.Fill(pval)
                BoxName = ""
                if Box == "Had": BoxName = "HAD"
                if Box == "BJet": BoxName = "BJET"
                if Box == "Mu": BoxName = "MU"
                if Box == "Ele": BoxName = "ELE"
                if Box == "MuMu": BoxName = "MU-MU"
                if Box == "EleEle": BoxName = "ELE-ELE"
                if Box == "MuEle": BoxName = "MU-ELE"
                result.append([S[0], BoxName, nObs, rangeMin, rangeMax, pval, modeVal, medianVal])
                #myhisto.GetXaxis().SetRangeUser(0., rangeMax*2.)
                myhisto.Write()
                oldhisto.Write()
                del data
    h.Write()
    pValHist.Write()
    fileOUT.Close()

    c1 = rt.TCanvas("c1","c1", 900, 600)
    c1.SetLogz()
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetPalette(900)
    h.Draw("colz")

    # the gray lines
    xLines = []
    yLines = []
    if Box != "Had":
        MRbinsGL = MRbins

    xL = array("d",MRbinsGL)
    yL = array("d",RsqbinsGL)
    for i in range(1,len(RsqbinsGL)-1):
        xLines.append(rt.TLine(xL[0], yL[i], xL[len(MRbinsGL)-1], yL[i]))
        xLines[i-1].SetLineStyle(2);
        xLines[i-1].SetLineColor(rt.kGray);
        
    for i in range(1,len(MRbinsGL)-1):
        yLines.append(rt.TLine(xL[i], yL[0], xL[i], yL[len(RsqbinsGL)-1]))
        yLines[i-1].SetLineStyle(2)
        yLines[i-1].SetLineColor(rt.kGray)

    for line in xLines: line.Draw()
    for line in yLines: line.Draw()

    # the black lines
    xLinesB = []
    yLinesB = []
    xLinesB.append(rt.TLine(650,0.3,3500,0.3))
    if Box == "MuMu" or Box == "MuEle" or Box == "EleEle":
        xLinesB.append(rt.TLine(450,0.3,650,0.3))
        xLinesB.append(rt.TLine(650,0.2,1000,0.2))
                             
    yLinesB.append(rt.TLine(2000,minRsq,2000,0.5))
    yLinesB.append(rt.TLine(1000,minRsq,1000,0.5))

    if Box == "MuMu" or Box == "MuEle" or Box == "EleEle":
        yLinesB.append(rt.TLine(650,0.2,650,0.3))
        yLinesB.append(rt.TLine(450,0.3,450,0.5))

    for i in range(0,len(xLinesB)): xLinesB[i].Draw()
    for i in range(0,len(yLinesB)): yLinesB[i].Draw()

    # the fit region in green
    frLines = []
    if Box == "Had":
        frLines.append(rt.TLine(400,minRsq,1000,minRsq))
        frLines.append(rt.TLine(1000,minRsq,1000,0.2))
        frLines.append(rt.TLine(650,0.2,1000,0.2))
        frLines.append(rt.TLine(650,0.2,650,0.3))
        frLines.append(rt.TLine(500,0.3,650,0.3))
        frLines.append(rt.TLine(500,0.3,500,0.5))
        frLines.append(rt.TLine(500,0.5,400,0.5))
        frLines.append(rt.TLine(400,minRsq,400,0.5))

    if Box == "Mu" or Box == "Ele" or Box == "BJet":
        frLines.append(rt.TLine(1000,minRsq,1000,0.2))
        frLines.append(rt.TLine(650,0.2,1000,0.2))
        frLines.append(rt.TLine(650,0.2,650,0.3))
        frLines.append(rt.TLine(450,0.3,650,0.3))
        frLines.append(rt.TLine(450,0.3,450,0.5))
        frLines.append(rt.TLine(450,0.5,300,0.5))

    if Box == "MuMu" or Box == "EleEle" or Box == "MuEle":
        frLines.append(rt.TLine(650,minRsq,650,0.2))
        frLines.append(rt.TLine(650,0.2,450,0.2))
        frLines.append(rt.TLine(450,0.2,450,0.3))
        frLines.append(rt.TLine(400,0.3,450,0.3))
        frLines.append(rt.TLine(400,0.3,400,0.5))

    ci = rt.TColor.GetColor("#006600");
    for frLine in frLines:
        frLine.SetLineColor(ci)
        #frLine.SetLineStyle(2)
        frLine.SetLineWidth(2)
        frLine.Draw()

    # write the text
    pt1 = rt.TPaveText(2070,0.21,2538,0.29,"br")
    pt2 = rt.TPaveText(2070,0.41,2538,0.48,"br")
    if Box == "Had" or Box == "BJet": pt3 = rt.TPaveText(1331,0.21,1656,0.29,"br")
    else: pt3 = rt.TPaveText(1200,0.21,1526.464,0.29,"br")
    pt4 = rt.TPaveText(1100,0.41,1426,0.48,"br")
    pt5 = rt.TPaveText(471,0.22,800,0.29,"br")
    if Box == "Had" or Box == "BJet": pt6 = rt.TPaveText(540,0.32,869,0.39,"br")
    else: pt6 = rt.TPaveText(341,0.32,668,0.39,"br")

    WriteText(pt1, result[0])
    WriteText(pt2, result[1])
    WriteText(pt3, result[2])
    WriteText(pt4, result[3])
    WriteText(pt5, result[4])
    WriteText(pt6, result[5])

    # draw the arrows
    #arrow1, arrow2 = WriteArrowsLep()
    #arrow1.Draw()
    #arrow2.Draw()

    c1.SaveAs("pvalue_new_%s.C" %Box)
    c1.SaveAs("pvalue_new_%s.pdf" %Box)
