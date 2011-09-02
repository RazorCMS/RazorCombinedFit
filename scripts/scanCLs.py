import ROOT as rt
import os
import sys
import RootTools
import glob
import getCLs
from sets import Set

pwd = os.environ['PWD']
def checkifexists(arginput):
    os.system("rm %s.list; ls %s > %s.list" %(arginput.split(".root")[0],arginput,arginput.split(".root")[0]))
    if os.stat('%s.list'%arginput.split(".root")[0]).st_size > 0:
        os.system("rm %s.list"%arginput.split(".root")[0])  
        return True
    os.system("rm %s.list"%arginput.split(".root")[0])            
    return False

if __name__ == '__main__':
    directory = sys.argv[1]
    filter = sys.argv[2]
    for filename in glob.glob("/data1/woodson/mSUGRA_tanB10_42X/mSUGRA_tanB10_M0-%s*.root" %filter):
        
        m0 = filename.split('.root')[0].split('_')[-2].split('-')[-1]
        m12 = filename.split('.root')[0].split('_')[-1].split('-')[-1]
        print "Looking for CLs(m0=%s,m12=%s) " %(m0,m12)    
        if os.path.exists("%s/CLs_m0_%s_m12_%s.root"%(pwd,m0,m12)): continue
        #if float(m0)>600 or float(m12)<500: continue
        Boxes = ["Had","Mu","MuMu","MuEle","Ele","EleEle"]
        lenlist = [len(glob.glob("%s/LimitBkgToys*_M0-%s_M12-%s_%s_*.root"%(directory,m0,m12,Box))) for Box in Boxes]
        if min(lenlist)==0: continue
        lenlist = [len(glob.glob("%s/LimitBkgSigToys*_M0-%s_M12-%s_%s_*.root"%(directory,m0,m12,Box))) for Box in Boxes]
        if min(lenlist)==0: continue
                
        print "Getting CLs(m0=%s,m12=%s) " %(m0,m12)
        getCLs.getCLs(m0, m12,directory)
