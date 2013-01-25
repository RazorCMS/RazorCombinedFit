from optparse import OptionParser
import os

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'MuTau':3,'Mu':4,'EleTau':5,'Ele':6,'Jet':7,'TauTauJet':8,'MultiJet':9}
cross_sections = {'SingleTop_s':4.21,'SingleTop_t':64.6,'SingleTop_tw':10.6,\
                               'TTj':157.5,'Zll':3048,'Znn':2*3048,'Wln':31314,\
                               'WW':43,'WZ':18.2,'ZZ':5.9,'Vgamma':173
                               }
lumi = 5.0

def writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin, label):
    
    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+label+outputBox,'RECREATE')
    print output.GetName()
    data.Write()
    output.Close()
    return data.numEntries()

def convertTree2Dataset(tree, outputFile, outputBox, config, box, min, max, run, calo, useWeight, write = True):
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
    if not calo: label += "PF_"
    else: label += "CALO_"
    if useWeight: label += "WEIGHT_"

    btagcutoff = 3
    if box == "MuEle" or box == "MuMu" or box == "EleEle" or box=="TauTauJet":
        btagcutoff = 1

    if box == "Jet" or box == "MultiJet" or box == "TauTauJet" or box=="EleEle" or box=="EleTau" or box=="Ele":
        noiseCut = "abs(TMath::Min( abs(atan2(MET_y,MET_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_y,MET_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"
    elif box == "MuEle" or box == "MuMu" or box == "MuTau" or box == "Mu":
        noiseCut = "abs(TMath::Min( abs(atan2(MET_NOMU_y,MET_NOMU_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_NOMU_y,MET_NOMU_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"
    
    if box == "Jet" or box == "MultiJet" or box == "TauTauJet":
        triggerReq = "HLT_RsqMR55_Rsq0p09_MR150 || HLT_RsqMR60_Rsq0p09_MR150 || HLT_RsqMR65_Rsq0p09_MR150"
    elif box == "MuMu" or box == "MuTau" or box == "Mu":
        triggerReq = "HLT_Mu12_RsqMR30_Rsq0p04_MR200 || HLT_Mu12_RsqMR40_Rsq0p04_MR200 ||  HLT_Mu12_RsqMR45_Rsq0p04_MR200"
    elif  box == "MuEle" or box == "EleEle" or box == "Ele" or box == "EleTau":
        triggerReq = "HLT_Ele12_CaloIdL_CaloIsoVL_TrkIdVL_TrkIsoVL_RsqMR30_Rsq0p04_MR200 || HLT_Ele12_CaloIdL_CaloIsoVL_TrkIdVL_TrkIsoVL_RsqMR40_Rsq0p04_MR200 || HLT_Ele12_CaloIdL_CaloIsoVL_TrkIdVL_TrkIsoVL_RsqMR45_Rsq0p04_MR200"
            
    #iterate over selected entries in the input tree
    if not calo:
        tree.Draw('>>elist','MR >= %f && MR <= %f && RSQ_PFTYPE1 >= %f && RSQ_PFTYPE1 <= %f && (BOX_NUM == %i) && GOOD_PF && (%s) && (%s)' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box],noiseCut,triggerReq),'entrylist')
    else:
        tree.Draw('>>elist','MR_CALO_NOMU >= %f && MR_CALO_NOMU <= %f && RSQ_CALO_NOMU >= %f && RSQ_CALO_NOMU <= %f && (BOX_NUM == %i) && GOOD_CALO && (%s) && (%s)' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box],noiseCut,triggerReq),'entrylist')
    elist = rt.gDirectory.Get('elist')
    
    entry = -1;
    while True:
        entry = elist.Next()
        if entry == -1: break
        tree.GetEntry(entry)
        
        if not calo:
            if tree.BTAG_NUM < btagmin: continue
        else:
            if tree.BTAG_NUM_CALO < btagmin: continue

        runrange = run.split(":")
        if len(runrange) == 2:
            minrun = int(runrange[0])
            maxrun = int(runrange[1])
            if tree.RUN_NUM < minrun: continue
            if tree.RUN_NUM > maxrun: continue

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        
        if not calo:
            a.setRealValue('MR',tree.MR)
            a.setRealValue('R',rt.TMath.Sqrt(tree.RSQ_PFTYPE1))
            a.setRealValue('Rsq',tree.RSQ_PFTYPE1)
            if tree.BTAG_NUM >= btagcutoff:
                a.setRealValue('nBtag',btagcutoff)
            else:
                a.setRealValue('nBtag',tree.BTAG_NUM)
            a.setRealValue('CHARGE',tree.CHARGE)
        else:
            a.setRealValue('MR',tree.MR_CALO_NOMU)
            a.setRealValue('R',rt.TMath.Sqrt(tree.RSQ_CALO_NOMU))
            a.setRealValue('Rsq',tree.RSQ_CALO_NOMU)
            if  tree.BTAG_NUM_CALO >= btagcutoff:
                a.setRealValue('nBtag',btagcutoff)
            else:
                a.setRealValue('nBtag',tree.BTAG_NUM_CALO)
            a.setRealValue('CHARGE',tree.CHARGE)
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
                    convertTree2Dataset(input.Get('EVENTS'), decorator, options.box+'.root', cfg,options.box,options.min,options.max,options.run,options.calo,options.useWeight)
                else:
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'MuEle.root', cfg,'MuEle',options.min,options.max,options.run,options.calo,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'MuMu.root', cfg,'MuMu',options.min,options.max,options.run,options.calo,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'EleEle.root', cfg,'EleEle',options.min,options.max,options.run,options.calo,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'MuTau.root', cfg,'MuTau',options.min,options.max,options.run,options.calo,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'Mu.root', cfg,'Mu',options.min,options.max,options.run,options.calo,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'EleTau.root', cfg,'EleTau',options.min,options.max,options.run,options.calo,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'Ele.root', cfg,'Ele',options.min,options.max,options.run,options.calo,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'Jet.root', cfg,'Jet',options.min,options.max,options.run,options.calo,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'TauTauJet.root', cfg,'TauTauJet',options.min,options.max,options.run,options.calo,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'MultiJet.root', cfg,'MultiJet',options.min,options.max,options.run,options.calo,options.useWeight)
            else:
                printEfficiencies(input.Get('EVENTS'), decorator, cfg, options.flavour)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
