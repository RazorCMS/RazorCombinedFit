import sys, os


if __name__ == '__main__':

    for LSPmass in range(25,50,25):
        os.system('mkdir -p /afs/cern.ch/work/l/lucieg/private/RazorMultiJetJan2014/MC/T2ttEle4jets/mLSP'+str(LSPmass))
        for mass in range(700,  725, 25):

            os.system( "python Will2DatasetwithSYS.py -c ../config_summer2012/RazorMultiJet2013_3D_hybrid.config  /afs/cern.ch/work/l/lucieg/public/forRazorStop/SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY/SMS-T2tt_mStop-Combo_mLSP_%s.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY.root --mstop %s --mlsp %s -d  /afs/cern.ch/work/l/lucieg/private/RazorMultiJetJan2014/MC/T2ttEle4jets/mLSP%s/"%(LSPmass,mass,LSPmass,LSPmass) )
       
#--rAbsAcc 0.00001 --rRelAcc 0.00001
