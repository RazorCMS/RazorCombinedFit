#!/usr/bin/env python

import ROOT as rt

if __name__ == '__main__':

    pkl = "/afs/cern.ch/user/w/wreece/work/LimitSetting/RazorMultiJet2011/SMS-T2tt_Mstop-225to1200_mLSP-50to1025_7TeV-Pythia6Z-Summer11-PU_START42_V11_FastSim-v1-wreece_030412-ByPoint.pkl"
    import pickle
    norms = pickle.load(file(pkl))

    T1 = rt.TFile.Open('T1.root')
    hT1 = T1.Get('NTOT_PROC0')

    hT2 = hT1.Clone()
    hT2.Reset()

    for point, count in norms.iteritems():
        hT2.Fill(point[0],point[1],count)
    
    T2 = rt.TFile.Open("T2.root",'recreate')
    hT2.Write()
    T2.Close()
