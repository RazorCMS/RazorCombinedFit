import sys, os, pprint, re
from optparse import OptionParser
import ROOT as rt
from array import array

if __name__ == '__main__':

    parser = OptionParser()
    (options,args) = parser.parse_args()
    boxName = args[0]

    masses = array('d',range(150, 800, 25))
    observedLimits = []
    expectedLimits = []
    expectedLimitsp1s = []
    expectedLimitsm1s = []
    expectedLimitsm2s = []
    expectedLimitsp2s = []

    if boxName == "T2tt":
        susy_xsecs = array('d',[80.268,
                                36.7994,
                                18.5245,
                                9.90959,
                                5.57596,
                                3.2781,
                                1.99608,
                                1.25277,
                                0.807323,
                                0.531443,
                                0.35683,
                                0.243755,
                                0.169688,
                                0.119275,
                                0.0855847,
                                0.0618641,
                                0.0452067,
                                0.0333988,
                                0.0248009,
                                0.0185257,
                                0.0139566,
                                0.0106123,
                                0.0081141,
                                0.00623244,
                                0.00480639,
                                0.00372717])

    elif boxName == "T1tttt":
        susy_xsecs = array('d', [])
    susy_xsecs_dict = dict(zip(masses, susy_xsecs))
    sideband = 'FULL'
    # njets = '_4jets'
    njets = '_gt6'
    model = 'T2tt'
    outfile = rt.TFile.Open('asymptoticFile.root','RECREATE')
    xsecUL_ExpMinus2 = rt.TH1F("xsecUL_ExpMinus2_%s_%s"%(model,boxName),"xsecUL_ExpMinus2_%s_%s"%(model,boxName),26, 150,800)
    xsecUL_ExpMinus = rt.TH1F("xsecUL_ExpMinus_%s_%s"%(model,boxName),"xsecUL_ExpMinus_%s_%s"%(model,boxName),26, 150,800)
    xsecUL_Exp = rt.TH1F("xsecUL_Exp_%s_%s"%(model,boxName),"xsecUL_Exp_%s_%s"%(model,boxName),26, 150,800)
    xsecUL_ExpPlus = rt.TH1F("xsecUL_ExpPlus_%s_%s"%(model,boxName),"xsecUL_ExpPlus_%s_%s"%(model,boxName),26, 150,800)
    xsecUL_ExpPlus2 = rt.TH1F("xsecUL_ExpPlus2_%s_%s"%(model,boxName),"xsecUL_ExpPlus2_%s_%s"%(model,boxName),26, 150,800)


    for mass in range(150, 800, 25):

        file = rt.TFile("combine_files%s_%s/higgsCombineT2tt_%s_25_%s%s.Asymptotic.mH120.root"%(njets, boxName, mass, boxName, njets))

        print file

       # file       = rt.TFile("combineCards_25_%s/higgsCombineT2tt_%s_%s_25.Asymptotic.mH120.root"%(sideband, boxName, mass))
        tree = file.Get("limit")
        tree.Draw(">>elist", "", "entrylist")
        # tree.Draw(">>elist")

        if tree.GetEntries() < 6:
            continue
        elist = rt.gDirectory.Get('elist')
        count = 0
        while True:
            entry = elist.Next()
            if entry == -1:
                break
            tree.GetEntry(entry)
            if count == 0:
                expectedLimitsm2s.append(tree.limit*susy_xsecs_dict[mass])
                xsecUL_ExpMinus2.Fill(mass,tree.limit*susy_xsecs_dict[mass]/1000.)
            if count == 1:
                expectedLimitsm1s.append(tree.limit*susy_xsecs_dict[mass])
                xsecUL_ExpMinus.Fill(mass,tree.limit*susy_xsecs_dict[mass]/1000.)
            if count == 2:
                expectedLimits.append(tree.limit*susy_xsecs_dict[mass])
                xsecUL_Exp.Fill(mass,tree.limit*susy_xsecs_dict[mass]/1000.)
            if count == 3:
                expectedLimitsp1s.append(tree.limit*susy_xsecs_dict[mass])
                xsecUL_ExpPlus.Fill(mass,tree.limit*susy_xsecs_dict[mass]/1000.)
            if count == 4:
                expectedLimitsp2s.append(tree.limit*susy_xsecs_dict[mass])
                xsecUL_ExpPlus2.Fill(mass,tree.limit*susy_xsecs_dict[mass]/1000.)
            if count == 5:
                observedLimits.append(tree.limit*susy_xsecs_dict[mass])
            count += 1

    outfile.Write()
    outfile.Close()

    observedLimits = array('d', observedLimits)
    observedLimit_plot = rt.TGraph(len(masses), masses, observedLimits)
    observedLimit_plot.SetLineColor(rt.kRed)
    observedLimit_plot.SetLineWidth(3)

    expectedLimits = array('d', expectedLimits)
    expectedLimit_plot = rt.TGraph(len(masses), masses, expectedLimits)
    expectedLimit_plot.SetLineWidth(3)
    expectedLimit_plot.SetLineStyle(rt.kDashed)

    expectedLimits = array('d', expectedLimits)
    emasses = array('d', [0.]*len(masses))

    expectedLimitsm1s = array('d', [ a - b for a,b in zip(expectedLimits, expectedLimitsm1s) ])
    expectedLimitsp1s = array('d', [ a - b for a,b in zip(expectedLimitsp1s, expectedLimits) ])
    expectedLimit1s_plot = rt.TGraphAsymmErrors(len(masses), masses, expectedLimits, emasses , emasses, expectedLimitsm1s, expectedLimitsp1s  )
    expectedLimit1s_plot.SetFillColor(rt.kGreen)
    #expectedLimit1s_plot.SetFillStyle(3005)
    expectedLimit1s_plot.SetMinimum(0.0001)

    expectedLimitsm2s = array('d', [ a - b for a,b in zip(expectedLimits, expectedLimitsm2s) ])
    expectedLimitsp2s = array('d', [ a - b for a,b in zip(expectedLimitsp2s, expectedLimits) ])
    expectedLimit2s_plot = rt.TGraphAsymmErrors(len(masses), masses, expectedLimits, emasses , emasses, expectedLimitsm2s, expectedLimitsp2s  )
    expectedLimit2s_plot.SetFillColor(rt.kYellow)
    #expectedLimit2s_plot.SetFillStyle(3005)
    expectedLimit2s_plot.SetMinimum(0.0001)


    susy_limit = rt.TGraph(len(masses),masses,susy_xsecs)
    susy_limit.SetMarkerStyle(24)
    susy_limit.SetLineColor(rt.kBlue)
    susy_limit.SetLineWidth(3)

    final_plot = rt.TMultiGraph()
    final_plot.Add(expectedLimit2s_plot)
    final_plot.Add(expectedLimit1s_plot)
    final_plot.Add(observedLimit_plot,"L")
    final_plot.Add(expectedLimit_plot,"L")
    final_plot.Add(susy_limit,"L")
    final_plot.SetMinimum(0.0001)
    # final_plot.SetTitle("Toy based limit, T2tt(mLSP=25GeV), %s, 3D fit;mStop(GeV);upper xsec"%boxName)
    final_plot.SetTitle("Asymptotic limit, T2tt(mLSP=25GeV), %s, 3D fit;mStop(GeV);upper xsec"%boxName)
    c = rt.TCanvas("c")
    c.SetLogy()
    final_plot.Draw("a4")

    leg = rt.TLegend(0.6,0.65,0.899,0.89)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    #leg.SetHeader("The Legend Title")
    leg.AddEntry(expectedLimit1s_plot,"expected +/- 1 #sigma","f")
    leg.AddEntry(expectedLimit2s_plot,"expected +/- 2 #sigma","f")
    leg.AddEntry(expectedLimit_plot,"expected","l")
    leg.AddEntry(observedLimit_plot,"observed","l")
    leg.AddEntry(susy_limit,"susy xsection","l")
    leg.Draw("SAME")



    boxName = re.sub(' ', '', boxName)
    c.SaveAs("limitToyFromAsym"+boxName+sideband+njets+".png")
