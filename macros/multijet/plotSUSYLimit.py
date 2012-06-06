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

    susyNLOThree = limit.Clone('susyNLOThree')
    susyNLOThree.Reset()

    susyNLOThird = limit.Clone('susyNLOThird')
    susyNLOThird.Reset()

    crossSec = rt.TFile.Open('referenceXSecs.root')
    stop = crossSec.Get('stop')

    for point in sorted(norms.keys()):
        #we exclude if xsec is less than th
        xs = getBinContent(limit, point[0], point[1])
        th = getBinContent1D(stop,point[0])

        def changePlot(plot, t, x):
            excluded = (t >= x)
            if True:
                setBinContent(plot, point[0], point[1], t/x)
        changePlot(susyNLO,th,xs)
        changePlot(susyNLOThree,3*th,xs)
        changePlot(susyNLOThird,0.33333*th, xs)

    limitFile = rt.TFile.Open('T2tt-SUSY-limit.root','recreate')
    susyNLO.Write()
    susyNLOThree.Write()
    susyNLOThird.Write()
    limitFile.Close()
