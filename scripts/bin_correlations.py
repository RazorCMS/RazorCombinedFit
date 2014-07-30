#! /usr/bin/env python
"""Plot correlations between bins in the French flag"""

import sys
import ROOT as rt

def find_last_bin_value(th1d):
    """Function to get the maximum filled bin of a TH1 histogram"""
    nbins = th1d.GetNbinsX()
    last_bin = 0
    for i in range(nbins, 0, -1):
        bin_content = th1d.GetBinContent(i)
        if bin_content > 0:
            last_bin = i
            break

    bin_value = th1d.GetXaxis().GetBinLowEdge(last_bin)

    return bin_value


def sum_bins(tree, xbin_number):
    """Give it a bin number in MR_Rsq, and it returns the a histrogram with the
    sum over the three btags"""
    tmp_x = rt.TH1D('tmp_x', 'tmp_x', 1000, 0., 1000.)
    tree.Project('tmp_x', str(xbin_number + '_1+' + xbin_number + '_2+' + xbin_number + '_3'))
    print str(xbin_number + '_1+' + xbin_number + '_2+' + xbin_number + '_3')

    return tmp_x


def make_2d_plot(tree, xbin_number, ybin_number, xmax, ymax):
    """Function to make a 2D plot, given two bins, it sums over all three btag
    bins. xbin_number has to be of the form b3_3 or b3_4, etc."""

    xy_hist = rt.TH2D("xy", "xy", int(xmax)+2, 0., int(xmax)+1, int(ymax)+2, 0., int(ymax)+1)


    tree.Project("xy", str(ybin_number + '_1+' + ybin_number + '_2+' +
                 ybin_number + '_3:' + xbin_number + '_1+' + xbin_number
                 + '_2+' + xbin_number + '_3'))

    return xy_hist


if __name__ == '__main__':
    ROOT_NAME = sys.argv[1]
    ROOT_FILE = rt.TFile.Open(ROOT_NAME)
    TREE = ROOT_FILE.Get("myTree")
    X_BIN_TMP = sum_bins(TREE, 'b4_3')
    Y_BIN_TMP = sum_bins(TREE, 'b3_4')
    X_MAX = find_last_bin_value(X_BIN_TMP)
    Y_MAX = find_last_bin_value(Y_BIN_TMP)
    print X_MAX, Y_MAX
    xy_hist = make_2d_plot(TREE, 'b4_3', 'b3_4', X_MAX, Y_MAX)
    wtf = rt.TFile.Open("wtf.root", 'recreate')
    xy_hist.Write()
    wtf.Close()
    ROOT_FILE.Close()

