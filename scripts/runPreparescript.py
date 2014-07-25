"""Script to run prepareCombineWorkspace.py on a mLSP strip"""
import sys, os
import ROOT as rt
import os.path

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
    ref_xsec = 1.e3*gluino_hist.GetBinContent(gluino_hist.FindBin(susy_mass))
    print "INFO: ref xsec taken to be: %s mass %d, xsec = %f fb" % \
        (gluino_hist_name, susy_mass, ref_xsec)

    return ref_xsec


if __name__ == '__main__':

    MODEL = sys.argv[1]

    strengthMod = ''
    # njets = '4jets'
    # box   = 'Ele'
    # name = 'Ele_4jets'
    box = 'BJetHS'
    njets = 'gt6'
    susy_xsecs = {150:80.268,
                  175:36.7994,
                  200:18.5245,
                  225:9.90959,
                  250:5.57596,
                  275:3.2781,
                  300:1.99608,
                  325:1.25277,
                  350:0.807323,
                  375:0.531443,
                  400:0.35683,
                  425:0.243755,
                  450:0.169688,
                  475:0.119275,
                  500:0.0855847,
                  525:0.0618641,
                  550:0.0452067,
                  575:0.0333988,
                  600:0.0248009,
                  625:0.0185257,
                  650:0.0139566,
                  675:0.0106123,
                  700:0.0081141,
                  725:0.00623244,
                  750:0.00480639,
                  775:0.00372717}

    for mass in range(400, 1425, 25):
    # for mass in range(150, 800, 25):

        if not os.path.isfile("Datasets/T1tttt/mLSP25/SMS-T1tttt_mGluino-"
                              "Combo_mLSP_25.0_8TeV-Pythia6Zstar-Summer12-"
                              "START52_V9_FSIM-v1-SUSY_MR450.0_R0.316227766017"
                              "_%s.0_25.0_%s.root" % (mass, box)):
            continue

        if MODEL != 'T1tttt':
            susy_xsecs[mass] *= 1000.

        # os.system( "python prepareCombineWorkspace.py --box %s
        # -i /afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/src/RazorCombinedFit/FitResults/razor_Single%s3D_%s_%s_FULL.root
        # --xsec %s -c /afs/cern.ch/user/l/lucieg/scratch1/Mar28_combine/CMSSW_6_1_2/src/RazorCombinedFit/config_summer2012/RazorMultiJet2013_3D_hybrid.config /afs/cern.ch/work/l/lucieg/private/MC/T2tt%s%s/mLSP25/SMS-T2tt_mStop-Combo_mLSP_25.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY_MR350.0_R0.282842712475_%s.0_25.0_%s.root"%(name, box, njets, box, str(susy_xsecs[mass]), box, njets, mass, box))


        if MODEL == 'T1tttt':
            os.system(("python scripts/prepareCombineWorkspace.py --box %s -i"
                       "/home/uscms208/cms/RazorCombinedFit_Git/fit_results/"
                       "fit_result_FULL_%s.root --xsec %s -c config_summer2012/"
                       "RazorMultiJet2013_3D_hybrid.config -m T1tttt "
                       "Datasets/T1tttt/mLSP25/"
                       "SMS-T1tttt_mGluino-Combo_mLSP_25.0_8TeV-Pythia6Zstar"
                       "-Summer12-START52_V9_FSIM-v1-SUSY_MR450.0_R0.316227766017_%s.0_25.0_%s.root") \
                      % (box, box, str(get_xsec(MODEL, mass)), mass, box))

        else:
            os.system(("python scripts/prepareCombineWorkspace.py --box %s -i"
                       "/home/uscms208/cms/RazorCombinedFit_Git/fit_results/"
                       "fit_result_FULL_%s.root --xsec %s -c config_summer2012/"
                       "RazorMultiJet2013_3D_hybrid.config Datasets/T2tt/mLSP25/"
                       "SMS-T2tt_mStop-Combo_mLSP_25.0_8TeV-Pythia6Z-Summer12-"
                       "START52_V9_FSIM-v1-SUSY_MR450.0_R0.316227766017_%s.0_25.0_"
                       "%s.root") \
                      % (box, box, str(susy_xsecs[mass]), mass, box))

        # os.system(" combine -M Asymptotic  razor_combine_%s_T2tt_MG_%s.000000_MCHI_25.000000.txt --rRelAcc 0.0001  -n T2tt_%s_25 --minimizerTolerance 0.0001"%(box, mass,mass))

        if MODEL == 'T1tttt':
            os.system("combine -M Asymptotic razor_combine_%s_%s_T1tttt_%s.0_25"
                      ".0.txt -n T1tttt_%s_25_%s_%s" % (box, njets, mass, mass,\
                                                        box, njets))
        else:
            os.system("combine -M Asymptotic  razor_combine_%s_%s_T2tt_%s.0_25.0.txt   -n T2tt_%s_25_%s_%s"%(box,njets, mass,mass, box, njets))
        os.system(" mkdir -p combine_files_%s_%s"%(njets, box))
        os.system(" mv razor_combine* combine_files_%s_%s"%(njets, box))
        os.system(" mv higgsCombine* combine_files_%s_%s"%(njets, box))
        os.system(" rm roostats*" )
