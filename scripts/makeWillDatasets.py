"""This script is to create all the datasets for the signal"""
from optparse import OptionParser
import os

if __name__ == '__main__':
    PARSER = OptionParser()
    PARSER.add_option('-d', '--directory', dest="out_dir", type="string",
                      default="./", help="Output directory")
    PARSER.add_option('-c', '--config', dest="config", type="string",
                      default=None, help="Config file")
    PARSER.add_option('-x', '--box', dest="box", type="string",
                      default="BJetHS", help="box")
    PARSER.add_option('-m', '--model', dest="model", type="string",
                      default="T2tt", help="Signal SMS")

    (OPTIONS, ARGS) = PARSER.parse_args()
    CFG = OPTIONS.config
    BOX = OPTIONS.box
    OUT_DIR = OPTIONS.out_dir
    MODEL = OPTIONS.model

    for mLSP in range(25, 50, 25):  # 725
        file_dir = OUT_DIR + "mLSP" + str(mLSP)

        # submit_dir is the same as file_dir
        log_dir = file_dir + "_log"

        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)

        pwd = os.environ['PWD']

        # for mStop in range(mLSP+100, 825, 25):
        for mStop in range(825, 1425, 25):
            print "Now creating (%s, %s)" % (mStop, mLSP)

            if MODEL == "T1tttt":
                print ("python scripts/Will2DatasetwithSYS.py --box %s -c %s "
                       "--mlsp=%s --mstop=%s -d %s root://osg-se.cac.cornell."
                       "edu//"
                       "xrootd/path/cms/store/user/salvati/Razor/MultiJet2012/"
                       "CMSSW_5_3_14/RMRTrees/T1tttt/SMS-T1tttt_"
                       "mGluino-Combo_mLSP_%s.0_8TeV-Pythia6Zstar-Summer12-"
                       "START52_V9_FSIM-v1-SUSY.root") % \
                        (BOX, CFG, mLSP, mStop, file_dir, mLSP)

            else:
                print ("python scripts/Will2DatasetwithSYS.py --box %s -c %s "
                       "--mlsp=%s --mstop=%s -d %s root://osg-se.cac.cornell."
                       "edu//"
                       "xrootd/path/cms/store/user/salvati/Razor/MultiJet2012/"
                       "CMSSW_5_3_14/RMRTrees/T2tt/SMS-T2tt_"
                       "mStop-Combo_mLSP_%s.0_8TeV-Pythia6Z-Summer12-START52_"
                       "V9_FSIM-v1-SUSY.root") % \
                          (BOX, CFG, mLSP, mStop, file_dir, mLSP)
            # os.system(("python scripts/Will2DatasetwithSYS.py --box %s -c %s "
            #            "--mlsp=%s --mstop=%s -d %s root://osg-se.cac.cornell."
            #            "edu//xrootd/path/cms/store/user/salvati/Razor/"
            #            "MultiJet2012/CMSSW_5_3_14/RMRTrees/T2tt/SMS-T2tt_"
            #            "mStop-Combo_mLSP_%s.0_8TeV-Pythia6Z-Summer12-START52_"
            #            "V9_FSIM-v1-SUSY.root") % \
            #           (BOX, CFG, mLSP, mStop, file_dir, mLSP))

            if MODEL == "T1tttt":
                file_name = (('SMS-T1tttt_mGluino-Combo_mLSP_%s.0_8TeV-'
                              'Pythia6Zstar-Summer12-START52_V9_FSIM-v1-SUSY_'
                              'MR450.0_R0.316227766017_%s.0_%s.0_%s.root') %\
                             (mLSP, mStop, mLSP, BOX))

            else:
                file_name = (('SMS-T2tt_mStop-Combo_mLSP_%s.0_8TeV-Pythia6Z-'
                              'Summer12-START52_V9_FSIM-v1-SUSY_MR450.0_'
                              'R0.316227766017_%s.0_%s.0_%s.root') %\
                             (mLSP, mStop, mLSP, BOX))
            runScriptName = file_dir + "/submit_script_%s_%s.sh" % (str(mStop),\
                                                                   str(mLSP))
            runScript = open(runScriptName, 'w')
            runScript.write('#$ -S /bin/sh\n')
            runScript.write('#$ -l arch=lx24-amd65\n')
            runScript.write('#$PBS -m ea\n')
            runScript.write('#$PBS -M es575@cornell.edu\n')
            runScript.write('#$PBS -j oe\n\n')
            runScript.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n\n')
            runScript.write('export SCRAM_ARCH=slc5_amd64_gcc472\n')
            runScript.write('cd %s\n' % pwd)
            runScript.write('eval `scramv1 runtime -sh`\n')
            runScript.write('source setup.sh ../\n')

            if MODEL == "T1tttt":
                runScript.write('xrdcp root://osg-se.cac.cornell.edu//xrootd/'
                                'path/cms/store/user/salvati/Razor/'
                                'MultiJet2012/CMSSW_5_3_14/RMRTrees/T1tttt/'
                                'SMS-T1tttt_mGluino-Combo_mLSP_25.0_8TeV-'
                                'Pythia6Zstar-Summer12-START52_V9_FSIM-v1-SUSY.'
                                'pkl /tmp/SMS-T1tttt_mGluino-Combo_mLSP_25.0_8'
                                'TeV-Pythia6Zstar-Summer12-START52_V9_FSIM-v1-'
                                'SUSY.pkl\n')
                runScript.write('python scripts/Will2DatasetwithSYS.py --box '
                                '%s '
                                '-c %s --mlsp=%s --mstop=%s -d /tmp/ '
                                'root://osg-se.'
                                'cac.cornell.edu//xrootd/path/cms/store/user/'
                                'salvati/Razor/MultiJet2012/CMSSW_5_3_14/'
                                'RMRTrees/'
                                'T1tttt/SMS-T1tttt_mGluino-Combo_mLSP_%s.0_8TeV'
                                '-Pythia6Zstar-Summer12-START52_V9_FSIM-v1'
                                '-SUSY.root\n\n' % (BOX, CFG, mLSP, mStop,
                                                    mLSP))
            else:
                runScript.write('xrdcp root://osg-se.cac.cornell.edu//xrootd/'
                                'path/'
                                'cms/store/user/salvati/Razor/MultiJet2012/'
                                'CMSSW_5_3_14/RMRTrees/T2tt/SMS-T2tt_mStop-'
                                'Combo.'
                                '0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-'
                                'SUSY.'
                                'pkl /tmp/SMS-T2tt_mStop-Combo.0_8TeV-Pythia6Z-'
                                'Summer12-START52_V9_FSIM-v1-SUSY.pkl\n')
                runScript.write('python scripts/Will2DatasetwithSYS.py --box '
                                '%s '
                                '-c %s --mlsp=%s --mstop=%s -d /tmp/ '
                                'root://osg-se.'
                                'cac.cornell.edu//xrootd/path/cms/store/user/'
                                'salvati/Razor/MultiJet2012/CMSSW_5_3_14/'
                                'RMRTrees/'
                                'T2tt/SMS-T2tt_mStop-Combo_mLSP_%s.0_8TeV-'
                                'Pythia6Z-'
                                'Summer12-START52_V9_FSIM-v1-SUSY.root\n\n' %\
                                (BOX, CFG, mLSP, mStop, mLSP))
            runScript.write('cp /tmp/%s %s/%s\n' %\
                            (file_name, file_dir, file_name))
            runScript.write('rm -f /tmp/%s\n\n' % file_name)
            runScript.write('exit')

            runScript.close()
            os.system('echo qsub %s -o %s' % (runScriptName, log_dir))
            os.system('qsub %s -o %s' % (runScriptName, log_dir))
