#! /usr/bin/env python
"""Macro to make 2D plots"""

import ROOT as rt
import os.path
import sys, re
from array import array


def get_frenchflag_binning():
    """Return the binning of the French flag plots"""
    mr_bins = [450, 600, 750, 900, 1200, 1600, 4000]
    rsq_bins = [0.10, 0.13, 0.20, 0.30, 0.41, 0.52, 0.64, 1.5]

    nbtag_bins = [1, 2, 3, 4]

    return mr_bins, rsq_bins, nbtag_bins


def get_xsec(model, mass):
    """Return the xsec for a given mass and model"""
    if model == 'T2tt':
        ref_xsec_file = './stop.root'
    elif model == 'T1tttt':
        ref_xsec_file = './gluino.root'

    print "INFO: Input ref xsec file!"
    gluino_file = rt.TFile.Open(ref_xsec_file, "READ")
    gluino_hist_name = ref_xsec_file.split("/")[-1].split(".")[0]
    gluino_hist = gluino_file.Get(gluino_hist_name)
    ref_xsec = 1.e3*gluino_hist.GetBinContent(gluino_hist.FindBin(mass))
    print "INFO: ref xsec taken to be: %s mass %d, xsec = %f fb" % \
        (gluino_hist_name, mass, ref_xsec)

    return ref_xsec


def add_text(mass, sig_eff, x_sec, nsig):
    """Create a text to add to the histogram"""
    sig_text = rt.TPaveText(0.55, 0.67, 0.9, 0.9, "ndc")
    sig_text.SetName("TPave_%s" % str(mass))
    sig_text.SetBorderSize(0)
    sig_text.SetTextSize(0.04)
    sig_text.SetFillColor(0)
    sig_text.SetFillStyle(0)
    sig_text.SetLineColor(0)
    sig_text.SetTextFont(42)
    sig_text.AddText("Eff = %.3f" % sig_eff)
    sig_text.AddText("#sigma = %i fb" % x_sec)
    sig_text.AddText("N_{sig} = %.2f" % nsig)
    return sig_text

if __name__ == '__main__':
    rt.gStyle.SetOptStat(0)

    MODEL = sys.argv[1]
    DIRECTORY = sys.argv[2]
    BOX = sys.argv[3]
    M_LSP = sys.argv[4]

    TWOD_HISTOS = {}
    MR_HISTOS = {}
    RSQ_HISTOS = {}
    MR_HISTOS_RSQ_GT03 = {}
    MR_HISTOS_RSQ_LT03 = {}
    SIGNAL_TEXT = {}
    CANVASES = {}

    X_BINS, Y_BINS, Z_BINS = get_frenchflag_binning()

    MR_BINS = array("d", X_BINS)
    RSQ_BINS = array("d", Y_BINS)
    NBTAG_BINS = array("d", X_BINS)
    LUMI = 19.3

    OUT_FILE = rt.TFile.Open(MODEL + "_2DHistos_" + BOX + ".root", 'recreate')

    for mStop in range(300, 800, 50):
        DIR = DIRECTORY+'/mLSP'+str(M_LSP)+'/'

        for filename in os.listdir(DIR):
            stop_mass = re.search('_' + str(mStop) + '.0_', str(filename))
            # print stop_mass_file
            box_name = re.search(BOX, str(filename))

            if stop_mass and box_name:
                xsec = get_xsec(MODEL, mStop)
                IN_file = rt.TFile.Open(DIR+'/'+filename)
                wHisto = IN_file.Get("wHisto")
                eff = wHisto.Integral()
                TWOD_HISTOS[mStop] = wHisto.Project3D('mStop_' + str(mStop) +
                                                      '_yxe')
                sigEvents = eff * LUMI * xsec
                TWOD_HISTOS[mStop].Scale(sigEvents /
                                         TWOD_HISTOS[mStop].Integral())
                TWOD_HISTOS[mStop].SetTitle(MODEL + " @ " + str(mStop) + " GeV")
                TWOD_HISTOS[mStop].GetXaxis().SetTitleOffset(1.15)
                TWOD_HISTOS[mStop].GetYaxis().SetTitleOffset(1.15)
                TWOD_HISTOS[mStop].GetZaxis().SetTitleOffset(0.7)
                TWOD_HISTOS[mStop].GetXaxis().CenterTitle()
                TWOD_HISTOS[mStop].GetYaxis().CenterTitle()
                TWOD_HISTOS[mStop].GetZaxis().CenterTitle()
                TWOD_HISTOS[mStop].SetXTitle("M_{R}")
                TWOD_HISTOS[mStop].SetYTitle("R^{2}")
                TWOD_HISTOS[mStop].SetZTitle("N events")

                MR_HISTOS[mStop] = wHisto.Project3D('mStop_' + str(mStop) +
                                                    '_x')
                MR_HISTOS[mStop].Scale(sigEvents / MR_HISTOS[mStop].Integral())
                MR_HISTOS[mStop].SetTitle(MODEL + " @ " + str(mStop) + " GeV")
                MR_HISTOS[mStop].GetXaxis().SetTitleOffset(1.15)
                MR_HISTOS[mStop].GetXaxis().CenterTitle()
                MR_HISTOS[mStop].SetXTitle("M_{R}")
                MR_HISTOS[mStop].GetYaxis().SetTitleOffset(1.15)
                MR_HISTOS[mStop].GetYaxis().CenterTitle()
                MR_HISTOS[mStop].SetYTitle("N events")

                SIGNAL_TEXT[mStop] = add_text(mStop, eff, xsec, sigEvents)

                RSQ_HISTOS[mStop] = wHisto.Project3D('mStop_' + str(mStop) +
                                                     '_y')
                RSQ_HISTOS[mStop].Scale(sigEvents /
                                        RSQ_HISTOS[mStop].Integral())
                RSQ_HISTOS[mStop].SetTitle(MODEL + " @ " + str(mStop) + " GeV")
                RSQ_HISTOS[mStop].GetXaxis().SetTitleOffset(1.15)
                RSQ_HISTOS[mStop].GetXaxis().CenterTitle()
                RSQ_HISTOS[mStop].SetXTitle("R^{2}")
                RSQ_HISTOS[mStop].GetYaxis().SetTitleOffset(1.15)
                RSQ_HISTOS[mStop].GetYaxis().CenterTitle()
                RSQ_HISTOS[mStop].SetYTitle("N events")


                wHisto.GetYaxis().SetRange(1, 3)
                MR_HISTOS_RSQ_LT03[mStop] = wHisto.Project3D('mStop_' +
                                                             str(mStop) +
                                                             '_RSQLT03_x')
                # MR_HISTOS_RSQ_LT03[mStop].Scale(sigEvents /
                #                                 MR_HISTOS_RSQ_LT03[mStop].
                #                                 Integral())
                MR_HISTOS_RSQ_LT03[mStop].Scale(1. / MR_HISTOS_RSQ_LT03[mStop].
                                                Integral())
                MR_HISTOS_RSQ_LT03[mStop].SetTitle(MODEL + " @ " + str(mStop) +
                                                   " GeV, R^{2} < 0.03")
                MR_HISTOS_RSQ_LT03[mStop].GetXaxis().SetTitleOffset(1.15)
                MR_HISTOS_RSQ_LT03[mStop].GetXaxis().CenterTitle()
                MR_HISTOS_RSQ_LT03[mStop].SetXTitle("M_{R}")
                MR_HISTOS_RSQ_LT03[mStop].GetYaxis().SetTitleOffset(1.15)
                MR_HISTOS_RSQ_LT03[mStop].GetYaxis().CenterTitle()
                MR_HISTOS_RSQ_LT03[mStop].SetYTitle("N events")
                MR_HISTOS_RSQ_LT03[mStop].SetLineColor(2)

                wHisto.GetYaxis().SetRange(4, 7)
                MR_HISTOS_RSQ_GT03[mStop] = wHisto.Project3D('mStop_' +
                                                             str(mStop) +
                                                             '_RSQGT03_x')
                # MR_HISTOS_RSQ_GT03[mStop].Scale(sigEvents /
                #                                 MR_HISTOS_RSQ_GT03[mStop].
                #                                 Integral())
                MR_HISTOS_RSQ_GT03[mStop].Scale(1. / MR_HISTOS_RSQ_GT03[mStop].
                                                Integral())
                MR_HISTOS_RSQ_GT03[mStop].SetTitle(MODEL + " @ " + str(mStop) +
                                                   " GeV, R^{2} > 0.03")
                MR_HISTOS_RSQ_GT03[mStop].GetXaxis().SetTitleOffset(1.15)
                MR_HISTOS_RSQ_GT03[mStop].GetXaxis().CenterTitle()
                MR_HISTOS_RSQ_GT03[mStop].SetXTitle("M_{R}")
                MR_HISTOS_RSQ_GT03[mStop].GetYaxis().SetTitleOffset(1.15)
                MR_HISTOS_RSQ_GT03[mStop].GetYaxis().CenterTitle()
                MR_HISTOS_RSQ_GT03[mStop].SetYTitle("N events")



                CANVASES[mStop] = rt.TCanvas()
                CANVASES[mStop].SetLogy()
                CANVASES[mStop].SetLogx()
                TWOD_HISTOS[mStop].Draw("colz")
                SIGNAL_TEXT[mStop].Draw()
                CANVASES[mStop].Print('%s_%s_2D_%s.pdf' % (MODEL, mStop, BOX),
                                      "pdf")

                OUT_FILE.cd()
                TWOD_HISTOS[mStop].Write()
                MR_HISTOS[mStop].Write()
                MR_HISTOS_RSQ_LT03[mStop].Write()
                MR_HISTOS_RSQ_GT03[mStop].Write()
                RSQ_HISTOS[mStop].Write()
                SIGNAL_TEXT[mStop].Write()
                IN_file.cd()
                wHisto.Delete()
                IN_file.Close()
                IN_file.Delete()

    OUT_FILE.Close()
