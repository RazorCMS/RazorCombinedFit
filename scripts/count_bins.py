"""Prints the bins in MR, RSQ, and BTAG for a given TH3D"""
import ROOT as rt
import sys


if __name__ == '__main__':
    ROOT_FILE = sys.argv[1]
    FILE = rt.TFile.Open(ROOT_FILE)
    # HIST = FILE.Get('wHisto')
    # HIST = FILE.Get('BJetLS/histoToy_Rsq_FULL_ALLCOMPONENTS')
    HIST = FILE.Get('BJetLS/histo3DToy_MRRsqBtag_FULL_ALLCOMPONENTS')
    x_axis = HIST.GetXaxis()
    y_axis = HIST.GetYaxis()
    z_axis = HIST.GetZaxis()

    MRbins = []
    Rsqbins = []

    print x_axis.GetNbins(), y_axis.GetNbins(), z_axis.GetNbins()
    for i in range(1, x_axis.GetNbins()+2):
        MRbins.append(x_axis.GetBinLowEdge(i))

    for i in range(1, y_axis.GetNbins()+2):
        Rsqbins.append(y_axis.GetBinLowEdge(i))

    print 'MRbins =', MRbins
    print 'Rsqbins =', Rsqbins
