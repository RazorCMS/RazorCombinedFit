#!/usr/bin/env python

import ROOT as rt

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
    
def calcSig(signal, background):
    
    #S/sqrt(B)
    significance = signal.Clone('%s_significance' % signal.GetName())
    
    xaxis = signal.GetXaxis()
    yaxis = signal.GetYaxis()
    
    for i in xrange(1,xaxis.GetNbins()+1):
        for j in xrange(1,yaxis.GetNbins()+1):
            bin = signal.GetBin(i,j)
            
            S = signal.GetBinContent(bin)
            B = background.GetBinContent(bin)

            sig = 0.0
            if B > 0.0:
                sig = S/rt.TMath.Sqrt(B)
            significance.SetBinContent(bin,sig)

    return significance

if __name__ == '__main__':
    
    pkl = "/afs/cern.ch/user/w/wreece/work/LimitSetting/RazorMultiJet2011/SMS-T2tt_Mstop-225to1200_mLSP-50to1025_7TeV-Pythia6Z-Summer11-PU_START42_V11_FastSim-v1-wreece_030412-ByPoint.pkl"
    import pickle
    norms = pickle.load(file(pkl))    
    
    smsHistos = rt.TFile.Open('sms-histos.root')
    effBJet = smsHistos.Get('effBJet')
    effHad = smsHistos.Get('effHad')
    effLep = smsHistos.Get('effLep')
    
    fitregion = "((((( (MR >= 500.000000) && (MR < 800.000000) ) && ( (RSQ >= 0.030000) && (RSQ < 0.090000) )) || (( (MR >= 500.000000) && (MR < 650.000000) ) && ( (RSQ >= 0.090000) && (RSQ < 0.200000) ))) || (( (MR >= 500.000000) && (MR < 600.000000) ) && ( (RSQ >= 0.200000) && (RSQ < 0.300000) ))) || (( (MR >= 500.000000) && (MR < 550.000000) ) && ( (RSQ >= 0.300000) && (RSQ < 0.500000) ))) || (( (MR >= 800.000000) && (MR < 3000.000000) ) && ( (RSQ >= 0.030000) && (RSQ < 0.037500) ))"

    signal_regions = {}
    signal_regions['sR1'] = '( ( (MR >= 800.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.030000) && (RSQ < 0.090000) ))'
    signal_regions['sR2'] = '( ( (MR >= 650.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.090000) && (RSQ < 0.20000) ))'
    signal_regions['sR3'] = '( ( (MR >= 600.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.20000) && (RSQ < 0.30000) ))'
    signal_regions['sR4'] = '( ( (MR >= 550.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.30000) && (RSQ < 0.50000) ))'   
    signal_regions['sR5'] = '( ( (MR >= 3000.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.030000) && (RSQ < 0.03750000) ))'   
    signal_regions['sR6'] = '( ( (MR >= 500.000000) && (MR < 4000.000000) ) && ( (RSQ >= 0.50000) && (RSQ < 1.00000) ))'  

    limitHistos = rt.TFile.Open('T2tt-plots-0.root')
    limit = limitHistos.Get('Limits')
    
    yieldBJet = effBJet.Clone('yieldBJet')
    yieldBJet.Reset()
    
    yieldHad = effHad.Clone('yieldBVeto')
    yieldHad.Reset()
    
    yieldLep = effLep.Clone('yieldLeptonBVeto')
    yieldLep.Reset()
    
    binningHistos = rt.TFile.Open("sms-binning.root")
    binning = binningHistos.Get("wHisto_BJet_0")
    
    sigTrees = rt.TFile.Open(pkl.replace('.pkl', '.root'))

    data = rt.TFile.Open('../../MultiJet-Run2011A-05Aug2011-v1-wreece_130312_MR500.0_R0.173205080757_BJet.root')
    dataTree = data.Get('RMRTree').reduce('!(%s)' % fitregion.replace('RSQ','Rsq'))
    dataHist = binning.Clone('dataHist')
    for i in xrange(dataTree.numEntries()):
        row = dataTree.get(i)
        dataHist.Fill(row.getRealValue('MR'),row.getRealValue('Rsq'))
    
    lumi = 4980
    def findYields(effHisto, output, verb = False):
        histos = []
        for point in norms:
            eff = getBinContent(effHisto, point[0], point[1])
            xsec = getBinContent(limit, point[0], point[1])
            y = eff*xsec*lumi
            
            if xsec == 0.0:
                continue

            tree = sigTrees.Get('RMRTree_%d_%d' % point)
            frac = tree.Draw("MR",fitregion,"gof")/(1.0*tree.GetEntries())
            setBinContent(output, point[0], point[1], y*(1-frac))

            if verb:
                print point, eff, xsec, lumi, y*(1-frac)

            if verb:
                sigHist = binning.Clone('sig_%d_%d' % point)
                tree.Project('sig_%d_%d' % point, "RSQ:MR", 'LEP_W*W_EFF*(!%s)' % fitregion)
                #scale so the integral is the expected number of signal events 
                print eff,sigHist.Integral(),1-frac
                sigHist.Scale( (y*(1-frac))/sigHist.Integral())
                histos.append(sigHist)
                histos.append(calcSig(sigHist, dataHist))

                regions = {}
                for region in signal_regions:
                    sR = y*(tree.Draw("MR",signal_regions[region],"gof")/(1.0*tree.GetEntries()))
                    regions[region] = sR
                print point, regions


        return histos
            
            
    histos = findYields(effBJet, yieldBJet, verb = True)
    findYields(effHad, yieldHad)
    findYields(effLep, yieldLep)
        
    sms = rt.TFile.Open('sms-yields-significance.root', 'recreate')
    yieldBJet.Write()
    yieldHad.Write()
    yieldLep.Write()
    dataHist.Write()
    for h in histos:
        h.Write()
    sms.Close()
        
        
