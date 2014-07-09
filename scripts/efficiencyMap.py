"""Macro to make efficiency plots"""
#! /usr/bin/env python

import ROOT as rt
import os.path
import sys, re


if __name__ == '__main__':
    rt.gStyle.SetOptStat(0)

    # BOX = sys.argv[1]
    MODEL = sys.argv[1]
    DIRECTORY = sys.argv[2]
    BOXES = ['BJetHS', 'BJetLS']

    EFF_HISTOS = {}

    for box in BOXES:
        if MODEL == 'T1tttt':
            EFF_HISTOS[box] = rt.TH2D(MODEL + "_" + box, MODEL + "_" + box,
                                      41, 400, 1425, 56, 0, 1400)
        elif MODEL == 'T2tt':
            EFF_HISTOS[box] = rt.TH2D(MODEL + "_" + box, MODEL + "_" + box,
                                      27, 150, 825, 29, 0, 725)

        # efficiencyMap = rt.TH2F("effMap", "efficiency map for " + BOX,
                                  # 32, 0., 800.,
        #                         4, 0., 100.)
        #                         # 32, 0., 800.)

        for mLSP in range(25, 725, 25):
            DIR = DIRECTORY+'/mLSP'+str(mLSP)+'/'

            for filename in os.listdir(DIR):
                print filename
                BOX_result = re.search(str(box), str(filename))

                if BOX_result:
                    IN_file = rt.TFile.Open(DIR+'/'+filename)
                    massPoint = re.findall("[0-9]+.0_[0-9]+.0", filename)
                    mStop, mLSP = re.split("_", massPoint[0])
                    wHisto = IN_file.Get("wHisto")
                    eff = wHisto.Integral()
                    #print massPoint, eff
                    EFF_HISTOS[box].Fill(float(mStop), float(mLSP), eff)
                    wHisto.Delete()
                    IN_file.Close()
                    IN_file.Delete()

    OUT_FILE = rt.TFile.Open(MODEL + "_EffHistos.root", 'recreate')
    for box in BOXES:
        EFF_HISTOS[box].Write()
    OUT_FILE.Close()

# c = rt.TCanvas("efficiencyMap" + str(box) + ".png")
# efficiencyMap.Draw("colz")
# c.SaveAs(c.GetName())


