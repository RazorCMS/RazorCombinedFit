#! /usr/bin/env python

import ROOT as rt
import os.path
import sys, re


if __name__ == '__main__':
    rt.gStyle.SetOptStat(0)

    BOX = sys.argv[1]
    DIRECTORY = sys.argv[2]

    efficiencyMap = rt.TH2F("effMap", "efficiency map for " + BOX, 32, 0., 800.,
                            4, 0., 100.)
                            # 32, 0., 800.)

    for mLSP in range(25, 50, 25):  # 725
        DIR = DIRECTORY+'/mLSP'+str(mLSP)+'/'

        for filename in os.listdir(DIR):
            print filename
            BOX_result = re.search(str(BOX), str(filename))

            if BOX_result:
                IN_file = rt.TFile.Open(DIR+'/'+filename)
                massPoint = re.findall("[0-9]+.0_[0-9]+.0", filename)
                mStop, mLSP = re.split("_", massPoint[0])
                wHisto = IN_file.Get("wHisto")
                eff = wHisto.Integral()
                #print massPoint, eff
                efficiencyMap.Fill(float(mStop), float(mLSP), eff)

c = rt.TCanvas("efficiencyMap" + str(BOX) + ".png")
efficiencyMap.Draw("colz")
c.SaveAs(c.GetName())
