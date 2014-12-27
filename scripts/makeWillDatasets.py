"""This script is to create all the datasets for the signal"""
from optparse import OptionParser
import os
import pickle as pkl
import sys


def read_pkl_file(pklfile):
    """Simple function to read a pickle file"""

    pickle_file = pkl.load(open(pklfile, 'rb'))
    return pickle_file


def check_mass(mstop, mlsp, pklfile):
    """Check if we have events in the SMS for a given mass point"""
    masses = (mstop, mlsp)
    if masses in pklfile:
        return True
    return False


if __name__ == '__main__':
    PARSER = OptionParser()
    PARSER.add_option('-d', '--directory', dest="out_dir", type="string",
                      default="./", help="Output directory")
    PARSER.add_option('-c', '--config', dest="config", type="string",
                      default=None, help="Config file")
    PARSER.add_option('-x', '--box', dest="box", type="string",
                      default="BJetHS", help="box")
    PARSER.add_option('-m', '--model', dest="model", type="string",
                      default=None, help="Signal SMS")
    PARSER.add_option('-p', '--pickle', dest="pk_file", type="string",
                      default=None, help="Pickle file")

    (OPTIONS, ARGS) = PARSER.parse_args()
    CFG = OPTIONS.config
    BOX = OPTIONS.box
    MODEL = OPTIONS.model

    # This is for data
    if MODEL is None:
        print 'We are doing data now'

        DATA_LOCATION = ('root://osg-se.cac.cornell.edu//'
                         'xrootd/path/cms/store/user/salvati/Razor/'
                         'MultiJet2012/CMSSW_5_3_14/mergedRMRTrees/')

        DATA_FILES = ARGS[1:]
        i = 0
        DATA = []
        while i < len(DATA_FILES):
            DATA.append(DATA_LOCATION + DATA_FILES[i])
            i += 1

        COMMAND_STRING = ("python scripts/Will2Dataset.py --box %s -c %s "
                          "-d /tmp/ %s ") % \
            (BOX, CFG, ARGS[0])

        for IN_FILE in DATA:
            COMMAND_STRING = COMMAND_STRING + IN_FILE + " "
        print COMMAND_STRING

        pwd = os.environ['PWD']
        runScriptName = "submit_script_%s.sh" % ARGS[0]
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
        runScript.write('source setup.sh ../\n\n')
        runScript.write(COMMAND_STRING + '\n')
        runScript.write('cp /tmp/%s*.root %s/%s.root\n' %
                        (ARGS[0], pwd, ARGS[0]))
        runScript.write('rm -f /tmp/%s*\n\n' % ARGS[0])
        runScript.write('exit')

        runScript.close()

        os.system('echo qsub %s' % runScriptName)
        # os.system('qsub %s' % runScriptName)

    # This is for signals
    else:
        PKL = OPTIONS.pk_file
        AVAILABLE_MASSES = read_pkl_file(PKL)
        OUT_DIR = OPTIONS.out_dir

        if MODEL == "T1tttt":
            LSP_MASSES = range(25, 50, 25)
            # LSP_MASSES = [1] + range(25, 1625, 25)
            STOP_MASSES = range(100, 1625, 25)
        else:
            # LSP_MASSES = range(25, 725, 25)
            LSP_MASSES = range(25, 50, 25)
            STOP_MASSES = range(125, 825, 25)

        for mLSP in LSP_MASSES:
            file_dir = OUT_DIR + "mLSP_" + str(mLSP)
            script_dir = file_dir + "_sh"
            log_dir = file_dir + "_log"

            if not os.path.isdir(file_dir):
                os.mkdir(file_dir)
            if not os.path.isdir(script_dir):
                os.mkdir(script_dir)
            if not os.path.isdir(log_dir):
                os.mkdir(log_dir)

            pwd = os.environ['PWD']

            for mStop in STOP_MASSES:

                if check_mass(mStop, mLSP, AVAILABLE_MASSES):
                    print "We have this mass:", (mStop, mLSP)
                else:
                    continue

                if not os.path.isdir(file_dir):
                    os.mkdir(file_dir)
                if not os.path.isdir(script_dir):
                    os.mkdir(script_dir)
                if not os.path.isdir(log_dir):
                    os.mkdir(log_dir)

                if MODEL == "T1tttt":
                    print ("python scripts/Will2DatasetwithSYS.py --box %s -c %s "
                           "--mlsp=%s --mstop=%s -d %s root://osg-se.cac.cornell."
                           "edu//"
                           "xrootd/path/cms/store/user/salvati/Razor/MultiJet2012/"
                           "CMSSW_5_3_14/RMRTrees/T1tttt_merged/SMS-T1tttt_"
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

                if BOX in ['Ele', 'Mu']:
                    mr_point = 'MR350.0_R0.282842712475'
                else:
                    mr_point = 'MR450.0_R0.316227766017'

                if MODEL == "T1tttt":
                    file_name = (('SMS-T1tttt_mGluino-Combo_mLSP_%s.0_8TeV-'
                                  'Pythia6Zstar-Summer12-START52_V9_FSIM-v1-SUSY_'
                                  '%s_%s.0_%s.0_%s.root') %
                                 (mLSP, mr_point, mStop, mLSP, BOX))

                else:
                    file_name = (('SMS-T2tt_mStop-Combo_mLSP_%s.0_8TeV-Pythia6Z-'
                                  'Summer12-START52_V9_FSIM-v1-SUSY_'
                                  '%s_%s.0_%s.0_%s.root') %
                                 (mLSP, mr_point, mStop, mLSP, BOX))

                runScriptName = script_dir + "/submit_script_%s_%s.sh"\
                    % (str(mStop), str(mLSP))
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
                                    'MultiJet2012/CMSSW_5_3_14/RMRTrees/'
                                    'T1tttt_merged/'
                                    'SMS-T1tttt_mGluino-Combo_8TeV-'
                                    'Pythia6Zstar-Summer12-START52_V9_FSIM-v1-SUSY.'
                                    'pkl /tmp/SMS-T1tttt_mGluino-Combo_8'
                                    'TeV-Pythia6Zstar-Summer12-START52_V9_FSIM-v1-'
                                    'SUSY.pkl\n')
                    runScript.write('python scripts/Will2DatasetwithSYS.py --box '
                                    '%s '
                                    '-c %s --mlsp=%s --mstop=%s -d /tmp/ '
                                    'root://osg-se.'
                                    'cac.cornell.edu//xrootd/path/cms/store/user/'
                                    'salvati/Razor/MultiJet2012/CMSSW_5_3_14/'
                                    'RMRTrees/'
                                    'T1tttt_merged/SMS-T1tttt_mGluino-Combo_mLSP_%s.0_8TeV'
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
                                    'Summer12-START52_V9_FSIM-v1-SUSY.root\n\n' %
                                    (BOX, CFG, mLSP, mStop, mLSP))
                runScript.write('cp /tmp/%s %s/%s\n' %
                                (file_name, file_dir, file_name))
                runScript.write('rm -f /tmp/%s\n\n' % file_name)
                runScript.write('exit')

                runScript.close()
                os.system('echo qsub %s -o %s' % (runScriptName, log_dir))
                os.system('qsub %s -o %s' % (runScriptName, log_dir))
