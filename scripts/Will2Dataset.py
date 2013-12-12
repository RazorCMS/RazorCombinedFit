from optparse import OptionParser
import os, array, sys

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'Mu':3,'Ele':4,'Had':5,'BJet':6,'BJetLS':7,'BJetHS':8}
cross_sections = {'SingleTop_s':4.21,'SingleTop_t':64.6,'SingleTop_tw':10.6,\
                               'TTj':157.5,'Zll':3048,'Znn':2*3048,'Wln':31314,\
                               'WW':43,'WZ':18.2,'ZZ':5.9,'Vgamma':173
                               }
lumi = 1.0

#sys.path.append(os.path.join(os.environ['RAZORFIT_BASE'],'macros/multijet'))
from CalcBDT import CalcBDT

MR_CUT_HAD  = 500.
MR_CUT_LEP  = 350.
RSQ_CUT     = 0.08
BDT_CUT     = -0.2

class BJetBoxLS(object):
    """The BJet search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'BJetLS'
        self.dumper = dumper
    def __call__(self, tree):
        return  tree.hadBoxFilter and tree.nJet >=6  and tree.hadTriggerFilter and tree.nCSVM > 0 and tree.MR >= MR_CUT_HAD and tree.RSQ >= RSQ_CUT and\
            tree.nMuonTight == 0 and tree.nElectronTight == 0 and not tree.isolatedTrack10Filter and tree.nMuonLoose == 0 and tree.nElectronLoose == 0 and self.dumper.bdt() < BDT_CUT 

class BJetBox(object):
    """The BJet search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'BJet'
        self.dumper = dumper
    def __call__(self, tree):
         return  tree.hadBoxFilter and tree.nJet >=6  and tree.nCSVM > 0 and tree.MR >= MR_CUT_HAD and tree.RSQ >= RSQ_CUT and tree.nMuonTight < 1 and tree.nElectronTight < 1 and not tree.isolatedTrack10Filter and tree.nMuonLoose < 1 and tree.nElectronLoose < 1 and tree.hadTriggerFilter  

 
class BJetBoxHS(object):
    """The BJet search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'BJetHS'
        self.dumper = dumper
    def __call__(self, tree):
        return  tree.hadBoxFilter and  tree.nJet >= 6  and tree.hadTriggerFilter and tree.nCSVM > 0 and tree.MR >= MR_CUT_HAD and tree.RSQ >= RSQ_CUT and\
            tree.nMuonTight == 0 and tree.nElectronTight == 0 and not tree.isolatedTrack10Filter and tree.nMuonLoose == 0 and tree.nElectronLoose == 0 and self.dumper.bdt() >= BDT_CUT 

class MuBox(object):
    """The Mu search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'Mu'
        self.dumper = dumper
    def __call__(self, tree):
        return tree.muBoxFilter and tree.nJetNoLeptons ==4 and tree.muTriggerFilter and tree.nCSVM > 0 and tree.MR >= MR_CUT_LEP and tree.RSQ >= RSQ_CUT and\
            tree.nMuonTight == 1 and tree.nElectronTight == 0 and tree.nMuonLoose == 1 and tree.nElectronLoose == 0 and not tree.isolatedTrack10LeptonFilter 

class EleBox(object):
    """The Ele search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'Ele'
        self.dumper = dumper
    def __call__(self, tree):
            return tree.eleBoxFilter and tree.nJetNoLeptons >3  and tree.eleTriggerFilter and tree.nCSVM > 0 and tree.MR >= MR_CUT_LEP and tree.RSQ >= RSQ_CUT and tree.nMuonTight == 0 and tree.nElectronTight == 1 and tree.nMuonLoose == 0 and tree.nElectronLoose == 1 and not tree.isolatedTrack10LeptonFilter 

        
            
class SelectBox(object):
    """Tells you which box this was"""
    def __init__(self,tree):
        self.selectors = {boxMap['BJetLS']:BJetBoxLS(CalcBDT(tree)),boxMap['BJetHS']:BJetBoxHS(CalcBDT(tree)),boxMap['Ele']:EleBox(None),boxMap['Mu']:MuBox(None)}
        self.tree = tree
    def box(self):
        for i in [3,4,8,7]:
            if self.selectors[i](self.tree):
                return i
        return -1
        

def writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin):
    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_BTAG_'+outputBox,'RECREATE')
    print 'writing dataset to ', output.GetName()
    for d in data:
        d.Write()
    output.Close()

def deltaMet(tree):
    """Javier's noise suppression cut"""
    pf = rt.TMath.ATan(tree.met_y/tree.met_x)
    #skip for MC that does not have the calo met present
    try:
        calo = rt.TMath.ATan(tree.caloMET_y/tree.caloMET_x)
    except ZeroDivisionError:
        calo = pf
    pi = rt.TMath.Pi() 
    return abs( min( (pf - calo), ( (2*pi) - pf + calo) ) - pi)

def convertTree2Dataset(tree, outputFile, config, min, max, filter, run, write = True):
    """This defines the format of the RooDataSet"""
    
    box = filter.name
    workspace = rt.RooWorkspace(box)
    variables = config.getVariablesRange(box,"variables",workspace)
    workspace.factory('W[0,0,+INF]')
   
    if filter.dumper is not None:
        for h in filter.dumper.sel.headers_for_MVA():
            workspace.factory('%s[0,-INF,+INF]' % h)
    
    args = workspace.allVars()
    data = rt.RooDataSet('RMRTree','Selected R and MR',args)
    
    #we cut away events outside our MR window
    mRmin = args['MR'].getMin()
    mRmax = args['MR'].getMax()

    #we cut away events outside our Rsq window
    rsqMin = args['Rsq'].getMin()
    rsqMax = args['Rsq'].getMax()
    rMin = rt.TMath.Sqrt(rsqMin)
    rMax = rt.TMath.Sqrt(rsqMax)
   
    events = set()
    
    selectionFilter = 0
    noiseFilter = 0
    metFilter = 0
    
    #entries = 10000
    ent=1
    entries = tree.GetEntries()
    print entries
    for entry in xrange(entries):
        tree.GetEntry(entry)
      
        e = (tree.run,tree.lumi,tree.event)
        #filter out duplicate events in case there are any
        if e in events:
            print 'duplicate found'
            continue
        events.add(e)        
        
        if not tree.metFilter:
            metFilter += 1
            print 'met'
            continue
        
        dphi = deltaMet(tree)
        if dphi < 1.0:
            noiseFilter += 1
            print 'noise'
            continue
        
        #apply the box based filter class
        if not filter(tree):
            selectionFilter += 1
            continue        
        
        bdt = -9999.
        if filter.dumper is not None:
            bdt = filter.dumper.bdt_val

        try:
            if tree.run <= run:
                continue
        except AttributeError:
            pass
        
        nBtag = tree.nCSVM

        #a.setRealValue('nJet',tree.nJet)

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        
        a.setRealValue('MR',tree.MR)
        a.setRealValue('Rsq',tree.RSQ)
        btagcutoff = 3
        if tree.nCSVM >= btagcutoff:
            a.setRealValue('nBtag',btagcutoff)
        else:
            a.setRealValue('nBtag',tree.nCSVM)

        
        a.setRealValue('nLepton',tree.nMuonLoose + tree.nElectronLoose + tree.nTauLoose)
        a.setRealValue('W',1.0)

        if filter.dumper is not None:
            for h in filter.dumper.sel.headers_for_MVA():
                a.setRealValue(h,getattr(filter.dumper.sel,h)())
        
        data.add(a)
        
    numEntries = data.numEntries()
    if min < 0: min = 0
    if max < 0: max = numEntries
    
    try:
        print 'Selection filter removed %f of events' % (selectionFilter/(1.0*entries))
        print 'Noise filter removed %f of events' % (noiseFilter/(1.0*entries))
        print 'MET filter removed %f of events' % (metFilter/(1.0*entries))
    except ZeroDivisionError:
        pass
    
    rdata = data.reduce(rt.RooFit.EventRange(min,max))
    if write:
        writeTree2DataSet([rdata], outputFile, '%s.root' % filter.name, rMin, mRmin)
       
    return rdata

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('--max',dest="max",type="int",default=-1,
                  help="The last event to take from the input Dataset")
    parser.add_option('--min',dest="min",type="int",default=0,
                  help="The first event to take from the input Dataset")  
    parser.add_option('-b','--btag',dest="btag",type="int",default=-1,
                  help="The maximum number of Btags to allow")     
    parser.add_option('-e','--eff',dest="eff",default=False,action='store_true',
                  help="Calculate the MC efficiencies")
    parser.add_option('-f','--flavour',dest="flavour",default='TTj',
                  help="The flavour of MC used as input")
    parser.add_option('-r','--run',dest="run",default=-1,type=float,
                  help="The minimum run number")
    parser.add_option('-d','--dir',dest="outdir",default="./",type="string",
                  help="Output directory to store datasets")
    parser.add_option('-x','--box',dest="box",default=None,type="string",
                  help="Specify only one box")
    parser.add_option('--name',dest="name",default='RMRTree',type="string",
                  help="The name of the TTree to use")
      
    (options,args) = parser.parse_args()
    
    if options.config is None:
        import inspect, os
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(convertTree2Dataset)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    
    print 'Input files are %s' % ', '.join(args)
    
    chain = rt.TChain(options.name)
    fName = None
    for f in args:
        if f.lower().endswith('.root'):
            chain.Add(f)
            if fName is None:
                name = os.path.basename(f)
                fName = name[:-5]
        else:
            "File '%s' of unknown type. Looking for .root files only" % f

 ##    if 'SingleMu' in fName or 'START' in fName:
##         convertTree2Dataset(chain,fName, cfg,options.min,options.max,MuBox(None),options.run)
   
##    if 'MultiJet' in fName or 'START' in fName:
##       convertTree2Dataset(chain,fName, cfg,options.min,options.max,BJetBoxLS(CalcBDT(chain)),options.run)
##        #convertTree2Dataset(chain,fName, cfg,options.min,options.max,BJetBoxHS(CalcBDT(chain)),options.run)
##        convertTree2Dataset(chain,fName, cfg,options.min,options.max,BJetBox(None),options.run)
    if 'SingleElectron' in fName or 'START' in fName:
        convertTree2Dataset(chain,fName, cfg,options.min,options.max,EleBox(None),options.run)
    
