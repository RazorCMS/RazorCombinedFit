#!/usr/bin/env python

import ROOT as rt
from plotSigNum import getBinContent, setBinContent

def getBinContent1D(histo, x):
    
    xaxis = histo.GetXaxis()
    xbin = xaxis.FindBin(x)
    
    bin = histo.GetBin(xbin)
    return histo.GetBinContent(bin)

if __name__ == '__main__':

    pkl = "/afs/cern.ch/user/w/wreece/work/LimitSetting/RazorMultiJet2011/SMS-T2tt_Mstop-225to1200_mLSP-50to1025_7TeV-Pythia6Z-Summer11-PU_START42_V11_FastSim-v1-wreece_030412-ByPoint.pkl"
    import pickle
    norms = pickle.load(file(pkl))    
    
    limitHistos = rt.TFile.Open('T2tt-plots-0.root')
    limit = limitHistos.Get('Limits')
    
    susyNLO = limit.Clone('susyNLO')
    susyNLO.Reset()

    crossSec = rt.TFile.Open('referenceXSecs.root')
    stop = crossSec.Get('stop')

    #rt.gROOT.Macro('/Users/wreece/Downloads/SMS_30_04_12/INCL/T2tt/sigma_limit_HAD.C')
    #rt.gROOT.Macro('/Users/wreece/Downloads/SMS_30_04_12/INCL/T2tt/sigma_limit_combined.C')
    #rt.gROOT.Macro('/Users/wreece/Downloads/SMS_30_04_12/BJET/T2tt/sigma_limit_combined.C')
    rt.gROOT.Macro('/Users/wreece/Downloads/SMS_30_04_12/BJET/T2tt/sigma_limit_HAD.C')
    incHad = rt.gDirectory.Get('plot_me_13')

    for point in sorted(norms.keys()):
        #we exclude if xsec is less than th
        xs = getBinContent(limit, point[0], point[1])
        inc = getBinContent(incHad, point[0], point[1])
        th = getBinContent1D(stop,point[0])

        if xs < inc:
            print point, xs, inc, th
            setBinContent(susyNLO, point[0], point[1], xs/inc)
        else:
            setBinContent(susyNLO, point[0], point[1], 1e-4)

    limitFile = rt.TFile.Open('T2tt-Inc-ratio.root','recreate')
    susyNLO.Write()
    limitFile.Close()
