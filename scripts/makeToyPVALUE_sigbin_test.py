from optparse import OptionParser
import ROOT as rt
import RootTools
import RazorCombinedFit
from array import *
import sys
import makeBluePlot


def set2DStyle(h) :
    h.GetXaxis().SetTitle("M_{R}[GeV]")
    h.GetYaxis().SetTitle("R^{2}")
    h.GetXaxis().SetTitleSize(0.065)
    h.GetXaxis().SetLabelSize(0.065)
    h.GetYaxis().SetTitleSize(0.065)
    h.GetYaxis().SetLabelSize(0.065)

def setCanvasStyle(c):
    c.SetLeftMargin(0.15)
    c.SetBottomMargin(0.15)

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

def findMedianKDE(func):
    nprobSum = int(1.0)
    probSum = array("d",[0.5])
    q = array("d",[0])
    func.GetQuantiles(nprobSum,q,probSum)
    medianVal = q[0]
    return medianVal

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
        if htemp.GetMean()>5.:
            return True
        else:
            return False
    return True

def useThisRho(minX,maxX,htemp):
    return 2.0
    if max>10. and maxX<=20:
        return 2.0
    if max>10. and maxX<=40:
        return 1.5
    return 1.0

def find68ProbRangeFromKDEMode(maxX,func, probVal=0.6827):
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

    epsilon=mode/3.0
    #epsilon = max(mode/2, (maxX - mode)/2)
    above68 = False
    numIter = 0
    sigmaMinus = mode
    sigmaPlus = mode
    while abs(probRange - probVal)>0.01 and numIter < 100.:
        numIter += 1
        if probRange < probVal:
            if above68:  epsilon = epsilon/2.0
            above68 = False
            sigmaMinus = sigmaMinus - epsilon
            sigmaPlus = sigmaPlus + epsilon
        else:
            if not above68: epsilon = epsilon/2.0
            above68 = True
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
            otherRoot = func.GetX(funcObs*(0.99),0,nObs-epsilon)
        elif otherRoot < nObs-epsilon:
            pvalKDE = func.Integral(0,otherRoot)
        pvalKDE += func.Integral(nObs,maxX)
    else:
        otherRoot = func.GetX(funcObs,nObs+epsilon,maxX)
        if otherRoot <= nObs+epsilon:
            otherRoot = func.GetX(funcObs*(0.99),nObs+epsilon,maxX)
        elif otherRoot > nObs+epsilon:
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
    if n > hToy.GetXaxis().GetLast() : return 0.
    Prob_n = hToy.GetBinContent(hToy.FindBin(n))
    Prob = 0
    for i in range(1, hToy.GetNbinsX()+1):
        if hToy.GetBinContent(i)<= Prob_n: Prob += hToy.GetBinContent(i)
    Prob = Prob/hToy.Integral() #useless, toy histograms are normalized
    return Prob

def getHistogramsWriteTable(MRbins, Rsqbins,nBtagbins, fileName, dataFileName, Box, outFolder, printPlots, fit3D, btagOpt):
    
    x = array("d",MRbins)
    y = array("d",Rsqbins)
    numberOfBinsGt2Sigma = 0
    if btagOpt>0:
        h =  rt.TH2D("h_%ib"%btagOpt,"", len(MRbins)-1, x, len(Rsqbins)-1, y)
        hOBS =  rt.TH2D("hOBS_%ib"%btagOpt,"hOBS_%ib"%btagOpt, len(MRbins)-1, x, len(Rsqbins)-1, y)
        hEXP =  rt.TH2D("hEXP_%ib"%btagOpt,"hEXP_%ib"%btagOpt, len(MRbins)-1, x, len(Rsqbins)-1, y)
        hNS =   rt.TH2D("hNS_%ib"%btagOpt,"", len(MRbins)-1, x, len(Rsqbins)-1, y)
    else:
        h =  rt.TH2D("h","", len(MRbins)-1, x, len(Rsqbins)-1, y)
        hOBS =  rt.TH2D("hOBS","hOBS", len(MRbins)-1, x, len(Rsqbins)-1, y)
        hEXP =  rt.TH2D("hEXP","hEXP", len(MRbins)-1, x, len(Rsqbins)-1, y)    
        hNS =  rt.TH2D("hNS","", len(MRbins)-1, x, len(Rsqbins)-1, y)
    set2DStyle(h)
    h.SetMaximum(1.)
    h.SetMinimum(0.)

    set2DStyle(hNS)
    fileIn = rt.TFile.Open(fileName)
    myTree = fileIn.Get("myTree")
    nToys  = myTree.GetEntries()
    dataFile = rt.TFile.Open(dataFileName)
    workspace = dataFile.Get(Box+"/Box"+Box+"_workspace")
#    alldata = workspace.obj("sigbkg")
    alldata = workspace.obj("RMRTree")
    
    # p-values 1D plot
    pValHist = rt.TH1D("pVal_%ib_%s" %(btagOpt,Box), "pVal%s" %Box, 20, 0., 1.)

    #prepare the latex table
    if btagOpt>0:
        tableFileName = "%s/table_%ib_%s.tex" %(outFolder,btagOpt,Box)
    else:
        tableFileName = "%s/table_%s.tex" %(outFolder,Box)
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
                if btagOpt==0:
                    sumName = "b%i_%i_1+b%i_%i_2+b%i_%i_3+" %(i,j,i,j,i,j)
                    varNames = ["b%i_%i_1"%(i,j),"b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)]
                elif btagOpt==1:
                    sumName = "b%i_%i_1+" %(i,j)
                    varNames = ["b%i_%i_1"%(i,j)]
                elif btagOpt==23:
                    sumName =  "b%i_%i_2+b%i_%i_3+" %(i,j,i,j)
                    varNames = ["b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)]

                varName  = "Plus".join(varNames)
            else:
                varName = "b%i_%i" %(i,j)
                sumName = "b%i_%i+" %(i,j)
                varNames = [varName]
            histoName = "Histo_%s" %varName
            # make an histogram of the expected yield
            myTree.Draw(sumName[:-1])
            htemp = rt.gPad.GetPrimitive("htemp")
            mean = htemp.GetMean()
            rms = htemp.GetRMS()
            numBin = array('f',[0])
            
            # GET THE OBSERVED NUMBER OF EVENTS
            if fit3D:
                if btagOpt==0:
                    data = alldata.reduce("MR>= %f && MR < %f && Rsq >= %f && Rsq < %f && nBtag >= %i." %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], 1))
                elif btagOpt==1:
                    data = alldata.reduce("MR>= %f && MR < %f && Rsq >= %f && Rsq < %f && nBtag >= %i. && nBtag < %i." %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], 1, 2))
                elif btagOpt==23:
                    data = alldata.reduce("MR>= %f && MR < %f && Rsq >= %f && Rsq < %f && nBtag >= %i." %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], 1))
            else:
                data = alldata.reduce("MR>= %f && MR < %f && Rsq >= %f && Rsq < %f && nBtag >= %i" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], nBtagbins[0]))
            nObs = data.numEntries()
            
            maxX = int(max(10.0,mean+10.*rms))
            minX = 0.0
            htemp.Scale(1./htemp.Integral())

            switchToKDE = decideToUseKDE(minX,maxX,htemp)
            
            del htemp
    
            rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"myhisto\");")
            myhisto = rt.TH1D("myhisto", histoName, maxX, 0., maxX)
            myTree.Project("myhisto", sumName[:-1]) #get b_i_j_1 + b_i_j_2 + b_i_j_3

            myhisto.Scale(1./myhisto.Integral())
            
            rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"orighisto\");")
            orighisto = myhisto.Clone("orighisto")
            
            rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"canvas\");")
            c = rt.TCanvas("canvas","canvas",800,600)
            orighisto.SetLineColor(rt.kBlack)
            orighisto.GetXaxis().SetTitle("Event Yield in Bin (%i < M_{R} < %i, %.2f < R^{2} < %.2f)"%(MRbins[i],MRbins[i+1],Rsqbins[j],Rsqbins[j+1]))
            orighisto.GetYaxis().SetTitle("Probability")
            orighisto.GetYaxis().SetTitleOffset(1.7)
            orighisto.GetXaxis().SetTitleOffset(1.2)
            c.SetLeftMargin(0.15)
            orighisto.Draw()
            if myhisto.GetEntries() != 0:
                if switchToKDE :#and fit3D:
                    nExp = [rt.RooRealVar(iVar,iVar,0,maxX) for iVar in varNames]
                    nExpSet = rt.RooArgSet("nExpSet")
                    nExpList = rt.RooArgList("nExpList")
                    for intVar in range(0,len(nExp)):
                        nExpSet.add(nExp[intVar])
                        nExpList.add(nExp[intVar])
                    dataset = rt.RooDataSet("dataset","dataset",myTree,nExpSet)
                    sumExp = rt.RooFormulaVar("sumExp","sumExp",sumName[:-1],nExpList)
                    sumExpData = dataset.addColumn(sumExp)
                    sumExpData.setRange(0,maxX)
                    rho = useThisRho(0.,maxX,myhisto)
                    rkpdf = rt.RooKeysPdf("rkpdf","rkpdf",sumExpData,dataset,rt.RooKeysPdf.NoMirror,rho)
                    func = rkpdf.asTF(rt.RooArgList(sumExpData))
                    # GETTING THE P-VALUE
                    pvalKDE,funcFillRight,funcFillLeft = getPValueFromKDE(nObs,maxX,func)
                    
                if switchToKDE: modeVal,rangeMin,rangeMax,probRange,funcFill68 = find68ProbRangeFromKDEMode(maxX,func)

                else: modeVal,rangeMin,rangeMax = find68ProbRange(myhisto)

                if switchToKDE:
                    medianVal = findMedianKDE(func)
                else:
                    medianVal = findMedian(myhisto)
                if switchToKDE: pval = pvalKDE
                else:
                    pval = getPValue(nObs, myhisto)
               
                # the p-value cannot be one... And we have a limited number of toys
                pvalmax = 1.-1./myhisto.GetEntries()
                pvalmin = 0.+1./(10*myhisto.GetEntries())
                if pval >pvalmax:
                    pval = pvalmax 
                # these are those bins where we see 0 and we expect 0
                if pval == pvalmax and myhisto.GetMaximumBin() == 1:
                    nsigma = 0.
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
                print "(i,j) = (%i,%i)"%(i,j)
                print "$[%4.0f,%4.0f]$ & $[%5.4f,%5.4f]$ & %i & %3.1f & %3.1f & $%3.1f \\pm %3.1f$ & %4.2f & %4.1f \\\\ \n" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], nObs, modeVal, medianVal, (rangeMax+rangeMin)/2, (rangeMax-rangeMin)/2, pval, nsigma)
                if pval<0.15 :
                    table.write("$[%4.0f,%4.0f]$ & $[%5.4f,%5.4f]$ & %i & %3.1f & %3.1f & $%3.1f \\pm %3.1f$ & %4.2f & %4.1f \\\\ \n" %(MRbins[i], MRbins[i+1], Rsqbins[j], Rsqbins[j+1], nObs, modeVal, medianVal, (rangeMax+rangeMin)/2, (rangeMax-rangeMin)/2, pval, nsigma))
                
               
                # fill the pvalue plot for non-empty bins with expected 0.5 (spikes at 0)
                if not (pval ==0.99 and modeVal == 0.5): pValHist.Fill(pval)

                BoxName = ""
                if Box == "MultiJet": BoxName = "MULTIJET"
                if Box == "TauTauJet": BoxName = "TAU-TAU-JET"
                if Box == "Jet1b": BoxName = "JET-1b"
                if Box == "Jet2b": BoxName = "JET-2b"
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
    if btagOpt>0:
        fileOUT = rt.TFile.Open("%s/pvalue_%ib_%s.root" %(outFolder,btagOpt,Box), "recreate")
    else:
        fileOUT = rt.TFile.Open("%s/pvalue_%s.root" %(outFolder,Box), "recreate")
    h.Write()
    hNS.Write()
    pValHist.Write()
    fileOUT.Close()
    
    if btagOpt>0:
        fileOUTint = rt.TFile.Open("%s/ExpectedObserved_%ib_%s.root"%(outFolder,btagOpt,Box), "recreate")
    else:
        fileOUTint = rt.TFile.Open("%s/ExpectedObserved_%s.root"%(outFolder,Box), "recreate")
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


    if dataFileName.find("Sideband")!=-1:
      #  yLines.append(rt.TLine(x[2], y[1], x[2], y[-1]))
        yLines.append(rt.TLine(450., 0.13, 450., 1.5))
        yLines[-1].SetLineStyle(2)
        yLines[-1].SetLineWidth(2)
        yLines[-1].SetLineColor(rt.kGreen)
       # xLines.append(rt.TLine(x[2], y[1], x[-1], y[1]))
        xLines.append(rt.TLine(450., 0.13, 4000., 0.13))
        xLines[-1].SetLineStyle(2)
        xLines[-1].SetLineWidth(2)
        xLines[-1].SetLineColor(rt.kGreen)
       
                      
    rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"c1\");")
    c1 = rt.TCanvas("c1","c1", 600, 400)
    c1.SetLogz()
    setCanvasStyle(c1)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    h.Draw("colz")

    for i in range(0,len(xLines)): xLines[i].Draw()
    for i in range(0,len(yLines)): yLines[i].Draw()

    if btagOpt>0:
        c1.SaveAs("%s/pvalue_sigbin_%ib_%s.C" %(outFolder,btagOpt,Box))
        c1.SaveAs("%s/pvalue_sigbin_%ib_%s.pdf" %(outFolder,btagOpt,Box))
    else:
        c1.SaveAs("%s/pvalue_sigbin_%s.C" %(outFolder,Box))
        c1.SaveAs("%s/pvalue_sigbin_%s.pdf" %(outFolder,Box))

    rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"c2\");")
    c2 = rt.TCanvas("c2","c2", 600, 400)
    setCanvasStyle(c2)
    # French flag Palette
    Red = array('d',  [0.00, 0.70, 0.90, 1.00, 1.00, 1.00, 1.00])
    Green = array('d',[0.00, 0.70, 0.90, 1.00, 0.90, 0.70, 0.00])
    Blue = array('d', [1.00, 1.00, 1.00, 1.00, 0.90, 0.70, 0.00])
    Length =array('d',[0.00, 0.20, 0.35, 0.50, 0.65, 0.8, 1.00]) # colors get darker faster at 4sigma
    rt.TColor.CreateGradientColorTable(7,Length,Red,Green,Blue,999)
    # French flag Palette
    #Red = array('d',  [0.00, 1.00, 1.00])
    #Green = array('d',[0.00, 1.00, 0.00])
    #Blue = array('d', [1.00, 1.00, 0.00])
    #Length =array('d',[0.00, 0.50, 1.00]) # standard color palette
    #rt.TColor.CreateGradientColorTable(3,Length,Red,Green,Blue,9999)
    hNS.SetMaximum(5.1)
    hNS.SetMinimum(-5.1) # so the binning is 0 2 4
    hNS.SetContour(999)
    # changes a few of the level colors by chaning the cut-offs
    # for external viewing:
    #hNS.SetContourLevel(6,1.5)
    #hNS.SetContourLevel(5,-1.5)
    #hNS.SetContourLevel(7,2.5)
    #hNS.SetContourLevel(4,-2.5)
    #hNS.SetBinContent(1, 1, -999)
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
            if binCont>=0.:
                xBin  = hNS.GetXaxis().GetBinLowEdge(iBinX) + .25*hNS.GetXaxis().GetBinWidth(iBinX)
                yBin = hNS.GetYaxis().GetBinLowEdge(iBinY) + .3*hNS.GetYaxis().GetBinWidth(iBinY)
            elif binCont<0.:
                xBin  = hNS.GetXaxis().GetBinLowEdge(iBinX) + .1*hNS.GetXaxis().GetBinWidth(iBinX) # left side of TLatex 10% across the binwidth in X
                yBin = hNS.GetYaxis().GetBinLowEdge(iBinY) + .3*hNS.GetYaxis().GetBinWidth(iBinY) # bottom of TLatex 30% across the binwidth in X
            tlatex = rt.TLatex(xBin,yBin,"%2.1f"%binCont)
            tlatex.SetTextSize(0.05)
            tlatex.SetTextFont(42)
            tlatexList.append(tlatex)
    for fGray in fGrayGraphs: fGray.Draw("F")
    for i in range(0,len(xLines)): xLines[i].Draw()
    for i in range(0,len(yLines)): yLines[i].Draw()

    if btagOpt>0:
        c2.SaveAs("%s/nSigma_%ib_%s.C" %(outFolder,btagOpt,Box))
        c2.SaveAs("%s/nSigma_%ib_%s.pdf" %(outFolder,btagOpt,Box))
    else:
        c2.SaveAs("%s/nSigma_%s.C" %(outFolder,Box))
        c2.SaveAs("%s/nSigma_%s.pdf" %(outFolder,Box))

    for tlatex in tlatexList: tlatex.Draw()
        
    # now for a log scale plot
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
        
    if btagOpt>0:
        c2.SaveAs("%s/nSigmaLog_%ib_%s.C" %(outFolder,btagOpt,Box))
        c2.SaveAs("%s/nSigmaLog_%ib_%s.pdf" %(outFolder,btagOpt,Box))
    else:
        c2.SaveAs("%s/nSigmaLog_%s.C" %(outFolder,Box))
        c2.SaveAs("%s/nSigmaLog_%s.pdf" %(outFolder,Box))

  
if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "\nRun the script as follows:\n"
        print "python scripts/makeToyPVALUE_sigbin.py BoxName ExpectedYieldRootFile DataRootFile OutDir"
        print "with:"
        print "- BoxName = name of the Box (MuMu, MuEle, etc)"
        print "- ExpectedYieldRootFile = file containing tree of expected yield distributions produced by expectedYield_sigbin.py "
        print "- DataRootFile = input root file containing data you fit"
        print "- OutDir = name of the output directory"
        print ""
        print "After the inputs you can specify the following options"
        print " --noBtag      this is a 0btag box (i.e. R2 stops at 0.5)"
        print " --printPlots  dump plots of individual KDEs and 68% prob interval calculation"
        print "--fit-region=NamedFitRegion in the output Fit Result file"
        sys.exit()
    
    Box = sys.argv[1]
    fileName = sys.argv[2]
    dataFileName = sys.argv[3]
    outFolder = sys.argv[4]
    
    noBtag = False
    
    printPlots = False

    fit3D = False
    
    frLabels = []
    for i in range(5,len(sys.argv)):
        if sys.argv[i] == "--noBtag": noBtag = True
        if sys.argv[i] == "--3D": fit3D = True
        if sys.argv[i].find("--fit-region=") != -1:
            frLabelString = sys.argv[i].replace("--fit-region=","")
            frLabels = frLabelString.split(",")
        if sys.argv[i] == "--printPlots": printPlots = True
            
        
    from RazorBox import getBinning
    MRbins    = getBinning(Box, "MR"   , "Btag")
    Rsqbins   = [0.08, 0.1, 0.15, 0.2, 0.3, 0.41, 0.52, 1.5]#getBinning(Box, "Rsq"  , "Btag")
    nBtagbins = getBinning(Box, "nBtag", "Btag")
   
    hList, hOBSList, hEXPList, hNSList, pValHistList = [], [], [], [], []
    if len(frLabels)<=1:
        btagToDo = [0] # THIS MEANS WE ARE INTEGRATING THE FULL BTAG REGION
    if len(frLabels)==3:
        btagToDo = [0,1,23] # THIS MEANS WE ARE DOING EACH BTAG REGION
    if len(frLabels)==2:
        btagToDo = [1,23]# THIS MEANS WE ARE DOING EACH BTAG REGION
    btagToDo = [0]
    for btagOpt in btagToDo:
        h, hOBS, hEXP, hNS, pValHist = getHistogramsWriteTable(MRbins, Rsqbins, nBtagbins, fileName, dataFileName, Box, outFolder, printPlots, fit3D, btagOpt)
        hList.append(h)
        hOBSList.append(hOBS)
        hEXPList.append(hEXP)
        hNSList.append(hNS)
        pValHistList.append(pValHist)
    
        for h, hOBS, hEXP, hNS, pValHist in zip(hList,hOBSList,hEXPList,hNSList,pValHistList):
            writeFilesDrawHistos(MRbins, Rsqbins, h, hOBS, hEXP, hNS, pValHist, Box, outFolder, fit3D, btagOpt)
