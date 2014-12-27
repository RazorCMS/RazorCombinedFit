import ROOT as rt
import os.path
import sys, glob, re
from array import array
from math import sqrt

def binnedHisto2D(tree, binsX, binsY, label='') :

    histo = rt.TH2F("histo"+label, "histo"+label, len(binsX) -1, binsX, len(binsY) -1, binsY)
   
    for i_binx in range(0, len(binsX) - 1):
        for i_biny in range(0, len(binsY) - 1):
        
            binx = binsX[i_binx]
            binx_p1 = binsX[i_binx+1]
            biny = binsY[i_biny]
            biny_p1 = binsY[i_biny+1]
            
            numEntries = (tree.reduce("MR > %s && MR < %s && Rsq > %s && Rsq < %s && nBtag <2"%(binx, binx_p1, biny, biny_p1)).numEntries())
            histo.Fill(binx, biny, numEntries)

    return histo



if __name__ == '__main__':
    rt.gStyle.SetOptStat(0)

    box   = sys.argv[1]
    njets = sys.argv[2]
    
    ########## binning def
    ##MRbins = array('d',[350, 450, 550, 700, 900, 1200, 1600, 2500, 4000])
    ##Rsqbins = array('d',[0.08, 0.10, 0.15, 0.20,0.30,0.41,0.52,0.64,0.80,1.5])

   # MRbins = array('d',[350., 370., 390.,  410.,  430., 450., 470.,  490., 510., 530., 550, 575., 600.,  625., 650.,700.,800.,  900., 1000.,4000.])
   # Rsqbins = array('d',[0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.17,  0.20,  0.23, 0.26, 0.30, 0.35, 0.40, 0.50,   0.7,  1.0,  1.5])
    MRbins = array('d',[350, 390, 450, 510, 600, 700., 900, 1000, 4000])
    Rsqbins = array('d',[0.08, 0.10, 0.15, 0.20,0.30,0.40,0.50,0.7,1.0,1.5])
       
    ###### SAMPLES
    #signal
    if box == 'Ele':
        filename = '/afs/cern.ch/user/l/lucieg/scratch1/Oct18/CMSSW_6_2_0/src/RazorCombinedFit/Datasets/SingleElectron-Run2012ABCD-22Jan2013-v1-SUSY_MR350.0_R0.282842712475_%s_BTAG_%s.root'%(njets, box)
    else :
         filename = '/afs/cern.ch/user/l/lucieg/scratch1/Oct18/CMSSW_6_2_0/src/RazorCombinedFit/Datasets/SingleMu-Run2012ABCD-22Jan2013-v1-SUSY_MR350.0_R0.282842712475_%s_BTAG_%s.root'%(njets, box)

    file = rt.TFile(filename)
    tree = file.Get("RMRTree")
  
    c = rt.TCanvas("plots/RsqMR2D_%s_%s.png"%(box,njets), "RsqMR2D_%s_%s.png"%(box,njets))
        
    c.cd()
    c.SetLogx()
    c.SetLogy()
    histo = binnedHisto2D(tree, MRbins, Rsqbins, '')
    histo.SetTitle("Rsq vs MR, %s box;MR(GeV);Rsq"%(box))
    histo.Draw("colz")
    c.SaveAs(c.GetName())
         
