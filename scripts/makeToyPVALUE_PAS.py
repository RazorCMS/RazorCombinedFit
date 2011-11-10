from optparse import OptionParser
import ROOT as rt
from array import *
import sys

def Rebin(h):
    myhisto = rt.TH1D("%s_REBIN" %h.GetName(), "%s_REBIN" %h.GetName(), 1000, 0., 100.)
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

    # the "temperature" plot for the pvalue
    h =  rt.TH2D("h","", 10, 300, 2000., 7, 0.09, 0.5);
    mybins = sorted([300.,350.,400.,450.,650.,800.,1000.,1250.,1500.,2000.])
    x = array("d",mybins)
    h.GetXaxis().Set(len(x)-1,x)
    mybinsy = sorted([0.09, 0.16, 0.2, 0.3, 0.4, 0.45, 0.5])
    y = array("d",mybinsy)
    h.GetYaxis().Set(len(y)-1,y)
    
    h.GetXaxis().SetTitle("M_{R}[GeV]")
    h.GetYaxis().SetTitle("R^{2}")
    h.SetMaximum(1.)
    h.SetMinimum(0.)
    
    # bins in mR
    MRbins = [300, 350, 400, 450, 650, 800, 1000, 1250, 1500, 7000]
    # bins in R^2
    Rsqbins = [0.09, 0.16, 0.20, 0.30, 0.40, 0.45, 0.50]
    # min bin in the signal region, for each bin or R^2
    # This depends on the box
    minRsq = 0.16
    hSregions = []
    binList1 = [[8,1],[8,2],[8,3],[8,4],[8,5]]
    binList2 = [[7,2],[7,3],[7,4],[7,5],[6,2],[6,3],[6,4],[6,5]]
    binList3 = [[5,3],[5,4],[5,5]]
    binList4 = [[3,5],[4,5]]            
    if Box == "Mu" or  Box == "Ele":
        binList1.append([8,0])
        minRsq = 0.09
        
    bname = ""
    for i in range(0,len(binList1)): bname = bname+"b%s_%i_%i+" %(Box,binList1[i][0], binList1[i][1])
    hSregions.append(["S1",bname[:-1], "MR>1500 && MR < 7000 && Rsq > %f && Rsq < 0.5" %minRsq,binList1])
    bname = ""
    for i in range(0,len(binList2)): bname = bname+"b%s_%i_%i+" %(Box,binList2[i][0], binList2[i][1])
    hSregions.append(["S2",bname[:-1], "MR>1000 && MR < 1500 && Rsq > 0.2 && Rsq<0.5",binList2])
    bname = ""
    for i in range(0,len(binList3)): bname = bname+"b%s_%i_%i+" %(Box,binList3[i][0], binList3[i][1])
    hSregions.append(["S3",bname[:-1], "MR>800 && MR < 1000 && Rsq > 0.3 && Rsq<0.5",binList3])
    bname = ""
    for i in range(0,len(binList4)): bname = bname+"b%s_%i_%i+" %(Box,binList4[i][0], binList4[i][1])
    hSregions.append(["S4",bname[:-1], "MR>450 && MR <= 800 && Rsq > 0.45 && Rsq<0.5",binList4])

    if Box == "EleEle" or Box == "MuMu" or Box == "MuEle":
        binList1 = [[8,0],[8,1],[8,2],[8,3],[8,4],[8,5],[7,0],[7,1],[7,2],[7,3],[7,4],[7,5],[6,0],[6,1],[6,2],[6,3],[6,4],[6,5],[5,0],[5,1],[5,2],[5,3],[5,4],[5,5],[4,0],[4,1],[4,2],[4,3],[4,4],[4,5]]
        binList2 = [[3,2], [3,3], [3,4], [3,5]]
        binList3 = [[2,3], [2,4], [2,5], [1,3], [1,4], [1,5]]
        hSregions = []
        bname = ""
        for i in range(0,len(binList1)): bname = bname+"b%s_%i_%i+" %(Box,binList1[i][0], binList1[i][1])
        hSregions.append(["S1",bname[:-1], "MR>650 && Rsq > 0.09 && Rsq < 0.5",binList1])
        bname = ""
        for i in range(0,len(binList2)): bname = bname+"b%s_%i_%i+" %(Box,binList2[i][0], binList2[i][1])
        hSregions.append(["S2",bname[:-1], "MR>450 && MR<= 650 && Rsq > 0.2 && Rsq < 0.5",binList2])
        bname = ""
        for i in range(0,len(binList3)): bname = bname+"b%s_%i_%i+" %(Box,binList3[i][0], binList3[i][1])
        hSregions.append(["S3",bname[:-1], "MR>350 && MR<= 450 && Rsq > 0.3 && Rsq < 0.5", binList3])
    
    fileIn = rt.TFile.Open(fileName)
    myTree = fileIn.Get("myTree")
    dataFile = rt.TFile.Open(datafileName)
    alldata = dataFile.Get("RMRTree")

    fileOUT = rt.TFile.Open("pvalue_%s.root" %Box, "recreate")

    print "%s Box & Observed & Predicted 68 Prob. & \"p-value\" \\\\" %Box
    # loop over regions
    result = []
    for region in hSregions:
        varName = region[1]
        # make an histogram of the expected yield
        myhisto = rt.TH1D("%s" %region[0], "%s" %region[0], 100, 0., 100.)
        myTree.Project(region[0], region[1])
        #myhisto.SetBinContent(1,0)
        if myhisto.GetEntries() != 0: 
            myhisto.Scale(1./myhisto.Integral())
            # get the observed number of events
            data = alldata.reduce(region[2])
            nObs = data.numEntries()
            modeVal,rangeMin,rangeMax = find68ProbRange(myhisto)
            #nq = 3
            #xq = [0, 0, 0]
            #yq = [0.16, 0.50, 0.84]
            #myhisto.GetQuantiles(3,xq,yq)
            #rangeMin = xq[0]
            #rangeMax = xq[2]
            #medianVal = xq[1]
            medianVal = findMedian(myhisto)
            pval,myhisto,oldhisto = getPValue(nObs, myhisto)
            for mybin in region[3]: h.SetBinContent(mybin[0]+1, mybin[1]+1, pval)
            if pval >0.99: pval = 0.99 
            print "%s & %i & $[%f, %f]$ & %f \\\\" %(region[0], nObs, rangeMin, rangeMax, pval)
            BoxName = ""
            if Box == "Had": BoxName = "HAD"
            if Box == "Mu": BoxName = "MU"
            if Box == "Ele": BoxName = "ELE"
            if Box == "MuMu": BoxName = "MU-MU"
            if Box == "EleEle": BoxName = "ELE-ELE"
            if Box == "MuEle": BoxName = "MU-ELE"
            result.append([region[0], BoxName, nObs, rangeMin, rangeMax, pval, modeVal, medianVal])
            #myhisto.GetXaxis().SetRangeUser(0., rangeMax*2.)
            myhisto.Write()
            oldhisto.Write()
            del data
    h.Write()
    fileOUT.Close()


    xLines = []
    yLines = []

    for i in range(0,5):
        xLines.append(rt.TLine(x[0], y[i+1], x[9], y[i+1]))
        xLines[i].SetLineStyle(2);
        xLines[i].SetLineColor(rt.kGray);
        

    for i in range(0,8):
        yLines.append(rt.TLine(x[i+1], y[0], x[i+1], y[6]))
        yLines[i].SetLineStyle(2)
        yLines[i].SetLineColor(rt.kGray)
                      
    c1 = rt.TCanvas("c1","c1", 900, 600)
    c1.SetLogz()
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetPalette(900)
    h.Draw("colz")

    for i in range(0,5): xLines[i].Draw()
    for i in range(0,8): yLines[i].Draw()

    # write the text
    if Box == "Mu" or Box == "Had" or Box == "Ele":
        pt1 = rt.TPaveText(1512.863,0.41674,1982.45,0.491657,"br")
        pt2 = rt.TPaveText(1012,0.41674,1482.45,0.491657,"br")
        pt3 = rt.TPaveText(650.4241,0.2124211,974.4978,0.2864867,"br")
        pt4 = rt.TPaveText(450.9832,0.362255,775.279,0.4314286,"br")

        WriteText(pt1, result[0])
        WriteText(pt2, result[1])
        WriteText(pt3, result[2])
        WriteText(pt4, result[3])

        # draw the arrows
        arrow1, arrow2 = WriteArrowsLep()
        arrow1.Draw()
        arrow2.Draw()

    else:
        pt1 = rt.TPaveText(1375.307,0.1856906,1844.894,0.2600568,"br")
        pt2 = rt.TPaveText(1002.958,0.3281512,1474.916,0.4034135,"br")
        pt3 = rt.TPaveText(303.3203,0.1149082,628.2366,0.1892745,"br")
        
        WriteText(pt1, result[0])
        WriteText(pt2, result[1])
        WriteText(pt3, result[2])

        # draw the arrows
        arrow1, arrow2 = WriteArrowsDiLep()
        arrow1.Draw()
        arrow2.Draw()

    # border lines
    bLines = []
    minRsq = 0.09
    if Box == "Mu" or Box == "Had" or Box == "Ele":
        if Box == "Had": minRsq = 0.16
        bLines.append(rt.TLine(1500,minRsq,1500,0.5))
        bLines.append(rt.TLine(1000,0.20,1000,0.5))
        bLines.append(rt.TLine(800,0.30,800,0.5))
        bLines.append(rt.TLine(450,0.45,450,0.5))
        bLines.append(rt.TLine(1000,0.20,1500,0.20))
        bLines.append(rt.TLine(800,0.30,1000,0.30))
        bLines.append(rt.TLine(450,0.45,800,0.45))
    else:
        bLines.append(rt.TLine(650,minRsq,650,0.5))
        bLines.append(rt.TLine(450,0.20,450,0.5))
        bLines.append(rt.TLine(350,0.30,350,0.5))
        bLines.append(rt.TLine(450,0.20,650,0.20))
        bLines.append(rt.TLine(350,0.30,450,0.30))
        
    for line in bLines:
        line.SetLineStyle(1)
        line.SetLineColor(rt.kBlack)
        line.Draw()


    # the fit region in dashed green
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
        frLines.append(rt.TLine(450,0.3,450,0.45))
        frLines.append(rt.TLine(450,0.45,400,0.45))
        frLines.append(rt.TLine(400,0.45,400,0.5))
        frLines.append(rt.TLine(400,0.5,300,0.5))

    if Box == "MuMu" or Box == "EleEle" or Box == "MuEle":
        frLines.append(rt.TLine(650,0.09,650,0.2))
        frLines.append(rt.TLine(650,0.2,450,0.2))
        frLines.append(rt.TLine(450,0.2,450,0.3))
        frLines.append(rt.TLine(350,0.3,450,0.3))
        frLines.append(rt.TLine(350,0.3,350,0.5))

    ci = rt.TColor.GetColor("#006600");
    for frLine in frLines:
        frLine.SetLineColor(ci)
        frLine.SetLineStyle(2)
        frLine.SetLineWidth(2)
        frLine.Draw()

    sometext = rt.TPaveText(405.3013,0.2062981,874.8884,0.2815603,"br")
    if Box == "MuMu" or Box == "EleEle" or Box == "MuEle": sometext = rt.TPaveText(281.9754,0.209882,751.5625,0.2851442,"br")
    sometext.SetFillColor(0)
    sometext.SetFillStyle(0)
    sometext.SetLineColor(0)
    sometext.SetTextAlign(13)
    sometext.SetTextSize(0.022)
    sometext.SetFillColor(0)
    sometext.SetBorderSize(0)
    sometext.SetTextAlign(13)
    sometext.SetTextFont(42)
    sometext.SetTextSize(0.0282392)
    sometext.AddText("Fit Region")
    sometext.Draw()
        
    c1.SaveAs("pValue_%s.C" %Box)
    c1.SaveAs("pValue_%s.pdf" %Box)
