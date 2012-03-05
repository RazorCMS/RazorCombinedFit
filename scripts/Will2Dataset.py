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

def writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin, bMin):
    
    if bMin >= 0:
        output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_nBtag_'+str(bMin)+'_'+outputBox,'RECREATE')
    else:
        output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+outputBox,'RECREATE')
    print output.GetName()
    for d in data:
        d.Write()
    output.Close()

def convertTree2Dataset(tree, outputFile, outputBox, config, box, min, max, bMin, bMax, run, write = True):
    """This defines the format of the RooDataSet"""
    
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

    nLeptons = 0
    
    nLooseElectrons = rt.TH2D('nLooseElectrons','nLooseElectrons',350,mRmin,mRmax,100,rsqMin,rsqMax)
    nLooseMuons = rt.TH2D('nLooseMuons','nLooseMuons',350,mRmin,mRmax,100,rsqMin,rsqMax)
    nLooseTaus = rt.TH2D('nLooseTaus','nLooseTaus',350,mRmin,mRmax,100,rsqMin,rsqMax)
    
    for entry in xrange(tree.GetEntries()):
        tree.GetEntry(entry)
        
        if tree.mRMB > mRmax or tree.mRMB < mRmin or tree.RsqMB < rsqMin or tree.RsqMB > rsqMax:
            continue
        if not tree.triggerFilter: continue
        if hasattr(tree,'selectionFilter') and not tree.selectionFilter: continue
        
        if tree.HBHENoiseFilterResultProducer2011NonIsoRecommended == 0 or tree.goodPrimaryVertexFilter == 0 or \
            tree.ecalDeadCellTPfilter == 0 or tree.eeNoiseFilter == 0 or tree.recovRecHitFilter == 0:
            continue
        
        #veto leptons to remove known sources of MET
        if tree.nMuonTight > 0 or tree.nElectronTight > 0 or tree.nTauTight > 0:
            nLeptons += 1
            continue
        
        if tree.nElectronLoose > 0: nLooseElectrons.Fill(tree.mRMB,tree.RsqMB)
        if tree.nMuonLoose > 0: nLooseMuons.Fill(tree.mRMB,tree.RsqMB)
        if tree.nTauLoose > 0: nLooseTaus.Fill(tree.mRMB,tree.RsqMB)
        
        nBtag = len([t for t in (tree.maxTCHE,tree.nextTCHE) if t >= 3.3])
        if bMin >= 0 and nBtag < bMin: continue
        if bMax >= 0 and nBtag > bMax: continue
        
        try:
            if tree.run <= run:
                continue
        except AttributeError:
            pass

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        
        a.setRealValue('Run',tree.run)
        a.setRealValue('Lumi',tree.lumi)
        a.setRealValue('Event',tree.event)
        
        a.setRealValue('MR',tree.mRMB, True)
        a.setRealValue('Rsq',tree.RsqMB, True)
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
        writeTree2DataSet([rdata,nLooseElectrons,nLooseMuons,nLooseTaus], outputFile, outputBox, rMin, mRmin, bMin)
    print 'nLeptons',nLeptons
    return rdata

def printEfficiencies(tree, outputFile, config, flavour):
    """Backout the MC efficiency from the weights"""
    print 'ERROR:: This functionality produces incorrect results as we\'re missing a factor somewhere...'
    
    cross_section = cross_sections[flavour]
    
    for box in boxMap:
        ds = convertTree2Dataset(tree, outputFile, 'Dummy', config, box, 0, -1, -1, write = False)
        row = ds.get(0)
        W = ds.mean(row['W'])
        n_i = (cross_section*lumi)/W
        n_f = ds.numEntries()
        print 'Efficienty: %s: %f (n_i=%f; n_f=%i)' % (box,n_f/n_i,n_i, n_f)  

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
    convertTree2Dataset(chain,fName, 'Had.root', cfg,'Had',options.min,options.max,-1,0,options.run)
    convertTree2Dataset(chain,fName, 'BJet.root', cfg,'BJet',options.min,options.max,1,-1,options.run)
