import eostools
import os.path

import pickle
from submitT2tt import makeTreeList

def filter(files, regexp):
    import re
    pattern = re.compile( regexp )
    # print files
    return [f for f in files if pattern.match(os.path.basename(f)) is not None]

def findMissing(files, minimum):

    def getIndex(fileName):
        return int(fileName.replace('.root','').split('_')[-1])
    files.sort()

    indexes = [getIndex(f) for f in files]

    missing = []
    for i in xrange(minimum,minimum+100):
        if not i in indexes:
            missing.append(i)
    return missing

def printCommands(missing,treeName, xsec):

    mStop = int(treeName.split('_')[-2])
    mLSP = int(treeName.split('_')[-1])

    pwd = os.getcwd()
    jobdir = os.path.join( pwd,'Job_%i_%s' % (mStop,mLSP) )

    signal = 'SMS-T2tt_Mstop-225to1200_mLSP-50to1025_7TeV-Pythia6Z-Summer11-PU_START42_V11_FastSim-v1-wreece_080212-SMS-ByPoint'
    for i in missing:
        
        outputFileName = "%s_%s_xsec_%f" %(signal,treeName, xsec)
        outputname = os.path.join(jobdir,"%s_%i.src" %(outputFileName,i))
        assert os.path.exists(outputname),'The src file %s does not exist' % outputname

        name = '%s_%f_RESUB' % (treeName,xsec)
        cmd = "bsub -q 8nh -J "+name+" source "+outputname
        print cmd
        print 'sleep 0.1'
    

if __name__ == '__main__':

    import sys

    xsec = 0.01
    index = 5001

    import pickle
    root_files = pickle.load(file("root_files.pkl"))
    output = sys.argv[1]

    import os.path

    for r in root_files:
        base = os.path.basename(r)

        out = os.path.join(output,base)
        if not os.path.exists(out):
            #xrdcp root://eoscms//eos/cms/store/cmst3/user/wreece/Razor2011/MultiJetAnalysis/scratch0/T2tt/LimitBkgSigToys_SMS-T2tt_Mstop-225to1200_mLSP-50to1025_7TeV-Pythia6Z-Summer11-PU_START42_V11_FastSim-v1-wreece_080212-SMS-ByPoint_RMRTree_1025_100_xsec_0.010000_RMRTree_1025_100_5001.root /tmp/wreece/
            print 'xrdcp root://eoscms//eos/cms%s %s' % (r,output)
        
