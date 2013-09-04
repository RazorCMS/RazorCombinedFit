import ROOT as rt
from optparse import OptionParser
from array import *
import sys
import RazorCombinedFit
import RootTools


def getBinning():
    MRbins = [500.0, 550.0, 600.0, 650.0, 700.0, 800, 900, 1000, 1200, 1500, 2000, 3000, 4000.0]
    Rsqbins = [0.05, 0.09, 0.2, 0.3, 0.4, 0.5, 1.0]

    return MRbins, Rsqbins

if __name__ == '__main__':
    # Load the signal p.d.f.
    # ---------------------------------------
    rt.gSystem.Load("../lib/libRazor")
    from ROOT import RooRazor2DSignal


    rt.RooRandom.randomGenerator().SetSeed(314159)

    
    # Define variables
    # ---------------------------------------
    MR = rt.RooRealVar("MR","MR",600,500,4000) 
    Rsq = rt.RooRealVar("Rsq","Rsq",0.1,0.05,1.)
    Ntot = rt.RooRealVar("Ntot","Ntot",100,0,1000000)

    MR.setConstant(rt.kFALSE)
    Rsq.setConstant(rt.kFALSE)
    
    MRRsq = rt.RooArgSet("MRRsq")
    MRRsq.add(MR)
    MRRsq.add(Rsq)
    
    #varList2D = rt.RooArgList(MR,Rsq)
    
    MRbins, Rsqbins = getBinning()
    
    x = array("d",MRbins)
    y = array("d",Rsqbins)
    
    MRRooBins = rt.RooBinning(len(MRbins)-1, x, "MRRooBins")
    RsqRooBins =  rt.RooBinning(len(Rsqbins)-1, y, "RsqRooBins")
    MR.setBinning(MRRooBins)
    Rsq.setBinning(RsqRooBins)

    tfile = rt.TFile.Open(sys.argv[1])
    nominal = tfile.Get("wHisto")
    jes = tfile.Get("wHisto_JESerr_pe")
    pdf = tfile.Get("wHisto_pdferr_pe")
    btag = tfile.Get("wHisto_btagerr_pe")
    isr = tfile.Get("wHisto_isrerr_pe")
    lep = tfile.Get("wHisto_leperr_pe")
    
    workspace = rt.RooWorkspace('newws')
    nominal.SetDirectory(0)
    jes.SetDirectory(0)
    pdf.SetDirectory(0)
    btag.SetDirectory(0)
    isr.SetDirectory(0)
    lep.SetDirectory(0)

    RootTools.Utils.importToWS(workspace,nominal)
    RootTools.Utils.importToWS(workspace,jes)
    RootTools.Utils.importToWS(workspace,pdf)
    RootTools.Utils.importToWS(workspace,btag)
    RootTools.Utils.importToWS(workspace,isr)
    RootTools.Utils.importToWS(workspace,lep)
    
    xJes = rt.RooRealVar("xJes","xJes",0.,-5.,5.) 
    xPdf = rt.RooRealVar("xPdf","xPdf",0.,-5.,5.)
    xBtag = rt.RooRealVar("xBtag","xBtag",0.,-5.,5.)
    xIsr = rt.RooRealVar("xIsr","xIsr",0.,-5.,5.)
    xLep = rt.RooRealVar("xLep","xLep",0.,-5.,5.)
    
    RootTools.Utils.importToWS(workspace,xJes)
    RootTools.Utils.importToWS(workspace,xPdf)
    RootTools.Utils.importToWS(workspace,xBtag)
    RootTools.Utils.importToWS(workspace,xIsr)
    RootTools.Utils.importToWS(workspace,xLep)
    RootTools.Utils.importToWS(workspace,MR)
    RootTools.Utils.importToWS(workspace,Rsq)
    
    rt.RooMsgService.instance().getStream(1).addTopic(rt.RooFit.Integration)
    
    #razor = RooRazor2DSignal("razor","razor", MR, Rsq, workspace, "wHisto","wHisto_JESerr_pe","wHisto_pdferr_pe","wHisto_btagerr_pe", "wHisto_leperr_pe", "wHiso_isrerr_pe", xJes, xPdf, xBtag, xLep, xIsr)

    razor = RooRazor2DSignal('razor','razor',\
                                         workspace.var('MR'),workspace.var('Rsq'),\
                                         workspace,\
                                         nominal.GetName(),jes.GetName(),pdf.GetName(),btag.GetName(),lep.GetName(),isr.GetName(),\
                                         workspace.var('xJes'),workspace.var('xPdf'),workspace.var('xBtag'),workspace.var('xLep'),workspace.var('xIsr'))
    
    #extrazor = rt.RooExtendPdf("extrazor","extrazor",razor,Ntot)
    razor.Print("v")

    RootTools.Utils.importToWS(workspace,razor)
    #RootTools.Utils.importToWS(workspace,extrazor)
    workspace.Print("v")

    workspace.var('xJes').setVal(0.0)
    workspace.var('xPdf').setVal(0.0)
    workspace.var('xBtag').setVal(0.0)
    workspace.var('xIsr').setVal(0.0)
    workspace.var('xLep').setVal(0.0)
    workspace.var('xIsr').setConstant()
    workspace.var('xLep').setConstant()
    
    razordata = razor.generate(MRRsq,10000)
    errorArgSet = rt.RooArgSet()
    errorArgSet.add(workspace.var('xJes'))
    errorArgSet.add(workspace.var('xPdf'))
    errorArgSet.add(workspace.var('xBtag'))
    

    fr = razor.fitTo(razordata,rt.RooFit.Save(),rt.RooFit.Constrained())
    fr.Print("v")

    par = 'xJes'
    
    MRframe  = MR.frame()
    razordata.plotOn(MRframe,rt.RooFit.Binning("MRRooBins"))
    workspace.var(par).setVal(-1.0)
    razor.plotOn(MRframe,rt.RooFit.LineColor(rt.kBlue-10))
    workspace.var(par).setVal(1.0)
    razor.plotOn(MRframe,rt.RooFit.LineColor(rt.kBlue-10))
    workspace.var(par).setVal(0.0)
    razor.plotOn(MRframe)
    Rsqframe  = Rsq.frame()
    razordata.plotOn(Rsqframe,rt.RooFit.Binning("RsqRooBins"))
    workspace.var(par).setVal(-1.0)
    razor.plotOn(Rsqframe,rt.RooFit.LineColor(rt.kBlue-10))
    workspace.var(par).setVal(1.0)
    razor.plotOn(Rsqframe,rt.RooFit.LineColor(rt.kBlue-10))
    workspace.var(par).setVal(0.0)
    razor.plotOn(Rsqframe)

    hist = rt.TH2D("hist","hist",len(x)-1,x,len(y)-1,y)
    razordata.fillHistogram(hist,rt.RooArgList(MR,Rsq))

    # Draw canvas
    # ---------------------------------------
    rt.gStyle.SetPalette(1)
    rt.gStyle.SetOptStat(0)
    c = rt.TCanvas("c","c",500,400)
    c.Divide(2,2)
    c.cd(1)
    rt.gPad.SetLogy(0)
    MRframe.Draw()
    c.cd(2)
    rt.gPad.SetLogy(0)
    Rsqframe.Draw()
    c.cd(3)
    rt.gPad.SetLogy(1)
    rt.gPad.SetLogx(1)
    hist.Draw("colz")
    c.cd(4)
    rt.gPad.SetLogy(1)
    rt.gPad.SetLogx(1)
    hist.Draw("surf2")
    c.Print("test.pdf")  
