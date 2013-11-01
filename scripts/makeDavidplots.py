from optparse import OptionParser
import os
import math
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from array import *
from pdfShit import *
import sys


boxMap = {'MuEle':[0],'MuMu':[1],'EleEle':[2],'MuMultiJet':[3,4],'MuJet':[3,4],'Mu':[4],'EleMultiJet':[5,6],'EleJet':[5,6],'Jet':[7],'Jet2b':[7],'Jet1b':[7],'MultiJet':[8,9]}
lumi = 19.3
xsec = 8.11

if __name__ == '__main__':

    signalFile = rt.TFile.Open("SMS/T2tt_MG_700.000000_MCHI_25.000000.root")
    bkgdFile = rt.TFile.Open("SidebandFits2012ABCD_FINAL.root")
    histoFile  = rt.TFile.Open("SMS/T2tt_histo.root")
    histo = histoFile.Get("SMSWALL")
    wall = histo.GetBinContent(histo.FindBin(700,25))
        
    box = "MultiJet"

    workspace = bkgdFile.Get("%s/Box%s_workspace"%(box,box))

    MR0 = workspace.var("MR0_TTj2b")
    R0 = workspace.var("R0_TTj2b")
    b = workspace.var("b_TTj2b")
    n = workspace.var("n_TTj2b")
    Ntot = workspace.var("Ntot_TTj2b")

    
    MR = workspace.var("MR")
    Rsq = workspace.var("Rsq")
    mr0 = MR0.getVal()
    r0 = R0.getVal()
    print "MR0_TTj2b=%f"%(mr0)
    print "R0_TTj2b=%f"%(r0)

    minMRsq = (MR.getMin()-mr0)*(Rsq.getMin()-r0)
    maxMRsq = (MR.getMax()-mr0)*(Rsq.getMax()-r0)/3.
    
    MRsq = rt.RooRealVar("MRsq","MRsq",minMRsq,maxMRsq)
    
    args = rt.RooArgSet()
    args.add(workspace.var("MR"))
    args.add(workspace.var("Rsq"))
    args.add(workspace.var("nBtag"))
    args.add(workspace.var("W"))
    
    args.add(MRsq)

    
    data = workspace.data("RMRTree")
    MRsqForm = rt.RooFormulaVar("MRsq","MRsqForm","(@0-%f)*(@1-%f)"%(mr0,r0),rt.RooArgList(MR,Rsq))
    data.addColumn(MRsqForm)
    
    #we cut away events outside our MR window
    mRmin = args['MR'].getMin()
    mRmax = args['MR'].getMax()

    #we cut away events outside our Rsq window
    rsqMin = args['Rsq'].getMin()
    rsqMax = args['Rsq'].getMax()
    rMin = rt.TMath.Sqrt(rsqMin)
    rMax = rt.TMath.Sqrt(rsqMax)

    btagmin =  args['nBtag'].getMin()
    btagmax =  args['nBtag'].getMax()
    
    sigmc = rt.RooDataSet('SigTree','Selected Signal R and MR',args)

    if box in ["Jet", "MultiJet", "EleEle", "Jet2b", "Jet1b", "EleJet", "EleMultiJet"]:
        noiseCut = "abs(TMath::Min( abs(atan2(MET_y,MET_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_y,MET_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"
    elif box in ["MuEle", "MuMu", "MuMultiJet","MuJet"]:
        noiseCut = "abs(TMath::Min( abs(atan2(MET_NOMU_y,MET_NOMU_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_NOMU_y,MET_NOMU_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"

    

    if box in ["Jet",  "MultiJet", "TauTauJet", "EleEle", "EleTau", "Ele", "Jet2b", "Jet1b", "EleMultiJet", "EleJet"]: 
        noiseCut = "abs(TMath::Min( abs(atan2(MET_y,MET_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_y,MET_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"
    elif box in ["MuEle", "MuMu", "MuTau", "Mu", "MuMultiJet", "MuJet"]:
        noiseCut = "abs(TMath::Min( abs(atan2(MET_NOMU_y,MET_NOMU_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_NOMU_y,MET_NOMU_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"
    

    #iterate over selected entries in the input tree
    boxCut = "(" + "||".join(["BOX_NUM==%i"%cut for cut in boxMap[box]]) + ")"
    print boxCut

    jetReq = "(MR>0.)"
    if box in ["MuMultiJet", "EleMultiJet"]:
        jetReq = "(NJET_NOMU>=4)"
    elif box in ["MuJet", "EleJet"]:
        jetReq = "(NJET_NOMU<=3)"
    boxCut = "(" + jetReq + "&&" + boxCut + ")"

    BTAGNOM = "btag_nom"

    
    condition = '(%s && GOOD_PF && (%s) && %s >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f)' % (boxCut,noiseCut,BTAGNOM,mRmin,mRmax,rsqMin,rsqMax)
    tree = signalFile.Get('EVENTS')
    
    tree.Draw('>>elist','(%s)' % (condition),'entrylist')
    
    elist = rt.gDirectory.Get('elist')
    
    entry = -1;
    while True:
        entry = elist.Next()
        if entry == -1: break
        tree.GetEntry(entry)
        
        a = rt.RooArgSet(args)
        
        a.setRealValue('MR',tree.MR)
        a.setRealValue('Rsq',tree.RSQ)
        a.setRealValue('nBtag',tree.btag_nom)
        a.setRealValue('W',0.95*tree.WISR*tree.WLEP*tree.WPU*lumi*xsec/wall)

        a.setRealValue('MRsq',(tree.MR-mr0)*(tree.RSQ-r0))
    
        sigmc.add(a)
    
    wsigmc = rt.RooDataSet(sigmc.GetName(),sigmc.GetTitle(),sigmc,sigmc.get(),"MR>=0.","W")
    wsigmc.Print("v")

    
    razPdf = rt.RooRazor1DTail_SYS("razor","razor", MRsq,b, n)

    
    c = rt.TCanvas("c","c",500,500)
    frame = MRsq.frame()
    wsigmc.plotOn(frame,rt.RooFit.MarkerColor(rt.kRed))
    data.plotOn(frame)
    #razPdf.plotOn(frame,rt.RooFit.Normalization(Ntot.getVal()))
    frame.Draw()
    #c.SetLogy()
    c.Print("MRsq.pdf")
