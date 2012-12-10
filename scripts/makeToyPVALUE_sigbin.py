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

def findMedian(myHisto):
    prob = 0
    median = 0
    for i in range(1, myHisto.GetNbinsX()+1):
        if prob <= 0.5 and prob+myHisto.GetBinContent(i) > 0.5:
            median = myHisto.GetBinCenter(i)
        prob = prob + myHisto.GetBinContent(i)
    return median

def find68ProbRange(hToy, probVal=0.6827):
    minVal = 0.
    maxVal = 100000.
    if hToy.Integral()<=0: return hToy.GetBinCenter(hToy.GetMaximumBin()),max(minVal,0.),maxVal
    # get the bin contents
    probsList = []
    for  i in range(1, hToy.GetNbinsX()+1):
        probsList.append(hToy.GetBinContent(i)/hToy.Integral())
    probsList.sort()
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
            fraction = (prob68-hToy.GetBinContent(i))/(hToy.GetBinContent(i+1)-hToy.GetBinContent(i))
            minVal = hToy.GetBinLowEdge(i)+hToy.GetBinWidth(i)*fraction
            foundMin = True
        if not foundMax and hToy.GetBinContent(hToy.GetNbinsX()-i) >= prob68:
            fraction = (prob68-hToy.GetBinContent(hToy.GetNbinsX()-i+1))/(hToy.GetBinContent(hToy.GetNbinsX()-i)-hToy.GetBinContent(hToy.GetNbinsX()-i+1))
            maxVal = hToy.GetBinLowEdge(hToy.GetNbinsX()-i)+hToy.GetBinWidth(hToy.GetNbinsX()-i)*(1-fraction)
            foundMax = True
    return hToy.GetBinCenter(hToy.GetMaximumBin()),max(minVal,0.),maxVal

def decideToUseKDE(minX,maxX,htemp):
    if maxX<=10:
        return False
    if htemp.GetMaximumBin() <= htemp.FindBin(3):
        return False
    return True

def useThisRho(minX,maxX,htemp):
    if max>10. and maxX<=20:
        return 2.0
    if max>10. and maxX<=40:
        return 1.5
    return 1.0

def find68ProbRangeFromKDEMedian(maxX,func, probVal=0.6827):
    mean = func.Mean(0.,maxX)
    funcMax = func.GetMaximum()
    mode = func.GetX(funcMax,0.,maxX)
    totalProb = func.Integral(0,maxX)
    nprobSum = int(1.0)
    probSum = array("d",[0.5])
    q = array("d",[0])
    func.GetQuantiles(nprobSum,q,probSum)
    median = q[0]
    # iterate first with a coarse epsilon
    # THEN iterate again with a smaller epsilon
    probRange = 0.
    epsilon=median/10.0
    above68=False
    numIter = 0
    sigmaMinus = median
    sigmaPlus = median
    while abs(probRange - probVal)>0.001 and numIter < 100.:
        numIter += 1
        if probRange < probVal:
            above68 = True
            sigmaMinus = sigmaMinus - epsilon
            sigmaPlus = sigmaPlus + epsilon
        else:
            if above68: epsilon = epsilon/10.0
            above68 = False
            sigmaMinus = sigmaMinus + epsilon
            sigmaPlus = sigmaPlus - epsilon
            
        if sigmaMinus<=0: sigmaMinus = 0.
        if sigmaPlus>=maxX: sigmaPlus = maxX
        if sigmaMinus<sigmaPlus : probRange = func.Integral(sigmaMinus,sigmaPlus)/totalProb
        else: probRange = 0.
        if numIter%5 == 0: print "iteration = %d"%numIter
    print "sigmaPlus = %f"%sigmaPlus
    print "sigmaMinus = %f"%sigmaMinus
    print "Int_[sigmaMinus,sigmaPlus] f(x) dx = %f"%probRange
   
    funcFill68 = func.Clone("funcFill68")
    funcFill68.SetRange(sigmaMinus,sigmaPlus)
    ic68 = rt.TColor(1404, 0.49, 0.60, 0.82,"")
    funcFill68.SetFillColor(ic68.GetColor(0.49,0.60,.82))
    funcFill68.SetFillStyle(3144)
    funcFill68.Draw("same")
    return mode,sigmaMinus,sigmaPlus,probRange,funcFill68

def getSigma(n, hToy):
    if hToy.GetMaximumBin() == hToy.FindBin(n): return 0.
    medianVal = findMedian(hToy)
    pVal = 1.-getPValue(n,hToy)
    if n>medianVal: return rt.TMath.NormQuantile(0.5 + pVal/2.)
    else: return -rt.TMath.NormQuantile(0.5 + pVal/2.)

def getSigmaFromPval(n, hToy, pVal):
    if hToy.GetMaximumBin() == hToy.FindBin(n): return 0.
    medianVal = findMedian(hToy)
    coreProb = 1. - pVal
    if n>medianVal: return rt.TMath.NormQuantile(0.5 + coreProb/2.)
    else: return -rt.TMath.NormQuantile(0.5 + coreProb/2.)

def getPValueFromKDE(nObs,maxX,func):
    funcObs = func.Eval(nObs)
    funcMax = func.GetMaximum()
    otherRoot = 0.
    rightSide = False
    veryNearMax = False
    epsilon = max(0.2,nObs/100)
    pvalKDE = 0
    totalProb = func.Integral(0,maxX)
    if abs(float(funcObs)-funcMax)/funcMax < 0.003:
        veryNearMax = True
        pvalKDE = 1.
        otherRoot = nObs
    elif func.Derivative(nObs)<0.:
        rightSide = True
        otherRoot = func.GetX(funcObs,0,nObs-epsilon)
        if otherRoot >= nObs-epsilon:
            otherRoot = func.GetX(funcObs-0.0005,0,nObs-epsilon)
        if otherRoot < nObs-epsilon:
            pvalKDE = func.Integral(0,otherRoot)
        pvalKDE += func.Integral(nObs,maxX)
    else:
        otherRoot = func.GetX(funcObs,nObs+epsilon,maxX)
        pvalKDE = func.Integral(0,nObs)
        pvalKDE += func.Integral(otherRoot,maxX)
    pvalKDE = pvalKDE/totalProb
    # DRAWING FUNCTION AND FILLS
    ic = rt.TColor(1398, 0.75, 0.92, 0.68,"")
    func.SetLineColor(ic.GetColor(0.1, .85, 0.5))
    funcFillRight = func.Clone("funcFillRight")
    funcFillLeft = func.Clone("funcFillLeft")
    if veryNearMax:
        funcFillRight.SetRange(nObs,maxX)
        funcFillLeft.SetRange(0,nObs)
    elif rightSide:
        funcFillRight.SetRange(nObs,maxX)
        funcFillLeft.SetRange(0,otherRoot)
    else:
        funcFillRight.SetRange(otherRoot,maxX)
        funcFillLeft.SetRange(0,nObs)
    funcFillRight.SetFillColor(ic.GetColor(0.1, .85, 0.5))
    funcFillRight.SetFillStyle(3002)
    funcFillLeft.SetFillColor(ic.GetColor(0.1, .85, 0.5))
    funcFillLeft.SetFillStyle(3002)
    func.Draw("same")
    funcFillRight.Draw("fcsame")
    if (rightSide and otherRoot < nObs-epsilon) or not rightSide:
        funcFillLeft.Draw("fcsame")
    # PRINTING INFORMATION
    print "nObs =  %d"%(nObs)
    print "f(nObs) =  %f"%(funcObs)
    print "fMax = %f"%(funcMax)
    print "percent diff = %f"%(abs(float(funcObs)-funcMax)/funcMax)
    print "other root = %f"%(otherRoot)
    print "total prob =  %f"%(totalProb)
    print "pvalKDE = %f"%pvalKDE
    return pvalKDE,funcFillRight,funcFillLeft

def getPValue(n, hToy):
    if hToy.Integral() <= 0.: return 0.
    Prob_n = hToy.GetBinContent(hToy.FindBin(n))
    Prob = 0
    for i in range(1, hToy.GetNbinsX()+1):
        if hToy.GetBinContent(i)<= Prob_n: Prob += hToy.GetBinContent(i)
    Prob = Prob/hToy.Integral()
    return Prob

def getHistogramsWriteTable(MRbins, Rsqbins,nBtagbins, fileName, dataFileName, Box, outFolder, printPlots = True, fit3D = True, btag = 0):
    
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
    nToys  = myTree.GetEntries()
    dataFile = rt.TFile.Open(dataFileName)
    alldata = dataFile.Get("RMRTree")
    
    # p-values 1D plot
    pValHist = rt.TH1D("pVal%s" %Box, "pVal%s" %Box, 20, 0., 1.)

    #prepare the latex table
    if fit3D: tableFileName = "%s/table_%s.tex" %(outFolder,Box)
    else: tableFileName = "%s/table_%s.tex" %(outFolder,Box)
    table = open(tableFileName,"w")
    table.write("\\errorcontextlines=9\n")
    table.write("\\documentclass[12pt]{article}\n")
    table.write("\\begin{document}\n")
    table.write("\\begin{table}[!ht]\n")
    table.write("\\begin{tiny}\n")
    table.write("\\begin{center}\n")
    table.write("\\begin{tabular}{|c|c|c|c|c|c|c|c|}\n")
    table.write("\\hline\n")
    table.write("$M_R$ Range & $R^2$ Range & Observed & Predicted Mode & Predicted Median & Predicted 68 Prob. Range & p-value & n$\\sigma$ \\\\\n")
    table.write("\\hline\n")
    # loop over regions
    result = []
    for i in range(0,len(MRbins)-1):
        for j in range(0,len(Rsqbins)-1):
            if fit3D:
                sumName = "b%i_%i_1+b%i_%i_2+b%i_%i_3+" %(i,j,i,j,i,j)
                varNames = ["b%i_%i_1"%(i,j),"b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)]
                varName = varNames[0]
            else:
                varName = "b%i_%i" %(i,j)
                sumName = "b%i_%i+" %(i,j)
            histoName = "Histo_%s" %varName
            # make an histogram of the expected yield
            myTree.Draw(sumName[:-1])
            htemp = rt.gPad.GetPrimitive("htemp")
            mean = htemp.GetMean()
            rms = htemp.GetRMS()
            numBin = array('f',[0])
            
            maxX = int(max(10.0,mean+5.*rms))
            minX = int(max(0.0,mean-5.*rms))
            htemp.Scale(1./htemp.Integral())
            
            # GET THE OBSERVED NUMBER OF EVENTS
            if fit3D:
                data = alldata.reduce("MR>= %f && MR < %f && Rsq >= %f && Rsq < %f && nBtag >= %i" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], nBtagbins[0]))
            else:
                data = alldata.reduce("MR>= %f && MR < %f && Rsq >= %f && Rsq < %f && nBtag >= %i" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], nBtagbins[0]))
            nObs = data.numEntries()
            
            switchToKDE = decideToUseKDE(minX,maxX,htemp)

            del htemp
            
            rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"myhisto\");")
            myhisto = rt.TH1D("myhisto", histoName, maxX, 0., maxX)
            myTree.Project("myhisto", sumName[:-1])
            myhisto.Scale(1./myhisto.Integral())
            
            rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"orighisto\");")
            orighisto = myhisto.Clone("orighisto")
            
            rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"canvas\");")
            c = rt.TCanvas("canvas","canvas",800,600)
            orighisto.SetLineColor(rt.kBlack)
            orighisto.Draw()
            if myhisto.GetEntries() != 0:
                if switchToKDE:
                    nExp = [rt.RooRealVar(varName,varName,0,maxX) for varName in varNames]
                    nExpSet = rt.RooArgSet("nExpSet")
                    nExpList = rt.RooArgList("nExpList")
                    for j in range(0,len(nExp)):
                        nExpSet.add(nExp[j])
                        nExpList.add(nExp[j])
                    dataset = rt.RooDataSet("dataset","dataset",myTree,nExpSet)
                    sumExp = rt.RooFormulaVar("sumExp","sumExp",sumName[:-1],nExpList)
                    sumExpData = dataset.addColumn(sumExp)
                    sumExpData.setRange(0,maxX)
                    rho = useThisRho(0.,maxX,myhisto)
                    rkpdf = rt.RooKeysPdf("rkpdf","rkpdf",sumExpData,dataset,rt.RooKeysPdf.NoMirror,rho)
                    func = rkpdf.asTF(rt.RooArgList(sumExpData))
                    # GETTING THE P-VALUE
                    pvalKDE,funcFillRight,funcFillLeft = getPValueFromKDE(nObs,maxX,func)
                    
                if switchToKDE: modeVal,rangeMin,rangeMax,probRange,funcFill68 = find68ProbRangeFromKDEMedian(maxX,func)

                else: modeVal,rangeMin,rangeMax = find68ProbRange(myhisto)

                medianVal = findMedian(myhisto)
                if switchToKDE: pval = pvalKDE
                else: pval = getPValue(nObs, myhisto)
                    
                # the p-value cannot be one... And we have a limited number of toys
                pvalmax = 1.-1./myhisto.GetEntries()
                pvalmin = 0.+1./(10*myhisto.GetEntries())
                if pval >pvalmax: pval = pvalmax 
                # these are those bins where we see 0 and we expect 0
                if pval == pvalmax and myhisto.GetMaximumBin() == 1: nsigma = 0.
                if pval==0: pval = pvalmin
                # use the adjusted p-value 
                h.SetBinContent(i+1, j+1, pval)
                nsigma = getSigmaFromPval(nObs, myhisto,pval)
                if pval==pvalmin:
                    if nsigma<0: nsigma = -5.0
                    else: nsigma = 5.0

                
                # FINISHING PLOTTING AND LEGEND
                nObsLine = rt.TLine(nObs,0.,nObs,1.05*orighisto.GetMaximum())
                icObs = rt.TColor(1404, 0.49, 0.60, 0.82,"")
                nObsLine.SetLineColor(icObs.GetColor(0.1,0.5,0.6))
                nObsLine.SetLineWidth(3)
                nObsLine.Draw("same")
                tleg = rt.TLegend(0.65,.65,.9,.9)
                tleg.AddEntry(nObsLine,"nObs = %d"%nObs,"l")
                if switchToKDE:
                    tleg.AddEntry(funcFillRight,"p-value = %.2f"%pval,"f")
                    tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,rangeMin,rangeMax),"f")
                else:
                    tleg.AddEntry(myhisto,"p-value = %.2f"%pval,"f")
                    tleg.AddEntry(myhisto,"68%% Range = [%.1f,%.1f]"%(rangeMin,rangeMax),"f")
                tleg.SetFillColor(rt.kWhite)
                tleg.Draw("same")
                rt.gStyle.SetOptStat(0)
                if printPlots: c.Print("%s/histotest_%s.pdf"%(outFolder,varName))
                del c
                
                hNS.SetBinContent(i+1, j+1, nsigma)
                if nObs==0 and (rangeMax+rangeMin/2)<1.:
                    hNS.SetBinContent(i+1, j+1, -999)
                hOBS.SetBinContent(i+1, j+1, nObs)
                hEXP.SetBinContent(i+1, j+1, (rangeMax+rangeMin)/2)
                hEXP.SetBinError(i+1, j+1, (rangeMax-rangeMin)/2)
                if (rangeMax+rangeMin)/2 == 50000.: continue
                if pval<0.15: table.write("$[%4.0f,%4.0f]$ & $[%5.4f,%5.4f]$ & %i & %3.1f & %3.1f & $%3.1f \\pm %3.1f$ & %4.2f & %4.2f \\\\ \n" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], nObs, modeVal, medianVal, (rangeMax+rangeMin)/2, (rangeMax-rangeMin)/2, pval, nsigma))

                # fill the pvalue plot for non-empty bins with expected 0.5 (spikes at 0)
                if not (pval ==0.99 and modeVal == 0.5): pValHist.Fill(pval)

                BoxName = ""
                if Box == "MultiJet": BoxName = "MULTIJET"
                if Box == "TauTauJet": BoxName = "TAU-TAU-JET"
                if Box == "Jet": BoxName = "JET"
                if Box == "Mu": BoxName = "MU"
                if Box == "Ele": BoxName = "ELE"
                if Box == "MuMu": BoxName = "MU-MU"
                if Box == "EleEle": BoxName = "ELE-ELE"
                if Box == "MuEle": BoxName = "MU-ELE"
                result.append([varName, BoxName, nObs, rangeMin, rangeMax, pval, modeVal, medianVal])
                del data

    # finish writing the table and close the tex file
    table.write("\\hline\n")
    table.write("\\end{tabular}\n")
    table.write("\\end{center}\n")
    table.write("\\end{tiny}\n")
    table.write("\\end{table}\n")
    table.write("\\end{document}\n")
    table.close()
    return h, hOBS, hEXP, hNS, pValHist

def writeFilesDrawHistos(MRbins, Rsqbins, h, hOBS, hEXP, hNS, pValHist, Box, outFolder, fit3D, btagOpt):
    fileOUT = rt.TFile.Open("%s/pvalue_%s.root" %(outFolder,Box), "recreate")
    h.Write()
    hNS.Write()
    pValHist.Write()
    fileOUT.Close()
    
    fileOUTint = rt.TFile.Open("%s/ExpectedObserved_RazorHad_Winter2012.root"%outFolder, "recreate")
    hOBS.Write()
    hEXP.Write()
    fileOUTint.Close()

    # the gray lines
    xLines = []
    yLines = []

    x = array("d",MRbins)
    y = array("d",Rsqbins)
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

                      
    rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"c1\");")
    c1 = rt.TCanvas("c1","c1", 900, 600)
    c1.SetLogz()
    setCanvasStyle(c1)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetPalette(900)
    h.Draw("colz")

    for i in range(0,len(xLines)): xLines[i].Draw()
    for i in range(0,len(yLines)): yLines[i].Draw()

    c1.SaveAs("%s/pvalue_sigbin_%s.C" %(outFolder,Box))
    c1.SaveAs("%s/pvalue_sigbin_%s.pdf" %(outFolder,Box))

    rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"c2\");")
    c2 = rt.TCanvas("c2","c2", 900, 600)
    setCanvasStyle(c2)
    # French flag Palette
    Red = array('d',  [0.00, 0.70, 0.90, 1.00, 1.00, 1.00, 1.00])
    Green = array('d',[0.00, 0.70, 0.90, 1.00, 0.90, 0.70, 0.00])
    Blue = array('d', [1.00, 1.00, 1.00, 1.00, 0.90, 0.70, 0.00])
    Length =array('d',[0.00, 0.20, 0.35, 0.50, 0.65, 0.8, 1.00]) # colors get darker faster at 4sigma
    rt.TColor.CreateGradientColorTable(7,Length,Red,Green,Blue,9999)
    hNS.SetMaximum(5.1)
    hNS.SetMinimum(-5.1) # so the binning is 0 2 4
    hNS.SetContour(9999)
    # changes a few of the level colors by chaning the cut-offs
    # for external viewing:
    #hNS.SetContourLevel(6,1.5)
    #hNS.SetContourLevel(5,-1.5)
    #hNS.SetContourLevel(7,2.5)
    #hNS.SetContourLevel(4,-2.5)
    hNS.SetBinContent(1, 1, -999)
    hNS.GetXaxis().SetMoreLogLabels()
    #hNS.GetYaxis().SetMoreLogLabels()
    hNS.GetXaxis().SetNoExponent()
    hNS.GetYaxis().SetNoExponent()
    hNS.Draw("colz")
    fGrayGraphs = []
    tlatexList = []
    col1 = rt.gROOT.GetColor(rt.kGray+1)
    col1.SetAlpha(0.3)
    for iBinX in range(1,hNS.GetNbinsX()+1):
        for iBinY in range(1,hNS.GetNbinsY()+1):
            if hNS.GetBinContent(iBinX,iBinY)!= -999: continue
            xBinLow = hNS.GetXaxis().GetBinLowEdge(iBinX)
            xBinHigh = xBinLow+hNS.GetXaxis().GetBinWidth(iBinX)
            yBinLow = hNS.GetYaxis().GetBinLowEdge(iBinY)
            yBinHigh = yBinLow+hNS.GetYaxis().GetBinWidth(iBinY)
            fGray = rt.TGraph(5)
            fGray.SetPoint(0,xBinLow,yBinLow)
            fGray.SetPoint(1,xBinLow,yBinHigh)
            fGray.SetPoint(2,xBinHigh,yBinHigh)
            fGray.SetPoint(3,xBinHigh,yBinLow)
            fGray.SetPoint(4,xBinLow,yBinLow)
            fGray.SetFillColor(rt.kGray+1)
            fGrayGraphs.append(fGray)
    for iBinX in range(1,hNS.GetNbinsX()+1):
        for iBinY in range(1,hNS.GetNbinsY()+1):
            binCont = hNS.GetBinContent(iBinX,iBinY)
            if binCont == -999: continue
            if abs(binCont)< 0.1: continue
            if binCont>=0:
                xBin  = hNS.GetXaxis().GetBinLowEdge(iBinX) + .25*hNS.GetXaxis().GetBinWidth(iBinX)
                yBin = hNS.GetYaxis().GetBinLowEdge(iBinY) + .3*hNS.GetYaxis().GetBinWidth(iBinY)
            elif binCont<0:
                xBin  = hNS.GetXaxis().GetBinLowEdge(iBinX) + .1*hNS.GetXaxis().GetBinWidth(iBinX) # left side of TLatex 10% across the binwidth in X
                yBin = hNS.GetYaxis().GetBinLowEdge(iBinY) + .3*hNS.GetYaxis().GetBinWidth(iBinY) # bottom of TLatex 30% across the binwidth in X
            tlatex = rt.TLatex(xBin,yBin,"%2.1f"%binCont)
            tlatex.SetTextSize(0.05)
            tlatex.SetTextFont(42)
            tlatexList.append(tlatex)
    for fGray in fGrayGraphs: fGray.Draw("F")
    for i in range(0,len(xLines)): xLines[i].Draw()
    for i in range(0,len(yLines)): yLines[i].Draw()
    c2.SaveAs("%s/nSigma_%s.C" %(outFolder,Box))
    c2.SaveAs("%s/nSigma_%s.pdf" %(outFolder,Box))

    for tlatex in tlatexList: tlatex.Draw()
        
    # now for a log scale plot
    c2.SetLogx()
    c2.SetLogy()
    tlabels = []
    tlabels.append(rt.TLatex(262,0.75, "0.8"))
    tlabels.append(rt.TLatex(262,0.375, "0.4"))
    tlabels.append(rt.TLatex(262,0.19, "0.2"))
    for tlabel in tlabels:
        tlabel.SetTextSize(0.055)
        tlabel.SetTextFont(42)
        tlabel.Draw()
    c2.SaveAs("%s/nSigmaLog_%s.C" %(outFolder,Box))
    c2.SaveAs("%s/nSigmaLog_%s.pdf" %(outFolder,Box))

  
if __name__ == '__main__':
    Box = sys.argv[1]
    fileName = sys.argv[2]
    dataFileName = sys.argv[3]
    outFolder = sys.argv[4]
    
    noBtag = False
    
    printPlots = True

    fit3D = False
    
    frLabels = []
    for i in range(5,len(sys.argv)):
        if sys.argv[i] == "--noBtag": noBtag = True
        if sys.argv[i] == "--3D": fit3D = True
        if sys.argv[i].find("--fit-region=") != -1:
            frLabelString = sys.argv[i].replace("--fit-region=","")
            frLabels = frLabelString.split("_")

        
    MRbins, Rsqbins, nBtagbins = makeBluePlot.Binning(Box, noBtag)
    
    hList, hOBSList, hEXPList, hNSList, pValHistList = [], [], [], [], []
    btagOpt = 0
    h, hOBS, hEXP, hNS, pValHist = getHistogramsWriteTable(MRbins, Rsqbins, nBtagbins, fileName, dataFileName, Box, outFolder, printPlots, fit3D, btagOpt)
    hList.append(h)
    hOBSList.append(hOBS)
    hEXPList.append(hEXP)
    hNSList.append(hNS)
    pValHistList.append(pValHist)

    
    for h, hOBS, hEXP, hNS, pValHist in zip(hList,hOBSList,hEXPList,hNSList,pValHistList):
        writeFilesDrawHistos(MRbins, Rsqbins, h, hOBS, hEXP, hNS, pValHist, Box, outFolder, fit3D, btagOpt)


    #ignore the individual b-tags for now:
    #for btag in nBtagbins[:-1]:
    #    h, hOBS, hEXP, hNS, pValHist = getHistogramsWriteTable(MRbins, Rsqbins, nBtagbins, fileName, dataFileName, Box, outFolder, printPlots, fit3D, btag)
    #    hList.append(h)
    #    hOBSList.append(hOBS)
    #    hEXPList.append(hEXP)
    #    hNSList.append(hNS)
    #    pValHistList.append(pValHist)
    
    #for h, hOBS, hEXP, hNS, pValHist, btag in zip(hList,hOBSList,hEXPList,hNSList,pValHistList,nBtagbins[:-1]):
    #    writeFilesDrawHistos(MRbins, Rsqbins, h, hOBS, hEXP, hNS, pValHist, Box, outFolder, fit3D, btag)
