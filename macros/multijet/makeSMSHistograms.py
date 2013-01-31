import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

import sys, pickle, array

def loadNorms():

    pkl = "/afs/cern.ch/user/w/wreece/public/Razor2012/SMS-T2tt_FineBin_Mstop-225to1200_mLSP-0to1000_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-PAT_CMG_V5_6_0_B.pkl"
    norms = pickle.load(file(pkl))
    
    def select_point(point):
        return (int(point[0]) % 50 == 0 and int(point[1]) in [0,100])
    
    result = {}
    for n in norms:
        if select_point(n):
            result[n] = norms[n]
    return result



if __name__ == '__main__':
    
    from optparse import OptionParser
    
    norms = loadNorms()
    print norms
    
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('--tree_name',dest="tree_name",type="string",default='EVENTS',
                  help="The name of the TTree to look at")
    
    (options,args) = parser.parse_args()

    if options.config is None:
        print 'No config file provided'
        sys.exit(-1)
    cfg = Config.Config(options.config)
    
    #take from the config
    binedgexLIST = []
    binedgeyLIST = []
    binning = cfg.getBinning('BJetLS')
    #MR and Rsq in that order
    binedgexLIST.extend(binning[0])
    binedgeyLIST.extend(binning[1])
    
    nbinx =  len(binedgexLIST)-1
    nbiny = len(binedgeyLIST)-1
    binedgex = array.array('d',binedgexLIST)
    binedgey = array.array('d',binedgeyLIST)
    
    boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'Mu':3,'Ele':4,'Had':5,'BJet':6,'BJetLS':7,'BJetHS':8}
    
    rootFile = rt.TFile.Open(args[0])
    tree = rootFile.Get(options.tree_name)
    
    for box in [3,4,8,7]:

        boxName = None
        for name, number in boxMap.iteritems():
            if number == box:
                boxName = name        
        output = rt.TFile.Open('signal_%s_%s.root' % (options.tree_name,boxName),'recreate')
        
        wHisto = rt.TH2D("wHisto","Nominal for BOX_NUM=%d" %box, nbinx, binedgex, nbiny, binedgey)
        BTAGerr = rt.TH2D("BTAGerr","Btag error for BOX_NUM=%d" %box, nbinx, binedgex, nbiny, binedgey)
        JESerr = rt.TH2D("JESerr","JES error for BOX_NUM=%d" %box, nbinx, binedgex, nbiny, binedgey)
        PDFerr = rt.TH2D("PDFerr","PDF error for BOX_NUM=%d" %box, nbinx, binedgex, nbiny, binedgey)
        
        tree.Project("wHisto", "RSQ:MR","LEP_W*W_EFF*(BOX_NUM==%d)"%box)
        
        wHisto.Write()
        BTAGerr.Write()
        JESerr.Write()
        PDFerr.Write()
        output.Close()
        
    rootFile.Close()
    