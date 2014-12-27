"""Simplified version of prepareCombine.py"""
import ROOT as rt
from optparse import OptionParser


def fillHistFromToy(my_histo, myTree):
    """Fills the 2D histo with the content of the bins in myTree
    my_histo must be a TH3"""
    my_histo.Reset()
    my_histo.Sumw2()
    for mr in range(0, my_histo.GetNbinsX()-1):
        for rsq in range(0, my_histo.GetNbinsY() - 1):
            for nb in range(1, my_histo.GetNbinsZ()):
                myTree.Draw("b%s_%s_%s" % (mr, rsq, nb))
                htemp = rt.gPad.GetPrimitive('htemp')
                mean = htemp.GetMean()
                rms = htemp.GetRMS()
                my_histo.SetBinContent(mr+1, rsq+1, nb, mean)
                my_histo.SetBinError(mr+1, rsq+1, nb, rms)
                print mean, rms, my_histo.GetBinContent(mr+1, rsq+1, nb)
    print my_histo.Integral()
    return my_histo


def fill2DHistFromToy(my_histo, myTree, nb):
    """Fills the 2D histo with the content of the bins in myTree
    my_histo must be a TH2"""
    my_histo.Reset()
    my_histo.Sumw2()
    for mr in range(0, my_histo.GetNbinsX()-1):
        for rsq in range(0, my_histo.GetNbinsY() - 1):
            myTree.Draw("b%s_%s_%s" % (mr, rsq, nb))
            htemp = rt.gPad.GetPrimitive('htemp')
            mean = htemp.GetMean()
            rms = htemp.GetRMS()
            my_histo.SetBinContent(mr+1, rsq+1, mean)
            my_histo.SetBinError(mr+1, rsq+1, rms)
            print mean, rms, my_histo.GetBinContent(mr+1, rsq+1)
    print my_histo.Integral()
    return my_histo


def unroll_hist(hist_name):
    """Function to unroll TH3s into TH1s,
    it does all b-tags at the same time"""
    n_bins = hist_name.GetNbinsX() * hist_name.GetNbinsY() *\
        hist_name.GetNbinsZ()

    hist_1d = rt.TH1F(hist_name.GetName(),
                      hist_name.GetTitle() + '+1d', n_bins, 0., n_bins)

    new_bin = 0
    for i in xrange(1, hist_name.GetNbinsX() + 1):
        for j in xrange(1, hist_name.GetNbinsY() + 1):
            for k in xrange(1, hist_name.GetNbinsZ() + 1):
                new_bin += 1
                hist_1d.\
                    SetBinContent(new_bin, hist_name.GetBinContent(i, j, k))
    return hist_1d


def unroll_2Dhist(hist_name, nb):
    """Function to unroll TH3s into TH1s,
    it depends on the number of b-tags"""
    n_bins = hist_name.GetNbinsX() * hist_name.GetNbinsY()

    hist_1d = rt.TH1F(hist_name.GetName(),
                      hist_name.GetTitle() + '+1d', n_bins, 0., n_bins)

    new_bin = 0
    for i in xrange(1, hist_name.GetNbinsX() + 1):
        for j in xrange(1, hist_name.GetNbinsY() + 1):
            new_bin += 1
            hist_1d.\
                SetBinContent(new_bin, hist_name.GetBinContent(i, j, nb))
    return hist_1d


def check_for_zeros(bkg_hist, data_hist):
    """If we find a zero bin histo for the background, but non-zero for data,
    set that bin to 0.1 entries in the background"""
    nbins = bkg_hist.GetNbinsX()
    for i in range(1, nbins+1):
        bkg = bkg_hist.GetBinContent(i)
        dat = data_hist.GetBinContent(i)
        if bkg == 0 and dat > 0:
            print "Warning: zero bin background.", i, bkg, dat
            bkg_hist.SetBinContent(i, dat / 5.)
            print "New content:", i, bkg_hist.GetBinContent(i), dat


def writeDataCard(fileName, *args):
    """Write the txt data card.
    Input: fileName plus a list with the following elements:
    number of bkgs
    number of signal events
    number of events in the datasets
    number of events in TTj1b TTj2b TTj3b"""

    datacard = open(fileName + '.txt', 'w')
    datacard.write('imax 1 number of channels\n')
    datacard.write('jmax 3 number of backgrounds\n')
    datacard.write('kmax 7 number of nuisance parameters (sources of '
                   'systematic uncertainties)\n')
    datacard.write('---------------\n')
    datacard.write('shapes * * %s.root $PROCESS $PROCESS_$SYSTEMATIC\n'
                   % fileName)
    datacard.write('---------------\n')
    datacard.write('bin 1\n')
    datacard.write('observation %i\n' % args[0])
    datacard.write('---------------\n')
    datacard.write('bin        \t1\t1\t1\t1\n')
    datacard.write('process    \tsignal\tTTj1b\tTTj2b\tVpj\n')
    datacard.write('process    \t0\t1\t2\t3\n')
    datacard.write('rate    \t%f\t%f\t%f\t%f\n' % (args[1], args[2],
                                                   args[3], args[4]))
    datacard.write('---------------\n')
    datacard.write('lumi lnN\t1.026\t1.0\t1.0\t1.0\n')
    datacard.write('trigger lnN\t1.050\t1.0\t1.0\t1.0\n')
    datacard.write('bgnorm lnN\t1.00\t1.1\t1.1\t1.1\n')
    datacard.write('Pdf shape \t1.00\t-\t-\t-\n')
    datacard.write('Jes shape \t1.00\t-\t-\t-\n')
    datacard.write('Btag shape \t1.00\t-\t-\t-\n')
    datacard.write('Isr shape \t1.00\t-\t-\t-\n')
    datacard.close()


def writeDataCardSimple(fileName, *args):
    """Write the txt data card.
    Input: fileName plus a list with the following elements:
    number of bkgs
    number of signal events
    number of events in the datasets
    number of events in TTj1b TTj2b TTj3b"""

    datacard = open(fileName + '.txt', 'w')
    datacard.write('imax 1 number of channels\n')
    datacard.write('jmax 1 number of backgrounds\n')
    datacard.write('kmax 7 number of nuisance parameters (sources of '
                   'systematic uncertainties)\n')
    datacard.write('---------------\n')
    datacard.write('shapes * * %s.root $PROCESS $PROCESS_$SYSTEMATIC\n'
                   % fileName)
    datacard.write('---------------\n')
    datacard.write('bin 1\n')
    datacard.write('observation %.1f\n' % args[0])
    datacard.write('---------------\n')
    datacard.write('bin        \t1\t1\n')
    datacard.write('process    \tsignal\tbackground\n')
    datacard.write('process    \t0\t1\n')
    datacard.write('rate    \t%f\t%f\n' % (args[1], args[2]))
    datacard.write('---------------\n')
    datacard.write('lumi lnN\t1.026\t1.0\n')
    datacard.write('trigger lnN\t1.050\t1.0\n')
    datacard.write('bgnorm lnN\t1.00\t1.1\n')
    datacard.write('Pdf shape \t1.00\t-\n')
    datacard.write('Jes shape \t1.00\t-\n')
    datacard.write('Btag shape \t1.00\t-\n')
    datacard.write('Isr shape \t1.00\t-\n')
    datacard.close()


def writeDataCardLeptonic(fileName, *args):
    """Write the txt data card.
    Input: fileName plus a list with the following elements:
    number of bkgs
    number of signal events
    number of events in the datasets
    number of events in TTj1b TTj2b TTj3b"""

    datacard = open(fileName + '.txt', 'w')
    datacard.write('imax 1 number of channels\n')
    datacard.write('jmax 2 number of backgrounds\n')
    datacard.write('kmax 7 number of nuisance parameters (sources of '
                   'systematic uncertainties)\n')
    datacard.write('---------------\n')
    datacard.write('shapes * * %s.root $PROCESS $PROCESS_$SYSTEMATIC\n'
                   % fileName)
    datacard.write('---------------\n')
    datacard.write('bin 1\n')
    datacard.write('observation %i\n' % args[0])
    datacard.write('---------------\n')
    datacard.write('bin        \t1\t1\t1\n')
    datacard.write('process    \tsignal\tTTj1b\tTTj2b\n')
    datacard.write('process    \t0\t1\t2\n')
    datacard.write('rate    \t%f\t%f\t%f\n' % (args[1], args[2], args[3]))
    datacard.write('---------------\n')
    datacard.write('lumi lnN\t1.026\t1.0\t1.0\n')
    datacard.write('trigger lnN\t1.050\t1.0\t1.0\n')
    datacard.write('bgnorm lnN\t1.00\t1.1\t1.1\n')
    datacard.write('Pdf shape \t1.00\t-\t-\n')
    datacard.write('Jes shape \t1.00\t-\t-\n')
    datacard.write('Btag shape \t1.00\t-\t-\n')
    datacard.write('Isr shape \t1.00\t-\t-\n')
    datacard.close()


if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option('-f', '--refXsecFile', metavar='FILE',
                      default='./stop.root', help="susy xsec file")
    parser.add_option('-x', '--refXsec', dest='refXsec', default=0.0,
                      type='float',
                      help='reference xsec for toy limit')
    parser.add_option('-b', '--box', dest="box", default='BJetLS',
                      type="string", help="Specify only one box")
    parser.add_option('-i', '--input', dest="input", default=None,
                      metavar='FILE',
                      help="An input file to read fit results and workspaces")
    parser.add_option('-d', '--dir', dest="outdir", default="./",
                      type="string",
                      help="Output directory to store datasets")
    parser.add_option('--fitmode', dest='fitmode', default='3D', type='string',
                      help='2D or 3D fit.')
    parser.add_option('--pdfmode', dest='totalPDF', default='split',
                      type='string',
                      help='limit on the total bkg PDF, instead of the '
                      'individual bkg components')
    parser.add_option('--leptonic', dest='isLeptonic', default=False,
                      action='store_true',
                      help="Leptonic fit")

    (options, args) = parser.parse_args()

    # Constants and input files
    LUMI = 19.3
    mStop = float(args[0].split("_")[-3])
    box = options.box
    sigFile = rt.TFile.Open(args[0], 'READ')
    MODEL = args[1]
    inFile = rt.TFile.Open(options.input, 'READ')
    outdir = options.outdir
    fitmode = options.fitmode
    totalPDF = options.totalPDF
    isLeptonic = options.isLeptonic
    refXsecFile = options.refXsecFile
    refXsec = options.refXsec
    # Calculate cross section

    if refXsec == 0.0:
        stopFile = rt.TFile.Open(refXsecFile, "READ")
        stopHistName = refXsecFile.split("/")[-1].split(".")[0]
        stopHist = stopFile.Get(stopHistName)
        refXsec = 1.e3 * stopHist.GetBinContent(stopHist.FindBin(mStop))
        print 'INFO: ref xsec is: %s mass %d, xsec = %f fb' % (stopHistName,
                                                               mStop, refXsec)

    # ########
    # Data Set
    data_obs = inFile.Get('%s/'
                          'histo3DData_MRRsqBtag_FULL_ALLCOMPONENTS' % box)
    data_obs.SetName('data_obs')
    data_obs.SetTitle('data_obs')

    # ########
    # Signal pdf
    signal = sigFile.Get('wHisto')
    sigNorm = signal.Integral()
    sigEvents = sigNorm * LUMI * refXsec
    print 'INFO: now multiplying efficiency * lumi * refXsec = ',\
        '%f * %f * %f = %f events' % (sigNorm, LUMI, refXsec, sigEvents)
    signal.SetName('signal')
    signal.SetTitle('signal')
    integral = signal.Integral()
    signal.Scale(sigEvents / integral)

    signal_PdfUp = sigFile.Get('wHisto_pdferr_up')
    signal_PdfDown = sigFile.Get('wHisto_pdferr_down')
    signal_JesUp = sigFile.Get('wHisto_JESerr_up')
    signal_JesDown = sigFile.Get('wHisto_JESerr_down')
    signal_BtagUp = sigFile.Get('wHisto_btagerr_up')
    signal_BtagDown = sigFile.Get('wHisto_btagerr_down')
    signal_IsrUp = sigFile.Get('wHisto_ISRerr_up')
    signal_IsrDown = sigFile.Get('wHisto_ISRerr_down')
    signal_PdfUp.SetName('signal_PdfUp')
    signal_PdfUp.SetTitle('signal_PdfUp')
    signal_PdfDown.SetName('signal_PdfDown')
    signal_PdfDown.SetTitle('signal_PdfDown')
    signal_JesUp.SetName('signal_JesUp')
    signal_JesUp.SetTitle('signal_JesUp')
    signal_JesDown.SetName('signal_JesDown')
    signal_JesDown.SetTitle('signal_JesDown')
    signal_BtagUp.SetName('signal_BtagUp')
    signal_BtagUp.SetTitle('signal_BtagUp')
    signal_BtagDown.SetName('signal_BtagDown')
    signal_BtagDown.SetTitle('signal_BtagDown')
    signal_IsrUp.SetName('signal_IsrUp')
    signal_IsrUp.SetTitle('signal_IsrUp')
    signal_IsrDown.SetName('signal_IsrDown')
    signal_IsrDown.SetTitle('signal_IsrDown')

    signal_PdfUp.Scale(sigEvents / signal_PdfUp.Integral())
    signal_PdfDown.Scale(sigEvents / signal_PdfDown.Integral())
    signal_JesUp.Scale(sigEvents / signal_JesUp.Integral())
    signal_JesDown.Scale(sigEvents / signal_JesDown.Integral())
    signal_BtagUp.Scale(sigEvents / signal_BtagUp.Integral())
    signal_BtagDown.Scale(sigEvents / signal_BtagDown.Integral())
    signal_IsrUp.Scale(sigEvents / signal_IsrUp.Integral())
    signal_IsrDown.Scale(sigEvents / signal_IsrDown.Integral())

    mGluino = float(args[0].split("_")[-3])
    mLSP = float(args[0].split("_")[-2])
    massPoint = "%0.1f_%0.1f" % (mGluino, mLSP)

    if isLeptonic is True and fitmode == '3D' and totalPDF == 'split':
        print 'Leptonic!!!'
        print 'Default case: all b-tags together, and split bkg PDF components'
        # Background pdf
        TTj1b_pdf = inFile.Get('Mu/'
                               'histo3DToyTTj1b_MRRsqBtag_FULL_ALLCOMPONENTS')
        TTj1b_pdf.SetName('TTj1b')
        TTj1b_pdf.SetTitle('TTj1b')
        TTj2b_pdf = inFile.Get('Mu/'
                               'histo3DToyTTj2b_MRRsqBtag_FULL_ALLCOMPONENTS')
        TTj2b_pdf.SetName('TTj2b')
        TTj2b_pdf.SetTitle('TTj2b')

        datacards = 'razor_combine_%s_%s_%s' %\
            (box, MODEL, massPoint)

        # Unroll all histograms
        signal_1d = unroll_hist(signal)
        signal_PdfUp_1d = unroll_hist(signal_PdfUp)
        signal_PdfDown_1d = unroll_hist(signal_PdfDown)
        signal_JesUp_1d = unroll_hist(signal_JesUp)
        signal_JesDown_1d = unroll_hist(signal_JesDown)
        signal_BtagUp_1d = unroll_hist(signal_BtagUp)
        signal_BtagDown_1d = unroll_hist(signal_BtagDown)
        signal_IsrUp_1d = unroll_hist(signal_IsrUp)
        signal_IsrDown_1d = unroll_hist(signal_IsrDown)

        TTj1b_1d = unroll_hist(TTj1b_pdf)
        TTj2b_1d = unroll_hist(TTj2b_pdf)
        data_obs_1d = unroll_hist(data_obs)

        writeDataCardLeptonic(datacards, data_obs_1d.Integral(),
                              signal_1d.Integral(),
                              TTj1b_1d.Integral(), TTj2b_1d.Integral())

        outFile = rt.TFile.Open(datacards + '.root', 'RECREATE')
        signal_1d.Write()
        signal_PdfUp_1d.Write()
        signal_PdfDown_1d.Write()
        signal_JesUp_1d.Write()
        signal_JesDown_1d.Write()
        signal_BtagUp_1d.Write()
        signal_BtagDown_1d.Write()
        signal_IsrUp_1d.Write()
        signal_IsrDown_1d.Write()
        TTj1b_1d.Write()
        TTj2b_1d.Write()
        data_obs_1d.Write()
        outFile.Close()

    elif fitmode == '3D' and totalPDF == 'split':
        print 'Default case: all b-tags together, and split bkg PDF components'
        # Background pdf
        TTj1b_pdf = inFile.Get('BJetHS/'
                               'histo3DToyTTj1b_MRRsqBtag_FULL_ALLCOMPONENTS')
        TTj1b_pdf.SetName('TTj1b')
        TTj1b_pdf.SetTitle('TTj1b')
        TTj2b_pdf = inFile.Get('BJetHS/'
                               'histo3DToyTTj2b_MRRsqBtag_FULL_ALLCOMPONENTS')
        TTj2b_pdf.SetName('TTj2b')
        TTj2b_pdf.SetTitle('TTj2b')
        Vpj_pdf = inFile.Get('BJetHS/'
                             'histo3DToyVpj_MRRsqBtag_FULL_ALLCOMPONENTS')
        Vpj_pdf.SetName('Vpj')
        Vpj_pdf.SetTitle('Vpj')

        datacards = 'razor_combine_%s_%s_%s' %\
            (box, MODEL, massPoint)

        # Unroll all histograms
        signal_1d = unroll_hist(signal)
        signal_PdfUp_1d = unroll_hist(signal_PdfUp)
        signal_PdfDown_1d = unroll_hist(signal_PdfDown)
        signal_JesUp_1d = unroll_hist(signal_JesUp)
        signal_JesDown_1d = unroll_hist(signal_JesDown)
        signal_BtagUp_1d = unroll_hist(signal_BtagUp)
        signal_BtagDown_1d = unroll_hist(signal_BtagDown)
        signal_IsrUp_1d = unroll_hist(signal_IsrUp)
        signal_IsrDown_1d = unroll_hist(signal_IsrDown)

        TTj1b_1d = unroll_hist(TTj1b_pdf)
        TTj2b_1d = unroll_hist(TTj2b_pdf)
        Vpj_1d = unroll_hist(Vpj_pdf)
        data_obs_1d = unroll_hist(data_obs)

        writeDataCard(datacards, data_obs_1d.Integral(), signal_1d.Integral(),
                      TTj1b_1d.Integral(), TTj2b_1d.Integral(),
                      Vpj_1d.Integral())
        outFile = rt.TFile.Open(datacards + '.root', 'RECREATE')
        signal_1d.Write()
        signal_PdfUp_1d.Write()
        signal_PdfDown_1d.Write()
        signal_JesUp_1d.Write()
        signal_JesDown_1d.Write()
        signal_BtagUp_1d.Write()
        signal_BtagDown_1d.Write()
        signal_IsrUp_1d.Write()
        signal_IsrDown_1d.Write()
        TTj1b_1d.Write()
        TTj2b_1d.Write()
        Vpj_1d.Write()
        data_obs_1d.Write()
        outFile.Close()

    elif fitmode == '3D' and totalPDF == 'totalPDF':
        print 'Special case: all b-tags, and keep total bkg PDF'
        bkg_pdf = inFile.Get('%s/histo3DToy_MRRsqBtag_FULL_ALLCOMPONENTS'
                             % box)
        bkg_pdf.SetName('background')
        bkg_pdf.SetTitle('background')

        datacards = 'razor_combine_%s_%s_%s' %\
            (box, MODEL, massPoint)

        # Unroll all histograms
        signal_1d = unroll_hist(signal)
        signal_PdfUp_1d = unroll_hist(signal_PdfUp)
        signal_PdfDown_1d = unroll_hist(signal_PdfDown)
        signal_JesUp_1d = unroll_hist(signal_JesUp)
        signal_JesDown_1d = unroll_hist(signal_JesDown)
        signal_BtagUp_1d = unroll_hist(signal_BtagUp)
        signal_BtagDown_1d = unroll_hist(signal_BtagDown)
        signal_IsrUp_1d = unroll_hist(signal_IsrUp)
        signal_IsrDown_1d = unroll_hist(signal_IsrDown)

        data_obs_1d = unroll_hist(data_obs)
        background_1d = unroll_hist(bkg_pdf)

        writeDataCardSimple(datacards, data_obs_1d.Integral(),
                            signal_1d.Integral(), background_1d.Integral())
        outFile = rt.TFile.Open(datacards + '.root', 'RECREATE')
        signal_1d.Write()
        signal_PdfUp_1d.Write()
        signal_PdfDown_1d.Write()
        signal_JesUp_1d.Write()
        signal_JesDown_1d.Write()
        signal_BtagUp_1d.Write()
        signal_BtagDown_1d.Write()
        signal_IsrUp_1d.Write()
        signal_IsrDown_1d.Write()
        background_1d.Write()
        data_obs_1d.Write()
        outFile.Close()

    elif fitmode == '2D' and totalPDF == 'split':
        print 'Special case: split by b-tags, and split bkg PDF components'

        TTj1b_pdf = inFile.Get('BJetHS/'
                               'histo3DToyTTj1b_MRRsqBtag_FULL_ALLCOMPONENTS')
        TTj1b_pdf.SetName('TTj1b')
        TTj1b_pdf.SetTitle('TTj1b')
        TTj2b_pdf = inFile.Get('BJetHS/'
                               'histo3DToyTTj2b_MRRsqBtag_FULL_ALLCOMPONENTS')
        TTj2b_pdf.SetName('TTj2b')
        TTj2b_pdf.SetTitle('TTj2b')
        Vpj_pdf = inFile.Get('BJetHS/'
                             'histo3DToyVpj_MRRsqBtag_FULL_ALLCOMPONENTS')
        Vpj_pdf.SetName('Vpj')
        Vpj_pdf.SetTitle('Vpj')

        # Unroll all histograms
        for nb in range(1, 4):
            datacards = 'razor_combine_%s_%s_%s_%s' %\
                (box, MODEL, massPoint, nb)

            signal_1d = (unroll_2Dhist(signal, nb))
            signal_PdfUp_1d = (unroll_2Dhist(signal_PdfUp, nb))
            signal_PdfDown_1d = (unroll_2Dhist(signal_PdfDown, nb))
            signal_JesUp_1d = (unroll_2Dhist(signal_JesUp, nb))
            signal_JesDown_1d = (unroll_2Dhist(signal_JesDown, nb))
            signal_BtagUp_1d = (unroll_2Dhist(signal_BtagUp, nb))
            signal_BtagDown_1d = (unroll_2Dhist(signal_BtagDown, nb))
            signal_IsrUp_1d = (unroll_2Dhist(signal_IsrUp, nb))
            signal_IsrDown_1d = (unroll_2Dhist(signal_IsrDown, nb))

            TTj1b_1d = (unroll_2Dhist(TTj1b_pdf, nb))
            TTj2b_1d = (unroll_2Dhist(TTj2b_pdf, nb))
            Vpj_1d = (unroll_2Dhist(Vpj_pdf, nb))
            data_obs_1d = (unroll_2Dhist(data_obs, nb))

            writeDataCard(datacards, data_obs_1d.Integral(),
                          signal_1d.Integral(),
                          TTj1b_1d.Integral(), TTj2b_1d.Integral(),
                          Vpj_1d.Integral())

            outFile = rt.TFile.Open(datacards + '.root', 'RECREATE')
            signal_1d.Write()
            signal_PdfUp_1d.Write()
            signal_PdfDown_1d.Write()
            signal_JesUp_1d.Write()
            signal_JesDown_1d.Write()
            signal_BtagUp_1d.Write()
            signal_BtagDown_1d.Write()
            signal_IsrUp_1d.Write()
            signal_IsrDown_1d.Write()
            TTj1b_1d.Write()
            TTj2b_1d.Write()
            Vpj_1d.Write()
            data_obs_1d.Write()
            outFile.Close()
            signal_1d.Delete()
            signal_PdfUp_1d.Delete()
            signal_PdfDown_1d.Delete()
            signal_JesUp_1d.Delete()
            signal_JesDown_1d.Delete()
            signal_BtagUp_1d.Delete()
            signal_BtagDown_1d.Delete()
            signal_IsrUp_1d.Delete()
            signal_IsrDown_1d.Delete()
            TTj1b_1d.Delete()
            TTj2b_1d.Delete()
            Vpj_1d.Delete()
            data_obs_1d.Delete()

    elif fitmode == '2D' and totalPDF == 'totalPDF':
        print 'Special case: split by b-tags, and keep total bkg PDF'
        bkg_pdf = inFile.Get('BJetHS/histo3DToy_MRRsqBtag_FULL_ALLCOMPONENTS')
        bkg_pdf.SetName('background')
        bkg_pdf.SetTitle('background')

        for nb in range(1, 4):
            datacards = 'razor_combine_%s_%s_%s_%s' %\
                (box, MODEL, massPoint, nb)

            signal_1d = unroll_2Dhist(signal, nb)
            signal_PdfUp_1d = unroll_2Dhist(signal_PdfUp, nb)
            signal_PdfDown_1d = unroll_2Dhist(signal_PdfDown, nb)
            signal_JesUp_1d = unroll_2Dhist(signal_JesUp, nb)
            signal_JesDown_1d = unroll_2Dhist(signal_JesDown, nb)
            signal_BtagUp_1d = unroll_2Dhist(signal_BtagUp, nb)
            signal_BtagDown_1d = unroll_2Dhist(signal_BtagDown, nb)
            signal_IsrUp_1d = unroll_2Dhist(signal_IsrUp, nb)
            signal_IsrDown_1d = unroll_2Dhist(signal_IsrDown, nb)

            data_obs_1d = unroll_2Dhist(data_obs, nb)
            background_1d = unroll_2Dhist(bkg_pdf, nb)

            writeDataCardSimple(datacards, data_obs_1d.Integral(),
                                signal_1d.Integral(), background_1d.Integral())

            outFile = rt.TFile.Open(datacards + '.root', 'RECREATE')
            signal_1d.Write()
            signal_PdfUp_1d.Write()
            signal_PdfDown_1d.Write()
            signal_JesUp_1d.Write()
            signal_JesDown_1d.Write()
            signal_BtagUp_1d.Write()
            signal_BtagDown_1d.Write()
            signal_IsrUp_1d.Write()
            signal_IsrDown_1d.Write()
            background_1d.Write()
            data_obs_1d.Write()
            outFile.Close()
            signal_1d.Delete()
            signal_PdfUp_1d.Delete()
            signal_PdfDown_1d.Delete()
            signal_JesUp_1d.Delete()
            signal_JesDown_1d.Delete()
            signal_BtagUp_1d.Delete()
            signal_BtagDown_1d.Delete()
            signal_IsrUp_1d.Delete()
            signal_IsrDown_1d.Delete()
            background_1d.Delete()
            data_obs_1d.Delete()

    # # Check if bkg has bins with zero content, and fix it
    # check_for_zeros(background_1d, data_obs_1d)
