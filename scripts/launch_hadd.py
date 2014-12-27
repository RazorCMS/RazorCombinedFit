#!/usr/bin/env python
"""This is to submit hadd of some root files to the PBS queue"""

import sys
import re
import os

if __name__ == '__main__':
    ARGS = sys.argv[1:]
    if not ARGS:
        print "usage: launch_hadd.py <out-file.root> <in-files-*.root>"
        sys.exit(1)

    OUT_FILE = ARGS[0]
    IN_FILE_LIST = ARGS[1:]

    PWD = os.environ['PWD']

    SUBMIT_FILE = open('hadd_launcher.sh', 'w')
    SUBMIT_FILE.write('#$ -S /bin/sh\n')
    SUBMIT_FILE.write('#$ -l arch=lx24-amd64\n')
    SUBMIT_FILE.write('#PBS -m ea\n')
    SUBMIT_FILE.write('#PBS -M es575@cornell.edu\n')
    SUBMIT_FILE.write('#$ -l mem_total=2G\n')
    SUBMIT_FILE.write('#PBS -j oe\n\n')
    SUBMIT_FILE.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    SUBMIT_FILE.write('export SCRAM_ARCH=slc5_amd64_gcc472\n')
    SUBMIT_FILE.write('cd %s\n' % PWD)
    SUBMIT_FILE.write('eval `scramv1 runtime -sh`\n\n')

    IN_FILE_LIST.insert(0, 'hadd -f /tmp/%s' % str(OUT_FILE))
    # IN_FILE_LIST.insert(1, str(OUT_FILE))
    SUBMIT_SCRIPT = ' '.join(IN_FILE_LIST)
    LFN_SUBMIT_SCRIPT = re.sub('/mnt/xrootd/',
                               'root://osg-se.cac.cornell.edu/'
                               '/xrootd/path/cms/store/', SUBMIT_SCRIPT)
    SUBMIT_FILE.write(LFN_SUBMIT_SCRIPT + '\n')
    # SUBMIT_FILE.write('xrdcp /tmp/' + OUT_FILE + ' ./' + OUT_FILE + '\n')
    # SUBMIT_FILE.write('xrdcp /tmp/' + OUT_FILE + ' root://osg-se.cac.cornell.edu//xrootd/path/cms/store/user/salvati/Razor/MultiJet2012/CMSSW_5_3_14/RMRTrees/T1tttt_merged/' + OUT_FILE + '\n')
    SUBMIT_FILE.write('xrdcp /tmp/' + OUT_FILE + ' root://osg-se.cac.cornell.'
                      'edu//xrootd/path/cms/store/user/salvati/Razor/'
                      'MultiJet2012/CMSSW_5_3_14/mergedRMRTrees/' +
                      OUT_FILE + '\n')
    SUBMIT_FILE.write('exit')
    SUBMIT_FILE.close()
