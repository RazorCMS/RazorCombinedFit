#!/usr/bin/env python

import ROOT as rt
import RootTools

def getPlots(fileName, weight, name):
    
    if False:
        fileName = fileName.replace('_Had.root','_nBtag_1_BJet.root')
    
    rsq = rt.TH1D('rsq_%s' % name, name, 10,0,0.5)
    mr = rt.TH1D('mr_%s' % name, name,25,500,3000)
    
    inputFile = rt.TFile.Open(fileName)
    tree = inputFile.Get('RMRTree')
    for i in xrange(tree.numEntries()):
        row = tree.get(i)
        rsq.Fill(row['Rsq'].getVal(),weight)
        mr.Fill(row['MR'].getVal(),weight)
    return (rsq,mr)

if __name__ == '__main__':
    
    RootTools.RazorStyle.setStyle()
    store = RootTools.RootFile.RootFile('razorMJDataMCPlots.root')
    colors = RootTools.RazorStyle.getColorList()
    
    plots = []
    plots.append(getPlots('TTJets_TuneZ2_7TeV-madgraph-tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.062006809,'T#bar{T}+Jets'))
    plots.append(getPlots('WZ_TuneZ2_7TeV_pythia6_tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.020149612,'WZ'))
    plots.append(getPlots('T_TuneZ2_t-channel_7TeV-powheg-tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.050557846,'T t-channel'))
    plots.append(getPlots('T_TuneZ2_s-channel_7TeV-powheg-tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.049174716,'T s-channel'))    
    plots.append(getPlots('T_TuneZ2_tW-channel-DR_7TeV-powheg-tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.030451367,'T tW-channel'))
    plots.append(getPlots('WW_TuneZ2_7TeV_pythia6_tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.049462593,'WW'))
    plots.append(getPlots('ZZ_TuneZ2_7TeV_pythia6_tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.006518777,'ZZ'))
    plots.append(getPlots('Tbar_TuneZ2_s-channel_7TeV-powheg-tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.053878763,'#bar{T} s-channel'))
    plots.append(getPlots('Tbar_TuneZ2_t-channel_7TeV-powheg-tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.052092087,'#bar{T} t-channel'))
    plots.append(getPlots('Tbar_TuneZ2_tW-channel-DR_7TeV-powheg-tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.052092087,'#bar{T} tW-channel'))
    plots.append(getPlots('DYJetsToLL_TuneZ2_M-50_7TeV-madgraph-tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',0.181731478,'DY+Jets'))
    plots.append(getPlots('WJetsToLNu_TuneZ2_7TeV-madgraph-tauola-wreece_110112_MR500.0_R0.173205080757_Had.root',1.296284825,'W+Jets'))        
    plots.append(getPlots('QCD_Pt-80toInf_6GenJets_TuneZ2_7TeV-pythia6-wreece_110112_MR500.0_R0.173205080757_Had.root',36.81047999,'QCD'))
    
    stacks = (rt.THStack('rsq','R^{2}'),rt.THStack('mr','M_{R}'))
    store.add(stacks[0])
    store.add(stacks[1])
    
    leg = rt.TLegend(0.71, 0.5, 0.9, 0.9)
    #leg.SetTextSize(0.05)
    leg.SetLineColor(rt.kWhite)
    leg.SetFillColor(rt.kWhite)
    leg.SetShadowColor(rt.kWhite)
    
    color_index = 0
    for p in plots:

        p[0].SetLineColor(colors[color_index])
        p[0].SetFillColor(colors[color_index])
        p[0].SetMarkerColor(colors[color_index])
        p[1].SetLineColor(colors[color_index])
        p[1].SetFillColor(colors[color_index])
        p[1].SetMarkerColor(colors[color_index])
        
        leg.AddEntry(p[0],p[0].GetTitle())
        
        store.add(p[0])
        store.add(p[1])
        
        stacks[0].Add(p[0])
        stacks[1].Add(p[1])
        
        color_index += 1
        
    data = getPlots('MultiJet-Run2011A-05Aug2011-v1-wreece_130112_MR500.0_R0.173205080757_Had.root',1.,'Data')
    leg.AddEntry(data[0],'Data')
    stacks[0].Add(data[0],'nostackerrors')
    stacks[1].Add(data[1],'nostackerrors')
    store.add(data[0])
    store.add(data[1])
    store.add(leg)

    store.write()
    