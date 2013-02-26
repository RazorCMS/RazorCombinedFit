from optparse import OptionParser
import os
import math
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from array import *
from pdfShit import *

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'MuTau':3,'Mu':4,'EleTau':5,'Ele':6,'Jet':7,'TauTauJet':8,'MultiJet':9}
lumi = 19.3

def getBinning(box):
    MRbins = cfg.getBinning(box)[0]
    Rsqbins = cfg.getBinning(box)[1]
    nBtagbins = cfg.getBinning(box)[2]
    print "SIGNAL BINNING"
    print "MR: ", MRbins
    print "Rsq: ", Rsqbins
    print "nBtag: ", nBtagbins
    return MRbins, Rsqbins, nBtagbins

def writeTree2DataSet(outputFile, outputBox, box, rMin, mRmin, label, args, smscount,jes_pe, pdf_pe, btag_pe, nominal, pdf_nom):
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
    pdf_nom.Scale(1./smscount.GetBinContent(smscount.FindBin(MG,MCHI)))
    print "signal efficiency from nominal     = %f"%nominal.Integral()
    print "signal efficiency from pdf nominal = %f"%pdf_nom.Integral()
    print "integral of pdf relative errors = %f"%pdf_pe.Integral()

    # now collapse the b-tag information for certain boxes
    if box=="TauTauJet" or box=="MuEle" or box=="EleEle" or box=="MuMu":
        for histo in [nominal, jes_pe, pdf_pe, btag_pe, pdf_nom]:
            for i in xrange(1,histo.GetXaxis().GetNbins()+1):
                for j in xrange(1,histo.GetYaxis().GetNbins()+1):
                    sumOverBtags = sum([histo.GetBinContent(i,j,k) for k in xrange(1,histo.GetZaxis().GetNbins()+1)])
                    histo.SetBinContent(i,j,1,sumOverBtags)
                    [histo.SetBinContent(i,j,k,0) for k in xrange(2,histo.GetZaxis().GetNbins()+1)]
                
    print "signal efficiency from nominal     = %f"%nominal.Integral()
    print "signal efficiency from pdf nominal = %f"%pdf_nom.Integral()
    nominal.Write()
    jes_pe.Write()
    pdf_pe.Write()
    btag_pe.Write()
    pdf_nom.Write()
    
    output.Close()


def getUpDownHistos(tree,mRmin,mRmax,rsqMin,rsqMax,btagcutoff, box,noiseCut):
    
    MRbins, Rsqbins, nBtagbins = getBinning(box)

    x = array("d",MRbins)
    y = array("d",Rsqbins)
    z = array("d",nBtagbins)
    
    jes_pe = rt.TH3D("wHisto_JESerr_pe", "wHisto_JESerr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_pe = rt.TH3D("wHisto_btagerr_pe", "wHisto_btagerr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)

    jes_up = rt.TH3D("wHisto_JESerr_up", "wHisto_JESerr_up", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    jes_down = rt.TH3D("wHisto_JESerr_down", "wHisto_JESerr_down", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    
    btag_up = rt.TH3D("wHisto_btagerr_up", "wHisto_btagerr_up", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_down = rt.TH3D("wHisto_btagerr_down", "wHisto_btagerr_down", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    
    nominal = rt.TH3D("wHisto", "wHisto", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
  
    ###### PROEJCTION METHOD OF GETTING HISTOS ######

    condition = '0.95*WLEP*WPU*((BOX_NUM == %i) && GOOD_PF && (%s) && btag_nom >= 1 && MR_JESup>=%f && MR_JESup<=%f && RSQ_JESup>=%f && RSQ_JESup<=%f)' % (boxMap[box],noiseCut,mRmin,mRmax,rsqMin,rsqMax)
    tree.Project('wHisto_JESerr_up','btag_nom:RSQ_JESup:MR_JESup','(%s)' % (condition) )

    condition = '0.95*WLEP*WPU*((BOX_NUM == %i) && GOOD_PF && (%s) && btag_nom >= 1 && MR_JESdown>=%f && MR_JESdown<=%f && RSQ_JESdown>=%f && RSQ_JESdown<=%f)' % (boxMap[box],noiseCut,mRmin,mRmax,rsqMin,rsqMax)
    tree.Project('wHisto_JESerr_down','btag_nom:RSQ_JESdown:MR_JESdown','(%s)' % (condition) )
    
    condition = '0.95*WLEP*WPU*((BOX_NUM == %i) && GOOD_PF && (%s) && btag_up >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f)' % (boxMap[box],noiseCut,mRmin,mRmax,rsqMin,rsqMax)
    tree.Project('wHisto_btagerr_up','btag_up:RSQ:MR','(%s)' % (condition) )

    condition = '0.95*WLEP*WPU*((BOX_NUM == %i) && GOOD_PF && (%s) && btag_down >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f)' % (boxMap[box],noiseCut,mRmin,mRmax,rsqMin,rsqMax)
    tree.Project('wHisto_btagerr_down','btag_down:RSQ:MR','(%s)' % (condition) )

    condition = '0.95*WLEP*WPU*((BOX_NUM == %i) && GOOD_PF && (%s) && btag_nom >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f)' % (boxMap[box],noiseCut,mRmin,mRmax,rsqMin,rsqMax)
    tree.Project('wHisto','btag_nom:RSQ:MR','(%s)' % (condition) )
    
    pdf_nom, pdf_pe = makePDFPlot(tree, nominal, condition, relative = True)
    ###### JES ######
    #using (UP - DOWN)/2:
    jes_pe.Add(jes_up,0.5)
    jes_pe.Add(jes_down,-0.5)

    #divide by (UP + NOM + DOWN)/3:
    jes_denom = rt.TH3D("wHisto_JESerr_denom", "wHisto_JESerr_denom", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    jes_denom.Add(jes_up,1.0/3.0)
    jes_denom.Add(nominal,1.0/3.0)
    jes_denom.Add(jes_down,1.0/3.0)

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
    
    print "Number of entries in Box %s nominal     = %i"%(box,nominal.GetEntries())
    print "Sum of weights in Box %s nominal        = %f"%(box,nominal.Integral())
    
    print "Number of entries in Box %s pdf nominal = %i"%(box,pdf_nom.GetEntries())
    print "Sum of weights in Box %s pdf nominal    = %f"%(box,pdf_nom.Integral())
    
    return jes_pe, pdf_pe, btag_pe, nominal, pdf_nom
    
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

    jes_pe, pdf_pe, btag_pe, nominal, pdf_nom = getUpDownHistos(tree,mRmin,mRmax,rsqMin,rsqMax,btagcutoff, box,noiseCut)
    
    writeTree2DataSet(outputFile, outputBox, box, rMin, mRmin, label, args, smscount, jes_pe, pdf_pe, btag_pe, nominal, pdf_nom)

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
    parser.add_option('--histofile',dest="histoFileName",default="T1bbbb_histo.root",type="string",
                  help="File containing histogram of map of SMS generated events")
    parser.add_option('-w','--weight',dest="useWeight",default=True,action='store_true',
                  help="Use weights, if available, default is WLEP*WPU")
      
    (options,args) = parser.parse_args()
    
    if options.config is None:
        import inspect, os
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(convertTree2Dataset)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    
    print 'Input files are %s' % ', '.join(args)
    histoFile = rt.TFile.Open(options.histoFileName)
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
