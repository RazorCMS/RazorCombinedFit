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
# for tanB = 40
#    M0M12Dict = {360:[400,600],560:[400,600],580:[400,600],
#                 720:[360,560],840:[300,540],
#                 1000:[200,460],1220:[160,400],
#                 1500:[160,400],1760:[160,400],
#                 1900:[160,400]}
# for tanB = 10 ORIGINAL
#    M0M12Dict = {120:[460,660],240:[460,660],
#                 380:[400,600],560:[400,600],
#                 720:[360,560],860:[300,540],
#                 1020:[200,460],1240:[160,400],
#                 1500:[160,400],1760:[160,400],
#                 1880:[160,400]}
# for tanB = 10 UPPER
#    M0M12Dict = {140:[460,760],240:[680,760],
#                 380:[620,760],560:[620,760],
#                 720:[580,760],840:[320,760],
#                 1020:[480,660],1240:[420,660],
#                 1500:[420,660],1760:[420,660],
#                 1880:[420,660]}
# for tanB = 10 Tot, Exp, Had, Lep, w/ Log Normal SYS scan
#    M0M12Dict = {120:[460,660],140:[460,760],240:[460,660],
#                 380:[400,660],560:[400,620],
#                 720:[360,620],860:[300,580],
#                 1020:[200,520],1240:[160,500],
#                 1500:[160,460],1760:[160,460],
#                 1880:[160,460]}
# for tanB = 10 Tot, Exp, Had, Lep, w/ Log Normal SYS scan
# with extra m0 strips
    M0M12Dict = {120:[460,660],180:[460,660],
                 240:[460,660],
                 380:[400,660],460:[400,660],
                 560:[400,620],
                 720:[360,620],
                 860:[300,580],980:[300,580],
                 1020:[200,520],1140:[200,500],
                 1240:[160,500],1360:[160,500],
                 1500:[160,460],1620:[160,460],
                 1760:[160,460],
                 1880:[160,460],1920:[160,460]}
# for tanB = 10 Had-only JES Test
#    M0M12Dict = {120:[400,660],240:[400,660],
#                 380:[400,600],560:[400,600],
#                 720:[360,600],860:[300,540],
#                 1020:[200,460],1240:[160,460],
#                 1500:[160,460],1760:[160,460],
#                 1880:[160,460]}
    m0m12pairs = [] 
    for m0 in M0M12Dict.keys():
        for m12 in xrange(M0M12Dict[m0][0],M0M12Dict[m0][1]+20,20):
            m0m12pairs.append([str(m0),str(m12)])

    for m0,m12 in m0m12pairs:
        print "Looking for CLs(tanB=%i,m0=%s,m12=%s) " %(tanB,m0,m12)    
        if os.path.exists("%s/CLs_m0_%s_m12_%s.root"%(pwd,m0,m12)): continue
       
#        Boxes = ["Had","Mu","Ele","MuMu","EleEle","MuEle"]
               
#        lenlist = [len(glob.glob("%s/LimitBkgToys*_M0-%s_M12-%s_%s_*.root"%(directory,m0,m12,Box))) for Box in Boxes]
#        if min(lenlist)==0: continue
#        lenlist = [len(glob.glob("%s/LimitBkgSigToys*_M0-%s_M12-%s_%s_*.root"%(directory,m0,m12,Box))) for Box in Boxes]
#        if min(lenlist)==0: continue
               
        if not glob.glob("%s/LimitBkgToys*_M0-%s_M12-%s_*.root"%(directory,m0,m12)): continue
        if not glob.glob("%s/LimitBkgSigToys*_M0-%s_M12-%s_*.root"%(directory,m0,m12)): continue
                
        print "Getting CLs(tanB=%i,m0=%s,m12=%s) " %(tanB,m0,m12)
        getCLs.getCLs(m0, m12,directory,tanB)
