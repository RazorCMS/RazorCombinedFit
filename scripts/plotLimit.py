# import sys, os, pprint
import re
from optparse import OptionParser
import ROOT as rt
from array import array
import os.path


def get_xsec(model):
    """Return the xsec IN PICOBARN for a given mass and model"""
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
        susy_xsecs_array.append(gluino_hist.GetBinContent(
            gluino_hist.FindBin(mass)))

    return susy_xsecs_array


if __name__ == '__main__':

    PARSER = OptionParser()

    PARSER.add_option('--fitMode', dest='fitMode', default='3D', type='string',
                      help='2D or 3D fit')
    PARSER.add_option('--totalPDF', dest='pdfMode', default='split',
                      type='string',
                      help='limit on the total bkg PDF, or on the individual '
                      'bkg components')
    PARSER.add_option('--nb', dest='nb', default='3', type='string',
                      help='number of btags')
    PARSER.add_option('--combination', dest='combination', default=False,
                      action="store_true",
                      help='run on the combination of the btags for the'
                      ' 2D case')

    (options, args) = PARSER.parse_args()

    MODEL = args[0]
    boxName = args[1]
    fitMode = options.fitMode
    pdfMode = options.pdfMode
    nb = options.nb
    combination = options.combination

    if MODEL == 'T1tttt':
        mass_range = range(400, 1425, 25)
    elif MODEL == 'T2tt':
        mass_range = range(150, 800, 25)

    # We just fill the masses array here.
    masses = array('d', [])
    for mass in mass_range:
        if fitMode == '3D':
            file_name = ("Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s"
                         "/higgsCombine%s_%s_%s_25."
                         "Asymptotic.mH120.root" %
                         (MODEL, boxName, fitMode, pdfMode,
                          boxName, MODEL, mass))
        elif fitMode == '2D' and combination is True:
            file_name = ('Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s'
                         '/higgsCombine%s_%s_%s.0_25.0.'
                         'Asymptotic.mH120.root' %
                         (MODEL, boxName, fitMode, pdfMode,
                          boxName, MODEL, mass))
        else:
            file_name = ("Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s"
                         "/higgsCombine%s_%s_%s_25_%s."
                         "Asymptotic.mH120.root" %
                         (MODEL, boxName, fitMode, pdfMode,
                          boxName, MODEL, mass, nb))
        # file_name = ("Tests/Rsq_gte0.15/combine_files_mergedboxes/higgsCombineT1tttt_%s_25."
        #              "Asymptotic.mH120.root" % (mass))
        if not os.path.exists(file_name):
            continue
        print file_name

        my_file = rt.TFile.Open(file_name, "READ")
        if not my_file.Get("limit"):
            continue
        masses.append(mass)

    observedLimits = []
    expectedLimits = []
    expectedLimitsp1s = []
    expectedLimitsm1s = []
    expectedLimitsm2s = []
    expectedLimitsp2s = []

    susy_xsecs = get_xsec(MODEL)

    susy_xsecs_dict = dict(zip(masses, susy_xsecs))
    print susy_xsecs_dict
    sideband = 'FULL'
    model = MODEL
    if fitMode == '3D' or (fitMode == '2D' and combination is True):
        outfile = rt.TFile.Open('Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s'
                                '/asymptoticFile_%s_%s_%s_%s_25.root'
                                % (MODEL, boxName, fitMode, pdfMode,
                                   model, boxName, fitMode, pdfMode),
                                'RECREATE')
    else:
        outfile = rt.TFile.Open('Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s'
                                '/asymptoticFile_%s_%s_%s_%s_25_%s.root' %
                                (MODEL, boxName, fitMode, pdfMode,
                                 model, boxName, fitMode, pdfMode, nb),
                                'RECREATE')

    # outfile = rt.TFile.Open('toysFile_%s_%s.root' % (model, boxName),
    # 'RECREATE')
    xsecUL_ExpMinus2 = rt.TH1F("xsecUL_ExpMinus2_%s_%s" % (model, boxName),
                               "xsecUL_ExpMinus2_%s_%s" % (model, boxName),
                               26, 150, 800)
    xsecUL_ExpMinus = rt.TH1F("xsecUL_ExpMinus_%s_%s" % (model, boxName),
                              "xsecUL_ExpMinus_%s_%s" % (model, boxName),
                              26, 150, 800)
    xsecUL_Exp = rt.TH1F("xsecUL_Exp_%s_%s" % (model, boxName),
                         "xsecUL_Exp_%s_%s" % (model, boxName), 26, 150, 800)
    xsecUL_ExpPlus = rt.TH1F("xsecUL_ExpPlus_%s_%s" % (model, boxName),
                             "xsecUL_ExpPlus_%s_%s" % (model, boxName),
                             26, 150, 800)
    xsecUL_ExpPlus2 = rt.TH1F("xsecUL_ExpPlus2_%s_%s" % (model, boxName),
                              "xsecUL_ExpPlus2_%s_%s" % (model, boxName),
                              26, 150, 800)

    # We actually take the asymptotic limit per mass point here
    # and write it to asymptoticFile.root
    for mass in mass_range:

        if fitMode == '3D':
            file_name = ("Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s"
                         "/higgsCombine%s_%s_%s_25."
                         "Asymptotic.mH120.root" %
                         (MODEL, boxName, fitMode, pdfMode,
                          boxName, MODEL, mass))
        elif fitMode == '2D' and combination is True:
            file_name = ('Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s'
                         '/higgsCombine%s_%s_%s.0_25.0.'
                         'Asymptotic.mH120.root' %
                         (MODEL, boxName, fitMode, pdfMode,
                          boxName, MODEL, mass))
        else:
            file_name = ("Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s"
                         "/higgsCombine%s_%s_%s_25_%s."
                         "Asymptotic.mH120.root" %
                         (MODEL, boxName, fitMode, pdfMode,
                          boxName, MODEL, mass, nb))

        if not os.path.exists(file_name):
            continue

        file = rt.TFile(file_name)

        # Toys
        # file = rt.TFile("Combine/T2tt/step2/mLSP25/higgsCombineToys%s_%s"
        #                 ".0_25.0_FULL_%s_0.HybridNew.mH120.root" %\
        #                 (model, mass, boxName))

        if not file.Get("limit"):
            continue

        print file
        tree = file.Get("limit")
        tree.Draw(">>elist", "", "entrylist")

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
                xsecUL_ExpMinus2.Fill(mass, tree.limit*susy_xsecs_dict[mass])
            if count == 1:
                expectedLimitsm1s.append(tree.limit*susy_xsecs_dict[mass])
                xsecUL_ExpMinus.Fill(mass, tree.limit*susy_xsecs_dict[mass])
            if count == 2:
                expectedLimits.append(tree.limit*susy_xsecs_dict[mass])
                xsecUL_Exp.Fill(mass, tree.limit*susy_xsecs_dict[mass])
            if count == 3:
                expectedLimitsp1s.append(tree.limit*susy_xsecs_dict[mass])
                xsecUL_ExpPlus.Fill(mass, tree.limit*susy_xsecs_dict[mass])
            if count == 4:
                expectedLimitsp2s.append(tree.limit*susy_xsecs_dict[mass])
                xsecUL_ExpPlus2.Fill(mass, tree.limit*susy_xsecs_dict[mass])
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

    expectedLimitsm1s = array('d', [a - b for a, b in
                                    zip(expectedLimits, expectedLimitsm1s)])
    expectedLimitsp1s = array('d', [a - b for a, b in
                                    zip(expectedLimitsp1s, expectedLimits)])
    expectedLimit1s_plot = rt.TGraphAsymmErrors(len(masses), masses,
                                                expectedLimits, emasses,
                                                emasses, expectedLimitsm1s,
                                                expectedLimitsp1s)
    expectedLimit1s_plot.SetFillColor(rt.kGreen)
    # expectedLimit1s_plot.SetFillStyle(3005)
    # expectedLimit1s_plot.SetMinimum(0.0001)

    expectedLimitsm2s = array('d', [a - b for a, b in
                                    zip(expectedLimits, expectedLimitsm2s)])
    expectedLimitsp2s = array('d', [a - b for a, b in
                                    zip(expectedLimitsp2s, expectedLimits)])
    expectedLimit2s_plot = rt.TGraphAsymmErrors(len(masses), masses,
                                                expectedLimits, emasses,
                                                emasses, expectedLimitsm2s,
                                                expectedLimitsp2s)
    expectedLimit2s_plot.SetFillColor(rt.kYellow)
    # expectedLimit2s_plot.SetFillStyle(3005)
    expectedLimit2s_plot.SetMinimum(0.0001)

    susy_limit = rt.TGraph(len(masses), masses, susy_xsecs)
    susy_limit.SetMarkerStyle(24)
    susy_limit.SetLineColor(rt.kBlue)
    susy_limit.SetLineWidth(3)

    final_plot = rt.TMultiGraph()
    final_plot.Add(expectedLimit2s_plot)
    final_plot.Add(expectedLimit1s_plot)
    final_plot.Add(observedLimit_plot, "L")
    final_plot.Add(expectedLimit_plot, "L")
    final_plot.Add(susy_limit, "L")
    final_plot.SetMinimum(0.0001)

    # final_plot.SetTitle("Toy based limit, T2tt(mLSP=25GeV), %s, 3D fit;"
    #                     "mStop(GeV);upper xsec" % boxName)
    if model == "T1tttt":
        final_plot.SetMinimum(0.01)
        final_plot.SetTitle("Asymptotic limit, T1tttt(mLSP=25GeV), %s, 3D fit;"
                            "mGluino(GeV);upper xsec" % boxName)
    c = rt.TCanvas("c")
    c.SetLogy()
    final_plot.Draw("a4")

    leg = rt.TLegend(0.6, 0.65, 0.899, 0.89)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    leg.AddEntry(expectedLimit1s_plot, "expected +/- 1 #sigma", "f")
    leg.AddEntry(expectedLimit2s_plot, "expected +/- 2 #sigma", "f")
    leg.AddEntry(expectedLimit_plot, "expected", "l")
    leg.AddEntry(observedLimit_plot, "observed", "l")
    leg.AddEntry(susy_limit, "susy xsection", "l")
    leg.Draw("SAME")

    boxName = re.sub(' ', '', boxName)
    if sideband is not 'FULL':
        c.SaveAs("limitFromAsym_"+model+'_'+boxName+'_'+sideband+".png")
        c.SaveAs("limitFromAsym_"+model+'_'+boxName+'_'+sideband+".C")
    else:
        if fitMode == '3D' or (fitMode == '2D' and combination is True):
            c.SaveAs('Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s'
                     '/limitFromAsym_%s_%s_%s_%s_25.png' %
                     (MODEL, boxName, fitMode, pdfMode,
                      model, boxName, fitMode, pdfMode))
            c.SaveAs('Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s'
                     '/limitFromAsym_%s_%s_%s_%s_25.pdf' %
                     (MODEL, boxName, fitMode, pdfMode,
                      model, boxName, fitMode, pdfMode))
            c.SaveAs('Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s'
                     '/limitFromAsym_%s_%s_%s_%s_25.C' %
                     (MODEL, boxName, fitMode, pdfMode,
                      model, boxName, fitMode, pdfMode))

        else:
            c.SaveAs('Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s'
                     '/limitFromAsym_%s_%s_25_%s.png' %
                     (MODEL, boxName, fitMode, pdfMode,
                      model, boxName, nb))
            c.SaveAs('Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s'
                     '/limitFromAsym_%s_%s_25_%s.C' %
                     (MODEL, boxName, fitMode, pdfMode,
                      model, boxName, nb))
