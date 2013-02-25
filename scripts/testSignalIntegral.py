from optparse import OptionParser
import ROOT as rt
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

    from RazorCombinedFit.Framework import Config
    cfg = Config.Config("/afs/cern.ch/work/s/salvati/CMSSW_6_1_1/src/RazorCombinedFit_wreece_101212_2011_style_fits/config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg")

    # Define variables
    # ---------------------------------------
    MR = rt.RooRealVar("MR","MR",500,4000) 
    Rsq = rt.RooRealVar("Rsq","Rsq",0.05,1.)
    Ntot = rt.RooRealVar("Ntot","Ntot",0,1000000)

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

    tfile = rt.TFile.Open("/afs/cern.ch/user/s/ssekmen/public/forWill/RzrMJSMS/SMS_T2tt_jan30_MR500.0_R0.22360679775_400.0_0.0_Ele.root")
    nominal = tfile.Get("wHisto")
    jes = tfile.Get("wHisto_JESerr_pe")
    pdf = tfile.Get("wHisto_pdferr_pe")
    btag = tfile.Get("wHisto_btagerr_pe")
    
    workspace = rt.RooWorkspace('newws')
    nominal.SetDirectory(0)
    jes.SetDirectory(0)
    pdf.SetDirectory(0)
    btag.SetDirectory(0)
    
    RootTools.Utils.importToWS(workspace,nominal)
    RootTools.Utils.importToWS(workspace,jes)
    RootTools.Utils.importToWS(workspace,pdf)
    RootTools.Utils.importToWS(workspace,btag)
    
    xJes = rt.RooRealVar("xJes","xJes",0.,-1.,1.) 
    xPdf = rt.RooRealVar("xPdf","xPdf",0.,-1.,1.)
    xBtag = rt.RooRealVar("xBtag","xBtag",0.,-1.,1.)

    rt.RooMsgService.instance().getStream(1).addTopic(rt.RooFit.Integration)
    razor = RooRazor2DSignal("razor","razor", MR, Rsq, workspace, "wHisto","wHisto_JESerr_pe","wHisto_pdferr_pe","wHisto_btagerr_pe", xJes, xPdf, xBtag)

    ## add nuisance parameters to the PDF
    xBtag_prime = rt.RooRealVar('xBtag_prime', 'xBtag_prime', 0)
    xJes_prime = rt.RooRealVar('xJes_prime', 'xJes_prime', 0)
    xPdf_prime = rt.RooRealVar('xPdf_prime', 'xPdf_prime', 0)
    eff_prime = rt.RooRealVar('eff_prime', 'eff_prime', 0)
    lumi_prime = rt.RooRealVar('lumi_prime', 'lumi_prime', 0)
    nuisArgs = rt.RooArgSet(xBtag_prime, xJes_prime, xPdf_prime, eff_prime, lumi_prime)

    lumi_value = rt.RooRealVar('lumi_value', 'lumi_value', 19300)
    eff_value = rt.RooRealVar('eff_value', 'eff_value', 1.0)
    lumi_uncert = rt.RooRealVar('lumi_uncert', 'lumi_uncert', 0.044)
    eff_uncert = rt.RooRealVar('eff_uncert', 'eff_uncert', 0.1)
    otherArgs = rt.RooArgSet(lumi_value, eff_value, lumi_uncert, eff_uncert )

    sigma = rt.RooRealVar('sigma', 'sigma', 0.001)
    poiArgs = rt.RooArgSet(sigma)

    workspace.defineSet("nuisance", nuisArgs, True)
    workspace.defineSet("other", otherArgs, True)
    workspace.defineSet("poi", poiArgs, True)
    workspace.factory("expr::lumi('@0 * pow( (1+@1), @2)', lumi_value, lumi_uncert, lumi_prime)")
    workspace.factory("expr::eff('@0 * pow( (1+@1), @2)', eff_value, eff_uncert, eff_prime)")

    ## now multiply the PDF by the already smeared nuisance parameters
    nuisFile = rt.TFile.Open("NuisanceTree.root","read")
    nuisTree = nuisFile.Get("nuisTree")
    nuisTree.Draw('>>nuisElist','nToy==1','entrylist')
    nuisElist = rt.gDirectory.Get('nuisElist')
    nuisEntry = nuisElist.Next()
    nuisTree.GetEntry(nuisEntry)
    for var in RootTools.RootIterator.RootIterator(workspace.set('nuisance')):
        # for each nuisance, grab gaussian distributed variables from ROOT tree
        varVal = eval('nuisTree.%s'%var.GetName())
        var.setVal(varVal)
        print "NUISANCE PAR %s = %f"%(var.GetName(),var.getVal())
    
    workspace.Print("v")
    
    razordata = razor.generate(MRRsq,100)

    #fr = razor.fitTo(razordata3D,rt.RooFit.Save())
    #fr.Print("v")
    
    MRframe  = MR.frame()
    razordata.plotOn(MRframe,rt.RooFit.Binning("MRRooBins"))
    razor.plotOn(MRframe)
    Rsqframe  = Rsq.frame()
    razordata.plotOn(Rsqframe,rt.RooFit.Binning("RsqRooBins"))
    razor.plotOn(Rsqframe)

    # Draw canvas
    # ---------------------------------------
    rt.gStyle.SetPalette(1)
    rt.gStyle.SetOptStat(0)
    c = rt.TCanvas("c","c",500,400)
    c.Divide(2,1)
    c.cd(1)
    #rt.gPad.SetLogy()
    MRframe.Draw()
    c.cd(2)
    #rt.gPad.SetLogy()
    Rsqframe.Draw()
    c.Print("test.pdf")  
