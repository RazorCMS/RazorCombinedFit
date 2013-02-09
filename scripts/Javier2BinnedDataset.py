from optparse import OptionParser
import os

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from array import *

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'MuTau':3,'Mu':4,'EleTau':5,'Ele':6,'Jet':7,'TauTauJet':8,'MultiJet':9}
lumi = 19.3


def getBinning(box):
    MRbins = cfg.getBinning(box)[0]
    Rsqbins = cfg.getBinning(box)[1]
    nBtagbins = cfg.getBinning(box)[2]
    return MRbins, Rsqbins, nBtagbins

def writeTree2DataSet(outputFile, outputBox, box, rMin, mRmin, label, args, smscount,jes_pe, pdf_pe, btag_pe, nominal):
    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+label+outputBox,'RECREATE')
    MGstringstart = outputFile.find("MG")+3
    MGstringend = outputFile.find("MCHI")-1
    MCHIstringstart = MGstringend+6
    MCHIstringend = MCHIstringstart+7
    MG = float(outputFile[MGstringstart:MGstringend])
    MCHI = float(outputFile[MCHIstringstart:MCHIstringend])
    print "(MG=%f,MCHI=%f)"%(MG,MCHI)
    print output.GetName()

    args.Print()
    
    nominal.Scale(1./smscount.GetBinContent(smscount.FindBin(MG,MCHI)))
    print "signal efficiency from hist = %f"%nominal.Integral()
    
    nominal.Write()
    jes_pe.Write()
    pdf_pe.Write()
    btag_pe.Write()
    
    output.Close()


def getUpDownHistos(tree,btagTree,mRmin,mRmax,rsqMin,rsqMax,btagcutoff, box,noiseCut):
    
    MRbins, Rsqbins, nBtagbins = getBinning(box)

    x = array("d",MRbins)
    y = array("d",Rsqbins)
    z = array("d",nBtagbins)
    
    jes_pe = rt.TH3D("wHisto_JESerr_pe", "wHisto_JESerr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    pdf_pe = rt.TH3D("wHisto_pdferr_pe", "wHisto_pdferr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_pe = rt.TH3D("wHisto_btagerr_pe", "wHisto_btagerr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)

    jes_up = rt.TH3D("wHisto_JESerr_up", "wHisto_JESerr_up", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_up = rt.TH3D("wHisto_btagerr_up", "wHisto_btagerr_up", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)

    nominal = rt.TH3D("wHisto", "wHisto", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
  
    jes_down = rt.TH3D("wHisto_JESerr_down", "wHisto_JESerr_down", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_down = rt.TH3D("wHisto_btagerr_down", "wHisto_btagerr_down", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)


    tree.Draw('>>elist','(BOX_NUM == %i) && GOOD_PF && (%s)' % (boxMap[box],noiseCut),'entrylist')
    
    elist = rt.gDirectory.Get('elist')
    
    entry = -1
    while True:
        entry = elist.Next()
        if entry == -1: break
        tree.GetEntry(entry)

        btagTree.Draw(">>btaglist",'eventNumber==%i'%tree.EVENT_NUM,'entrylist')
        btaglist = rt.gDirectory.Get('btaglist')
        btagentry = btaglist.Next()
        btagTree.GetEntry(btagentry)
        
        if tree.MR_JESup >= mRmin and tree.MR_JESup <= mRmax and tree.RSQ_JESup >= rsqMin and tree.RSQ_JESup <= rsqMax:
            if (btagTree.nomBtag >= 1):
                jes_up.Fill(tree.MR_JESup,tree.RSQ_JESup,btagTree.nomBtag, tree.WLEP*tree.WPU)
                
        if tree.MR >= mRmin and tree.MR <= mRmax and tree.RSQ_PFTYPE1 >= rsqMin and tree.RSQ_PFTYPE1 <= rsqMax:
            if (btagTree.nomBtag >= 1):
                nominal.Fill(tree.MR,tree.RSQ_PFTYPE1,btagTree.nomBtag, tree.WLEP*tree.WPU)
            
        if tree.MR >= mRmin and tree.MR <= mRmax and tree.RSQ_PFTYPE1 >= rsqMin and tree.RSQ_PFTYPE1 <= rsqMax:
            if (btagTree.upBtag >= 1):
                btag_up.Fill(tree.MR,tree.RSQ_PFTYPE1,min(btagTree.upBtag, btagcutoff), tree.WLEP*tree.WPU)
            if (btagTree.downBtag >= 1 ):
                btag_down.Fill(tree.MR,tree.RSQ_PFTYPE1,min(btagTree.downBtag, btagcutoff), tree.WLEP*tree.WPU)

    ###### JES ######
    #using (UP - NOM):
    jes_pe.Add(jes_up,1.0)
    jes_pe.Add(nominal,-1.0)

    #divide by (UP + 2*NOM)/3:
    jes_denom = rt.TH3D("wHisto_JESerr_denom", "wHisto_JESerr_denom", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    jes_denom.Add(jes_up,1.0/3.0)
    jes_denom.Add(nominal,2.0/3.0)

    jes_pe.Divide(jes_denom)

    ###### BTAG ######
    #using (UP - DOWN)/2:
    btag_pe.Add(btag_up,0.5)
    btag_pe.Add(btag_down,-0.5)

    #divide by (UP + NOM + DOWN)/3
    btag_denom = rt.TH3D("wHisto_btagerr_denom", "wHisto_btagerr_denom", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_denom.Add(btag_up,1.0/3.0)
    btag_denom.Add(nominal,1.0/3.0)
    btag_denom.Add(btag_down,1.0/3.0)
    
    btag_pe.Divide(btag_denom)

    
    print "Number of entries in Box %s = %f"%(box,nominal.GetEntries())
    print "Sum of weights in Box %s = %f"%(box,nominal.Integral())
    
    return jes_pe, pdf_pe, btag_pe, nominal
    
def convertTree2Dataset(tree, smscount, outputFile, outputBox, config, box, min, max, run, useWeight, btagFileName = None, write = True):
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
        
    # get the btag tree ONCE
    btagFile = rt.TFile.Open(btagFileName)
    btagTree = btagFile.Get("BTAGTree")

    jes_pe, pdf_pe, btag_pe, nominal = getUpDownHistos(tree,btagTree,mRmin,mRmax,rsqMin,rsqMax,btagcutoff, box,noiseCut)
    
    if write:
        if useWeight:
            writeTree2DataSet(outputFile, outputBox, box, rMin, mRmin, label, args, smscount, jes_pe, pdf_pe, btag_pe, nominal)
        else:  
            writeTree2DataSet(outputFile, outputBox, box, rMin, mRmin, label, args, smscount, jes_pe, pdf_pe, btag_pe, nominal)

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
    parser.add_option('--btagfile',dest="btagFileName",type="string",default=None,
                  help="text file containing corrected btags")      
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
                    convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, options.box+'.root', cfg,options.box,options.min,options.max,options.run,options.useWeight,options.btagFileName)
                else:
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'MuEle.root', cfg,'MuEle',options.min,options.max,options.run,options.useWeight,options.btagFileName)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'MuMu.root', cfg,'MuMu',options.min,options.max,options.run,options.useWeight,options.btagFileName)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'),  decorator, 'EleEle.root', cfg,'EleEle',options.min,options.max,options.run,options.useWeight,options.btagFileName)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'MuTau.root', cfg,'MuTau',options.min,options.max,options.run,options.useWeight,options.btagFileNam)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'Mu.root', cfg,'Mu',options.min,options.max,options.run,options.useWeight,options.btagFileName)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'EleTau.root', cfg,'EleTau',options.min,options.max,options.run,options.useWeight)
                    #convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'Ele.root', cfg,'Ele',options.min,options.max,options.run,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'Jet.root', cfg,'Jet',options.min,options.max,options.run,options.useWeight,options.btagFileName)
                    convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'),  decorator, 'TauTauJet.root', cfg,'TauTauJet',options.min,options.max,options.run,options.useWeight,options.btagFileName)
                    convertTree2Dataset(input.Get('EVENTS'), histoFile.Get('SMSCount'), decorator, 'MultiJet.root', cfg,'MultiJet',options.min,options.max,options.run,options.useWeight,options.btagFileName)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
