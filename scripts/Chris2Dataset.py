from optparse import OptionParser
import os

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from CalcBDT import CalcBDT

boxMap = {'MuEle':[0],'MuMu':[1],'EleEle':[2],'Mu':[3],'Ele':[4],'Had':[5],'BJet':[6], 'BJetLS':[7],'BJetHS':[8]}

cross_sections = {'SingleTop_s':4.21,
                  'SingleTop_t':64.6,
                  'SingleTop_tw':10.6,
                  'TTj':157.5,
                  'Zll':3048,
                  'Znn':2*3048,
                  'Wln':31314,
                  'WW':43,
                  'WZ':18.2,
                  'ZZ':5.9,
                  'Vgamma':173
                  }
lumi = 19.3

def writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin, label):
    
    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+label+outputBox,'RECREATE')
    print output.GetName()
    data.Write()
    output.Close()
    return data.numEntries()

def convertTree2Dataset(tree, outputFile, outputBox, config, box, min, max, run, calo, useWeight, isMC, write = True):
    """This defines the format of the RooDataSet"""
    workspace = rt.RooWorkspace(box)
    variables = config.getVariablesRange(box,"variables",workspace)
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

    btagmin =  args['nBtag'].getMin()
    btagmax =  args['nBtag'].getMax()

    label ="BTAG_"
    if useWeight: label += "WEIGHT_"

    btagcutoff = 3
    njetcutoff = 8
  
    #box selection -- should apply the very same cuts for MC & data...
    if box in ['Ele']:
        boxCut = "nJetNoLeptons == 4 && metFilter && eleBoxFilter && eleTriggerFilter && nCSVM >0 && MR >= 350. && RSQ >= 0.05 && nMuonTight == 0 && nElectronTight == 1 && nMuonLoose == 0 && nElectronLoose == 1 &&  !isolatedTrack10LeptonFilter"
    elif box in ['Mu']:
        boxCut = "nJetNoLeptons == 4 && metFilter && muBoxFilter && muTriggerFilter && nCSVM >0  && MR >= 350. && RSQ >= 0.05 && nMuonTight == 1 && nElectronTight == 0 && nMuonLoose == 1 && nElectronLoose == 0 &&  !isolatedTrack10LeptonFilter"
    elif box in ['BJetHS','BJetLS']:
        boxCut = "nJet == 6 && hadBoxFilter && hadTriggerFilter && nCSVM > 0 && MR >= 350. && RSQ >= 0.05  && nMuonTight == 0 && nElectronTight == 0 && !isolatedTrack10Filter && nMuonLoose == 0 && nElectronLoose == 0 "#&& self.dumper.bdt() >= -0.2"
        
    tree.Draw('>>elist','MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f' % (mRmin,mRmax,rsqMin,rsqMax),'entrylist')
    elist = rt.gDirectory.Get('elist')
    
    entry = -1;
    nEvents=0
    while True:
        nEvents+=1
        #if nEvents > 10000: break
        entry = elist.Next()
        if entry == -1: break
        tree.GetEntry(entry)

                   
        runrange = run.split(":")
        if len(runrange) == 2:
            minrun = int(runrange[0])
            maxrun = int(runrange[1])
            if tree.RUN_NUM < minrun: continue
            if tree.RUN_NUM > maxrun: continue

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        
        a.setRealValue('MR',tree.MR)
        a.setRealValue('R',rt.TMath.Sqrt(tree.RSQ))
        a.setRealValue('Rsq',tree.RSQ)
       
        if tree.nCSVM >= btagcutoff:
            a.setRealValue('nBtag',btagcutoff)
        else:
            a.setRealValue('nBtag',tree.nCSVM)

    ##     if tree.nJetNoLeptons >= (btagcutoff):
##             a.setRealValue('nBtag', btagcutoff - 3)
##         else:
##             a.setRealValue('nBtag',tree.nJetNoLeptons - 3)


        if box in ['Ele','Mu']:
            if tree.nJetNoLeptons >= njetcutoff:
                a.setRealValue('nJet',njetcutoff)
            else:
                a.setRealValue('nJet',tree.nJetNoLeptons)
        else :
            if tree.nJet >= njetcutoff:
                a.setRealValue('nJet',njetcutoff)
            else:
                a.setRealValue('nJet',tree.nJet)
        
        if useWeight:
            try:
                a.setRealValue('W',tree.WXSEC*lumi/5.0)
            except AttributeError:
                a.setRealValue('W',1.0)
        else:
            a.setRealValue('W',1.0)
            
        data.add(a)
    numEntries = data.numEntries()
    if min < 0: min = 0
    if max < 0: max = numEntries
    
    rdata = data.reduce(rt.RooFit.EventRange(min,max))
    wdata = rt.RooDataSet(rdata.GetName(),rdata.GetTitle(),rdata,rdata.get(),"MR>=0.","W")
    print "Number of Entries in Box %s = %d"%(box,rdata.numEntries())
    print "Sum of Weights in Box %s = %.1f"%(box,wdata.sumEntries())
    if write:
        if useWeight:
            writeTree2DataSet(wdata, outputFile, outputBox, rMin, mRmin, label)
        else:  
            writeTree2DataSet(rdata, outputFile, outputBox, rMin, mRmin, label)
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
    parser.add_option('-r','--run',dest="run",default="none",type="string",
                  help="The run range in the format min_run_number:max_run_number")
    parser.add_option('-d','--dir',dest="outdir",default="./",type="string",
                  help="Output directory to store datasets")
    parser.add_option('-x','--box',dest="box",default=None,type="string",
                  help="Specify only one box")
    parser.add_option('-l','--calo',dest="calo",default=False,action='store_true',
                  help="Use CALO jets, instead of PF jets")
    parser.add_option('-w','--weight',dest="useWeight",default=False,action='store_true',
                  help="Use weights, if available, default is WXSEC")
    parser.add_option('--MC',dest="isMC",default=False,action='store_true',
                  help="Slightly different variables for MC")
      
    (options,args) = parser.parse_args()
    
    if options.config is None:
        import inspect, os
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(convertTree2Dataset)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    
    print 'Input files are %s' % ', '.join(args)
    for f in args:
        if f.lower().endswith('.root'):
            input = rt.TFile.Open(f)
            decorator = options.outdir+"/"+os.path.basename(f)[:-5]
            print decorator
            if not options.eff:
                #dump the trees for the different datasets
                if options.box != None:
                    convertTree2Dataset(input.Get('RMRTree'), decorator, options.box+'.root', cfg,options.box,options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                else:
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'Mu.root', cfg,'Mu',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'Ele.root', cfg,'Ele',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'BJetHS.root', cfg,'BJetHS',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'BJetLS.root', cfg,'BJetLS',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
            else:
                printEfficiencies(input.Get('RMRTree'), decorator, cfg, options.flavour)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
