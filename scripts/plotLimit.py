import sys, os, pprint, re
from optparse import OptionParser
import ROOT as rt
from array import array


def get_xsec(model):
    """Return the xsec for a given mass and model"""
    if model == 'T2tt':
        ref_xsec_file = './stop.root'
    elif model == 'T1tttt':
        ref_xsec_file = './gluino.root'

    print "INFO: Input ref xsec file!"
    gluino_file = rt.TFile.Open(ref_xsec_file, "READ")
    gluino_hist_name = ref_xsec_file.split("/")[-1].split(".")[0]
    gluino_hist = gluino_file.Get(gluino_hist_name)

    susy_xsecs_array = array('d', [])
    if model == "T2tt":
        masses = range(150, 800, 25)
    else:
        masses = range(400, 1425, 25)

    for mass in masses:
        susy_xsecs_array.append(1.e3*gluino_hist.GetBinContent(gluino_hist.FindBin(mass)))

    return susy_xsecs_array


if __name__ == '__main__':

    parser = OptionParser()
    (options, args) = parser.parse_args()
    boxName = args[0]
    MODEL = args[1]

    if MODEL == 'T1tttt':
        masses = array('d', [])
        njets = '_gt6'
        for mass in range(400, 1425, 25):
            file = rt.TFile("combine_files%s_%s/higgsCombineT1tttt_%s_25_%s%s.Asymptotic.mH120.root"%(njets, boxName, mass, boxName, njets))
            if not file.Get("limit"):
                continue
            masses.append(mass)
    else:
        masses = array('d', range(150, 800, 25))

    observedLimits = []
    expectedLimits = []
    expectedLimitsp1s = []
    expectedLimitsm1s = []
    expectedLimitsm2s = []
    expectedLimitsp2s = []

    susy_xsecs = get_xsec(MODEL)

    susy_xsecs_dict = dict(zip(masses, susy_xsecs))
    sideband = 'FULL'
    # njets = '_4jets'
    njets = '_gt6'
    # model = 'T2tt'
    model = MODEL
    # outfile = rt.TFile.Open('asymptoticFile_%s_%s.root' % (model, boxName),'RECREATE')
    outfile = rt.TFile.Open('toysFile_%s_%s.root' % (model, boxName),'RECREATE')
    xsecUL_ExpMinus2 = rt.TH1F("xsecUL_ExpMinus2_%s_%s"%(model,boxName),"xsecUL_ExpMinus2_%s_%s"%(model,boxName),26, 150,800)
    xsecUL_ExpMinus = rt.TH1F("xsecUL_ExpMinus_%s_%s"%(model,boxName),"xsecUL_ExpMinus_%s_%s"%(model,boxName),26, 150,800)
    xsecUL_Exp = rt.TH1F("xsecUL_Exp_%s_%s"%(model,boxName),"xsecUL_Exp_%s_%s"%(model,boxName),26, 150,800)
    xsecUL_ExpPlus = rt.TH1F("xsecUL_ExpPlus_%s_%s"%(model,boxName),"xsecUL_ExpPlus_%s_%s"%(model,boxName),26, 150,800)
    xsecUL_ExpPlus2 = rt.TH1F("xsecUL_ExpPlus2_%s_%s"%(model,boxName),"xsecUL_ExpPlus2_%s_%s"%(model,boxName),26, 150,800)


    # for mass in range(150, 800, 25):
    for mass in range(300, 625, 25):
    # for mass in range(400, 1425, 25):

        ## Asymptotic
        # file = rt.TFile("combine_files%s_%s/higgsCombineT1tttt_%s_25_%s%s"
        #                 ".Asymptotic.mH120.root" %\
        #                 (njets, boxName, mass, boxName, njets))

        ## Toys
        file = rt.TFile("Combine/T2tt/step2/mLSP25/higgsCombineToys%s_%s"
                        ".0_25.0_FULL_%s_0.HybridNew.mH120.root" %\
                        (model, mass, boxName))

        # file = rt.TFile("combineCards_25/higgsCombineT2tt_All_%s_25.Asymptotic.mH120.root"%str(mass))
        if not file.Get("limit"):
            continue


        print file

       # file       = rt.TFile("combineCards_25_%s/higgsCombineT2tt_%s_%s_25.Asymptotic.mH120.root"%(sideband, boxName, mass))
        tree = file.Get("limit")

        tree.Draw(">>elist", "", "entrylist")
        # tree.Draw(">>elist")

        if tree.GetEntries() < 6:
            print "Wait, we'got less than 6 entries in this tree"
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
    if model == "T1tttt":
        expectedLimit1s_plot.SetMinimum(10)

    expectedLimitsm2s = array('d', [ a - b for a,b in zip(expectedLimits, expectedLimitsm2s) ])
    expectedLimitsp2s = array('d', [ a - b for a,b in zip(expectedLimitsp2s, expectedLimits) ])
    expectedLimit2s_plot = rt.TGraphAsymmErrors(len(masses), masses, expectedLimits, emasses , emasses, expectedLimitsm2s, expectedLimitsp2s  )
    expectedLimit2s_plot.SetFillColor(rt.kYellow)
    #expectedLimit2s_plot.SetFillStyle(3005)
    expectedLimit2s_plot.SetMinimum(0.0001)
    if model == "T1tttt":
        expectedLimit2s_plot.SetMinimum(10)


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
    if model == "T1tttt":
        final_plot.SetMinimum(10)

    final_plot.SetTitle("Toy based limit, T2tt(mLSP=25GeV), %s, 3D fit;mStop(GeV);upper xsec"%boxName)
    # final_plot.SetTitle("Asymptotic limit, T2tt(mLSP=25GeV), %s, 3D fit;mStop(GeV);upper xsec"%boxName)
    c = rt.TCanvas("c")
    c.SetLogy()
    final_plot.Draw("a4")

    leg = rt.TLegend(0.6, 0.65, 0.899, 0.89)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    leg.AddEntry(expectedLimit1s_plot,"expected +/- 1 #sigma","f")
    leg.AddEntry(expectedLimit2s_plot,"expected +/- 2 #sigma","f")
    leg.AddEntry(expectedLimit_plot,"expected","l")
    leg.AddEntry(observedLimit_plot,"observed","l")
    leg.AddEntry(susy_limit,"susy xsection","l")
    leg.Draw("SAME")



    boxName = re.sub(' ', '', boxName)
    c.SaveAs("limitToyFromToys"+model+boxName+sideband+njets+".png")
