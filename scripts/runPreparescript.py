"""Script to run prepareCombineWorkspace.py on a mLSP strip"""
import sys
import os
import ROOT as rt
import os.path
from optparse import OptionParser


def get_xsec(model, susy_mass):
    """Return the xsec for a given mass and model"""
    if model == 'T2tt':
        ref_xsec_file = './stop.root'
    elif model == 'T1tttt':
        ref_xsec_file = './gluino.root'

    print "INFO: Input ref xsec file!"
    gluino_file = rt.TFile.Open(ref_xsec_file, "READ")
    gluino_hist_name = ref_xsec_file.split("/")[-1].split(".")[0]
    gluino_hist = gluino_file.Get(gluino_hist_name)
    ref_xsec = gluino_hist.GetBinContent(gluino_hist.FindBin(susy_mass))
    print "INFO: ref xsec taken to be: %s mass %d, xsec = %f pb" % \
        (gluino_hist_name, susy_mass, ref_xsec)

    return ref_xsec


if __name__ == '__main__':

    PARSER = OptionParser()
    PARSER.add_option('--fitMode', dest='fitMode', default='3D', type='string',
                      help='2D or 3D fit')
    PARSER.add_option('--totalPDF', dest='pdfMode', default='split',
                      type='string',
                      help='limit on the total bkg PDF, or on the individual '
                      'bkg components')

    (options, args) = PARSER.parse_args()

    MODEL = args[0]
    box = args[1]
    smsdir = args[2]
    fitMode = options.fitMode
    pdfMode = options.pdfMode

    if MODEL == 'T1tttt':
        mass_range = range(400, 1425, 25)
    elif MODEL == 'T2tt':
        mass_range = range(150, 800, 25)

    if box in ['Ele', 'Mu']:
        mr_point = 'MR350.0_R0.387298334621'
    else:
        mr_point = 'MR450.0_R0.316227766017'

    for mass in mass_range:

        if MODEL == 'T1tttt' and not\
            os.path.isfile("Datasets/T1tttt_complete/%s/mLSP_25/"
                           "SMS-T1tttt_mGluino-"
                           "Combo_mLSP_25.0_8TeV-Pythia6Zstar-Summer12-"
                           "START52_V9_FSIM-v1-SUSY_%s"
                           "_%s.0_25.0_%s.root" % (box, mr_point, mass, box)):
            continue

        elif MODEL == 'T2tt' and box in ['Ele', 'Mu'] and not\
            os.path.isfile("%s/SMS-T2tt_mStop-Combo_mLSP_25.0_8TeV-Pythia6Z"
                           "-Summer12-START52_V9_FSIM-v1-SUSY_"
                           "%s_%s.0_25.0_%s.root" %
                           (smsdir, mr_point, mass, box)):
            continue

        elif MODEL == 'T2tt' and box in ['BJetHS', 'BJetLs'] and not\
            os.path.isfile("tmp_Datasets_Aug11/mLSP_25/SMS-T2tt_mStop-Combo_"
                           "mLSP_25.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-"
                           "v1-SUSY_%s_%s.0_25.0_%s.root"
                           % (mr_point, mass, box)):
            continue

        if MODEL == 'T1tttt':
            os.system(("python scripts/prepareCombineSimple.py --box %s -i"
                       "/home/uscms208/cms/CMSSW_6_1_2/src/"
                       "RazorCombinedFit_lucieg_May29/fit_results/"
                       "razor_output_Rsq_gte0.15_%s.root "
                       "--refXsecFile ./gluino.root "
                       "--fitmode=%s --pdfmode=%s "
                       "Datasets/T1tttt_complete/%s/mLSP_25/"
                       "SMS-T1tttt_mGluino-Combo_mLSP_25.0_8TeV-Pythia6Zstar"
                       "-Summer12-START52_V9_FSIM-v1-SUSY_%s_"
                       "%s.0_25.0_%s.root %s")
                      % (box, box, fitMode, pdfMode, box, mr_point,
                         mass, box, MODEL))

        elif MODEL == 'T2tt' and box in ['Ele', 'Mu']:
            os.system(('python scripts/prepareCombineSimple.py --box %s -i '
                       '/home/uscms208/cms/CMSSW_6_1_2/src/'
                       'RazorCombinedFit_lucieg_May29/fit_results/'
                       'razor_output_Rsq_gte0.15_%s.root '
                       '--refXsecFile ./stop.root '
                       '--fitmode=%s --pdfmode=%s --leptonic '
                       '%s/SMS-T2tt_mStop-Combo_mLSP_25.0_8TeV-Pythia6Z-'
                       'Summer12-START52_V9_FSIM-v1-SUSY_%s_%s.0_25.0_%s.root'
                       ' %s')
                      % (box, box, fitMode, pdfMode, smsdir, mr_point,
                         mass, box, MODEL))

        elif MODEL == 'T2tt':
            os.system(("python scripts/prepareCombineSimple.py --box %s -i"
                       "/home/uscms208/cms/CMSSW_6_1_2/src/"
                       "RazorCombinedFit_lucieg_May29/fit_results/"
                       "razor_output_Rsq_gte0.15_%s.root "
                       "--refXsecFile ./stop.root "
                       "--fitmode=%s --pdfmode=%s "
                       "tmp_Datasets_Aug11/mLSP_25/"
                       "SMS-T2tt_mStop-Combo_mLSP_25.0_8TeV-Pythia6Z-"
                       "Summer12-START52_V9_FSIM-v1-SUSY_%s_"
                       "%s.0_25.0_%s.root %s")
                      % (box, box, fitMode, pdfMode, mr_point,
                         mass, box, MODEL))

        if fitMode == '2D':
            for nb in range(1, 4):
                os.system("combine -M Asymptotic razor_combine_%s_%s_"
                          "%s.0_25.0_%s.txt -n %s_%s_%s_25_%s" %
                          (box, MODEL, mass, nb, box, MODEL, mass, nb))
        elif fitMode == '3D':
            os.system("combine -M Asymptotic razor_combine_%s_%s_"
                      "%s.0_25.0.txt -n %s_%s_%s_25" %
                      (box, MODEL, mass, box, MODEL, mass))

    os.system(" mkdir -p Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s" %
              (MODEL, box, fitMode, pdfMode))
    os.system(" mv razor_combine* Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s" %
              (MODEL, box, fitMode, pdfMode))
    os.system(" mv higgsCombine* Tests/Rsq_gte0.15/combine_files_%s_%s_%s_%s" %
              (MODEL, box, fitMode, pdfMode))
    os.system(" rm roostats*")
