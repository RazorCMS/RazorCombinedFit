import ROOT as rt
import os
import sys
import RootTools
import glob
import getCLs
from sets import Set

pwd = os.environ['PWD']

if __name__ == '__main__':
    directory = sys.argv[1]
    tanB = 10
    filemap = "/afs/cern.ch/user/w/woodson/scratch0/CMSSW_4_2_7/src/runMDLimit/mSUGRA_tanB10_SYS/mSUGRA_tanB10_PDF_M0-*"
    if len(sys.argv) > 2:
        filefilter = sys.argv[2]
        filemap = filemap.split('*')[0]+filefilter+'*'
    for filename in glob.glob(filemap):
        
        m0 = filename.split('.root')[0].split('_')[-2].split('-')[-1]
        m12 = filename.split('.root')[0].split('_')[-1].split('-')[-1]
        print "Looking for CLs(tanB=%i,m0=%s,m12=%s) " %(tanB,m0,m12)    
        if os.path.exists("%s/CLs_m0_%s_m12_%s.root"%(pwd,m0,m12)): continue
        
        Boxes = ["Had","Mu","MuMu","Ele","EleEle","MuEle"]
               
        lenlist = [len(glob.glob("%s/LimitBkgToys*_M0-%s_M12-%s_%s_*.root"%(directory,m0,m12,Box))) for Box in Boxes]
        if min(lenlist)==0: continue
        lenlist = [len(glob.glob("%s/LimitBkgSigToys*_M0-%s_M12-%s_%s_*.root"%(directory,m0,m12,Box))) for Box in Boxes]
        if min(lenlist)==0: continue
                
        print "Getting CLs(tanB=%i,m0=%s,m12=%s) " %(tanB,m0,m12)
        getCLs.getCLs(m0, m12,directory,tanB)
