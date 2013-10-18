from optparse import OptionParser
import os

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

#boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'MuTau':3,'Mu':4,'EleTau':5,'Ele':6,'Jet':7,'Jet2b':7,'Jet1b':7,'TauTauJet':8,'MultiJet':9}
#boxMap = {'MuEle':[0],'MuMu':[1],'Ele':[2],'MuMultiJet':[3,4],'MuJet':[3,4],'Mu':[4],'EleMultiJet':[5,6],'EleJet':[5,6],'Jet':[7],'Jet2b':[7],'Jet1b':[7],'MultiJet':[8,9]}

boxMap = {'MuEle':[0],'MuMu':[1],'EleEle':[2],'Mu':[3],'Ele':[4],'Had':[5],'BJet':[6]}


cross_sections = {'SingleTop_s':4.21,'SingleTop_t':64.6,'SingleTop_tw':10.6,\
                               'TTj':157.5,'Zll':3048,'Znn':2*3048,'Wln':31314,\
                               'WW':43,'WZ':18.2,'ZZ':5.9,'Vgamma':173
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
    if btagmax <= 1.: label = "NoBTAG_"

    if useWeight: label += "WEIGHT_"

    btagcutoff = 3
    if box in ["MuEle", "MuMu", "EleEle", "TauTauJet"]:
        btagcutoff = 1

    #iterate over selected entries in the input tree
    boxCut = "(" + "||".join(["BOX_NUM==%i"%cut for cut in boxMap[box]]) + ")"
    print boxCut
      
    if isMC: tree.Draw('>>elist','MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f' % (mRmin,mRmax,rsqMin,rsqMax),'entrylist')
    else: tree.Draw('>>elist','MR >= %f && MR <= %f && RSQ_PFTYPE1 >= %f && RSQ_PFTYPE1 <= %f && %s  && (%s) && (%s) && (%s)' % (mRmin,mRmax,rsqMin,rsqMax,boxCut,noiseCut,triggerReq,jetReq),'entrylist')
    elist = rt.gDirectory.Get('elist')
    
    entry = -1;
    nEvents=0
    while True:
        nEvents+=1
        #if nEvents > 100000: break
        entry = elist.Next()
        if entry == -1: break
        tree.GetEntry(entry)

        #box selection
        boxCut = False
        if box in ['Ele']:
            boxCut = tree.nJetNoLeptons >= 4 and tree.metFilter and tree.eleBoxFilter and tree.eleTriggerFilter and tree.nCSVM >0 and tree.MR >= 350. and tree.RSQ >= 0.05 and tree.nMuonTight == 0 and tree.nElectronTight == 1 and tree.nMuonLoose == 0 and tree.nElectronLoose == 1 and not tree.isolatedTrack10LeptonFilter

        if not(boxCut): continue
        if tree.nCSVM < btagmin: continue
        if box =="Jet1b" and tree.nCSVM>=2: continue
        if box =="Jet2b" and tree.nCSVM<2: continue
        #if box in ["MuJet","EleJet"]:
        #if tree.nCSVM==1 and tree.nCSVM_CSV[2]==0: continue
        #if tree.RSQ_PFTYPE1>0.7: print tree.nCSVM, tree.nCSVM_CSV[2], tree.RSQ_PFTYPE1
                
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
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'MuEle.root', cfg,'MuEle',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'MuMu.root', cfg,'MuMu',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'EleEle.root', cfg,'EleEle',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'MuJet.root', cfg,'MuJet',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'MuMultiJet.root', cfg,'MuMultiJet',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'EleJet.root', cfg,'EleJet',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'EleMultiJet.root', cfg,'EleMultiJet',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2DataseGt(input.Get('RMRTree'), decorator, 'Jet2b.root', cfg,'Jet2b',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    #convertTree2Dataset(input.Get('RMRTree'), decorator, 'Jet.root', cfg,'Jet',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
                    convertTree2Dataset(input.Get('RMRTree'), decorator, 'MultiJet.root', cfg,'MultiJet',options.min,options.max,options.run,options.calo,options.useWeight,options.isMC)
            else:
                printEfficiencies(input.Get('RMRTree'), decorator, cfg, options.flavour)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
