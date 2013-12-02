from optparse import OptionParser
import os
import math
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from array import *
from pdfShit import *

boxMap = {'MuEle':[0],'MuMu':[1],'EleEle':[2],'MuMultiJet':[3,4],'MuJet':[3,4],'Mu':[4],'EleMultiJet':[5,6],'EleJet':[5,6],'Jet':[7],'Jet2b':[7],'Jet1b':[7],'MultiJet':[8,9]}
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

def writeTree2DataSet(outputFile, outputBox, box, rMin, mRmin, label, args, histoFileName, jes_pe, pdf_pe, btag_pe, isr_pe, nominal, pdf_nom, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down):
    MGstringstart = outputFile.find("MG")+3
    MGstringend = outputFile.find("MCHI")-1
    MCHIstringstart = MGstringend+6
    MCHIstringend = MCHIstringstart+7
    MG = float(outputFile[MGstringstart:MGstringend])
    MCHI = float(outputFile[MCHIstringstart:MCHIstringend])
    print "(MG=%f,MCHI=%f)"%(MG,MCHI)

    args.Print()
    histoFile = rt.TFile.Open(histoFileName)
    smscount = histoFile.Get("SMSWALL")
    for histo in [nominal, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down]:     
        histo.Scale(1./smscount.GetBinContent(smscount.FindBin(MG,MCHI)))
    
    print "signal efficiency from nominal     = %f"%nominal.Integral()
    print "signal efficiency from pdf nominal = %f"%pdf_nom.Integral()
    print "integral of pdf relative errors = %f"%pdf_pe.Integral()

    #clear underflow and overflow bins in b-tags
    for histo in [jes_pe, pdf_pe, btag_pe, isr_pe, nominal, pdf_nom, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down]:
        for i in xrange(1,histo.GetXaxis().GetNbins()+1):
            for j in xrange(1,histo.GetYaxis().GetNbins()+1):
                #clear underflow and overflow bins in b-tags
                k = 0
                histo.SetBinContent(i,j,k,0)
                k = histo.GetZaxis().GetNbins()+1
                histo.SetBinContent(i,j,k,0)
        
    histoFile.Close()
    print "signal efficiency from nominal     = %f"%nominal.Integral()
    print "signal efficiency from pdf nominal = %f"%pdf_nom.Integral()

    
    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+label+outputBox,'RECREATE')
    print "writing dataset to", output.GetName()

    for histo in [jes_pe, pdf_pe, btag_pe, isr_pe, nominal, pdf_nom, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down]:
        histo.Write()
    
    output.Close()


def getUpDownHistos(tree,mRmin,mRmax,rsqMin,rsqMax,btagcutoff, box,noiseCut,histoFileName,outputFile):
    
    MRbins, Rsqbins, nBtagbins = getBinning(box)

    x = array("d",MRbins)
    y = array("d",Rsqbins)
    z = array("d",nBtagbins)
    
    jes_pe = rt.TH3D("wHisto_JESerr_pe", "wHisto_JESerr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_pe = rt.TH3D("wHisto_btagerr_pe", "wHisto_btagerr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    isr_pe = rt.TH3D("wHisto_ISRerr_pe", "wHisto_ISRerr_pe", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)

    jes_up = rt.TH3D("wHisto_JESerr_up", "wHisto_JESerr_up", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    jes_down = rt.TH3D("wHisto_JESerr_down", "wHisto_JESerr_down", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    
    btag_up = rt.TH3D("wHisto_btagerr_up", "wHisto_btagerr_up", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_down = rt.TH3D("wHisto_btagerr_down", "wHisto_btagerr_down", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    
    isr_up = rt.TH3D("wHisto_ISRerr_up", "wHisto_ISRerr_up", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    isr_down = rt.TH3D("wHisto_ISRerr_down", "wHisto_ISRerr_down", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    
    nominal = rt.TH3D("wHisto", "wHisto", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
  
    ###### PROEJCTION METHOD OF GETTING HISTOS ######
    BTAGNOM = "btag_nom"
    BTAGUP = "btag_up"
    BTAGDOWN = "btag_down"

    #BTAGNOM = "BTAG_NUM"
    #BTAGUP = "BTAG_NUM"
    #BTAGDOWN = "BTAG_NUM"

    boxCut = "(" + "||".join(["BOX_NUM==%i"%cut for cut in boxMap[box]]) + ")"
    
    jetReq = "(MR>0.)"
    if box in ["MuMultiJet", "EleMultiJet"]:
        jetReq = "(NJET_NOMU>=4)"
    elif box in ["MuJet", "EleJet"]:
        jetReq = "(NJET_NOMU<=3)"
    boxCut = "(" + jetReq + "&&" + boxCut + ")"
    print boxCut

    nB = 0
    nT = 0
    if outputFile.find("T1bbbb")!=-1:
        nB = 4
        nT = 0
    elif outputFile.find("T1tbbb")!=-1:
        nB = 3
        nT = 1
    elif outputFile.find("T1ttbb")!=-1:
        nB = 2
        nT = 2
    elif outputFile.find("T1tttb")!=-1:
        nB = 1
        nT = 3
    elif outputFile.find("T1tttt")!=-1:
        nB = 0
        nT = 4
    elif outputFile.find("T2bb")!=-1:
        nB = 2
        nT = 0
    elif outputFile.find("T2tb")!=-1:
        nB = 1
        nT = 1
    elif outputFile.find("T2tt")!=-1:
        nB = 0
        nT = 2
        
    #quarkCut = "N_B_gen==%i&&N_T_gen==%i"%(nB,nT)
    quarkCut = "(MR>0.)"
    print quarkCut

    condition = '0.95*WISR*WLEP*WPU*(%s && GOOD_PF && (%s) && %s >= 1 && MR_JESup>=%f && MR_JESup<=%f && RSQ_JESup>=%f && RSQ_JESup<=%f && (%s))' % (boxCut,noiseCut,BTAGNOM,mRmin,mRmax,rsqMin,rsqMax,quarkCut)
    tree.Project('wHisto_JESerr_up','%s:RSQ_JESup:MR_JESup'%(BTAGNOM),'(%s)' % (condition) )

    # BUG ALERT! WPU MISSING IN ALL THE FOLLOWING PROJECTIONS ORIGINALLY! SPOTTED 10/31/2013
    condition = '0.95*WISR*WLEP*WPU*(%s && GOOD_PF && (%s) && %s >= 1 && MR_JESdown>=%f && MR_JESdown<=%f && RSQ_JESdown>=%f && RSQ_JESdown<=%f && (%s))' % (boxCut,noiseCut,BTAGNOM,mRmin,mRmax,rsqMin,rsqMax,quarkCut)
    tree.Project('wHisto_JESerr_down','%s:RSQ_JESdown:MR_JESdown'%(BTAGNOM),'(%s)' % (condition) )
    
    condition = '0.95*WISR*WLEP*WPU*(%s && GOOD_PF && (%s) && %s >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f && (%s))' % (boxCut,noiseCut,BTAGUP,mRmin,mRmax,rsqMin,rsqMax,quarkCut)
    tree.Project('wHisto_btagerr_up','%s:RSQ:MR'%(BTAGUP),'(%s)' % (condition) )

    condition = '0.95*WISR*WLEP*WPU*(%s && GOOD_PF && (%s) && %s >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f && (%s))' % (boxCut,noiseCut,BTAGDOWN,mRmin,mRmax,rsqMin,rsqMax,quarkCut)
    tree.Project('wHisto_btagerr_down','%s:RSQ:MR'%(BTAGDOWN),'(%s)' % (condition) )
    
    condition = '0.95*WISRUP*WLEP*WPU*(%s && GOOD_PF && (%s) && %s >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f && (%s))' % (boxCut,noiseCut,BTAGNOM,mRmin,mRmax,rsqMin,rsqMax,quarkCut)
    tree.Project('wHisto_ISRerr_up','%s:RSQ:MR'%(BTAGNOM),'(%s)' % (condition) )
    
    condition = '0.95*WISRDOWN*WLEP*WPU*(%s && GOOD_PF && (%s) && %s >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f && (%s))' % (boxCut,noiseCut,BTAGNOM,mRmin,mRmax,rsqMin,rsqMax,quarkCut)
    tree.Project('wHisto_ISRerr_down','%s:RSQ:MR'%(BTAGNOM),'(%s)' % (condition) )
    
    condition = '0.95*WISR*WLEP*WPU*(%s && GOOD_PF && (%s) && %s >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f && (%s))' % (boxCut,noiseCut,BTAGNOM,mRmin,mRmax,rsqMin,rsqMax,quarkCut)
    tree.Project('wHisto','%s:RSQ:MR'%(BTAGNOM),'(%s)' % (condition) )

    #BUG ALERT! condition should be the NOMINAL! SPOTTED 10/31/2013
    condition = '0.95*WISR*WLEP*WPU*(%s && GOOD_PF && (%s) && %s >= 1 && MR>=%f && MR<=%f && RSQ>=%f && RSQ<=%f && (%s))' % (boxCut,noiseCut,BTAGNOM,mRmin,mRmax,rsqMin,rsqMax,quarkCut)
    pdf_nom, pdf_pe = makePDFPlot(tree, box, nominal, condition, relative = True, BTAGNOM = BTAGNOM, histoFileName = histoFileName,outputFile = outputFile)
    
    pdf_up = pdf_pe.Clone("wHisto_pdferr_up") 
    pdf_up.SetTitle("wHisto_pdferr_up") 
    pdf_up.Multiply(pdf_nom)
    pdf_up.Add(pdf_nom)
    
    pdf_down = pdf_pe.Clone("wHisto_pdferr_down") 
    pdf_down.SetTitle("wHisto_pdferr_down") 
    pdf_down.Multiply(pdf_nom)
    pdf_down.Scale(-1.0)
    pdf_down.Add(pdf_nom)
    
    ###### JES ######
    #using (UP - DOWN)/2:
    jes_pe.Add(jes_up,0.5)
    jes_pe.Add(jes_down,-0.5)

    #divide by (UP + NOM + DOWN)/3:
    jes_denom = rt.TH3D("wHisto_JESerr_denom", "wHisto_JESerr_denom", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    jes_denom.Add(jes_up,1.0/3.0)
    jes_denom.Add(pdf_nom,1.0/3.0)
    jes_denom.Add(jes_down,1.0/3.0)

    jes_pe.Divide(jes_denom)

    ###### BTAG ######
    #using (UP - DOWN)/2:
    btag_pe.Add(btag_up,0.5)
    btag_pe.Add(btag_down,-0.5)

    #divide by (UP + NOM + DOWN)/3
    btag_denom = rt.TH3D("wHisto_btagerr_denom", "wHisto_btagerr_denom", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_denom.Add(btag_up,1.0/3.0)
    btag_denom.Add(pdf_nom,1.0/3.0)
    btag_denom.Add(btag_down,1.0/3.0)
    
    btag_pe.Divide(btag_denom)

    

    ###### ISR ######
    #using (UP - DOWN)/2:
    isr_pe.Add(isr_up,0.5)
    isr_pe.Add(isr_down,-0.5)

    #divide by (UP + NOM + DOWN)/3
    isr_denom = rt.TH3D("wHisto_ISRerr_denom", "wHisto_ISRerr_denom", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    isr_denom.Add(isr_up,1.0/3.0)
    isr_denom.Add(pdf_nom,1.0/3.0)
    isr_denom.Add(isr_down,1.0/3.0)
    
    isr_pe.Divide(isr_denom)
    
    print "Number of entries in Box %s nominal     = %i"%(box,nominal.GetEntries())
    print "Sum of weights in Box %s nominal        = %f"%(box,nominal.Integral())
    
    print "Number of entries in Box %s pdf nominal = %i"%(box,pdf_nom.GetEntries())
    print "Sum of weights in Box %s pdf nominal    = %f"%(box,pdf_nom.Integral())
    
    return jes_pe, pdf_pe, btag_pe, isr_pe, nominal, pdf_nom, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down
    
def convertTree2Dataset(tree, histoFileName, outputFile, outputBox, config, box, min, max, run, useWeight, write = True):
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
    if box in ["MuEle", "MuMu", "EleEle"]:
        btagcutoff = 1

    if box in ["Jet", "MultiJet", "EleEle", "Jet2b", "Jet1b", "EleJet", "EleMultiJet"]:
        noiseCut = "abs(TMath::Min( abs(atan2(MET_y,MET_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_y,MET_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"
    elif box in ["MuEle", "MuMu", "MuMultiJet","MuJet"]:
        noiseCut = "abs(TMath::Min( abs(atan2(MET_NOMU_y,MET_NOMU_x)-atan2(MET_CALO_y,MET_CALO_x) ), abs( TMath::TwoPi()-atan2(MET_NOMU_y,MET_NOMU_x)+atan2(MET_CALO_y,MET_CALO_x ) ) ) - TMath::Pi()) > 1.0"

    jes_pe, pdf_pe, btag_pe, isr_pe, nominal, pdf_nom, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down = getUpDownHistos(tree,mRmin,mRmax,rsqMin,rsqMax,btagcutoff, box,noiseCut,histoFileName,outputFile)
    
    writeTree2DataSet(outputFile, outputBox, box, rMin, mRmin, label, args, histoFileName, jes_pe, pdf_pe, btag_pe, isr_pe, nominal, pdf_nom, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down)

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
    for f in args:
        if f.lower().endswith('.root'):
            input = rt.TFile.Open(f)
            decorator = options.outdir+"/"+os.path.basename(f)[:-5]
            print decorator
            if not options.eff:
                #dump the trees for the different datasets
                if options.box != None:
                    convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, options.box+'.root', cfg,options.box,options.min,options.max,options.run,options.useWeight)
                else:
                    if f.find("T2tt")!=-1 or f.find("T1tttt")!=-1:
                        convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, 'MuEle.root', cfg,'MuEle',options.min,options.max,options.run,options.useWeight)
                        convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, 'MuMu.root', cfg,'MuMu',options.min,options.max,options.run,options.useWeight)
                        convertTree2Dataset(input.Get('EVENTS'), options.histoFileName,  decorator, 'EleEle.root', cfg,'EleEle',options.min,options.max,options.run,options.useWeight)
                        convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, 'MuJet.root', cfg,'MuJet',options.min,options.max,options.run,options.useWeight)
                        convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, 'MuMultiJet.root', cfg,'MuMultiJet',options.min,options.max,options.run,options.useWeight)
                        convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, 'EleJet.root', cfg,'EleJet',options.min,options.max,options.run,options.useWeight)
                        convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, 'EleMultiJet.root', cfg,'EleMultiJet',options.min,options.max,options.run,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, 'Jet1b.root', cfg,'Jet1b',options.min,options.max,options.run,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, 'Jet2b.root', cfg,'Jet2b',options.min,options.max,options.run,options.useWeight)
                    convertTree2Dataset(input.Get('EVENTS'), options.histoFileName, decorator, 'MultiJet.root', cfg,'MultiJet',options.min,options.max,options.run,options.useWeight)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
