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
            
def GetErrorsX(nbinx, nbiny, myTree, printPlots, outFolder, fit3D, btag):
    err = []
    # for each bin of x, get the error on the sum of the y bins
    if printPlots:
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"canvasd\");")
        d = rt.TCanvas("canvasd","canvasd",800,600)
    for i in range(0,nbinx-1):
        sumName = ""
        varNames = []
        for j in range(0,nbiny-1):
            if fit3D:
                if btag<=0:
                    sumName = sumName+"b%i_%i_0+b%i_%i_1+b%i_%i_2+b%i_%i_3+" %(i,j,i,j,i,j,i,j)
                    varNames.extend(["b%i_%i_0"%(i,j),"b%i_%i_1"%(i,j),"b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)])
                else:
                    sumName = sumName+"b%i_%i_%i+" %(i,j,btag-1)
                    varNames.append("b%i_%i_%i" %(i,j,btag-1))
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
            mode,xmin,xmax,probRange,funcFill68 = makeToyPVALUE_sigbin.find68ProbRangeFromKDEMedian(maxX,func)
            tleg = rt.TLegend(0.6,.65,.9,.9)
            if switchToKDE:
                tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,xmin,xmax),"f")
            else:
                tleg.AddEntry(myhisto,"68%% Range = [%.1f,%.1f]"%(xmin,xmax),"f")
            tleg.SetFillColor(rt.kWhite)
            tleg.Draw("same")
            rt.gStyle.SetOptStat(0)
            if printPlots:
                if fit3D and btag>0: d.Print("%s/functest%ib_X_%i.pdf"%(outFolder,btag,i))
                else: d.Print("%s/functest_X_%i.pdf"%(outFolder,i))
        else:
            xmax, xmin = GetProbRange(myhisto)
        print xmin, xmax
        err.append((xmax-xmin)/2.)
    myhisto.Delete()
    del d
    del myhisto
    return err
            
def GetErrorsY(nbinx, nbiny, myTree, printPlots, outFolder, fit3D, btag):
    err = []
    # for each bin of y, get the error on the sum of the x bins
    if printPlots:
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"canvasd\");")
        d = rt.TCanvas("canvasd","canvasd",800,600)
    for j in range(0,nbiny-1):
        sumName = ""
        varNames = []
        for i in range(0,nbinx-1):
            if fit3D:
                if btag<=0:
                    sumName = sumName+"b%i_%i_0+b%i_%i_1+b%i_%i_2+b%i_%i_3+" %(i,j,i,j,i,j,i,j)
                    varNames.extend(["b%i_%i_0"%(i,j),"b%i_%i_1"%(i,j),"b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)])
                else:
                    sumName = sumName+"b%i_%i_%i+" %(i,j,btag-1)
                    varNames.append("b%i_%i_%i" %(i,j,btag-1))
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
            ic = rt.TColor(1398, 0.75, 0.92, 0.68,"")
            func.SetLineColor(ic.GetColor(0.1, .85, 0.5))
            func.Draw("same")
            mode,xmin,xmax,probRange,funcFill68 = makeToyPVALUE_sigbin.find68ProbRangeFromKDEMedian(maxX,func)
            tleg = rt.TLegend(0.6,.65,.9,.9)
            if switchToKDE:
                tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,xmin,xmax),"f")
            else:
                tleg.AddEntry(myhisto,"68%% Range = [%.1f,%.1f]"%(xmin,xmax),"f")
            tleg.SetFillColor(rt.kWhite)
            tleg.Draw("same")
            rt.gStyle.SetOptStat(0)
            if printPlots:
                if fit3D and btag>0: d.Print("%s/functest%ib_Y_%i.pdf"%(outFolder,btag,i))
                else: d.Print("%s/functest_Y_%i.pdf"%(outFolder,i))
        else:
            xmax, xmin = GetProbRange(myhisto)
        print xmin, xmax
        err.append((xmax-xmin)/2.)
    myhisto.Delete()
    del d
    del myhisto
    return err




def goodPlot(varname, outFolder, Label, Energy, Lumi, hMRTOTcopy, hMRTOT, hMRTTj, hMRVpj, hMRData, fit3D, btag):
    rt.gStyle.SetOptStat(0000)
    rt.gStyle.SetOptTitle(0)
    c1 = rt.TCanvas("c%s" %varname,"c%s" %varname, 900, 600)
    c1.SetLogy()
    c1.SetLeftMargin(0.15)
    c1.SetRightMargin(0.05)
    c1.SetTopMargin(0.05)
    c1.SetBottomMargin(0.15)

    # MR PLOT
    hMRTOTcopy.SetMinimum(0.1)
    hMRTOTcopy.SetFillStyle(1001)
    hMRTOTcopy.SetFillColor(rt.kBlue-10)
    hMRTOTcopy.SetLineColor(rt.kBlue)
    hMRTOTcopy.SetLineWidth(2)
    hMRTOTcopy.GetXaxis().SetLabelSize(0.06)
    hMRTOTcopy.GetYaxis().SetLabelSize(0.06)
    hMRTOTcopy.GetXaxis().SetTitleSize(0.06)
    hMRTOTcopy.GetYaxis().SetTitleSize(0.06)
    hMRTOTcopy.GetXaxis().SetTitleOffset(1.1)
    hMRTOTcopy.GetXaxis().SetRange(0,FindLastBin(hMRTOTcopy))
    hMRTOTcopy.GetYaxis().SetTitle("Events")
    if varname == "MR": hMRTOTcopy.SetMaximum(hMRTOTcopy.GetMaximum()*2.)
    elif varname == "RSQ": hMRTOTcopy.SetMaximum(hMRTOTcopy.GetMaximum()*5.)
    if hMRTOTcopy.GetBinContent(hMRTOTcopy.GetNbinsX())>=10.: hMRTOTcopy.SetMinimum(10.0)
    elif hMRTOTcopy.GetBinContent(hMRTOTcopy.GetNbinsX())>=1.: hMRTOTcopy.SetMinimum(1.0)
    hMRTOTcopy.Draw("e2")

    # Vpj is shown only if it has some entry
    showVpj = hMRVpj != None
    if showVpj:
        if  hMRVpj.Integral()<=1: showVpj = False
    # TTj is shown only if it has some entry
    showTTj = hMRTTj != None
    if showTTj:
        if  hMRTTj.Integral()<=1: showTTj = False
    
    if showTTj:
        hMRTTj.SetFillStyle(0)
        hMRTTj.SetLineColor(rt.kOrange)
        hMRTTj.SetLineWidth(2)
        hMRTTj.Draw("histsame")
    if showVpj:
        hMRVpj.SetFillStyle(0)
        hMRVpj.SetLineColor(rt.kRed)
        hMRVpj.SetLineWidth(2)
        hMRVpj.Draw("histsame")
    hMRData.SetLineColor(rt.kBlack)
    hMRData.SetMarkerStyle(20)
    hMRData.SetMarkerColor(rt.kBlack)
    hMRData.Draw("pesame")
    hMRTOT.SetLineColor(rt.kBlue)
    hMRTOT.SetLineWidth(2)
    hMRTOT.SetFillStyle(0)
    hMRTOT.Draw("histosame")

    if showTTj and showVpj:
        leg = rt.TLegend(0.63,0.63,0.93,0.93)
    else:
        leg = rt.TLegend(0.63,0.78,0.93,0.93)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetLineColor(0)

    if fit3D and btag>0 and btag<4:
        btagLabel = "%i b-tag"%(btag)
    elif fit3D and btag==4:
        btagLabel = "#geq 4 b-tag"
    else:
        btagLabel = "#geq 1 b-tag"
    if datasetName=="TTJets":
        if noBtag: leg.AddEntry(hMRData,"t#bar{t}+jets %s no b-tag" %Box,"lep")
        else: leg.AddEntry(hMRData,"t#bar{t}+jets %s %s" %(Box,btagLabel),"lep")
    elif datasetName=="WJets":
        if noBtag: leg.AddEntry(hMRData,"W+jets %s no b-tag" %Box,"lep")
        else: leg.AddEntry(hMRData,"W+jets %s %s" %(Box,btagLabel),"lep")
    elif datasetName=="ZJets":
        if noBtag: leg.AddEntry(hMRData,"Z(ll)+jets %s no b-tag" %Box,"lep")
        else: leg.AddEntry(hMRData,"Z(ll)+jets %s %s" %(Box,btagLabel),"lep")
    elif datasetName=="ZNuNu":
        if noBtag: leg.AddEntry(hMRData,"Z(#nu#nu)+jets %s no b-tag" %Box,"lep")
        else: leg.AddEntry(hMRData,"Z(#nu#nu)+jets %s %s" %(Box,btagLabel),"lep")
    elif datasetName=="SMCocktail":
        if noBtag: leg.AddEntry(hMRData,"Total SM %s no Btag" %Box,"lep")
        else: leg.AddEntry(hMRData,"Total SM %s %s" %(Box,btagLabel),"lep")
    else:
        if noBtag: leg.AddEntry(hMRData,"Data %s no Btag" %Box,"lep")
        else: leg.AddEntry(hMRData,"Data %s %s" %(Box,btagLabel),"lep")
    leg.AddEntry(hMRTOTcopy,"Total Background")
    if showVpj:
        leg.AddEntry(hMRVpj,"W+jets","l")
    if showTTj:
        leg.AddEntry(hMRTTj,"t#bar{t}+jets","l")
    leg.Draw("same")

    # plot labels
    pt = rt.TPaveText(0.4,0.73,0.4,0.93,"ndc")
    pt.SetBorderSize(0)
    pt.SetTextSize(0.05)
    pt.SetFillColor(0)
    pt.SetFillStyle(0)
    pt.SetLineColor(0)
    pt.SetTextAlign(21)
    pt.SetTextFont(42)
    pt.SetTextSize(0.042)
    text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
    if not (datasetName=="TTJets" or datasetName=="WJets"):
        text = pt.AddText("Razor %s #int L = %3.2f fb^{-1}" %(Box,Lumi))
    pt.Draw()
    
    frLines = []
    if Box == "Jet" or Box == "TauTauJet" or Box == "MultiJet":
        if varname=="MR": frLines.append(rt.TLine(550,hMRTOTcopy.GetMinimum(),550,hMRTOTcopy.GetMaximum()))
        elif varname=="RSQ": frLines.append(rt.TLine(0.24,hMRTOTcopy.GetMinimum(),0.24,hMRTOTcopy.GetMaximum()))
    else:
        if varname=="MR": frLines.append(rt.TLine(500,hMRTOTcopy.GetMinimum(),500,hMRTOTcopy.GetMaximum()))
        elif varname=="RSQ": frLines.append(rt.TLine(0.15,hMRTOTcopy.GetMinimum(),0.15,hMRTOTcopy.GetMaximum()))

    ci = rt.TColor.GetColor("#006600");
    if showSidebandL:
        for frLine in frLines:
            frLine.SetLineColor(ci)
            frLine.SetLineWidth(2)
            frLine.Draw()
    
    c1.Update()

    if fit3D and btag>0:
        c1.SaveAs("%s/%s_%s_%ib.pdf" %(outFolder,varname,Label,btag))
        c1.SaveAs("%s/%s_%s_%ib.C" %(outFolder,varname,Label,btag))
    else:
        c1.SaveAs("%s/%s_%s.pdf" %(outFolder,varname,Label))
        c1.SaveAs("%s/%s_%s.C" %(outFolder,varname,Label))
    del c1
if __name__ == '__main__':
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gROOT.ForceStyle()

    Box = sys.argv[1]
    fileName = sys.argv[2]
    fitfileName = sys.argv[3]
    outFolder = sys.argv[4]
    if outFolder[-1] == "/": outFolder = outFolder[:-1]
    noBtag = False
    showSidebandL = False
    fit3D = False
    Lumi = 5.
    Energy = 8.
    Preliminary = "Preliminary"
    datasetName = ""
    newFR = False
    for i in range(4,len(sys.argv)):
        if sys.argv[i] == "--noBtag": noBtag = True
        #Turn off sideband line, until we can figure out a better way to show it.
        #if sys.argv[i] == "--SidebandL": showSidebandL = True
        if sys.argv[i] == "--3D": fit3D = True
        if sys.argv[i] == "--newFR": newFR = True
        if sys.argv[i] == "--forPaper": Preliminary = ""
        if sys.argv[i].find("-MC=") != -1:
            Preliminary = "Simulation"
            datasetName = sys.argv[i].replace("-MC=","")
        if sys.argv[i].find("-Lumi=") != -1: Lumi = float(sys.argv[i].replace("-Lumi=",""))
        if sys.argv[i].find("-Energy=") != -1: Energy = float(sys.argv[i].replace("-Energy=",""))

    Label = fitfileName.split("/")[-1].replace(".root","").replace("razor_output_","")

    MRbins, Rsqbins, nBtagbins = makeBluePlot.Binning(Box, noBtag, newFR)
    if not fit3D: nBtagbins = [1,5]
    x = array("d",MRbins)
    y = array("d",Rsqbins)
    z = array("d",nBtagbins)

    # file with bkg predictions from toys
    fileIn = rt.TFile.Open(fileName)
    myTree = fileIn.Get("myTree")

    # file with output fit
    fitFile = rt.TFile.Open(fitfileName)
    print fitfileName

    if newFR: frLabels = ["LowMR_MedMR_LowRsq_HighMR"]
    else: frLabels = ["FULL"]
        
    if fit3D: frLabels.extend(["%ib"%btag for btag in nBtagbins[:-1]])
    
    # TTj histograms
    hMRTTjList = [fitFile.Get("%s/histoToyTTj_MR_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    hRSQTTjList = [fitFile.Get("%s/histoToyTTj_Rsq_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]
    if fit3D:
        hBTAGTTjList = [fitFile.Get("%s/histoToyTTj_nBtag_%s_ALLCOMPONENTS" %(Box,frLabel)) for frLabel in frLabels]

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

    printPlots = True
    btag = 0 # THIS MEANS WE ARE DOING THE FULL BTAG REGION
    
    for hMRTOT, hMRTTj, hMRVpj, hMRData, hRSQTOT, hRSQTTj, hRSQVpj, hRSQData in zip(hMRTOTList, hMRTTjList, hMRVpjList, hMRDataList, hRSQTOTList, hRSQTTjList, hRSQVpjList, hRSQDataList):

        errMR = GetErrorsX(len(MRbins),len(Rsqbins),myTree,printPlots,outFolder,fit3D,btag)
        errRSQ = GetErrorsY(len(MRbins),len(Rsqbins),myTree,printPlots,outFolder,fit3D,btag)
    
        hMRTOTcopy = hMRTOT.Clone(hMRTOT.GetName()+"COPY")
        for i in range(1,len(errMR)+1):
            print hMRTOT.GetBinContent(i),errMR[i-1],hMRTOT.GetBinError(i)
            hMRTOTcopy.SetBinError(i,max(errMR[i-1],hMRTOT.GetBinError(i)))
            hMRTOT.SetBinError(i,0.)
        
        hRSQTOTcopy = hRSQTOT.Clone(hRSQTOT.GetName()+"COPY")
        for i in range(1,len(errRSQ)+1):
            hRSQTOTcopy.SetBinError(i,max(errRSQ[i-1],hRSQTOT.GetBinError(i)))
            hRSQTOT.SetBinError(i,0.)

        goodPlot("MR", outFolder, Label, Energy, Lumi, hMRTOTcopy, hMRTOT, hMRTTj, hMRVpj, hMRData, fit3D, btag)
        goodPlot("RSQ", outFolder, Label, Energy, Lumi, hRSQTOTcopy, hRSQTOT, hRSQTTj, hRSQVpj, hRSQData, fit3D, btag)
        
        btag += 1
    
