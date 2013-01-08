from optparse import OptionParser
import ROOT as rt
from array import *
import sys
import makeBluePlot
#import plotStyle
import makeToyPVALUE_sigbin
import os

def FindLastBin(h):
    for i in range(1,h.GetXaxis().GetNbins()):
        thisbin = h.GetXaxis().GetNbins()-i
        if h.GetBinContent(thisbin)>=0.1: return thisbin+1
    return h.GetXaxis().GetNbins()    

def GetProbRange(h):
    # find the maximum
    binMax = h.GetMaximumBin()
    # move left and right until integrating 68%
    prob = h.GetMaximum()/h.Integral()
    iLeft = 1
    iRight = 1
    while prob < 0.68 and binMax+iRight <= h.GetXaxis().GetNbins():
        print binMax-iLeft,binMax+iRight, prob
        probRight = 0.
        if h.GetBinContent(binMax+iRight) <= 0.: iRight += 1
        else: probRight = h.GetBinContent(binMax+iRight)
        probLeft = 0.
        if h.GetBinContent(binMax+iLeft) <= 0. and binMax > 1 : iLeft += 1
        else: probLeft = h.GetBinContent(binMax-iLeft)
        if probRight > probLeft:
            prob += probRight/h.Integral()
            iRight += 1
        else:
            if binMax > 1:
                prob += probLeft/h.Integral()
                iLeft += 1
    return h.GetXaxis().GetBinUpEdge(binMax+iRight), h.GetXaxis().GetBinLowEdge(binMax-iLeft)
            
def GetErrorsX(nbinx, nbiny, myTree, printPlots, outFolder, fit3D, btagOpt):
    err = []
    # for each bin of x, get the error on the sum of the y bins
    if printPlots:
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"canvasd\");")
        d = rt.TCanvas("canvasd","canvasd",800,600)
    for i in range(0,nbinx-1):
        sumName = ""
        varNames = []
        for j in range(0,nbiny-1):
            if j==0 and i==0: continue #WE ALWAYS SKIP THE BIN IN THE BOTTOM LEFT CORNER
            if fit3D:
                sumName = sumName+"b%i_%i_1+b%i_%i_2+b%i_%i_3+" %(i,j,i,j,i,j)
                varNames.extend(["b%i_%i_1"%(i,j),"b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)])
            else:
                sumName = sumName+"b%i_%i+" %(i,j)
                varNames.append("b%i_%i" %(i,j))
        myTree.Draw(sumName[:-1])
        htemp = rt.gPad.GetPrimitive("htemp")
        mean = htemp.GetMean()
        rms = htemp.GetRMS()
        maxX = int(max(10.0,mean+5.*rms))
        htemp.Scale(1./htemp.Integral())
        
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"hsum\");")
        myhisto = rt.TH1D("hsum", "hsum", maxX, 0., maxX)
        myTree.Project("hsum", sumName[:-1])
        myhisto.Scale(1./myhisto.Integral())
        
        switchToKDE = makeToyPVALUE_sigbin.decideToUseKDE(0.,maxX,myhisto)
        
        # USING ROOKEYSPDF
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
            rho = makeToyPVALUE_sigbin.useThisRho(0.,maxX,myhisto)
            rkpdf = rt.RooKeysPdf("rkpdf","rkpdf",sumExpData,dataset,rt.RooKeysPdf.NoMirror,rho)
            func = rkpdf.asTF(rt.RooArgList(sumExpData))
            myhisto.Draw()
            ic = rt.TColor(1398, 0.75, 0.92, 0.68,"")
            func.SetLineColor(ic.GetColor(0.1, .85, 0.5))
            func.Draw("same")
            mode,xmin,xmax,probRange,funcFill68 = makeToyPVALUE_sigbin.find68ProbRangeFromKDEMode(maxX,func)
            tleg = rt.TLegend(0.6,.65,.9,.9)
            if switchToKDE:
                tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,xmin,xmax),"f")
            else:
                tleg.AddEntry(myhisto,"68%% Range = [%.1f,%.1f]"%(xmin,xmax),"f")
            tleg.SetFillColor(rt.kWhite)
            tleg.Draw("same")
            rt.gStyle.SetOptStat(0)
            if printPlots:
                if fit3D: d.Print("%s/functest_X_%i.pdf"%(outFolder,i))
                else: d.Print("%s/functest_X_%i.pdf"%(outFolder,i))
        else:
            xmax, xmin = GetProbRange(myhisto)
        print xmin, xmax
        err.append((xmax-xmin)/2.)
    myhisto.Delete()
    if printPlots: del d
    del myhisto
    return err
            
def GetErrorsY(nbinx, nbiny, myTree, printPlots, outFolder, fit3D, btagOpt):
    err = []
    # for each bin of y, get the error on the sum of the x bins
    if printPlots:
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"canvasd\");")
        d = rt.TCanvas("canvasd","canvasd",800,600)
    for j in range(0,nbiny-1):
        sumName = ""
        varNames = []
        for i in range(0,nbinx-1):
            if j==0 and i==0: continue #WE ALWAYS SKIP THE BIN IN THE BOTTOM LEFT CORNER
            if fit3D:
                sumName = sumName+"b%i_%i_1+b%i_%i_2+b%i_%i_3+" %(i,j,i,j,i,j)
                varNames.extend(["b%i_%i_1"%(i,j),"b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)])
            else:
                sumName = sumName+"b%i_%i+" %(i,j)
                varNames.append("b%i_%i" %(i,j))
        myTree.Draw(sumName[:-1])
        htemp = rt.gPad.GetPrimitive("htemp")
        mean = htemp.GetMean()
        rms = htemp.GetRMS()
        maxX = int(max(10.0,mean+5.*rms))
        htemp.Scale(1./htemp.Integral())

        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"hsum\");")
        myhisto = rt.TH1D("hsum", "hsum", maxX, 0., maxX)
        myTree.Project("hsum", sumName[:-1])
        myhisto.Scale(1./myhisto.Integral())
        
        switchToKDE = makeToyPVALUE_sigbin.decideToUseKDE(0.,maxX,myhisto)
        
        # USING ROOKEYSPDF
        if switchToKDE:
            nExp = [rt.RooRealVar(varName,varName,0,maxX) for varName in varNames]
            nExpSet = rt.RooArgSet("nExpSet")
            nExpList = rt.RooArgList("nExpList")
            for i in range(0,len(nExp)):
                nExpSet.add(nExp[i])
                nExpList.add(nExp[i])
            dataset = rt.RooDataSet("dataset","dataset",myTree,nExpSet)
            sumExp = rt.RooFormulaVar("sumExp","sumExp",sumName[:-1],nExpList)
            sumExpData = dataset.addColumn(sumExp)
            sumExpData.setRange(0,maxX)
            rho = makeToyPVALUE_sigbin.useThisRho(0.,maxX,myhisto)
            rkpdf = rt.RooKeysPdf("rkpdf","rkpdf",sumExpData,dataset,rt.RooKeysPdf.NoMirror,rho)
            func = rkpdf.asTF(rt.RooArgList(sumExpData))
            myhisto.Draw()
            func.SetLineColor(rt.TColor.GetColor(0.1, .85, 0.5))
            func.Draw("same")
            mode,xmin,xmax,probRange,funcFill68 = makeToyPVALUE_sigbin.find68ProbRangeFromKDEMode(maxX,func)
            tleg = rt.TLegend(0.6,.65,.9,.9)
            if switchToKDE:
                tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,xmin,xmax),"f")
            else:
                tleg.AddEntry(myhisto,"68%% Range = [%.1f,%.1f]"%(xmin,xmax),"f")
            tleg.SetFillColor(rt.kWhite)
            tleg.Draw("same")
            rt.gStyle.SetOptStat(0)
            if printPlots:
                if fit3D: d.Print("%s/functest_Y_%i.pdf"%(outFolder,j))
                else: d.Print("%s/functest_Y_%i.pdf"%(outFolder,j))
        else:
            xmax, xmin = GetProbRange(myhisto)
        print xmin, xmax
        err.append((xmax-xmin)/2.)
    myhisto.Delete()
    if printPlots: del d
    del myhisto
    return err

def GetErrorsZ(nbinx, nbiny, nbinz, myTree, printPlots, outFolder, fit3D, btagOpt):
    err = []
    # for each bin of z, get the error on the sum of the x, y, bins
    if printPlots:
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"canvasd\");")
        d = rt.TCanvas("canvasd","canvasd",800,600)
    for k in range(1,nbinz):
        sumName = ""
        varNames = []
        for i in range(0,nbinx-1):
            for j in range(0,nbiny-1):
                if j==0 and i==0: continue #WE ALWAYS SKIP THE BIN IN THE BOTTOM LEFT CORNER
                sumName = sumName+"b%i_%i_%i+" %(i,j,k)
                varNames.extend(["b%i_%i_%i"%(i,j,k)])
        myTree.Draw(sumName[:-1])
        htemp = rt.gPad.GetPrimitive("htemp")
        mean = htemp.GetMean()
        rms = htemp.GetRMS()
        maxX = int(max(10.0,mean+5.*rms))
        htemp.Scale(1./htemp.Integral())
        
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"hsum\");")
        myhisto = rt.TH1D("hsum", "hsum", maxX, 0., maxX)
        myTree.Project("hsum", sumName[:-1])
        myhisto.Scale(1./myhisto.Integral())
        
        switchToKDE = makeToyPVALUE_sigbin.decideToUseKDE(0.,maxX,myhisto)
        
        # USING ROOKEYSPDF
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
            rho = makeToyPVALUE_sigbin.useThisRho(0.,maxX,myhisto)
            rkpdf = rt.RooKeysPdf("rkpdf","rkpdf",sumExpData,dataset,rt.RooKeysPdf.NoMirror,rho)
            func = rkpdf.asTF(rt.RooArgList(sumExpData))
            myhisto.Draw()
            func.SetLineColor(rt.TColor.GetColor(0.1, .85, 0.5))
            func.Draw("same")
            mode,xmin,xmax,probRange,funcFill68 = makeToyPVALUE_sigbin.find68ProbRangeFromKDEMode(maxX,func)
            tleg = rt.TLegend(0.6,.65,.9,.9)
            if switchToKDE:
                tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,xmin,xmax),"f")
            else:
                tleg.AddEntry(myhisto,"68%% Range = [%.1f,%.1f]"%(xmin,xmax),"f")
            tleg.SetFillColor(rt.kWhite)
            tleg.Draw("same")
            rt.gStyle.SetOptStat(0)
            if printPlots:
                if fit3D: d.Print("%s/functest_Z_%i.pdf"%(outFolder,k))
                else: d.Print("%s/functest_Z_%i.pdf"%(outFolder,k))
        else:
            xmax, xmin = GetProbRange(myhisto)
        print xmin, xmax
        err.append((xmax-xmin)/2.)
    myhisto.Delete()
    if printPlots: del d
    del myhisto
    return err


def goodPlot(varname, outFolder, Label, Energy, Lumi, hMRTOTcopy, hMRTOT, hMRTTj1b, hMRTTj2b, hMRVpj, hMRData, c1, pad1, pad2, fit3D, btag):
    rt.gStyle.SetOptStat(0000)
    rt.gStyle.SetOptTitle(0)
    
    #c1.SetLeftMargin(0.15)
    #c1.SetRightMargin(0.05)
    #c1.SetTopMargin(0.05)
    #c1.SetBottomMargin(0.05)
    
    pad1.Range(-213.4588,-0.3237935,4222.803,5.412602);
    pad2.Range(-213.4588,-2.206896,4222.803,3.241379);

    pad1.SetLeftMargin(0.15)
    pad2.SetLeftMargin(0.15)
    pad1.SetRightMargin(0.05)
    pad2.SetRightMargin(0.05)
    pad1.SetTopMargin(0.05)
    pad2.SetTopMargin(0.)
    pad1.SetBottomMargin(0.)
    #pad2.SetTopMargin(0.04)
    #pad1.SetBottomMargin(0.004)
    pad2.SetBottomMargin(0.40)
    
    pad1.Draw()
    pad1.cd()
    rt.gPad.SetLogy()

    # MR PLOT
    hMRTOTcopy.SetMinimum(0.5)
    hMRTOTcopy.SetFillStyle(1001)
    hMRTOTcopy.SetFillColor(rt.kBlue-10)
    hMRTOTcopy.SetLineColor(rt.kBlue)
    hMRTOTcopy.SetLineWidth(2)
    hMRTOTcopy.GetXaxis().SetTitle("")
    hMRTOTcopy.GetXaxis().SetLabelOffset(0.16)
    hMRTOTcopy.GetXaxis().SetLabelSize(0.06)
    hMRTOTcopy.GetYaxis().SetLabelSize(0.06)
    hMRTOTcopy.GetXaxis().SetTitleSize(0.06)
    hMRTOTcopy.GetYaxis().SetTitleSize(0.06)
    hMRTOTcopy.GetXaxis().SetTitleOffset(1)
    hMRTOTcopy.GetXaxis().SetTicks("+-")
    hMRTOTcopy.GetXaxis().SetRange(0,FindLastBin(hMRTOTcopy))
    hMRTOTcopy.GetYaxis().SetTitle("Events")
    if varname == "MR": hMRTOTcopy.SetMaximum(hMRTOTcopy.GetMaximum()*2.)
    elif varname == "RSQ": hMRTOTcopy.SetMaximum(hMRTOTcopy.GetMaximum()*2.)
    elif varname == "BTAG": hMRTOTcopy.SetMaximum(hMRTOTcopy.GetMaximum()*5.)
    if hMRTOTcopy.GetBinContent(hMRTOTcopy.GetNbinsX())>=10.: hMRTOTcopy.SetMinimum(5.)
    if hMRTOTcopy.GetBinContent(hMRTOTcopy.GetNbinsX())>=100.: hMRTOTcopy.SetMinimum(50.)
    hMRTOTcopy.Draw("e2")

    # TTj1b is shown only if it has some entry
    showTTj1b = hMRTTj1b != None
    if showTTj1b:
        if  hMRTTj1b.Integral()<=1: showTTj1b = False
    # TTj2b is shown only if it has some entry
    showTTj2b = hMRTTj2b != None
    if showTTj2b:
        if  hMRTTj2b.Integral()<=1: showTTj2b = False
    # Vpj is shown only if it has some entry
    showVpj = hMRVpj != None
    if showVpj:
        if  hMRVpj.Integral()<=1: showVpj = False
    
    if showVpj:
        hMRVpj.SetFillStyle(0)
        col1 = rt.gROOT.GetColor(rt.kGreen-7)
        col1.SetAlpha(1.0)
        hMRVpj.SetLineColor(rt.kGreen-3)
        hMRVpj.SetLineWidth(2)
        if varname == "BTAG":
            hMRVpj.Add(hMRTTj1b)
            col1.SetAlpha(1.0)
            hMRVpj.SetFillStyle(1001)
            hMRVpj.SetFillColor(rt.kGreen-7)
        hMRVpj.Draw("histsame")
    if showTTj2b:
        hMRTTj2b.SetFillStyle(0)
        col1 = rt.gROOT.GetColor(rt.kRed-4)
        col1.SetAlpha(1.0)
        hMRTTj2b.SetLineColor(rt.kRed)
        hMRTTj2b.SetLineWidth(2)
        if varname == "BTAG":
            col1.SetAlpha(1.0)
            hMRTTj2b.SetFillStyle(1001)
            hMRTTj2b.SetFillColor(rt.kRed-4)
        hMRTTj2b.Draw("histsame")
    if showTTj1b:
        hMRTTj1b.SetFillStyle(0)
        col2 = rt.gROOT.GetColor(rt.kViolet-4)
        col2.SetAlpha(1.0)
        hMRTTj1b.SetLineColor(rt.kViolet)
        hMRTTj1b.SetLineWidth(2)
        if varname == "BTAG":
            col2.SetAlpha(1.0)
            hMRTTj1b.SetFillStyle(1001)
            hMRTTj1b.SetFillColor(rt.kViolet-4)
        hMRTTj1b.Draw("histsame")
    if varname =="BTAG":
        hMRTOTcopy.SetFillStyle(1001)
        hMRTOTcopy.SetFillColor(rt.kBlue-10)
        hMRTOTcopy.SetLineColor(rt.kBlue) 
        hMRTOTcopy.Draw("e2same")
    hMRData.SetLineColor(rt.kBlack)
    hMRData.SetMarkerStyle(20)
    hMRData.SetMarkerColor(rt.kBlack)
    hMRData.Draw("pesame")
    hMRTOT.SetLineWidth(2)
    hMRTOT.SetFillStyle(0)
    hMRTOT.DrawCopy("histsame")
    if showTTj2b and showTTj1b and showVpj:
        leg = rt.TLegend(0.65,0.55,0.93,0.93)
    elif showTTj2b and showTTj1b:
        leg = rt.TLegend(0.65,0.65,0.93,0.93)
    else:
        leg = rt.TLegend(0.65,0.72,0.93,0.93)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetLineColor(0)

    if noBtag:
        btagLabel = "no b-tag"
    else:
        btagLabel = "#geq 1 b-tag"
        
    if datasetName=="TTJets" or datasetName=="WJets" or datasetName=="DYJetsToLL" or datasetName=="ZJetsToNuNu" or  datasetName=="SMCocktail":
        leg.AddEntry(hMRData,"Simulated Data","lep")
    else:
        leg.AddEntry(hMRData,"Data","lep")
    leg.AddEntry(hMRTOTcopy,"Total Background")
    if showTTj1b and showTTj2b:
        if varname=="BTAG":
            if showVpj:
                leg.AddEntry(hMRTTj1b,"1 b-tag, t#bar{t}+jets","f")
                leg.AddEntry(hMRVpj,"1 b-tag, V+jets","f")
            else:
                leg.AddEntry(hMRTTj1b,"1 b-tag","f")
            leg.AddEntry(hMRTTj2b,"#geq 2 b-tag","f")
        else:
            if showVpj:
                leg.AddEntry(hMRTTj1b,"1 b-tag, t#bar{t}+jets","l")
                leg.AddEntry(hMRVpj,"1 b-tag, V+jets","l")
            else:
                leg.AddEntry(hMRTTj1b,"1 b-tag","l")
            leg.AddEntry(hMRTTj2b,"#geq 2 b-tag","l")
    leg.Draw("same")

    # plot labels
    #pt = rt.TPaveText(0.4,0.73,0.4,0.93,"ndc")
    pt = rt.TPaveText(0.4,0.8,0.5,0.93,"ndc")
    pt.SetBorderSize(0)
    pt.SetTextSize(0.05)
    pt.SetFillColor(0)
    pt.SetFillStyle(0)
    pt.SetLineColor(0)
    pt.SetTextAlign(21)
    pt.SetTextFont(42)
    pt.SetTextSize(0.042)
    text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
    if datasetName=="TTJets":
        text = pt.AddText("t#bar{t}+jets %s Box %s" %(Box,btagLabel))
    elif datasetName=="WJets":
        text = pt.AddText("W+jets %s Box %s" %(Box,btagLabel))
    elif datasetName=="SMCocktail":
        text = pt.AddText("Total SM %s Box %s" %(Box,btagLabel))
    elif datasetName=="ZJetsToNuNu":
        text = pt.AddText("Z(#nu#nu)+jets %s Box %s" %(Box,btagLabel))
    elif datasetName=="DYJetsToLL":
        text = pt.AddText("Z(ll)+jets")
    else:
        text = pt.AddText("Razor %s Box %s #int L = %3.2f fb^{-1}" %(Box,btagLabel,Lumi))
    pt.Draw()
    pad1.Draw()
    
    c1.Update()
    
    c1.cd()

    pad2.Draw()
    pad2.cd()
    rt.gPad.SetLogy(0)
    hMRData.Sumw2()
    hMRTOTcopy.Sumw2()
    hMRDataDivide = hMRData.Clone(hMRData.GetName()+"Divide")
    hMRDataDivide.Sumw2()

    hMRTOTclone = hMRTOT.Clone(hMRTOTcopy.GetName()+"Divide") 
    hMRTOTcopyclone = hMRTOTcopy.Clone(hMRTOTcopy.GetName()+"Divide") 
    hMRTOTcopyclone.GetYaxis().SetLabelSize(0.12)
    hMRTOTcopyclone.SetTitle("")
    hMRTOTcopyclone.SetMaximum(3.5)
    hMRTOTcopyclone.SetMinimum(0.)
    if varname=="BTAG": hMRTOTcopyclone.GetXaxis().SetLabelSize(0.28)
    else: hMRTOTcopyclone.GetXaxis().SetLabelSize(0.18)
    hMRTOTcopyclone.GetXaxis().SetTitleSize(0.18)
    hMRTOTcopyclone.GetXaxis().SetTitleOffset(0.85)
 
    for i in range(1, hMRData.GetNbinsX()+1):
        tmpVal = hMRTOTcopyclone.GetBinContent(i)
        if tmpVal != -0.:
            hMRDataDivide.SetBinContent(i, hMRDataDivide.GetBinContent(i)/tmpVal)
            hMRDataDivide.SetBinError(i, hMRDataDivide.GetBinError(i)/tmpVal)
            hMRTOTcopyclone.SetBinContent(i, hMRTOTcopyclone.GetBinContent(i)/tmpVal)
            hMRTOTcopyclone.SetBinError(i, hMRTOTcopyclone.GetBinError(i)/tmpVal)
            hMRTOTclone.SetBinContent(i, hMRTOTclone.GetBinContent(i)/tmpVal)
            hMRTOTclone.SetBinError(i, hMRTOTclone.GetBinError(i)/tmpVal)

    hMRTOTcopyclone.GetXaxis().SetTitleOffset(1.)
    hMRTOTcopyclone.GetXaxis().SetLabelOffset(0.02)
    if varname == "MR":
        hMRTOTcopyclone.GetXaxis().SetTitle("M_{R} [GeV]")
    if varname == "RSQ":
        hMRTOTcopyclone.GetXaxis().SetTitle("R^{2}")
    if varname == "BTAG":
        hMRTOTcopyclone.GetXaxis().SetTitle("n_{b-tag}")

    hMRTOTcopyclone.GetYaxis().SetNdivisions(504,rt.kTRUE)
    hMRTOTcopyclone.GetYaxis().SetTitleOffset(0.3)
    hMRTOTcopyclone.GetYaxis().SetTitleSize(0.16)
    hMRTOTcopyclone.GetYaxis().SetTitle("Data/Bkgd")
    hMRTOTcopyclone.GetXaxis().SetTicks("+")
    hMRTOTcopyclone.GetXaxis().SetTickLength(0.07)
    hMRTOTcopyclone.SetMarkerColor(rt.kBlue-10)
    hMRTOTcopyclone.Draw("e2")
    hMRDataDivide.Draw('pesame')
    hMRTOTcopyclone.Draw("axissame")

    pad2.Update()
    pad1.cd()
    pad1.Update()
    pad1.Draw()
    c1.cd()
    
    if fit3D and btag>0:
        c1.Print("%s/%s_%ib_%s.pdf" %(outFolder,varname,btag,Label))
        c1.Print("%s/%s_%ib_%s.C" %(outFolder,varname,btag,Label))
    else:
        c1.Print("%s/%s_%s.pdf" %(outFolder,varname,Label))
        c1.Print("%s/%s_%s.C" %(outFolder,varname,Label))
    
if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "\nRun the script as follows:\n"
        print "python scripts/make1DProj.py BoxName ExpectedYieldRootFile RazorFitOutputRootFile OutDir"
        print "with:"
        print "- BoxName = name of the Box (MuMu, MuEle, etc)"
        print "- ExpectedYieldRootFile = file containing tree of expected yield distributions produced by expectedYield_sigbin.py "
        print "- RazorFitOutputRootFile = output root file from running analysis SingleBoxFit, contains fit result and plots"
        print "- OutDir = name of the output directory"
        print ""
        print "After the inputs you can specify the following options"
        print " --noBtag      this is a 0btag box (i.e. R2 stops at 0.5)"
        print " --forPaper    Don't print Preliminary"
        print " --printPlots  dump plots of individual KDEs and 68% prob interval calculation"
        print "--fit-region=NamedFitRegion in the output Fit Result file"
        print " -MC=MCDataSetName  options include TTJets, WJets, ZJetsToNuNu, DYJetsToLL, and SMCocktail"
        sys.exit()
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gROOT.ForceStyle()

    Box = sys.argv[1]
    fileName = sys.argv[2]
    fitfileName = sys.argv[3]
    outFolder = sys.argv[4]
    if outFolder[-1] == "/": outFolder = outFolder[:-1]
    noBtag = False
    fit3D = False
    Lumi = 5.
    Energy = 8.
    Preliminary = "Preliminary"
    datasetName = ""
    printPlots = False
    frLabels = []
    for i in range(4,len(sys.argv)):
        if sys.argv[i] == "--noBtag": noBtag = True
        if sys.argv[i] == "--3D": fit3D = True
        if sys.argv[i] == "--forPaper": Preliminary = ""
        if sys.argv[i] == "--printPlots": printPlots = True
        if sys.argv[i].find("--fit-region=") != -1:
            frLabelString = sys.argv[i].replace("--fit-region=","")
            frLabels = [frLabelString]
        if sys.argv[i].find("-MC=") != -1:
            Preliminary = "Simulation"
            datasetName = sys.argv[i].replace("-MC=","")
        if sys.argv[i].find("-Lumi=") != -1: Lumi = float(sys.argv[i].replace("-Lumi=",""))
        if sys.argv[i].find("-Energy=") != -1: Energy = float(sys.argv[i].replace("-Energy=",""))

    Label = fitfileName.split("/")[-1].replace(".root","").replace("razor_output_","")

    MRbins, Rsqbins, nBtagbins = makeBluePlot.Binning(Box, noBtag)
        
    x = array("d",MRbins)
    y = array("d",Rsqbins)
    z = array("d",nBtagbins)

    # file with bkg predictions from toys
    fileIn = rt.TFile.Open(fileName)
    myTree = fileIn.Get("myTree")

    # file with output fit
    fitFile = rt.TFile.Open(fitfileName)
    print fitfileName

    if frLabels == []: frLabels = []
    #if fit3D: frLabels.extend(["%ib"%btag for btag in nBtagbins[:-1]])
    print frLabels
        
    # TTj1b histograms
    hMRTTj1bList = [fitFile.Get("%s/histoToyTTj1b_MR_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    hRSQTTj1bList = [fitFile.Get("%s/histoToyTTj1b_Rsq_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    if fit3D:
        hBTAGTTj1bList = [fitFile.Get("%s/histoToyTTj1b_nBtag_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]

    # TTj2b histograms
    hMRTTj2bList = [fitFile.Get("%s/histoToyTTj2b_MR_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    hRSQTTj2bList = [fitFile.Get("%s/histoToyTTj2b_Rsq_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    if fit3D:
        hBTAGTTj2bList = [fitFile.Get("%s/histoToyTTj2b_nBtag_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]

    # Vpj histograms
    hMRVpjList = [fitFile.Get("%s/histoToyVpj_MR_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    hRSQVpjList = [fitFile.Get("%s/histoToyVpj_Rsq_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    if fit3D:
        hBTAGVpjList = [fitFile.Get("%s/histoToyVpj_nBtag_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]

    # Total Bkg histograms
    hMRTOTList = [fitFile.Get("%s/histoToy_MR_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    hRSQTOTList = [fitFile.Get("%s/histoToy_Rsq_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    if fit3D:
        hBTAGTOTList = [fitFile.Get("%s/histoToy_nBtag_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]

    # Data histograms    
    hMRDataList = [fitFile.Get("%s/histoData_MR_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    hRSQDataList = [fitFile.Get("%s/histoData_Rsq_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    if fit3D:
        hBTAGDataList = [fitFile.Get("%s/histoData_nBtag_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]

    btag = 0 # THIS MEANS WE ARE DOING THE FULL BTAG REGION
    btagToDo = [0]
    
    for hMRTOT, hMRTTj1b, hMRTTj2b, hMRVpj, hMRData, hRSQTOT, hRSQTTj1b, hRSQTTj2b, hRSQVpj, hRSQData, hBTAGTOT, hBTAGTTj1b, hBTAGTTj2b, hBTAGVpj, hBTAGData, btag in zip(hMRTOTList, hMRTTj1bList, hMRTTj2bList, hMRVpjList, hMRDataList, hRSQTOTList, hRSQTTj1bList, hRSQTTj2bList, hRSQVpjList, hRSQDataList, hBTAGTOTList, hBTAGTTj1bList, hBTAGTTj2bList, hBTAGVpjList, hBTAGDataList,btagToDo):

        errMR = GetErrorsX(len(MRbins),len(Rsqbins),myTree,printPlots,outFolder,fit3D,btag)
        errRSQ = GetErrorsY(len(MRbins),len(Rsqbins),myTree,printPlots,outFolder,fit3D,btag)
        errBTAG = GetErrorsZ(len(MRbins),len(Rsqbins),len(nBtagbins),myTree,printPlots,outFolder,fit3D,btag)
        hMRTOTcopy = hMRTOT.Clone(hMRTOT.GetName()+"COPY")
        for i in range(1,len(errMR)+1):
            print hMRTOT.GetBinContent(i),errMR[i-1],hMRTOT.GetBinError(i)
            hMRTOTcopy.SetBinError(i,max(errMR[i-1],hMRTOT.GetBinError(i)))
            hMRTOT.SetBinError(i,0.)
        
        hRSQTOTcopy = hRSQTOT.Clone(hRSQTOT.GetName()+"COPY")
        for i in range(1,len(errRSQ)+1):
            hRSQTOTcopy.SetBinError(i,max(errRSQ[i-1],hRSQTOT.GetBinError(i)))
            hRSQTOT.SetBinError(i,0.)

            
        hBTAGTOTcopy = hBTAGTOT.Clone(hBTAGTOT.GetName()+"COPY")
        for i in range(1,len(errBTAG)+1):
            hBTAGTOTcopy.SetBinError(i,max(errBTAG[i-1],hBTAGTOT.GetBinError(i)))
            hBTAGTOT.SetBinError(i,0.)

        c1 = rt.TCanvas("c1","c1", 900, 700)
        pad1 = rt.TPad("pad1","pad1",0,0.25,1,1)
        pad2 = rt.TPad("pad2","pad2",0,0,1,0.25)

        goodPlot("MR", outFolder, Label, Energy, Lumi, hMRTOTcopy, hMRTOT, hMRTTj1b, hMRTTj2b, hMRVpj, hMRData, c1, pad1, pad2, fit3D, btag)
        goodPlot("RSQ", outFolder, Label, Energy, Lumi, hRSQTOTcopy, hRSQTOT, hRSQTTj1b, hRSQTTj2b, hRSQVpj, hRSQData,  c1, pad1, pad2, fit3D, btag)
        if fit3D: goodPlot("BTAG", outFolder, Label, Energy, Lumi, hBTAGTOTcopy, hBTAGTOT, hBTAGTTj1b, hBTAGTTj2b, hBTAGVpj, hBTAGData,  c1, pad1, pad2, fit3D, btag)
    
