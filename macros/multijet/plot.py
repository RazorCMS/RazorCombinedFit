#! /usr/bin/env python

import ROOT as rt
import os.path
import sys, glob, re
from array import *

def file_key(filename):
    #massPoint = re.findall("[0-9]+.000000",filename)
    massPoint = re.findall("[0-9]+.0",filename)
    gluinoMass    = massPoint[0]
    LSPMass  = massPoint[1]
    return float(gluinoMass)

def getHybridCLsArrays(directory, LSPmassStrip, Box):
    tfile = rt.TFile.Open("%s/xsecUL_%s.root"%(directory,Box))
    print "%s/xsecUL_%s.root"%(directory,Box)
    xsecTree = tfile.Get("xsecTree")
    xsecTree.Draw("")
    gluinoMassArray = array('d')
    gluinoMassArray_er = array('d')
    observedLimit = array('d')
    observedLimit_er = array('d')
    expectedLimit = array('d')
    expectedLimit_minus1sigma = array('d')
    expectedLimit_plus1sigma = array('d')
    expectedLimit_minus2sigma = array('d')
    expectedLimit_plus2sigma = array('d')

    
    xsecTree.Draw('>>elist',' mchi==%f'%(float(LSPmassStrip)),'entrylist')

    elist = rt.gDirectory.Get('elist')
    entry = -1
    while True:
        entry = elist.Next()
        if entry == -1: break
        xsecTree.GetEntry(entry)

        gluinoMassArray.append(xsecTree.mg)
        gluinoMassArray_er.append(0.0)
        exec 'xsecULObs = xsecTree.xsecULObs_%s'%Box
        exec 'xsecULExp = xsecTree.xsecULExp_%s'%Box
        exec 'xsecULExpPlus = xsecTree.xsecULExpPlus_%s'%Box
        exec 'xsecULExpMinus = xsecTree.xsecULExpMinus_%s'%Box
        
        observedLimit.append(xsecULObs)#*crossSections[i])
        observedLimit_er.append(0.0)#*crossSections[i])
        
        expectedLimit.append(xsecULExp)#*crossSections[i])
        expectedLimit_minus1sigma.append(xsecULExp - xsecULExpMinus)#*crossSections[i])
        expectedLimit_plus1sigma.append(xsecULExpPlus - xsecULExp)#*crossSections[i])
        expectedLimit_minus2sigma.append(xsecULExp - xsecULExpMinus)#*crossSections[i])
        expectedLimit_plus2sigma.append(xsecULExpPlus - xsecULExp)#*crossSections[i])  

    return gluinoMassArray, gluinoMassArray_er, observedLimit, observedLimit_er, expectedLimit, expectedLimit_minus1sigma, expectedLimit_plus1sigma, expectedLimit_minus2sigma, expectedLimit_plus2sigma


def getAsymptoticCLsArrays(directory, LSPmassStrip, box):
    gluinoMassArray = array('d')
    gluinoMassArray_er = array('d')
    observedLimit = array('d')
    observedLimit_er = array('d')
    expectedLimit = array('d')
    expectedLimit_minus1sigma = array('d')
    expectedLimit_plus1sigma = array('d')
    expectedLimit_minus2sigma = array('d')
    expectedLimit_plus2sigma = array('d')
    
    i=0
    for filename in sorted(glob.glob(directory+'/Asym*'),key=file_key):
        massPoint = re.findall("[0-9]+.000000",filename)
        gluinoMass    = massPoint[0]
        LSPMass  = massPoint[1]
        print "LSP mass = %s, gluino mass = %s"%(LSPMass,gluinoMass)
        
        if not(float(LSPMass) == float(LSPmassStrip)) :
            continue
        if filename.find("_%s_"%box)==-1:
            continue

        tfile = rt.TFile(filename)
        result_sigma = tfile.Get("result_sigma")

        expected_med          = result_sigma.GetExpectedUpperLimit(0)
        expected_minus1sigma  = result_sigma.GetExpectedUpperLimit(-1)
        expected_plus1sigma   = result_sigma.GetExpectedUpperLimit(1)
        expected_minus2sigma  = result_sigma.GetExpectedUpperLimit(-2)
        expected_plus2sigma   = result_sigma.GetExpectedUpperLimit(2)
      
        observed_high    = result_sigma.UpperLimit()
        observed_high_er = result_sigma.UpperLimitEstimatedError()

        gluinoMassArray.append(float(gluinoMass))
        gluinoMassArray_er.append(0.0)
        
        observedLimit.append(float(observed_high))#*crossSections[i])
        observedLimit_er.append(float(observed_high_er))#*crossSections[i])
        
        expectedLimit.append(float(expected_med))#*crossSections[i])
        expectedLimit_minus1sigma.append(float(expected_med - expected_minus1sigma))#*crossSections[i])
        expectedLimit_plus1sigma.append(float(expected_plus1sigma - expected_med ))#*crossSections[i])
        expectedLimit_minus2sigma.append(float( expected_med - expected_minus2sigma))#*crossSections[i])
        expectedLimit_plus2sigma.append(float(expected_plus2sigma - expected_med ))#*crossSections[i])
        i+=1

    return gluinoMassArray, gluinoMassArray_er, observedLimit, observedLimit_er, expectedLimit, expectedLimit_minus1sigma, expectedLimit_plus1sigma, expectedLimit_minus2sigma, expectedLimit_plus2sigma
    
def setstyle():
    # For the canvas:
    rt.gStyle.SetCanvasBorderMode(0)
    rt.gStyle.SetCanvasColor(rt.kWhite)
    rt.gStyle.SetCanvasDefH(400) #Height of canvas
    rt.gStyle.SetCanvasDefW(600) #Width of canvas
    rt.gStyle.SetCanvasDefX(0)   #POsition on screen
    rt.gStyle.SetCanvasDefY(0)
    
    # For the Pad:
    rt.gStyle.SetPadBorderMode(0)
    # rt.gStyle.SetPadBorderSize(Width_t size = 1)
    rt.gStyle.SetPadColor(rt.kWhite)
    rt.gStyle.SetPadGridX(False)
    rt.gStyle.SetPadGridY(False)
    rt.gStyle.SetGridColor(0)
    rt.gStyle.SetGridStyle(3)
    rt.gStyle.SetGridWidth(1)
    
    # For the frame:
    rt.gStyle.SetFrameBorderMode(0)
    rt.gStyle.SetFrameBorderSize(1)
    rt.gStyle.SetFrameFillColor(0)
    rt.gStyle.SetFrameFillStyle(0)
    rt.gStyle.SetFrameLineColor(1)
    rt.gStyle.SetFrameLineStyle(1)
    rt.gStyle.SetFrameLineWidth(1)
    
    # set the paper & margin sizes
    rt.gStyle.SetPaperSize(20,26)
    rt.gStyle.SetPadTopMargin(0.09)
    rt.gStyle.SetPadRightMargin(0.065)
    rt.gStyle.SetPadBottomMargin(0.15)
    rt.gStyle.SetPadLeftMargin(0.17)
    
    # use large Times-Roman fonts
    rt.gStyle.SetTitleFont(132,"xyz")  # set the all 3 axes title font
    rt.gStyle.SetTitleFont(132," ")    # set the pad title font
    rt.gStyle.SetTitleSize(0.06,"xyz") # set the 3 axes title size
    rt.gStyle.SetTitleSize(0.06," ")   # set the pad title size
    rt.gStyle.SetLabelFont(132,"xyz")
    rt.gStyle.SetLabelSize(0.05,"xyz")
    rt.gStyle.SetLabelColor(1,"xyz")
    rt.gStyle.SetTextFont(132)
    rt.gStyle.SetTextSize(0.08)
    rt.gStyle.SetStatFont(132)
    
    # use bold lines and markers
    rt.gStyle.SetMarkerStyle(8)
    rt.gStyle.SetLineStyleString(2,"[12 12]") # postscript dashes
    
    #..Get rid of X error bars
    rt.gStyle.SetErrorX(0.001)
    
    # do not display any of the standard histogram decorations
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptFit(11111111)
    
    # put tick marks on top and RHS of plots
    rt.gStyle.SetPadTickX(1)
    rt.gStyle.SetPadTickY(1)
    
    ncontours = 999
    
    stops = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
    red =   [ 1.0,   0.95,  0.95,  0.65,   0.15 ]
    green = [ 1.0,  0.85, 0.7, 0.5,  0.3 ]
    blue =  [ 0.95, 0.6 , 0.3,  0.45, 0.65 ]
    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)
        
    npoints = len(s)
    rt.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    rt.gStyle.SetNumberContours(ncontours)
   
    rt.gStyle.cd()
        

if __name__ == '__main__':
    directory      = sys.argv[1]
    LSPmassStrip   = sys.argv[2]
    box = sys.argv[3]
    box = box.lower()

    if box.lower() == "tautaujet":
        Box = "TauTauJet"
    elif box.lower() == "multijet":
        Box = "MultiJet"
    elif box.lower() == "jet":
        Box = "Jet"
    elif box.lower() == "all" and directory.lower().find("notau"):
        Box = "Jet+MultiJet"
    elif box.lower() == "all":
        Box = "Jet+TauTauJet+MultiJet"
    elif box.lower() == "had":
        Box = "Had"
    elif box.lower() == "lep":
        Box = "Lep"
    elif box.lower() == 'bjeths':
        Box = "BJetHS"

    if Box == "Lep" or Box == "Had" or Box == "BJetHS":
        rootFile = rt.TFile.Open(directory+"/stop.root")
        h_xsec = rootFile.Get("stop")
    else:
        rootFile = rt.TFile.Open(directory+"/gluino.root")
        h_xsec = rootFile.Get("gluino")

    N_xsec = h_xsec.GetNbinsX();
    mass_xsec = array('d')
    sig_xsec = array('d')
    sig_xsec_up = array('d')
    sig_xsec_down = array('d')
    sig_xsec_err = array('d')

    for i in range(0,N_xsec):
        if h_xsec.GetBinContent(i+1) <= 0.0: continue;
        mass_xsec.append(h_xsec.GetXaxis().GetBinCenter(i+1))
        sig_xsec.append(h_xsec.GetBinContent(i+1))
        sig_xsec_up.append(h_xsec.GetBinContent(i+1)+h_xsec.GetBinError(i+1));
        sig_xsec_down.append(h_xsec.GetBinContent(i+1)-h_xsec.GetBinError(i+1))
        sig_xsec_err.append(h_xsec.GetBinError(i+1))
        
    X_xsec = array('d')
    Y_xsec = array('d')
    X_xsec_up = array('d')
    Y_xsec_up = array('d')
    X_xsec_down = array('d')
    Y_xsec_down = array('d')
    X_xsec_err  = array('d')
    Y_xsec_err = array('d')

    N_g_xsec = len(mass_xsec)
    for i in range(0,N_g_xsec):
        X_xsec.append(mass_xsec[i])
        Y_xsec.append(sig_xsec[i])
        X_xsec_up.append(mass_xsec[i])
        Y_xsec_up.append(sig_xsec_up[i])
        X_xsec_down.append(mass_xsec[i])
        Y_xsec_down.append(sig_xsec_down[i])
        X_xsec_err.append(0)
        Y_xsec_err.append(sig_xsec_err[i])

    setstyle()
    c = rt.TCanvas("c")
    c.SetLogy()
    
    xsec_gr_nom = rt.TGraph(N_g_xsec, X_xsec, Y_xsec)
    xsec_gr_nom.SetMarkerSize(0)
    xsec_gr_nom.SetLineWidth(2)
    xsec_gr_nom.SetLineStyle(1)
    xsec_gr_nom.SetLineColor(rt.kOrange)
    
    xsec_gr = rt.TGraphErrors(N_g_xsec, X_xsec, Y_xsec, X_xsec_err, Y_xsec_err)  
    xsec_gr.SetMarkerStyle(23)
    xsec_gr_nom.SetLineWidth(2)
    xsec_gr.SetMarkerSize(0)
    xsec_gr.SetLineColor(rt.kOrange)
    xsec_gr.SetFillColor(rt.kBlue-7)

    h_limit = rt.TMultiGraph()
    if Box == "Lep" or Box == "Had":
        h_limit.SetTitle(" ;m_{#tilde{t}} [GeV];95% CL upper limit on #sigma #times BR [pb]")
    else:
        h_limit.SetTitle(" ;m_{#tilde{g}} [GeV];95% CL upper limit on #sigma #times BR [pb]")

    if directory.lower().find("hybrid") !=-1:      
        gluinoMassArray, gluinoMassArray_er, observedLimit, observedLimit_er, expectedLimit, expectedLimit_minus1sigma, expectedLimit_plus1sigma, expectedLimit_minus2sigma, expectedLimit_plus2sigma = getHybridCLsArrays(directory, LSPmassStrip, Box)
    else:
        gluinoMassArray, gluinoMassArray_er, observedLimit, observedLimit_er, expectedLimit, expectedLimit_minus1sigma, expectedLimit_plus1sigma, expectedLimit_minus2sigma, expectedLimit_plus2sigma = getAsymptoticCLsArrays(directory, LSPmassStrip, box)

    rt.gStyle.SetOptStat(0)


    #gluinoMassArray         = array('d')
    #gluinoMassArray_er      = array('d')
    #observedLimit    = array('d')
    #observedLimit_er = array('d')
    #expectedLimit    = array('d')
    #expectedLimit_minus2sigma = array('d')
    #expectedLimit_minus1sigma = array('d')
    #expectedLimit_plus1sigma  = array('d')
    #expectedLimit_plus2sigma  = array('d')

    ##i=0
    ###for filename in glob.glob(directory+'/*/Asym*'):
    ##for filename in sorted(glob.glob(directory+'/Asym*'),key=file_key):
    ##    #massPoint = re.findall("[0-9]+.000000",filename)
    ##    massPoint = re.findall("[0-9]+.0",filename)
    ##    gluinoMass    = massPoint[0]
    ##    LSPMass  = massPoint[1]
    ##    print "LSP mass = %s, gluino mass = %s"%(LSPMass,gluinoMass)
    ##    #sys.exit()
    ##    if not(float(LSPMass) == float(LSPmassStrip)) :
    ##        continue
    ##    if filename.find("_%s_"%box)==-1:
    ##        continue

    ##    print filename
    ##    file = rt.TFile(filename)
    ##    result_sigma = file.Get("result_sigma")

    ##    expected_med          = result_sigma.GetExpectedUpperLimit(0)
    ##    expected_minus1sigma  = result_sigma.GetExpectedUpperLimit(-1)
    ##    expected_plus1sigma   = result_sigma.GetExpectedUpperLimit(1)
    ##    expected_minus2sigma  = result_sigma.GetExpectedUpperLimit(-2)
    ##    expected_plus2sigma   = result_sigma.GetExpectedUpperLimit(2)
      
    ##    observed_high    = result_sigma.UpperLimit()
    ##    observed_high_er = result_sigma.UpperLimitEstimatedError()

    ##    gluinoMassArray.append(float(gluinoMass))
    ##    gluinoMassArray_er.append(0.0)
        
    ##    observedLimit.append(float(observed_high))
    ##    observedLimit_er.append(float(observed_high_er))
        
    ##    expectedLimit.append(float(expected_med))
    ##    expectedLimit_minus1sigma.append(float(expected_med - expected_minus1sigma))
    ##    expectedLimit_plus1sigma.append(float(expected_plus1sigma - expected_med ))
    ##    expectedLimit_minus2sigma.append(float( expected_med - expected_minus2sigma))
    ##    expectedLimit_plus2sigma.append(float(expected_plus2sigma - expected_med ))
    ##    i+=1
     
    rt.gStyle.SetOptStat(0)
    j = 0
    while j < len(observedLimit):
        if (j>1 and j<len(observedLimit)-1 and observedLimit[j]>2*observedLimit[j+1] and observedLimit[j]>2*observedLimit[j-1]):
            gluinoMassArray.pop(j)
            gluinoMassArray_er.pop(j)
            observedLimit.pop(j)
            expectedLimit.pop(j)
            expectedLimit_minus2sigma.pop(j)
            expectedLimit_plus2sigma.pop(j)
            expectedLimit_minus1sigma.pop(j)
            expectedLimit_plus1sigma.pop(j)
            print gluinoMassArray
        j+=1
        
    nPoints = len(observedLimit)
    gr_observedLimit = rt.TGraph(nPoints, gluinoMassArray, observedLimit)
    gr_observedLimit.SetMarkerColor(1)
    gr_observedLimit.SetMarkerStyle(22)
    gr_observedLimit.SetMarkerSize(1)
    gr_observedLimit.SetLineWidth(3)
    gr_observedLimit.SetLineColor(rt.kBlack)


    gr_expectedLimit = rt.TGraph(nPoints, gluinoMassArray, expectedLimit)
    gr_expectedLimit.SetLineWidth(3)
    gr_expectedLimit.SetLineStyle(2)
   
    gr_expectedLimit2sigma = rt.TGraphAsymmErrors(nPoints, gluinoMassArray, expectedLimit, gluinoMassArray_er, gluinoMassArray_er, expectedLimit_minus2sigma, expectedLimit_plus2sigma)
    gr_expectedLimit2sigma.SetLineColor(5)
    gr_expectedLimit2sigma.SetFillColor(5)
    gr_expectedLimit2sigma.SetFillStyle(1001)
   
    gr_expectedLimit1sigma = rt.TGraphAsymmErrors(nPoints, gluinoMassArray, expectedLimit, gluinoMassArray_er, gluinoMassArray_er, expectedLimit_minus1sigma, expectedLimit_plus1sigma)
    
    col1 = rt.gROOT.GetColor(rt.kGreen-7)
    col1.SetAlpha(0.5)
    gr_expectedLimit1sigma.SetLineColor(rt.kGreen-7)
    gr_expectedLimit1sigma.SetFillColor(rt.kGreen-7)
    gr_expectedLimit1sigma.SetFillStyle(3001)

    if box.lower() == "all" or box.lower() == "multijet" or box.lower() == "lep" or box.lower() == "had" or box.lower() == 'bjeths':
        h_limit.SetMaximum(30)
    else:
        h_limit.SetMaximum(10)
        
    if box.lower() == "all" or box.lower() == "multijet" or box.lower() == "lep" or box.lower() == "had" or box.lower() == 'bjeths':
        h_limit.SetMinimum(3e-4)
    else:
        h_limit.SetMinimum(1e-4)
    h_limit.Add(gr_expectedLimit2sigma)
    h_limit.Add(gr_expectedLimit1sigma)
    h_limit.Add(gr_observedLimit)
    h_limit.Add(xsec_gr)
    h_limit.Add(xsec_gr_nom)
    h_limit.Draw("a3")
    if Box == "Had" or Box == "Lep" or Box == "BJetHS":
        h_limit.GetXaxis().SetLimits(225,825)
    elif float(LSPmassStrip)==100.:
        h_limit.GetXaxis().SetLimits(625,1925)
    elif float(LSPmassStrip)==0.:
        h_limit.GetXaxis().SetLimits(525,1925)
    print h_limit.GetXaxis().GetXmin(), h_limit.GetXaxis().GetXmax()
    gr_expectedLimit.Draw("c same")
    xsec_gr_nom.Draw("c same")
    gr_observedLimit.Draw("c SAME")

    
    l = rt.TLatex()
    l.SetTextAlign(12)
    l.SetTextSize(0.05)
    l.SetTextFont(132)
    l.SetNDC()
    l.DrawLatex(0.32,0.85,"CMS Preliminary");
    l.DrawLatex(0.55,0.85,"#sqrt{s} = 8 TeV    #int L dt = 19.3 fb^{-1}")

    if Box == "Lep" or Box == "Had" or Box == "BJetHS":
        l.DrawLatex(0.34,0.955,"pp#rightarrow#tilde{t}#tilde{t};   #tilde{t}#rightarrowt#tilde{#chi}^{0}_{1};   m_{#tilde{#chi}} = %.0f GeV"%float(LSPmassStrip))
        l.SetTextColor(rt.kBlue+2)
        l.DrawLatex(0.55,0.785,"Razor MultiJet")
    else:
        l.DrawLatex(0.34,0.955,"pp#rightarrow#tilde{g}#tilde{g};   #tilde{g}#rightarrowbb#tilde{#chi}^{0};   m_{#tilde{#chi}} = %.0f GeV"%float(LSPmassStrip))    
        l.DrawLatex(0.55,0.719,"%s #geq 1b-tag"%Box)
        l.SetTextColor(rt.kBlue+2)
        l.DrawLatex(0.55,0.785,"Razor Inclusive")
        

    leg = rt.TLegend(0.55,0.45,0.9,0.67)
    leg.SetTextFont(132)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    if Box == "Lep" or Box == "Had" or Box == "BJetHS":
        leg.AddEntry(xsec_gr, "#sigma_{NLO+NLL} (#tilde{t}#tilde{t})","lf")
    else:
        leg.AddEntry(xsec_gr, "#sigma_{NLO+NLL} (#tilde{g}#tilde{g})","lf")
    leg.AddEntry(gr_observedLimit, "observed limit","l")
    leg.AddEntry(gr_expectedLimit, "expected limit","l")
    leg.AddEntry(gr_expectedLimit1sigma, "expected limit #pm 1 #sigma","f")
    leg.AddEntry(gr_expectedLimit2sigma, "expected limit #pm 2 #sigma","f")
#    leg.Draw("SAME")

    c.SaveAs(directory+"/limits_LSPMass_"+re.sub('\.','_',LSPmassStrip)+"_"+box+".pdf")
