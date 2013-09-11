import ROOT as rt
import sys
import RootTools


if __name__ == '__main__':
    inputFile = rt.TFile.Open(sys.argv[1])

    Dataset = inputFile.Get('RMRTree')
    args = Dataset.get(0)

    argset = rt.RooArgSet()
    for a in RootTools.RootIterator.RootIterator(args):
        if a.GetName() in ['MR', 'Rsq', 'W']:
            argset.add(a)

    MR = argset['MR']
    Rsq = argset['Rsq']
    W = argset['W']
    wRMRTree = rt.RooDataSet('wRMRTree', 'wRMRTree', argset)

    nbins = 100

    minMR = MR.getMin()
    maxMR = MR.getMax()
    maxRsq = Rsq.getMax()
    minRsq = Rsq.getMin()
    stepMR = (maxMR - minMR) / nbins
    stepRsq = (maxRsq - minRsq) / nbins

    for j in range(0, nbins):
        for i in range(0, nbins):
            mrLow, mrHigh = minMR+stepMR*i, minMR+stepMR*(i+1)
            rsqLow, rsqHigh = minRsq+stepRsq*j, minRsq+stepRsq*(j+1)

            cutString = 'MR>=%s && MR<%s && Rsq>=%s && Rsq<%s' % (mrLow, mrHigh, rsqLow, rsqHigh)
            W.setVal(int(Dataset.sumEntries(cutString)))
            MR.setVal((mrLow+mrHigh)/2)
            Rsq.setVal((rsqLow + rsqHigh) / 2)

            wRMRTree.add(rt.RooArgSet(MR, Rsq, W))

    wRMRTree.Print()

    WeightedDataset = rt.RooDataSet('WeightedDataset', 'WeightedDataset', wRMRTree, rt.RooArgSet(MR, Rsq, W), "", W.GetName())
    WeightedDataset.SetName('RMRTree')

    # This is for the DataHist
    histo2D = Dataset.createHistogram(MR, Rsq, 100, 100)
    histo2D.SetName("StartingHisto")
    histo2D.Sumw2()
    histo2Dweighted = rt.TH2D('histo2Dweighted', 'histo2Dweighted', 100, MR.getMin(), MR.getMax(), 100, Rsq.getMin(), Rsq.getMax())
    histo2Dweighted.SetName('EndHisto')
    histo2Dweighted.Sumw2()
    for rsqbin in range(1, histo2D.GetNbinsY()+1):
        for mrbin in range(1, histo2D.GetNbinsX()+1):
            mr = histo2D.GetXaxis().GetBinCenter(mrbin)
            rsq = histo2D.GetYaxis().GetBinCenter(rsqbin)
            histo2Dweighted.Fill(mr, rsq, histo2D.GetBinContent(histo2D.FindBin(mr, rsq)))
    BinnedDataset = rt.RooDataHist('RMRTree', 'RMRTree', rt.RooArgList(MR, Rsq), histo2Dweighted)
    histOutFile = rt.TFile("DataHist_BJetHS.root", 'RECREATE')
    BinnedDataset.Write()
    histOutFile.Close()

    outFile = rt.TFile("Weighted_BJetHS.root", "RECREATE")
    wRMRTree.Write()
    WeightedDataset.Write()
    outFile.Close()
