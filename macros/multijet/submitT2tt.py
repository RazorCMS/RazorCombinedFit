import os
import glob

import pickle

def makeTreeList(step):
    """Make a list of trees to look at with a toy"""

    import pickle
    fileName = "/afs/cern.ch/user/w/wreece/work/LimitSetting/RazorMultiJet2011/SMS-T2tt_Mstop-225to1200_mLSP-50to1025_7TeV-Pythia6Z-Summer11-PU_START42_V11_FastSim-v1-wreece_030412-ByPoint.pkl"
    SMSPoints = pickle.load(file(fileName))
    keys = sorted(SMSPoints.keys())

    massStop = set()
    massLSP = set()
    for k in keys:
        massStop.add(k[0])
        massLSP.add(k[1])

    massPointsStop = sorted([m for m in massStop])
    massPointsLSP = sorted([m for m in massLSP])
    
    treeList = set()
    for i in xrange(len(massPointsStop)):
        for j in xrange(len(massPointsLSP)):
            point = (massPointsStop[i],massPointsLSP[j])
            if SMSPoints.has_key(point):
                if ((point[0]-massPointsStop[0]) % step) == 0 and ((point[1]-massPointsLSP[0]) % step) == 0:
                    treeList.add('RMRTree_%i_%i' % point)

    #shuffle to spread the mass points out
    result = [t for t in treeList]
    import random                
    random.shuffle(result)
    return result

if __name__ == "__main__":

    xsec = 10
    index = 1001

    config = "config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg"
    fitName = "/afs/cern.ch/user/w/wreece/work/LimitSetting/RazorMultiJet2011/BJet_FitRegion_10b.root"
    SMSTree = "/afs/cern.ch/user/w/wreece/work/LimitSetting/RazorMultiJet2011/SMS-T2tt_Mstop-225to1200_mLSP-50to1025_7TeV-Pythia6Z-Summer11-PU_START42_V11_FastSim-v1-wreece_030412-ByPoint-2.root"

    treeList = makeTreeList(50)
    for tree in treeList:
        cmd = "python runMDLimit_SMS.py --multijet -t 50 -i %i -n 20 -q 2nd --xsec %f --input %s --tree_name %s --config %s %s" % (index,xsec,fitName,tree,config,SMSTree)
        print cmd
        #print 'sleep 120'
