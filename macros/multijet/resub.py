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
        print 'sleep 1'
    

if __name__ == '__main__':

    xsec = 0.01
    index = 1001

    import pickle
    root_files = pickle.load(file("root_files.pkl"))
    trees = makeTreeList(50)

    bkg = filter(root_files,'LimitBkgToys.*RMRTree_[0-9]+_[0-9]+_%s[0-9]+\\.root$' % str(index)[0] )
    for tree in trees:
        point_files = filter(bkg,'LimitBkgToys.*%s_[0-9]+\\.root$' % tree)
        missing = findMissing(point_files, index)
        printCommands(missing,tree,xsec)
        #break
    
    
