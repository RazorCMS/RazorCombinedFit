from optparse import OptionParser
import os

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'Mu':3,'Ele':4,'Had':5}
cross_sections = {'SingleTop_s':4.21,'SingleTop_t':64.6,'SingleTop_tw':10.6,\
                               'TTj':157.5,'Zll':3048,'Znn':2*3048,'Wln':31314,\
                               'WW':43,'WZ':18.2,'ZZ':5.9,'Vgamma':173
                               }
lumi = 1.0

class HadBox(object):
    """The Had search box used in the analysis"""
    def __init__(self):
        self.name = 'Had'
    def __call__(self, tree):
        nLepton = tree.nMuonTight + tree.nElectronTight + tree.nTauTight
        return tree.nJet >= 6 and tree.maxTCHE < 3.3 and nLepton == 0
    
class BJetBox(object):
    """The BJet search box used in the analysis"""
    def __init__(self):
        self.name = 'BJet'
    def __call__(self, tree):
        nLepton = tree.nMuonTight + tree.nElectronTight + tree.nTauTight
        return tree.nJet >= 6 and tree.maxTCHE >= 3.3 and nLepton == 0

class BJet5JBox(object):
    """The BJet search box used in the analysis, but with >= 5 jets rather than 6"""
    def __init__(self):
        self.name = 'BJet5J'
    def __call__(self, tree):
        nLepton = tree.nMuonTight + tree.nElectronTight + tree.nTauTight
        return tree.nJet >= 5 and tree.maxTCHE >= 3.3 and nLepton == 0
    
class CR5JBVetoBox(object):
    """A control region for the hadronic shape without signal: No leptons, no bjets"""
    def __init__(self):
        self.name = 'CR5JBVeto'
    def __call__(self,tree):
        nLepton = tree.nMuonTight + tree.nElectronTight + tree.nTauTight
        #this is a tight veto on the btagging
        return tree.nJet == 5 and tree.maxTCHE < 1.7 and nLepton == 0

class CR5JSingleLeptonBVetoBox(object):
    """A control region for the hadronic shape without signal: Signal lepton, no bjets"""
    def __init__(self):
        self.name = 'CR5JSingleLeptonBVeto'
    def __call__(self,tree):
        nLepton = tree.nMuonLoose + tree.nElectronLoose + tree.nTauLoose
        #this is a tight veto on the btagging
        return tree.nJet == 5 and tree.maxTCHE < 1.7 and nLepton == 1
    
class CR6JSingleLeptonBVetoBox(object):
    """A control region for the Had box: One lepton, no bjets - Should give handle on W+Jets"""
    def __init__(self):
        self.name = 'CR6JSingleLeptonBVeto'
    def __call__(self, tree):
        nLepton = tree.nMuonLoose + tree.nElectronLoose + tree.nTauLoose
        return tree.nJet >= 6 and tree.maxTCHE < 3.3 and nLepton == 1
    
class CR6JSingleLeptonBJetBox(object):
    """A control region for the BJet box: One lepton, at least one bjet - Should give handle on TTbar"""
    def __init__(self):
        self.name = 'CR6JSingleLeptonBJet'
    def __call__(self, tree):
        nLepton = tree.nMuonLoose + tree.nElectronLoose + tree.nTauLoose
        return tree.nJet >= 6 and tree.maxTCHE >= 3.3 and nLepton == 1

def writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin):
    
    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+outputBox,'RECREATE')
    print output.GetName()
    for d in data:
        d.Write()
    output.Close()

def convertTree2Dataset(tree, outputFile, config, min, max, filter, run, write = True):
    """This defines the format of the RooDataSet"""
    
    box = filter.name
    workspace = rt.RooWorkspace(box)
    variables = config.getVariablesRange(box,"variables",workspace)
    #
    workspace.factory('Run[0,0,+INF]')
    workspace.factory('Lumi[0,0,+INF]')
    workspace.factory('Event[0,0,+INF]')
    #
    workspace.factory('nBtag[0,0,2.0]')
    workspace.factory('nLepton[0,0,15.0]')
    workspace.factory('nElectron[0,0,15.0]')
    workspace.factory('nMuon[0,0,15.0]')
    workspace.factory('nTau[0,0,15.0]')
    workspace.factory('nVertex[1,0.,50.]')
    workspace.factory('nJet[0,0,15.0]')
    workspace.factory('W[0,0,+INF]')

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

    nLooseElectrons = rt.TH2D('nLooseElectrons','nLooseElectrons',350,mRmin,mRmax,100,rsqMin,rsqMax)
    nLooseMuons = rt.TH2D('nLooseMuons','nLooseMuons',350,mRmin,mRmax,100,rsqMin,rsqMax)
    nLooseTaus = rt.TH2D('nLooseTaus','nLooseTaus',350,mRmin,mRmax,100,rsqMin,rsqMax)
    
    for entry in xrange(tree.GetEntries()):
        tree.GetEntry(entry)
        
        ####First, apply a common selection
        
        #take only events in the MR and R2 region
        if tree.mR > mRmax or tree.mR < mRmin or tree.Rsq < rsqMin or tree.Rsq > rsqMax:
            continue
        #events must have passed one of our triggers
        if not tree.triggerFilter: continue
        
        #veto events with suspect btagging
        if tree.maxTCHE < 0 or tree.nextTCHE < 0: continue
        
        #apply all those MET tail filters
        if tree.HBHENoiseFilterResultProducer2011NonIsoRecommended == 0 or tree.goodPrimaryVertexFilter == 0 or \
            tree.ecalDeadCellTPfilter == 0 or tree.eeNoiseFilter == 0 or tree.recovRecHitFilter == 0:
            continue

        #apply the box based filter class
        if not filter(tree): continue
        
        #veto events with multiple loose leptons
        nLeptonLoose = tree.nMuonLoose + tree.nElectronLoose + tree.nTauLoose
        if nLeptonLoose > 1: continue
        
        if tree.nElectronLoose > 0: nLooseElectrons.Fill(tree.mR,tree.Rsq)
        if tree.nMuonLoose > 0: nLooseMuons.Fill(tree.mR,tree.Rsq)
        if tree.nTauLoose > 0: nLooseTaus.Fill(tree.mR,tree.Rsq)
        
        try:
            if tree.run <= run:
                continue
        except AttributeError:
            pass
        
        nBtag = len([t for t in (tree.maxTCHE,tree.nextTCHE) if t >= 3.3])

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        
        a.setRealValue('Run',tree.run)
        a.setRealValue('Lumi',tree.lumi)
        a.setRealValue('Event',tree.event)
        
        a.setRealValue('MR',tree.mR, True)
        a.setRealValue('Rsq',tree.Rsq, True)
        a.setRealValue('nBtag',nBtag)
        a.setRealValue('nLepton',tree.nMuonLoose + tree.nElectronLoose + tree.nTauLoose)
        a.setRealValue('nElectron',tree.nElectronLoose)
        a.setRealValue('nMuon',tree.nMuonLoose)
        a.setRealValue('nTau',tree.nTauLoose)
        a.setRealValue('nJet',tree.nJet)
        a.setRealValue('nVertex',tree.nVertex)        
        a.setRealValue('W',1.0)
        
        data.add(a)
    numEntries = data.numEntries()
    if min < 0: min = 0
    if max < 0: max = numEntries
    
    rdata = data.reduce(rt.RooFit.EventRange(min,max))
    if write:
        writeTree2DataSet([rdata,nLooseElectrons,nLooseMuons,nLooseTaus], outputFile, '%s.root' % filter.name, rMin, mRmin)
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
      
    (options,args) = parser.parse_args()
    
    if options.config is None:
        import inspect, os
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(convertTree2Dataset)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    
    print 'Input files are %s' % ', '.join(args)
    
    chain = rt.TChain('RMRTree')
    fName = None
    for f in args:
        if f.lower().endswith('.root'):
            chain.Add(f)
            if fName is None:
                name = os.path.basename(f)
                fName = name[:-5]
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,HadBox(),options.run)
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,BJetBox(),options.run)
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,BJet5JBox(),options.run)
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,CR5JBVetoBox(),options.run)
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,CR5JSingleLeptonBVetoBox(),options.run)
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,CR6JSingleLeptonBVetoBox(),options.run)
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,CR6JSingleLeptonBJetBox(),options.run)
