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
    modeVal,rangeMin,rangeMax = makeToyPVALUE_sigbin.find68ProbRange(h)
    return rangeMax, rangeMin

def GetErrorsX(nbinx, nbiny, myTree, printPlots, outFolder, fit3D, btagOpt, myYbinning):
    err = []
    # for each bin of x, get the error on the sum of the y bins
    if printPlots:
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"canvasd\");")
        d = rt.TCanvas("canvasd","canvasd",800,600)
    for i in range(0,nbinx-1):
        sumName = ""
        varNames = []
        for j in myYbinning:
            #if j==0 and i==0: continue #WE ALWAYS SKIP THE BIN IN THE BOTTOM LEFT CORNER
            if btagOpt == 0:
                sumName = sumName+"b%i_%i_1+b%i_%i_2+b%i_%i_3+" %(i,j,i,j,i,j)
                varNames.extend(["b%i_%i_1"%(i,j),"b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)])
            elif btagOpt == 23:
                sumName = sumName+"b%i_%i_2+b%i_%i_3+" %(i,j,i,j)
                varNames.extend(["b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)])
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
            mode,xmin,xmax,probRange,funcFill68 = makeToyPVALUE_sigbin.find68ProbRangeFromKDEMode(maxX,func)
        else:
            xmax, xmin = GetProbRange(myhisto)
        print xmin, xmax
        err.append((xmax-xmin)/2.)
        
        #now making plots
        myhisto.Draw()
        tleg = rt.TLegend(0.6,.65,.9,.9)
        if switchToKDE:
            ic = rt.TColor(1398, 0.75, 0.92, 0.68,"")
            func.SetLineColor(rt.TColor.GetColor(0.1, .85, 0.5))
            func.Draw("same")
            funcFill68.SetRange(xmin,xmax)
            ic68 = rt.TColor(1404, 0.49, 0.60, 0.82,"")
            funcFill68.SetLineColor(rt.TColor.GetColor(0.1, .85, 0.5))
            funcFill68.SetFillColor(ic68.GetColor(0.49,0.60,.82))
            funcFill68.SetFillStyle(3144)
            funcFill68.Draw("same")
            tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,xmin,xmax),"f")
        else:
            tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,xmin,xmax),"f")
        tleg.SetFillColor(rt.kWhite)
        tleg.Draw("same")
        rt.gStyle.SetOptStat(0)
        
        #now printing plots
        if printPlots:
            if btagOpt>0:
                d.Print("%s/functest_X_%ib_%i.pdf"%(outFolder,btagOpt,i))
            else:
                d.Print("%s/functest_X_%i.pdf"%(outFolder,i))
                
    myhisto.Delete()
    if printPlots: del d
    del myhisto
    return err
            
def GetErrorsY(nbinx, nbiny, myTree, printPlots, outFolder, fit3D, btagOpt, myXbinning):
    err = []
    # for each bin of y, get the error on the sum of the x bins
    if printPlots:
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"canvasd\");")
        d = rt.TCanvas("canvasd","canvasd",800,600)
    for j in range(0,nbiny-1):
        sumName = ""
        varNames = []
        for i in myXbinning:
            #if j==0 and i==0: continue #WE ALWAYS SKIP THE BIN IN THE BOTTOM LEFT CORNER
            if btagOpt == 0:
                sumName = sumName+"b%i_%i_1+b%i_%i_2+b%i_%i_3+" %(i,j,i,j,i,j)
                varNames.extend(["b%i_%i_1"%(i,j),"b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)])
            elif btagOpt == 23:
                sumName = sumName+"b%i_%i_2+b%i_%i_3+" %(i,j,i,j)
                varNames.extend(["b%i_%i_2"%(i,j),"b%i_%i_3"%(i,j)])
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
            mode,xmin,xmax,probRange,funcFill68 = makeToyPVALUE_sigbin.find68ProbRangeFromKDEMode(maxX,func)
        else:
            xmax, xmin = GetProbRange(myhisto)
        print xmin, xmax
        err.append((xmax-xmin)/2.)
        
        #now making plots
        myhisto.Draw()
        tleg = rt.TLegend(0.6,.65,.9,.9)
        if switchToKDE:
            ic = rt.TColor(1398, 0.75, 0.92, 0.68,"")
            func.SetLineColor(rt.TColor.GetColor(0.1, .85, 0.5))
            func.Draw("same")
            funcFill68.SetRange(xmin,xmax)
            ic68 = rt.TColor(1404, 0.49, 0.60, 0.82,"")
            funcFill68.SetLineColor(rt.TColor.GetColor(0.1, .85, 0.5))
            funcFill68.SetFillColor(ic68.GetColor(0.49,0.60,.82))
            funcFill68.SetFillStyle(3144)
            funcFill68.Draw("same")
            tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,xmin,xmax),"f")
        else:
            tleg.AddEntry(funcFill68,"%.1f%% Range = [%.1f,%.1f]"%(probRange*100,xmin,xmax),"f")
        tleg.SetFillColor(rt.kWhite)
        tleg.Draw("same")
        rt.gStyle.SetOptStat(0)
        
        #now printing plots
        if printPlots:
            if btagOpt>0:
                d.Print("%s/functest_Y_%ib_%i.pdf"%(outFolder,btagOpt,j))
            else:
                d.Print("%s/functest_Y_%i.pdf"%(outFolder,j))
                
    myhisto.Delete()
    if printPlots: del d
    del myhisto
    return err


def goodPlot(varname, Box, outFolder, Label, Energy, Lumi, hMRTOTcopy, hMRTOT, hMRData, hMRSignal, c1, pad1, pad2, fit3D, btagOpt):
    rt.gStyle.SetOptStat(0000)
    rt.gStyle.SetOptTitle(0)
    predColor = rt.kGreen
    
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
    pad2.SetBottomMargin(0.47)
    
    pad1.Draw()
    pad1.cd()
    rt.gPad.SetLogy()

    MRbins, Rsqbins, nBtagbins = makeBluePlot.Binning(Box, False)
    binMap = {"MR":MRbins,"RSQ":Rsqbins}
    print binMap
    print binMap[varname]
    print binMap[varname][0]
    # MR PLOT
    hMRData.SetLineWidth(2)
    hMRTOTcopy.SetFillStyle(1001)
    hMRTOTcopy.SetFillColor(predColor-10)
    hMRTOTcopy.SetLineColor(predColor)
    hMRTOTcopy.SetLineWidth(2)
    hMRData.GetXaxis().SetTitle("")
    hMRData.GetXaxis().SetLabelOffset(0.16)
    hMRData.GetXaxis().SetLabelSize(0.065)
    hMRData.GetYaxis().SetLabelSize(0.065)
    hMRData.GetXaxis().SetTitleSize(0.06)
    hMRData.GetYaxis().SetTitleSize(0.08)
    hMRData.GetXaxis().SetTitleOffset(0.8)
    hMRData.GetYaxis().SetTitleOffset(0.7)
    hMRData.GetXaxis().SetTicks("+-")
    hMRData.GetYaxis().SetTitle("Events")

    if varname=="RSQ":
        hMRData.SetMinimum(.5)
        hMRData.SetMaximum(1.e3)
    elif varname=="MR":
        hMRData.SetMinimum(.05)
        hMRData.SetMaximum(1.e3)
        hMRData.GetXaxis().SetNdivisions(509)
    rsqLabel = ""
    fitLabel = ""
    
    if btagOpt==0:
        projRegion = "LowRsq_LowMR_HighMR"
        lowRsqRegion = "LowRsq"
        lowMRRegion = "LowMR"
    elif btagOpt==23:
        projRegion = "LowRsq2b_LowMR2b_HighMR2b_LowRsq3b_LowMR3b_HighMR3b"
        lowRsqRegion = "LowRsq2b_LowRsq3b"
        lowMRRegion = "LowMR2b_LowMR3b"
        
    if hMRData.GetName()=="histoData0_%s_Rsq1DSlice"%projRegion:
        hMRData.GetXaxis().SetRange(2,hMRData.GetNbinsX())
        rsqLabel = "400#leqM_{R}<550"
        fitLabel = "Low M_{R} Side-band"
    elif hMRData.GetName()=="histoData1_%s_Rsq1DSlice"%projRegion:
        hMRData.GetXaxis().SetRange(2,hMRData.GetNbinsX())
        rsqLabel = "550#leqM_{R}<900"
        fitLabel = "Extrapolation Region"
    elif hMRData.GetName()=="histoData2_%s_Rsq1DSlice"%projRegion:
        hMRData.GetXaxis().SetRange(2,hMRData.GetNbinsX())
        rsqLabel = "M_{R}#geq900"
        fitLabel = "Extrapolation Region"
    elif hMRData.GetName()=="histoData0_%s_MR1DSlice"%projRegion:
        hMRData.GetXaxis().SetRange(2,hMRData.GetNbinsX()-1)
        rsqLabel = "0.25#leqR^{2}<0.3"
        fitLabel = "Low R^{2} Sideband"
    elif hMRData.GetName()=="histoData1_%s_MR1DSlice"%projRegion:
        hMRData.GetXaxis().SetRange(3,hMRData.GetNbinsX()-1)
        rsqLabel = "0.3#leqR^{2}<0.41"
        fitLabel = "Extrapolation Region"
    elif hMRData.GetName()=="histoData2_%s_MR1DSlice"%projRegion:
        hMRData.GetXaxis().SetRange(3,hMRData.GetNbinsX()-1)
        rsqLabel = "0.41#leqR^{2}<0.52"
        fitLabel = "Extrapolation Region"
    elif hMRData.GetName()=="histoData3_%s_MR1DSlice"%projRegion:
        hMRData.GetXaxis().SetRange(3,hMRData.GetNbinsX()-1)
        rsqLabel = "R^{2}#geq0.52"
        fitLabel = "Extrapolation Region"
    elif hMRData.GetName()=="histoData0_%s_MR1DSlice"%lowMRRegion:
        rsqLabel = "0.3#leqR^{2}<1.5"
        fitLabel = "Low M_{R} Sideband"
        hMRData.GetXaxis().SetNdivisions(206,False)
        #hMRData.SetMaximum(5.e2)
        #hMRData.SetMinimum(40)
    elif hMRData.GetName()=="histoData0_%s_Rsq1DSlice"%lowRsqRegion:
        rsqLabel = "450#leqM_{R}<4000"
        fitLabel = "Low R^{2} Sideband"
        hMRData.GetXaxis().SetNdivisions(205,False)
        #hMRData.SetMaximum(5.e2)
        #hMRData.SetMinimum(40)
        
    hMRData.Draw("pe")
    hMRTOTcopy.Draw("e2same")

    showSignal = (hMRSignal !=None) and (Label.find("_0p0_") == -1)

    showSignal = True
    hMRData.SetLineColor(rt.kBlack)
    hMRData.SetMarkerStyle(20)
    hMRData.SetMarkerColor(rt.kBlack)
    hMRTOT.SetLineWidth(2)
    hMRTOT.SetFillStyle(0)
    hMRTOT.SetLineColor(predColor)
    hMRTOT.SetMarkerColor(predColor)
    hMRTOTcopy.SetMarkerColor(predColor)
    hMRTOT.DrawCopy("histsame")
    hMRData.Draw('pesame')

    if showSignal:
        c4 = rt.gROOT.GetColor(rt.kGray+2)
        c4.SetAlpha(1.0)
        hMRSignal.SetLineColor(rt.kBlack)
        hMRSignal.SetFillColor(rt.kGray+2)
        hMRSignal.SetLineStyle(2)
        hMRSignal.SetFillStyle(3005)
        hMRSignal.SetLineWidth(2)
        hMRSignal.Draw("histfsame")
    
    if showSignal:
        leg = rt.TLegend(0.7,0.67,0.93,0.93)
    else:
        leg = rt.TLegend(0.7,0.72,0.93,0.93)
    leg.SetFillColor(0)
    leg.SetTextFont(42)
    leg.SetLineColor(0)

    if noBtag:
        btagLabel = "no b-tag"
    else:
        if btagOpt==0:
            btagLabel = "#geq1 b-tag"
            if Box=="Jet2b": 
                btagLabel = "#geq2 b-tag"
        elif btagOpt==1:
            btagLabel = "1 b-tag"
        elif btagOpt==23:
            btagLabel = "#geq2 b-tag"
        
    #leg.AddEntry(hMRData,"Simulation","lep")
    leg.AddEntry(hMRData,"Data","lep")
    leg.AddEntry(hMRTOTcopy,"Total Bkgd")

    if showSignal:
        leg.AddEntry(hMRSignal,"Signal","fl")
    leg.Draw("same")

    # plot labels
    pt = rt.TPaveText(0.25,0.5,0.7,0.93,"ndc")
    pt.SetBorderSize(0)
    pt.SetTextSize(0.05)
    pt.SetFillColor(0)
    pt.SetFillStyle(0)
    pt.SetLineColor(0)
    pt.SetTextAlign(21)
    pt.SetTextFont(42)
    pt.SetTextSize(0.062)
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
        text = pt.AddText("Razor %s Box #int L = %3.1f fb^{-1}" %(Box.replace("Jet2b","2b-Jet"),Lumi))
            
    text = pt.AddText("")
    text = pt.AddText("                            %s,  %s" %(rsqLabel,btagLabel))
    text = pt.AddText("                                                        %s"%(fitLabel))

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
 
    for i in range(1, hMRData.GetNbinsX()+1):
        tmpVal = hMRTOTcopyclone.GetBinContent(i)
        if tmpVal != -0.:
            hMRDataDivide.SetBinContent(i, hMRDataDivide.GetBinContent(i)/tmpVal)
            hMRDataDivide.SetBinError(i, hMRDataDivide.GetBinError(i)/tmpVal)
            hMRTOTcopyclone.SetBinContent(i, hMRTOTcopyclone.GetBinContent(i)/tmpVal)
            hMRTOTcopyclone.SetBinError(i, hMRTOTcopyclone.GetBinError(i)/tmpVal)
            hMRTOTclone.SetBinContent(i, hMRTOTclone.GetBinContent(i)/tmpVal)
            hMRTOTclone.SetBinError(i, hMRTOTclone.GetBinError(i)/tmpVal)

    hMRDataDivide.GetXaxis().SetTitleOffset(0.97)
    hMRDataDivide.GetXaxis().SetLabelOffset(0.02)
    if varname == "MR":
        hMRDataDivide.GetXaxis().SetTitle("M_{R} [GeV]")
    if varname == "RSQ":
        hMRDataDivide.GetXaxis().SetTitle("R^{2}")
        
    hMRDataDivide.GetYaxis().SetLabelSize(0.18)
    hMRDataDivide.SetTitle("")
    hMRDataDivide.SetMaximum(3.5)
    hMRDataDivide.SetMinimum(0.)
    hMRDataDivide.GetXaxis().SetLabelSize(0.22)
    hMRDataDivide.GetXaxis().SetTitleSize(0.22)
    hMRDataDivide.GetYaxis().SetNdivisions(504,rt.kTRUE)
    hMRTOTcopyclone.GetYaxis().SetNdivisions(504,rt.kTRUE)
    #if varname=="MR": hMRDataDivide.GetXaxis().SetNdivisions(509,rt.kTRUE)
    hMRDataDivide.GetYaxis().SetTitleOffset(0.2)
    hMRDataDivide.GetYaxis().SetTitleSize(0.22)
    hMRDataDivide.GetYaxis().SetTitle("Data/Bkgd")
    hMRDataDivide.GetXaxis().SetTicks("+")
    hMRDataDivide.GetXaxis().SetTickLength(0.07)
    hMRTOTcopyclone.SetMarkerColor(predColor-10)
    hMRDataDivide.Draw('pe')
    hMRTOTcopyclone.Draw("e2same")
    hMRTOTcopyclone.Draw("axissame")
    hMRDataDivide.Draw('pesame')

    pad2.Update()
    pad1.cd()
    pad1.Update()
    pad1.Draw()
    c1.cd()

    myExtraLabel = hMRTOT.GetName().split("Toy")[-1]
    c1.Print("%s/%sSlice_%s_%s.pdf" %(outFolder,varname,Label,myExtraLabel))
    c1.Print("%s/%sSlice_%s_%s.C" %(outFolder,varname,Label,myExtraLabel))
    
if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "\nRun the script as follows:\n"
        print "python scripts/make1DSlice.py BoxName ExpectedYieldRootFile RazorFitOutputRootFile OutDir"
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
    Lumi = 19.3
    Energy = 8.
    Preliminary = "Preliminary"
    datasetName = ""
    printPlots = False
    for i in range(4,len(sys.argv)):
        if sys.argv[i] == "--noBtag": noBtag = True
        if sys.argv[i] == "--3D": fit3D = True
        if sys.argv[i] == "--forPaper": Preliminary = ""
        if sys.argv[i] == "--printPlots": printPlots = True
        if sys.argv[i].find("-MC=") != -1:
            Preliminary = "Simulation"
            datasetName = sys.argv[i].replace("-MC=","")
        if sys.argv[i].find("-Label=") != -1:
            Label = sys.argv[i].replace("-Label=","")
        if sys.argv[i].find("-Lumi=") != -1: Lumi = float(sys.argv[i].replace("-Lumi=",""))
        if sys.argv[i].find("-Energy=") != -1: Energy = float(sys.argv[i].replace("-Energy=",""))

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
    
    btagToDo = [0] # THIS MEANS WE ARE INTEGRATING THE FULL BTAG REGION
    #btagToDo = [0, 23] # THIS MEANS WE ARE INTEGRATING >=2 BTAGS

    
    myRsqbinnings = [[0],[1],[2],[3,4,5],[1,2,3,4,5]]
    myMRbinnings = [[0,1],[2,3],[4,5,6,7],[1,2,3,4,5,6,7]]


    for btagOpt in btagToDo:
        if btagOpt==0:
            projRegion = "LowRsq_LowMR_HighMR"
            lowRsqRegion = "LowRsq"
            lowMRRegion = "LowMR"
            
        elif btagOpt==23:
            projRegion = "LowRsq2b_LowMR2b_HighMR2b_LowRsq3b_LowMR3b_HighMR3b"
            lowRsqRegion = "LowRsq2b_LowRsq3b"
            lowMRRegion = "LowMR2b_LowMR3b"
        
        
        myRsqHists = ["0_%s_Rsq1DSlice"%projRegion,
                      "1_%s_Rsq1DSlice"%projRegion,
                      "2_%s_Rsq1DSlice"%projRegion,
                      "0_%s_Rsq1DSlice"%lowRsqRegion]
        myMRHists = ["0_%s_MR1DSlice"%projRegion,
                     "1_%s_MR1DSlice"%projRegion,
                     "2_%s_MR1DSlice"%projRegion,
                     "3_%s_MR1DSlice"%projRegion,
                     "0_%s_MR1DSlice"%lowMRRegion]

        # Total Bkg histograms
        hMRTOTList = [fitFile.Get("%s/histoToy%s" %(Box,myHist)) for myHist in myMRHists]
        hRSQTOTList = [fitFile.Get("%s/histoToy%s" %(Box,myHist)) for myHist in myRsqHists]
        
        # Data histograms    
        hMRDataList = [fitFile.Get("%s/histoData%s" %(Box,myHist)) for myHist in myMRHists]
        hRSQDataList = [fitFile.Get("%s/histoData%s" %(Box,myHist)) for myHist in myRsqHists]
        
        # Signal histograms    
        hMRSignalList = [fitFile.Get("%s/histoToySignal%s" %(Box,myHist)) for myHist in myMRHists]
        hRSQSignalList = [fitFile.Get("%s/histoToySignal%s" %(Box,myHist)) for myHist in myRsqHists]
    
        for hMRTOT, hMRData, hMRSignal, myRsqbinning, in zip(hMRTOTList, hMRDataList,  hMRSignalList, myRsqbinnings):
            errMR = GetErrorsX(len(MRbins),len(Rsqbins),myTree,printPlots,outFolder,fit3D, btagOpt, myRsqbinning)
        
            hMRTOTcopy = hMRTOT.Clone(hMRTOT.GetName()+"COPY")
            for i in range(1,len(errMR)+1):
                hMRTOTcopy.SetBinError(i,max(errMR[i-1],hMRTOT.GetBinError(i)))
                hMRTOT.SetBinError(i,0.)
            
            c1 = rt.TCanvas("c1","c1", 500, 400)
            pad1 = rt.TPad("pad1","pad1",0,0.25,1,1)
            pad2 = rt.TPad("pad2","pad2",0,0,1,0.25)
        
            goodPlot("MR",  Box, outFolder, Label, Energy, Lumi, hMRTOTcopy, hMRTOT, hMRData, hMRSignal, c1, pad1, pad2, fit3D, btagOpt)
            
        for hRSQTOT, hRSQData, hRSQSignal, myMRbinning in zip(hRSQTOTList, hRSQDataList, hRSQSignalList, myMRbinnings):
            errRSQ = GetErrorsY(len(MRbins),len(Rsqbins),myTree,printPlots,outFolder,fit3D,btagOpt, myMRbinning)
            
            hRSQTOTcopy = hRSQTOT.Clone(hRSQTOT.GetName()+"COPY")
            for i in range(1,len(errRSQ)+1):
                hRSQTOTcopy.SetBinError(i,max(errRSQ[i-1],hRSQTOT.GetBinError(i)))
                hRSQTOT.SetBinError(i,0.)

            c1 = rt.TCanvas("c1","c1", 500, 400)
            pad1 = rt.TPad("pad1","pad1",0,0.25,1,1)
            pad2 = rt.TPad("pad2","pad2",0,0,1,0.25)
        
            goodPlot("RSQ", Box, outFolder, Label, Energy, Lumi, hRSQTOTcopy, hRSQTOT, hRSQData, hRSQSignal, c1, pad1, pad2, fit3D, btagOpt)
        
    
