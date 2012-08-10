from optparse import OptionParser
import ROOT as rt
from array import *
import sys
import makeBluePlot
import plotStyle
import makeToyPVALUE_sigbin

def FindLastBin(h):
    for i in range(1,h.GetXaxis().GetNbins()):
        thisbin = h.GetXaxis().GetNbins()-i
        if h.GetBinContent(thisbin)>=0.1: return thisbin+1
    return h.GetXaxis().GetNbins()    

def GetProbRange(h):
    # find the maximum
    binMax = h.GetMaximumBin()
    # move left and right until integrating 68%
    prob = h.GetMaximum()
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
            
def GetErrors(nbinx, nbiny, myTree):
    err = []
    # for each bin of x, get the error on the sum of the y bins
    for i in range(0,nbinx-1):
        varName = ""
        for j in range(0,nbiny-1): varName = varName+"b%i_%i+" %(i,j)
        myTree.Draw(varName[:-1])
        htemp = rt.gPad.GetPrimitive("htemp");
        xmax, xmin = GetProbRange(htemp)
        print xmin, xmax
        err.append((xmax-xmin)/2.)
    return err

def goodPlot(varname, Label, Energy, Lumi, hMRTOTcopy, hMRTOT, hMRTTj, hMRVpj, hMRData):
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
    if varname == "RSQ": hMRTOTcopy.SetMaximum(hMRTOTcopy.GetMaximum()*5.)
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
    if noBtag: leg.AddEntry(hMRData,"Data %s no Btag" %Box,"lep")
    else: leg.AddEntry(hMRData,"Data %s #geq 1 Btag" %Box,"lep")
    leg.AddEntry(hMRTOTcopy,"Total Background")
    if showTTj and showVpj:
        leg.AddEntry(hMRVpj,"W+jets","l")
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
    text = pt.AddText("Razor %s #int L = %3.2f fb^{-1}" %(Box,Lumi))
    pt.Draw()
    
    c1.Update()

    c1.SaveAs("%s_%s.pdf" %(varname,Label))
    c1.SaveAs("%s_%s.C" %(varname,Label))
    
if __name__ == '__main__':
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gROOT.ForceStyle()

    Box = sys.argv[1]
    fileName = sys.argv[2]
    fitfileName = sys.argv[3]
    noBtag = False
    Lumi = 5.
    Energy = 8.
    Preliminary = "Preliminary"
    for i in range(4,len(sys.argv)):
        if sys.argv[i] == "--noBtag": noBtag = True
        if sys.argv[i] == "--forPaper": Preliminary = ""
        if sys.argv[i] == "--simulation": Preliminary = "Simulation"
        if sys.argv[i].find("-Lumi=") != -1: Lumi = float(sys.argv[i].replace("-Lumi=",""))
        if sys.argv[i].find("-Energy=") != -1: Energy = float(sys.argv[i].replace("-Energy=",""))

    Label = fitfileName.split("/")[-1].replace(".root","").replace("razor_output_","")

    MRbins, Rsqbins = makeBluePlot.Binning(Box, noBtag)
    #if noBtag: nBtagbins = [1., 2., 3., 4., 5.]

    x = array("d",MRbins)
    y = array("d",Rsqbins)
    #z = array("d",nBtagbins)

    hMR =  rt.TH1D("hMR","hMR", len(MRbins)-1, x)
    hRSQ =  rt.TH1D("hRSQ","hRSQ", len(Rsqbins)-1, y)
    #if noBtag: hBTAG = rt.TH1D("hBTAG","hBTAG", len(Rsqbins)-1, z)

    hMRBKG =  rt.TH1D("hMR","hMR", len(MRbins)-1, x)
    hRSQBKG =  rt.TH1D("hRSQ","hRSQ", len(Rsqbins)-1, y)
    #if noBtag: hBTAGBKG = rt.TH1D("hBTAG","hBTAG", len(Rsqbins)-1, z)

    # file with bkg predictions from toys
    fileIn = rt.TFile.Open(fileName)
    myTree = fileIn.Get("myTree")

    # file with output fit
    fitFile = rt.TFile.Open(fitfileName)

    # TTj histograms
    hMRTTj = fitFile.Get("%s/histoToyTTj_MR_FULL_ALLCOMPONENTS" %Box)
    hRSQTTj = fitFile.Get("%s/histoToyTTj_Rsq_FULL_ALLCOMPONENTS" %Box)
    #hBTAGTTj = fitFile.Get("%s/histoToyTTj_nBtag_FULL_ALLCOMPONENTS" %Box)

    # Vpj histograms
    hMRVpj = fitFile.Get("%s/histoToyVpj_MR_FULL_ALLCOMPONENTS" %Box)
    hRSQVpj = fitFile.Get("%s/histoToyVpj_Rsq_FULL_ALLCOMPONENTS" %Box)
    #hBTAGVpj = fitFile.Get("%s/histoToyVpj_nBtag_FULL_ALLCOMPONENTS" %Box)

    # Total Bkg histograms
    hMRTOT = fitFile.Get("%s/histoToy_MR_FULL_ALLCOMPONENTS" %Box)
    hRSQTOT = fitFile.Get("%s/histoToy_Rsq_FULL_ALLCOMPONENTS" %Box)
    #hBTAGTOT = fitFile.Get("%s/histoToy_nBtag_FULL_ALLCOMPONENTS" %Box)

    # Data histograms    
    hMRData = fitFile.Get("%s/histoData_MR_FULL_ALLCOMPONENTS" %Box)
    hRSQData = fitFile.Get("%s/histoData_Rsq_FULL_ALLCOMPONENTS" %Box)
    #hBTAGData = fitFile.Get("%s/histoData_nBtag_FULL_ALLCOMPONENTS")

    errMR = GetErrors(len(MRbins),len(Rsqbins),myTree)
    errRSQ = GetErrors(len(Rsqbins),len(MRbins),myTree)
    hMRTOTcopy = hMRTOT.Clone()
    hMRTOTcopy.SetName(hMRTOT.GetName()+"COPY")
    for i in range(1,len(errMR)+1):
        hMRTOTcopy.SetBinError(i,max(errMR[i-1],hMRTOT.GetBinError(i)))
        hMRTOT.SetBinError(i,0.)
    hRSQTOTcopy = hRSQTOT.Clone()
    hRSQTOTcopy.SetName(hRSQTOT.GetName()+"COPY")
    for i in range(1,len(errRSQ)+1):
        hRSQTOTcopy.SetBinError(i,max(errRSQ[i-1],hRSQTOT.GetBinError(i)))
        hRSQTOT.SetBinError(i,0.)

    goodPlot("MR", Label, Energy, Lumi, hMRTOTcopy, hMRTOT, hMRTTj, hMRVpj, hMRData)
    goodPlot("RSQ", Label, Energy, Lumi, hRSQTOTcopy, hRSQTOT, hRSQTTj, hRSQVpj, hRSQData)
