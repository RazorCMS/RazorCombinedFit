#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
import sys, glob, re
from array import *
import pickle

if __name__ == '__main__':
    directory      = sys.argv[1]
    LSPmassStrip   = sys.argv[2]

    rootFile = rt.TFile.Open("SMS_XSECS.root")
    h_xsec = rootFile.Get("stop_xsec")
    h_xsec_unc = rootFile.Get("stop_xsec_unc")

    N_xsec = h_xsec.GetNbinsX();
    mass_xsec = array('d')
    sig_xsec = array('d')

    for i in range(0,N_xsec):
        if h_xsec.GetBinContent(i+1) <= 0.0: continue;
        mass_xsec.append(h_xsec.GetXaxis().GetBinCenter(i+1))
        sig_xsec.append(h_xsec.GetBinContent(i+1))
        #sig_xsec_up.push_back(h_xsec->GetBinContent(i+1)*(1.+0.01*h_xsec_unc->GetBinContent(i+1)));
        #sig_xsec_down.push_back(h_xsec->GetBinContent(i+1)*(1.-0.01*h_xsec_unc->GetBinContent(i+1)));

    X_xsec = array('d')
    Y_xsec = array('d')

    N_g_xsec = len(mass_xsec)
    for i in range(0,N_g_xsec):
        X_xsec.append(mass_xsec[i])
        Y_xsec.append(sig_xsec[i])

    c = rt.TCanvas("c")
    c.SetLogy()

    xsec_gr = rt.TGraph(N_g_xsec, X_xsec, Y_xsec)
    xsec_gr.SetMarkerStyle(23)
    xsec_gr.SetMarkerSize(0)
    xsec_gr.SetLineWidth(3)
    xsec_gr.SetLineStyle(7)
    xsec_gr.SetFillColor(0)
    xsec_gr.SetLineColor(1)
    #xsec_gr.Draw("ACP");
    xsec_gr.Draw("CP");

    crossSections = [ 18.5245 , 5.57596 ,1.99608, 0.807323, 0.35683, 0.169668, 0.0855847, 0.0452067, 0.0248009, 0.0139566, 0.0081141, 0.00480639,0.00289588] 
    #cross_sections_er [ 14.9147,  14.7529, 14.6905, 14.3597%  , 14.2848%,  14.2368% ,14.9611%,  15.8177% ,  16.6406%,  17.56% ,18.4146%,   19.4088% ,  20.516%]    

    h_limit = rt.TMultiGraph()
    h_limit.SetTitle("Asymptotic CL scan, limits for MLSP = "+LSPmassStrip +"GeV;stop mass (GeV);95% CL upper limit on #sigma x BR [pb] ")

    stopMass         = array('d')
    stopMass_er      = array('d')
    observedLimit    = array('d')
    observedLimit_er = array('d')
    expectedLimit    = array('d')
    expectedLimit_minus2sigma = array('d')
    expectedLimit_minus1sigma = array('d')
    expectedLimit_plus1sigma  = array('d')
    expectedLimit_plus2sigma  = array('d')

    i=0
    #for filename in glob.glob(directory+'/*/Asym*'):
    for filename in glob.glob(directory+'/Asym*'):
        massPoint = re.findall("[0-9]+.0",filename)
        sMass    = massPoint[0]
        LSPMass  = massPoint[1]

        if not(float(LSPMass) == float(LSPmassStrip)) :
            continue

        print filename
        file = rt.TFile(filename)
        result_sigma = file.Get("result_sigma")

        expected_med          = result_sigma.GetExpectedUpperLimit(0)
        expected_minus1sigma  = result_sigma.GetExpectedUpperLimit(-1)
        expected_plus1sigma   = result_sigma.GetExpectedUpperLimit(1)
        expected_minus2sigma  = result_sigma.GetExpectedUpperLimit(-2)
        expected_plus2sigma   = result_sigma.GetExpectedUpperLimit(2)
      
        observed_high    = result_sigma.UpperLimit()
        observed_high_er = result_sigma.UpperLimitEstimatedError()

        stopMass.append(float(sMass))
        stopMass_er.append(0.0)
        
        observedLimit.append(float(observed_high))#*crossSections[i])
        observedLimit_er.append(float(observed_high_er))#*crossSections[i])
        
        expectedLimit.append(float(expected_med))#*crossSections[i])
        expectedLimit_minus1sigma.append(float(expected_med - expected_minus1sigma))#*crossSections[i])
        expectedLimit_plus1sigma.append(float(expected_plus1sigma - expected_med ))#*crossSections[i])
        expectedLimit_minus2sigma.append(float( expected_med - expected_minus2sigma))#*crossSections[i])
        expectedLimit_plus2sigma.append(float(expected_plus2sigma - expected_med ))#*crossSections[i])
        i+=1

     
    nPoints = len(stopMass)  
    rt.gStyle.SetOptStat(0)

    gr_observedLimit = rt.TGraphErrors(nPoints, stopMass, observedLimit, stopMass_er,  observedLimit_er)
    gr_observedLimit.SetMarkerColor(1)
    gr_observedLimit.SetMarkerStyle(22)
    gr_observedLimit.SetMarkerSize(1)
  
    gr_expectedLimit1sigma = rt.TGraphAsymmErrors(nPoints, stopMass, expectedLimit, stopMass_er, stopMass_er, expectedLimit_minus2sigma, expectedLimit_plus2sigma)
    gr_expectedLimit1sigma.SetFillColor(5)
    gr_expectedLimit1sigma.SetFillStyle(1001)
   
    gr_expectedLimit2sigma = rt.TGraphAsymmErrors(nPoints, stopMass, expectedLimit, stopMass_er, stopMass_er, expectedLimit_minus1sigma, expectedLimit_plus1sigma)
    gr_expectedLimit2sigma.SetFillColor(8)
    gr_expectedLimit2sigma.SetFillStyle(3001)
    
    h_limit.Add(gr_expectedLimit1sigma)
    h_limit.Add(gr_expectedLimit2sigma)
    
    #xsec_gr.Draw("CP");
    h_limit.Draw("a3 same")
    gr_observedLimit.Draw("P SAME")
    xsec_gr.Draw("CP SAME");

    leg = rt.TLegend(0.6,0.7,0.9,0.9)
    leg.AddEntry(gr_observedLimit, "observed limit","lep")
    leg.AddEntry(gr_expectedLimit1sigma, "expected limit +- 1 #sigma")
    leg.AddEntry(gr_expectedLimit2sigma, "expected limit +- 2 #sigma")
    leg.Draw("SAME")

    c.SaveAs("limits_LSPMass_"+re.sub('\.','_',LSPmassStrip)+"Logy.png")
