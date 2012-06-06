#!/usr/bin/env python

import ROOT as rt

from bayesProb import getLimit

def getBinContent(histo, x, y):
    
    xaxis = histo.GetXaxis()
    yaxis = histo.GetYaxis()
    
    xbin = xaxis.FindBin(x)
    ybin = yaxis.FindBin(y)
    
    bin = histo.GetBin(xbin,ybin)
    
    return histo.GetBinContent(bin)
    
def setBinContent(histo, x, y, val):
    
    xaxis = histo.GetXaxis()
    yaxis = histo.GetYaxis()
    
    xbin = xaxis.FindBin(x)
    ybin = yaxis.FindBin(y)
    
    bin = histo.GetBin(xbin,ybin)
    
    histo.SetBinContent(bin, val)
    
if __name__ == '__main__':
    
    pkl = "/afs/cern.ch/user/w/wreece/work/LimitSetting/RazorMultiJet2011/SMS-T2tt_Mstop-225to1200_mLSP-50to1025_7TeV-Pythia6Z-Summer11-PU_START42_V11_FastSim-v1-wreece_030412-ByPoint.pkl"
    import pickle
    norms = pickle.load(file(pkl))    
    
    smsHistos = rt.TFile.Open('sms-histos.root')
    effBJet = smsHistos.Get('effBJet')

    limitHistos = rt.TFile.Open('T2tt-plots-0.root')
    limit = limitHistos.Get('Limits')

    bayes = limit.Clone('bayes')
    bayes.Reset()

    bayesR = limit.Clone('bayesR')
    bayesR.Reset()

    signal_regions = {}
    signal_regions['sR5'] = '( ( (MR >= 3000.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.030000) && (RSQ < 0.03750000) ))'   
    signal_regions['sR1'] = '( ( (MR >= 800.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.030000) && (RSQ < 0.090000) ))'
    signal_regions['sR2'] = '( ( (MR >= 650.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.090000) && (RSQ < 0.20000) ))'
    signal_regions['sR3'] = '( ( (MR >= 600.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.20000) && (RSQ < 0.30000) ))'
    signal_regions['sR4'] = '( ( (MR >= 550.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.30000) && (RSQ < 0.50000) ))'   
    signal_regions['sR6'] = '( ( (MR >= 500.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.50000) && (RSQ < 1.00000) ))'  

    binningHistos = rt.TFile.Open("sms-binning.root")
    binning = binningHistos.Get("wHisto_BJet_0")

    sigTrees = rt.TFile.Open(pkl.replace('.pkl', '.root'))
    for point in norms:
        eff = getBinContent(effBJet, point[0], point[1])
        xsec = getBinContent(limit, point[0], point[1])

        tree = sigTrees.Get('RMRTree_%d_%d' % point)

        regions = {}
        for region in signal_regions:
            sigHist = binning.Clone('sig_%d_%d' % point)
            sigHist.Reset()
            tree.Project('sig_%d_%d' % point, "RSQ:MR", 'LEP_W*W_EFF*( (BOX_NUM==6) && (%s) )' % signal_regions[region])
            sR = sigHist.Integral()
            #sR = (tree.Draw("MR:RSQ",'(BOX_NUM == 6) && (LEP_W*W_EFF*(%s))' % signal_regions[region],"gof")/(1.0*tree.GetEntries()))
            regions[region] = sR
        print point, regions, sum(regions.values()), eff
        sigeff = [regions['sR5'], regions['sR1'], regions['sR2'], regions['sR3'], regions['sR4'], regions['sR6']] 
        
        blimit = getLimit(sigeff,'tmp.root')
        setBinContent(bayes, point[0], point[1], blimit)
        setBinContent(bayesR, point[0], point[1], blimit/xsec)
        print point, blimit, xsec, blimit/xsec

        #break
        

    outputFile = rt.TFile.Open('BayseLimit.root','recreate')
    limit.Write()
    bayes.Write()
    bayesR.Write()
    outputFile.Close()
