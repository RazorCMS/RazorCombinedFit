from optparse import OptionParser
import os

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from array import *

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'MuTau':3,'Mu':4,'EleTau':5,'Ele':6,'Jet':7,'TauTauJet':8,'MultiJet':9}
lumi = 19.3


def getBinning():
    MRbins =  [450, 700, 1200, 1600, 2500, 4000]
    Rsqbins = [0.25,0.41,0.64,0.80,1.5]
    nBtagbins = [1.,2.,3.,4.]
    return MRbins, Rsqbins, nBtagbins

def writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin, label, args, smscount):
    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+label+outputBox,'RECREATE')
    MGstringstart = outputFile.find("MG")+3
    MGstringend = outputFile.find("MCHI")-1
    MCHIstringstart = MGstringend+6
    MCHIstringend = MCHIstringstart+7
    MG = float(outputFile[MGstringstart:MGstringend])
    MCHI = float(outputFile[MCHIstringstart:MCHIstringend])
    print "(MG=%f,MCHI=%f)"%(MG,MCHI)
    print output.GetName()
    data.Write()

    args.Print()
    varList3D = rt.RooArgList(args['MR'],args['Rsq'],args['nBtag'])

    MRbins, Rsqbins, nBtagbins = getBinning()

    x = array("d",MRbins)
    y = array("d",Rsqbins)
    z = array("d",nBtagbins)
    
    nominal = rt.TH3D("wHisto", "wHisto", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    data.fillHistogram(nominal,varList3D,"MR>0.")
    nominal.Scale(1./smscount.GetBinContent(smscount.FindBin(MG,MCHI)))
    print "signal efficiency = %f"%nominal.Integral()
    
    jes_pe = rt.TH3D("wHisto_JESerr_pe", "wHisto_JESerr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    pdf_pe = rt.TH3D("wHisto_pdferr_pe", "wHisto_pdferr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_pe = rt.TH3D("wHisto_btagerr_pe", "wHisto_btagerr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    
    nominal.Write()
    jes_pe.Write()
    pdf_pe.Write()
    btag_pe.Write()
    
    output.Close()
    return data.numEntries()

def convertTree2Dataset(tree, smscount, outputFile, outputBox, config, box, min, max, run, useWeight, write = True):
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
    label = ""

    btagcutoff = 3
    if box == "MuEle" or box == "MuMu" or box == "EleEle" or box=="TauTauJet":
        btagcutoff = 1

    if box == "Jet" or box == "MultiJet" or box == "TauTauJet" or box=="EleEle" or box=="EleTau" or box=="Ele":
        noiseCut = "abs(TMath::Min( abs(atan2(MET_y,MET_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_y,MET_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"
    elif box == "MuEle" or box == "MuMu" or box == "MuTau" or box == "Mu":
        noiseCut = "abs(TMath::Min( abs(atan2(MET_NOMU_y,MET_NOMU_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_NOMU_y,MET_NOMU_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"
            
    #iterate over selected entries in the input tree
        
    tree.Draw('>>elist','MR >= %f && MR <= %f && RSQ_PFTYPE1 >= %f && RSQ_PFTYPE1 <= %f && (BOX_NUM == %i) && GOOD_PF && (%s)' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box],noiseCut),'entrylist')
    
    elist = rt.gDirectory.Get('elist')
    
    entry = -1;
    while True:
        entry = elist.Next()
        if entry == -1: break
        tree.GetEntry(entry)
        
        if tree.BTAG_NUM < btagmin: continue

        runrange = run.split(":")
        if len(runrange) == 2:
            minrun = int(runrange[0])
            maxrun = int(runrange[1])
            if tree.RUN_NUM < minrun: continue
            if tree.RUN_NUM > maxrun: continue

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        
        a.setRealValue('MR',tree.MR)
        a.setRealValue('R',rt.TMath.Sqrt(tree.RSQ_PFTYPE1))
        a.setRealValue('Rsq',tree.RSQ_PFTYPE1)
        if tree.BTAG_NUM >= btagcutoff:
            a.setRealValue('nBtag',btagcutoff)
        else:
            a.setRealValue('nBtag',tree.BTAG_NUM)
                
        if useWeight:
            try:
                a.setRealValue('W',tree.WLEP*tree.WPU)
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
            writeTree2DataSet(wdata, outputFile, outputBox, rMin, mRmin, label, args, smscount)
        else:  
            writeTree2DataSet(rdata, outputFile, outputBox, rMin, mRmin, label, args, smscount)
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
    parser.add_option('-r','--run',dest="run",default="none",type="string",
                  help="The run range in the format min_run_number:max_run_number")
    parser.add_option('-d','--dir',dest="outdir",default="./",type="string",
                  help="Output directory to store datasets")
    parser.add_option('-x','--box',dest="box",default=None,type="string",
                  help="Specify only one box")
    parser.add_option('-w','--weight',dest="useWeight",default=True,action='store_true',
                  help="Use weights, if available, default is WLEP*WPU")
      
    (options,args) = parser.parse_args()
    
    if options.config is None:
        import inspect, os
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(convertTree2Dataset)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    
    print 'Input files are %s' % ', '.join(args)
    histoFile = rt.TFile.Open('SMS/T1bbbb_histo.root')
    for f in args:
        if f.lower().endswith('.root'):
            input = rt.TFile.Open(f)
            decorator = options.outdir+"/"+os.path.basename(f)[:-5]
            print decorator
            if not options.eff:
                #dump the trees for the different datasets
                if options.box != None:
                    convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, options.box+'.root', cfg,options.box,options.min,options.max,options.run,options.useWeight)
                else:
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'MuEle.root', cfg,'MuEle',options.min,options.max,options.run,options.useWeight)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'MuMu.root', cfg,'MuMu',options.min,options.max,options.run,options.useWeight)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'),  decorator, 'EleEle.root', cfg,'EleEle',options.min,options.max,options.run,options.useWeight)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'MuTau.root', cfg,'MuTau',options.min,options.max,options.run,options.useWeight)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'Mu.root', cfg,'Mu',options.min,options.max,options.run,options.useWeight)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'EleTau.root', cfg,'EleTau',options.min,options.max,options.run,options.useWeight)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'Ele.root', cfg,'Ele',options.min,options.max,options.run,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'Jet.root', cfg,'Jet',options.min,options.max,options.run,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'),  decorator, 'TauTauJet.root', cfg,'TauTauJet',options.min,options.max,options.run,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'MultiJet.root', cfg,'MultiJet',options.min,options.max,options.run,options.useWeight)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
