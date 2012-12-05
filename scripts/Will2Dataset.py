from optparse import OptionParser
import os, array

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
#import CalcBDT

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'Mu':3,'Ele':4,'Had':5,'BJet':6}
cross_sections = {'SingleTop_s':4.21,'SingleTop_t':64.6,'SingleTop_tw':10.6,\
                               'TTj':157.5,'Zll':3048,'Znn':2*3048,'Wln':31314,\
                               'WW':43,'WZ':18.2,'ZZ':5.9,'Vgamma':173
                               }
lumi = 1.0

class HadDumper(object):

    def headers_for_MVA(self):
        return ['thetaH1','thetaH2','topMass1','topMass2','wMass1','wMass2',\
                    'jet1mult','jet2mult','jet3mult','jet4mult','jet5mult','jet6mult',\
                    'jet1girth','jet2girth','jet3girth','jet4girth','jet5girth','jet6girth']

    def __init__(self, tree):

        self.tree = tree

        self.vars = {}
        self.reader = rt.TMVA.Reader()
        for h in self.headers_for_MVA():
            self.vars['%s_var'%h] = array.array('f',[0])
            self.reader.AddVariable(h,self.vars['%s_var'%h])

        self.vars['mr_var'] = array.array('f',[0])
        self.vars['rsq_var'] = array.array('f',[0])
        self.vars['nvertex_var'] = array.array('f',[0])
        
        self.reader.AddSpectator('MR',self.vars['mr_var'])
        self.reader.AddSpectator('RSQ',self.vars['rsq_var'])
        self.reader.AddSpectator('nVertex',self.vars['nvertex_var'])
        self.reader.BookMVA('BDT','/afs/cern.ch/user/w/wreece/work/CMGTools/V5_6_0/CMGTools/CMSSW_5_3_3_patch3/src/CMGTools/Susy/prod/MultiJet/TMVAClassification_BDT.weights.xml')        
        
        self.jets = []

    def thetaH1(self):
        if self.tree.bestHemi == 1:
            return self.tree.hemi1ThetaH
        return self.tree.hemi2ThetaH
    def thetaH2(self):
        if self.tree.bestHemi == 2:
            return self.tree.hemi1ThetaH
        return self.tree.hemi2ThetaH

    def topMass1(self):
        if self.tree.bestHemi == 1:
            return self.tree.hemi1TopMass
        return self.tree.hemi2TopMass
    def topMass2(self):
        if self.tree.bestHemi == 2:
            return self.tree.hemi1TopMass
        return self.tree.hemi2TopMass

    def wMass1(self):
        if self.tree.bestHemi == 1:
            return self.tree.hemi1WMass
        return self.tree.hemi2WMass
    def wMass2(self):
        if self.tree.bestHemi == 2:
            return self.tree.hemi1WMass
        return self.tree.hemi2WMass

    def tag_jets(self):
        #order by btag output - high to low
        jets = sorted([(self.tree.jet_csv.at(i),i) for i in xrange(len(self.tree.jet_csv))],reverse=True)
        self.jets = [i for b, i in jets]

    def jetNpt(self, n):
        return self.tree.jet_pt.at(self.jets[n])

    def jet1pt(self):
        return self.jetNpt(0)
    def jet2pt(self):
        return self.jetNpt(1)
    def jet3pt(self):
        return self.jetNpt(2)
    def jet4pt(self):
        return self.jetNpt(3)
    def jet5pt(self):
        return self.jetNpt(4)
    def jet6pt(self):
        return self.jetNpt(5)

    def jet1mult(self):
        return self.tree.jet_mult.at(self.jets[0])
    def jet2mult(self):
        return self.tree.jet_mult.at(self.jets[1])
    def jet3mult(self):
        return self.tree.jet_mult.at(self.jets[2])
    def jet4mult(self):
        return self.tree.jet_mult.at(self.jets[3])
    def jet5mult(self):
        return self.tree.jet_mult.at(self.jets[4])
    def jet6mult(self):
        return self.tree.jet_mult.at(self.jets[5])

    def jet1girth(self):
        return self.tree.jet_girth_ch.at(self.jets[0])
    def jet2girth(self):
        return self.tree.jet_girth_ch.at(self.jets[1])
    def jet3girth(self):
        return self.tree.jet_girth_ch.at(self.jets[2])
    def jet4girth(self):
        return self.tree.jet_girth_ch.at(self.jets[3])
    def jet5girth(self):
        return self.tree.jet_girth_ch.at(self.jets[4])
    def jet6girth(self):
        return self.tree.jet_girth_ch.at(self.jets[5])

    
    def bdt(self):
        self.tag_jets()
        for h in self.headers_for_MVA():
            self.vars['%s_var'%h][0] = getattr(self,h)()
        self.vars['mr_var'] = self.tree.MR
        self.vars['rsq_var'] = self.tree.RSQ
        self.vars['nvertex_var'] = self.tree.nVertex
        return self.reader.EvaluateMVA('BDT')


class HadBox(object):
    """The Had search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'Had'
        self.dumper = dumper
    def __call__(self, tree):
        nTight = tree.nMuonTight + tree.nElectronTight
        nLoose = tree.nMuonLoose + tree.nElectronLoose
        return tree.metFilter and not tree.muTriggerFilter and not tree.eleTriggerFilter and\
            tree.MR >= 450 and tree.RSQ >= 0.03 and tree.hadBoxFilter and tree.hadTriggerFilter and\
            tree.nJet >= 6 and tree.nCSVL == 0 and nTight == 0 and nLoose == 0 and not tree.isolatedTrack10Filter
    
class BJetBox(object):
    """The BJet search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'BJet'
        self.dumper = dumper
    def __call__(self, tree):
        nTight = tree.nMuonTight + tree.nElectronTight
        nLoose = tree.nMuonLoose + tree.nElectronLoose
        return tree.metFilter and not tree.muTriggerFilter and not tree.eleTriggerFilter and\
             tree.MR >= 450 and tree.RSQ >= 0.03 and tree.hadBoxFilter and tree.hadTriggerFilter\
              and tree.nJet >= 6 and tree.nCSVM > 0 and nTight == 0 and nLoose == 0 and not tree.isolatedTrack10Filter 

class CR6JSingleLeptonBVetoBox(object):
    """A control region for the Had box: One lepton, no bjets - Should give handle on W+Jets"""
    def __init__(self):
        self.name = 'CR6JSingleLeptonBVeto'
        self.dumper = None
    def __call__(self, tree):
        nTight = tree.nMuonTight + tree.nElectronTight
        nLoose = tree.nMuonLoose + tree.nElectronLoose
        return tree.metFilter and\
             tree.MR >= 450 and tree.RSQ >= 0.03 and tree.hadBoxFilter and tree.hadTriggerFilter\
             and tree.nJet >= 6 and tree.nCSVL == 0 and nTight == 1 and nLoose == 1        
    

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
    workspace.factory('nLepton[0,0,15.0]')
    workspace.factory('nElectron[0,0,15.0]')
    workspace.factory('nMuon[0,0,15.0]')
    workspace.factory('nTau[0,0,15.0]')
    workspace.factory('nVertex[1,0.,50.]')
    workspace.factory('nJet[0,0,15.0]')
    workspace.factory('W[0,0,+INF]')
    workspace.factory('BDT[0,-INF,+INF]')
    workspace.factory('genInfo[0,-INF,+INF]')
    
    if filter.dumper is not None:
        for h in filter.dumper.headers_for_MVA():
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

    nLooseElectrons = rt.TH2D('nLooseElectrons','nLooseElectrons',350,mRmin,mRmax,100,rsqMin,rsqMax)
    nLooseMuons = rt.TH2D('nLooseMuons','nLooseMuons',350,mRmin,mRmax,100,rsqMin,rsqMax)
    nLooseTaus = rt.TH2D('nLooseTaus','nLooseTaus',350,mRmin,mRmax,100,rsqMin,rsqMax)
    
    for entry in xrange(tree.GetEntries()):
        tree.GetEntry(entry)
        
        ####First, apply a common selection
        
        #take only events in the MR and R2 region
        if tree.MR > mRmax or tree.MR < mRmin or tree.RSQ < rsqMin or tree.RSQ > rsqMax:
            continue

        #apply the box based filter class
        if not filter(tree): continue
        bdt = -9999.
        if filter.dumper is not None:
            bdt = filter.dumper.bdt()
        
        #veto events with multiple loose leptons
        nLeptonLoose = tree.nMuonLoose + tree.nElectronLoose + tree.nTauLoose
        if nLeptonLoose > 1: continue
        
        if tree.nElectronLoose > 0: nLooseElectrons.Fill(tree.MR,tree.RSQ)
        if tree.nMuonLoose > 0: nLooseMuons.Fill(tree.MR,tree.RSQ)
        if tree.nTauLoose > 0: nLooseTaus.Fill(tree.MR,tree.RSQ)
        
        try:
            if tree.run <= run:
                continue
        except AttributeError:
            pass
        
        nBtag = tree.nCSVM

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        
        a.setRealValue('Run',tree.run)
        a.setRealValue('Lumi',tree.lumi)
        a.setRealValue('Event',tree.event)
        
        a.setRealValue('MR',tree.MR, True)
        a.setRealValue('Rsq',tree.RSQ, True)
        a.setRealValue('nBtag',nBtag)
        a.setRealValue('nLepton',tree.nMuonLoose + tree.nElectronLoose + tree.nTauLoose)
        a.setRealValue('nElectron',tree.nElectronLoose)
        a.setRealValue('nMuon',tree.nMuonLoose)
        a.setRealValue('nTau',tree.nTauLoose)
        a.setRealValue('nJet',tree.nJet)
        a.setRealValue('nVertex',tree.nVertex)        
        a.setRealValue('W',1.0)
        a.setRealValue('BDT',bdt)
        
        a.setRealValue('genInfo',tree.genInfo)
        
        if filter.dumper is not None:
            for h in filter.dumper.headers_for_MVA():
                a.setRealValue(h,getattr(filter.dumper,h)())
        
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
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,HadBox(HadDumper(chain)),options.run)
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,BJetBox(HadDumper(chain)),options.run)
    convertTree2Dataset(chain,fName, cfg,options.min,options.max,CR6JSingleLeptonBVetoBox(),options.run)

