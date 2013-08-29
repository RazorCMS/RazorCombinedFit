from optparse import OptionParser
import os, sys
from array import array
import pickle
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from BTagSFUtil import BTag
from LepSFUtil import *
from pdfUtil import *

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'Mu':3,'Ele':4,'Had':5,'BJet':6}
cross_sections = {'SingleTop_s':4.21,'SingleTop_t':64.6,'SingleTop_tw':10.6,\
                               'TTj':157.5,'Zll':3048,'Znn':2*3048,'Wln':31314,\
                               'WW':43,'WZ':18.2,'ZZ':5.9,'Vgamma':173
                               }
lumi = 1.0

sys.path.append(os.path.join(os.environ['RAZORFIT_BASE'],'macros/multijet'))
from CalcBDT import CalcBDT

from Boxes import *

# Find the probability of an event having at least one btag
def findBTagProb(jets, efftype = 'data', SFerrdir = 0, doLight = False, CFerrdir = 0):
    pr_j = 1
    for j in jets:
        if j.pt < 30 or abs(j.eta) > 2.4 or j.btagv < 0:
            continue
        eff_fast, eff_fastE = tagger.getEfficiencyFastSim(j.btagv, j.pt, j.eta, j.partonFlavour)
        #FF: full factor = SF*CF
        SF, SFerr = tagger.getBTagScaleFullSim(j.btagv, j.pt, j.eta, j.partonFlavour)
        CF, CFerr = tagger.getBTagScaleFastSim(j.btagv, j.pt, j.eta, j.partonFlavour)        
      
        if SFerrdir:
            if (not doLight and abs(j.partonFlavour) in [4,5]) or (doLight and not abs(j.partonFlavour) in [4,5]):
                SF = SF + (SFerrdir*SFerr)
                #print 'eff, efferr SF', eff_fast, eff_fast*SF, eff_fast*SF*CF
        if CFerrdir:
            CF = CF + (CFerrdir*CFerr)
            #print 'eff, efferr CF', eff_fast, eff_fast*CF, eff_fast*SF*CF
        eff_data = eff_fast*SF*CF
        eff = 1
        if efftype == 'data':
            eff = eff_data
        if efftype == 'fast':
            eff = eff_fast
        pr_j = pr_j*(1 - eff)
        
    pr_e = 1 - pr_j
    return pr_e

# Find the probability of an event having one muon
def findLeptonProb(flavor, pt = 0., eta = 0., errDir = 0):
    if flavor == 'mu':
        SFID, SFIso, SFTrigger  = muonScaling.getScaleFactor(pt, eta, errDir)
    elif flavor == 'ele':
        SFID = eleScaling.getScaleFactor(pt, eta, errDir)
        SFIso = 1.
        SFTrigger = 1.
    else :
        SFID = 1.
        SFIso = 1.
        SFTrigger = 1.
  
    return SFID, SFIso, SFTrigger

def writeTree2DataSet(data, outputdir, outputFile, outputBox, rMin, mRmin, mstop, mlsp):
    output = rt.TFile.Open(outputdir +'/'+outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+str(mstop)+'_'+str(mlsp)+'_'+outputBox,'RECREATE')
    print output.GetName()
    for d in data:
        d.Write()
    output.Close()

def convertTree2Dataset(tree, outputDir, outputFile, config, Min, Max, filter, run, mstop, mlsp, write = True):
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
        for h in filter.dumper.sel.headers_for_MVA():
            workspace.factory('%s[0,-INF,+INF]' % h)
    
    args = workspace.allVars()
    data = rt.RooDataSet('RMRTree','Selected R and MR',args)
    
    #we cut away events outside our MR window
    if box == 'BJetHS' or box == 'BJetLS':
        mRmin = 500.0#args['MR'].getMin()
    else :
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
    
    events = {}


    # Get the binning:

    # define the loosest bin ranges
    varBin = 0
    #loose_bin = 'Had'
    #if loose_bin not in boxes:
    #    loose_bin = 'Had'

    print box

    binedgexLIST = []
    binedgeyLIST = []
    #either use a binning scheme defined here or take from the config
    if not config.hasBinning(box):
        # if the bin is fixed, do 50 GeV in mR
        # and 0.1 in R^2
        binwMR = 50.
        binwR2 = 0.1
        #use a fixed bin for mR
        if varBin != 1: maxVal = mRmax
        else: maxVal = 700.
        mRedge = mRmin
        while mRedge < maxVal: 
            binedgexLIST.append(mRedge)
            mRedge = mRedge + binwMR
        binedgexLIST.append(maxVal)
        if varBin == 1:
            if mRmax> 800: binedgexLIST.append(800)
            if mRmax> 900: binedgexLIST.append(900)
            if mRmax> 1000: binedgexLIST.append(1000)
            if mRmax> 1200: binedgexLIST.append(1200)
            if mRmax> 1600: binedgexLIST.append(1600)
            if mRmax> 2000: binedgexLIST.append(2000)
            if mRmax> 2800: binedgexLIST.append(2800)
            binedgexLIST.append(mRmax)

            #use a fixed bin for R^2
            if varBin != 1:
                R2edge = rsqMin
                while R2edge <rsqMax: 
                    binedgexLIST.append(R2edge)
                    R2edge = R2edge + binwR2
                binedgeyLIST.append(rsqMax)
            else: 
               #use fixed binning 
                binedgeyLIST = [rsqMin,0.18,0.2,0.3,0.4,0.5]
    else:
        #take from the config
        binning = config.getBinning(box)
        #MR and Rsq in that order
        binedgexLIST.extend(binning[0])
        binedgeyLIST.extend(binning[1])

    nbinx =  len(binedgexLIST)-1
    nbiny = len(binedgeyLIST)-1    

    print binedgexLIST
    print binedgeyLIST

    binedgex = array('d',binedgexLIST)
    binedgey = array('d',binedgeyLIST)

    print binedgex
    print binedgey

    # Book the histograms
    wHisto          = rt.TH2D("wHisto", "wHisto", nbinx, binedgex, nbiny, binedgey)
    wHisto_JESup    = rt.TH2D("wHisto_JESup", "wHisto_JESup", nbinx, binedgex, nbiny, binedgey)
    wHisto_JESdown  = rt.TH2D("wHisto_JESdown", "wHisto_JESdown", nbinx, binedgex, nbiny, binedgey)
    wHisto_pdfcen   = rt.TH2D("wHisto_pdfcen", "wHisto_pdfcen", nbinx, binedgex, nbiny, binedgey)
    wHisto_pdferr   = rt.TH2D("wHisto_pdferr", "wHisto_pdferr", nbinx, binedgex, nbiny, binedgey)
    wHisto_btagup   = rt.TH2D("wHisto_btagup", "wHisto_btagup", nbinx, binedgex, nbiny, binedgey)
    wHisto_btagdown = rt.TH2D("wHisto_btagdown", "wHisto_btagdown", nbinx, binedgex, nbiny, binedgey)
    wHisto_lepup    = rt.TH2D("wHisto_lepup", "wHisto_lepup", nbinx, binedgex, nbiny, binedgey)
    wHisto_lepdown  = rt.TH2D("wHisto_lepdown", "wHisto_lepdown", nbinx, binedgex, nbiny, binedgey)
    wHisto_isrup    = rt.TH2D("wHisto_isrup", "wHisto_isrup", nbinx, binedgex, nbiny, binedgey)
    wHisto_isrdown  = rt.TH2D("wHisto_isrdown", "wHisto_isrdown", nbinx, binedgex, nbiny, binedgey)

    # Book histograms for PDFs:
    vwHisto_pdfCTEQ = []
    vwHisto_pdfNNPDF = []

    for icteq in range(45):
        wHisto_pdfCTEQ = rt.TH2D("wHisto_pdfCTEQ_%s" % icteq, "wHisto_pdfCTEQ_%s" % icteq, \
                                 nbinx, binedgex, nbiny, binedgey)
        vwHisto_pdfCTEQ.append(wHisto_pdfCTEQ)

    for innpdf in range(101):
        wHisto_pdfNNPDF = rt.TH2D("wHisto_pdfNNPDF_%s" % innpdf, "wHisto_pdfNNPDF_%s" % innpdf, \
                                 nbinx, binedgex, nbiny, binedgey)
        vwHisto_pdfNNPDF.append(wHisto_pdfNNPDF)
        
    # Load the file with the SMS number of total events per each point
    #file = open('/afs/cern.ch/work/l/lucieg/public/forRazorStop/SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY/SMS-T2tt_mStop-Combo_mLSP_'+str(mlsp)+'_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY.pkl','rb')
    file = open('/afs/cern.ch/work/l/lucieg/public/forRazorStop/SMS-T2tt_mStop-Combo_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY/SMS-T2tt_mStop-Combo.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY.pkl','rb')
    norms = pickle.load(file)
    print norms
    print 'Number of entries:', tree.GetEntries()

    isrWeightSum = 0
    for entry in xrange(tree.GetEntries()):
        tree.GetEntry(entry)
        isrWeightSum += tree.isrWeight
        
    for entry in xrange(tree.GetEntries()):
        tree.GetEntry(entry)

        if (entry % 50000 ==  0): print entry

        if (mstop != tree.mStop or mlsp != tree.mLSP):
            continue

        # Get the original event weight, which is 1/nevts for a given process
        point = (tree.mStop, tree.mLSP)
        
        weight = 1./(norms[point]) 

        ####First, apply a common selection
        #take only events in the MR and R2 region
        if tree.MR > mRmax or tree.MR < mRmin or tree.RSQ < rsqMin or tree.RSQ > rsqMax:
            continue

        #apply the box based filter class
        if not filter(tree): continue
        bdt = -9999.
        if filter.dumper is not None:
            bdt = filter.dumper.bdt()

        #### now fill info histo and workspace
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
        e = (tree.run,tree.lumi,tree.event)
        #filter out duplicate events in case there are any
        if e in events:
            continue
        events[e] = None
       
        a.setRealValue('MR',tree.MR, True)
        a.setRealValue('Rsq',tree.RSQ, True)
        a.setRealValue('nBtag',nBtag)
        a.setRealValue('nLepton',tree.nMuonLoose + tree.nElectronLoose )#+ tree.nTauLoose)
        a.setRealValue('nElectron',tree.nElectronLoose)
        a.setRealValue('nMuon',tree.nMuonLoose)
        a.setRealValue('nTau',tree.nTauLoose)
        a.setRealValue('nJet',tree.nJet)
        a.setRealValue('nVertex',tree.nVertex)
        a.setRealValue('W',1.0)
        a.setRealValue('BDT',bdt)
        
        a.setRealValue('genInfo',tree.genInfo)

        if filter.dumper is not None:
            for h in filter.dumper.sel.headers_for_MVA():
                a.setRealValue(h,getattr(filter.dumper.sel,h)())
        
        data.add(a)

        #### systematics
        # Get the btag systematics
        jet_pt = tree.jet_pt
        jet_eta = tree.jet_eta
        jet_csv = tree.jet_csv
        jet_fl = tree.jet_fl

        jets = []
        for j in range(0, len(jet_pt)):
            tag = 0
            xjet = BJet(jet_pt[j], jet_eta[j], jet_csv[j], jet_fl[j])
            jets.append(xjet)

        bt_prob_fast = findBTagProb(jets, efftype='fast')

        btw_nominal = findBTagProb(jets, 'data')/bt_prob_fast

        btw_SF_bc_up = findBTagProb(jets, efftype='data', SFerrdir=+1)/bt_prob_fast
        btw_SF_bc_Eup = abs(btw_nominal - btw_SF_bc_up)
        btw_SF_bc_dw = findBTagProb(jets, efftype='data', SFerrdir=-1)/bt_prob_fast
        btw_SF_bc_Edw = abs(btw_nominal - btw_SF_bc_dw)
     
        btw_SF_lt_up = findBTagProb(jets, efftype='data', SFerrdir=+1, doLight=True)/bt_prob_fast
        btw_SF_lt_Eup = abs(btw_nominal - btw_SF_lt_up)
        btw_SF_lt_dw = findBTagProb(jets, efftype='data', SFerrdir=-1, doLight=True)/bt_prob_fast
        btw_SF_lt_Edw = abs(btw_nominal - btw_SF_lt_dw)
     
        btw_CF_up = findBTagProb(jets, efftype='data', CFerrdir=+1)/bt_prob_fast
        btw_CF_Eup = abs(btw_nominal - btw_CF_up)
        btw_CF_dw = findBTagProb(jets, efftype='data', CFerrdir=-1)/bt_prob_fast
        btw_CF_Edw = abs(btw_nominal - btw_CF_dw)
      
        btw_Eup = rt.TMath.Sqrt(btw_SF_bc_Eup**2 + min(btw_SF_lt_Eup, btw_SF_lt_Edw)**2 + btw_CF_Edw**2)
        btw_Edw = rt.TMath.Sqrt(btw_SF_bc_Edw**2 + min(btw_SF_lt_Eup, btw_SF_lt_Edw)**2 + btw_CF_Eup**2)

        btw_up = btw_nominal + btw_Eup
        btw_dw = btw_nominal - btw_Edw

        # Get lepton systematics
        pt = 0.
        eta = 0.
        if len(tree.muTight_pt) > 0 :
            flavor = 'mu'
            pt  = tree.muTight_pt[0]
            eta = tree.muTight_eta[0]
        elif len(tree.eleTight_pt) > 0 :
            flavor = 'ele'
            pt  = tree.eleTight_pt[0]
            eta = tree.eleTight_eta[0]
        else :
            flavor = ''

        if flavor == 'ele' and abs(eta)>2.5:
            continue
        
        SFID_nominal, SFIso_nominal, SFTrigger_nominal = findLeptonProb(flavor, pt, eta,  errDir = 0)
        SFID_Up     , SFIso_Up     , SFTrigger_Up      = findLeptonProb(flavor, pt, eta,  errDir = 1 )
        SFID_Down   , SFIso_Down   , SFTrigger_Down    = findLeptonProb(flavor, pt, eta,  errDir = -1)

        EIDUp        = abs( SFID_nominal - SFID_Up )
        EIsoUp       = abs( SFIso_nominal - SFIso_Up )
        ETriggerUp   = abs( SFTrigger_nominal - SFTrigger_Up )

        EIDDown      = abs( SFID_nominal - SFID_Down )
        EIsoDown     = abs( SFIso_nominal - SFIso_Down )
        ETriggerDown = abs( SFTrigger_nominal - SFTrigger_Down )

        lepw_Eup = rt.TMath.Sqrt( EIDUp*EIDUp + EIsoUp*EIsoUp + ETriggerUp*ETriggerUp )
        lepw_Edw = rt.TMath.Sqrt( EIDDown*EIDDown + EIsoDown*EIsoDown + ETriggerDown*ETriggerDown )

        lepw_nominal = SFID_nominal*SFIso_nominal*SFTrigger_nominal
        lepw_up      = lepw_nominal + lepw_Eup
        lepw_dw      = lepw_nominal - lepw_Edw

        #get isr
        isrw_nominal = tree.isrWeight #/ isrWeightSum
        isrw_up      = tree.isrWeightUp 
        isrw_dw      = tree.isrWeightDown 
        
        # Fill the histograms:

        MR = tree.MR
        RSQ = tree.RSQ

        wHisto.Fill(MR, RSQ, weight*btw_nominal*lepw_nominal*isrw_nominal)
        #err
        wHisto_JESup.Fill(tree.MR_JES_UP, tree.RSQ_JES_DOWN, weight*btw_nominal*lepw_nominal*isrw_nominal)
        wHisto_JESdown.Fill(tree.MR_JES_DOWN, tree.RSQ_JES_DOWN, weight*btw_nominal*lepw_nominal*isrw_nominal)
        wHisto_btagup.Fill(MR, RSQ, weight*btw_up*lepw_nominal*isrw_nominal)
        wHisto_btagdown.Fill(MR, RSQ, weight*btw_dw*lepw_nominal*isrw_nominal)
        wHisto_lepup.Fill(MR, RSQ, weight*lepw_up*btw_nominal*isrw_nominal)
        wHisto_lepdown.Fill(MR, RSQ, weight*lepw_dw*btw_nominal*isrw_nominal)
        wHisto_isrup.Fill(MR, RSQ, weight*isrw_up*btw_nominal*lepw_nominal)
        wHisto_isrdown.Fill(MR, RSQ, weight*isrw_dw*btw_nominal*lepw_nominal)
        # PDFs:
        CTEQ66_W = tree.CTEQ66_W
        NNPDF_W = tree.MRST2006NNLO_W

        for icteq in range(45):
            vwHisto_pdfCTEQ[icteq].Fill(MR, RSQ, weight*btw_nominal*lepw_nominal*CTEQ66_W[icteq])
        for innpdf in range(101):
            vwHisto_pdfNNPDF[innpdf].Fill(MR, RSQ, weight*btw_nominal*lepw_nominal*NNPDF_W[innpdf])        

    #end of the tree loop
    
    # Make the overall PDF histograms:

    # evaluate CTEQ:
    # Following are the histogrrams storing +- % error on the PDF center:
    for i in range(1, nbinx+1):
        for j in range(1, nbiny+1):
            pdfcenters = []
            pdferrors = []
            if wHisto.GetBinContent(i,j) != 0 and wHisto.Integral() != 0.:
                w = []
                for k in range(0,45):
                    w.append(vwHisto_pdfCTEQ[k].GetBinContent(i,j))
                pdfCTEQcen, pdfCTEQerr = GetPDFCenErr(w, 'CTEQ')
                pdfcenters.append(pdfCTEQcen)
                pdferrors.append(pdfCTEQerr)
                #print 'orig central:', wHisto.GetBinContent(i,j), hw[0]
                w = []
                for k in range(0,101):
                    w.append(vwHisto_pdfNNPDF[k].GetBinContent(i,j))
                pdfNNPDFcen, pdfNNPDFerr = GetPDFCenErr(w, 'NNPDF')
                pdfcenters.append(pdfNNPDFcen)
                pdferrors.append(pdfNNPDFerr)
                pdfcen, pdferr = GetPDFEnvelope(pdfcenters, pdferrors)
                wHisto_pdfcen.SetBinContent(i,j,pdfcen)
                wHisto_pdferr.SetBinContent(i,j,pdferr)
                print 'pdfcen, pdferr, err/cen', pdfcen, pdferr, pdferr/pdfcen

    # PDFs done

    # Percent error histograms:
    wHisto_JESup_pe = rt.TH2D("wHisto_JESup_pe", "wHisto_JESup_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_JESdown_pe = rt.TH2D("wHisto_JESdown_pe", "wHisto_JESdown_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_JESerr_pe = rt.TH2D("wHisto_JESerr_pe", "wHisto_JESerr_pe", nbinx, binedgex, nbiny, binedgey)    
    wHisto_pdferr_pe = rt.TH2D("wHisto_pdferr_pe", "wHisto_pdferr_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_btagup_pe = rt.TH2D("wHisto_btagup_pe", "wHisto_btagup_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_btagdown_pe = rt.TH2D("wHisto_btagdown_pe", "wHisto_btagdown_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_btagerr_pe = rt.TH2D("wHisto_btagerr_pe", "wHisto_btagerr_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_lepup_pe = rt.TH2D("wHisto_lepup_pe", "wHisto_lepup_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_lepdown_pe = rt.TH2D("wHisto_lepdown_pe", "wHisto_lepdown_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_leperr_pe = rt.TH2D("wHisto_leperr_pe", "wHisto_leperr_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_isrup_pe = rt.TH2D("wHisto_isrup_pe", "wHisto_isrup_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_isrdown_pe = rt.TH2D("wHisto_isrdown_pe", "wHisto_isrdown_pe", nbinx, binedgex, nbiny, binedgey)
    wHisto_isrerr_pe = rt.TH2D("wHisto_isrerr_pe", "wHisto_isrerr_pe", nbinx, binedgex, nbiny, binedgey)

    for i in range(1, nbinx+1):
        for j in range(1, nbiny+1):
            nominal = wHisto.GetBinContent(i, j)
            JESup = wHisto_JESup.GetBinContent(i, j)
            JESdown = wHisto_JESdown.GetBinContent(i, j)
            pdfcen = wHisto_pdfcen.GetBinContent(i, j)
            pdferr = wHisto_pdferr.GetBinContent(i, j)
            btagup = wHisto_btagup.GetBinContent(i, j)
            btagdown = wHisto_btagdown.GetBinContent(i, j)
            lepup = wHisto_lepup.GetBinContent(i, j)
            lepdown = wHisto_lepdown.GetBinContent(i, j)
            isrup = wHisto_lepup.GetBinContent(i, j)
            isrdown = wHisto_lepdown.GetBinContent(i, j)

            if nominal == 0:
                
                JESup_pe = 0
                wHisto_JESup_pe.SetBinContent(i, j, JESup_pe)
                
                JESdown_pe = 0
                wHisto_JESdown_pe.SetBinContent(i, j, JESdown_pe)

                JESerr_pe = 0
                wHisto_JESerr_pe.SetBinContent(i, j, JESerr_pe)
                
                pdferr_pe = 0
                wHisto_pdferr_pe.SetBinContent(i, j, pdferr)
                
                btagup_pe = 0
                wHisto_btagup_pe.SetBinContent(i, j, btagup_pe)
                
                btagdown_pe = 0
                wHisto_btagdown_pe.SetBinContent(i, j, btagdown_pe)

                btagerr_pe = 0
                wHisto_btagerr_pe.SetBinContent(i, j, btagerr_pe)

                lepup_pe = 0
                wHisto_lepup_pe.SetBinContent(i, j, lepup_pe)
                
                lepdown_pe = 0
                wHisto_lepdown_pe.SetBinContent(i, j, lepdown_pe)

                leperr_pe = 0
                wHisto_leperr_pe.SetBinContent(i, j, leperr_pe)

                isrup_pe = 0
                wHisto_isrup_pe.SetBinContent(i, j, isrup_pe)
                
                isrdown_pe = 0
                wHisto_isrdown_pe.SetBinContent(i, j, isrdown_pe)

                isrerr_pe = 0
                wHisto_isrerr_pe.SetBinContent(i, j, isrerr_pe)
              
                continue


            JESup_pe = abs(nominal - JESup) / nominal
            wHisto_JESup_pe.SetBinContent(i, j, JESup_pe)

            JESdown_pe = abs(nominal - JESdown) / nominal
            wHisto_JESdown_pe.SetBinContent(i, j, JESdown_pe)

            JESerr_pe = (JESup - JESdown) / (2*nominal)
            if abs(JESerr_pe) > 0.75:
                JESerr_pe = 0.75*(JESerr_pe / abs(JESerr_pe))
            wHisto_JESerr_pe.SetBinContent(i, j, JESerr_pe)
            
            pdferr_pe = pdferr / pdfcen
            wHisto_pdferr_pe.SetBinContent(i, j, pdferr_pe)

            btagup_pe = abs(nominal - btagup) / nominal
            wHisto_btagup_pe.SetBinContent(i, j, btagup_pe)

            btagdown_pe = abs(nominal - btagdown) / nominal
            wHisto_btagdown_pe.SetBinContent(i, j, btagdown_pe)

            btagerr_pe = (btagup_pe + btagdown_pe) / 2.
            wHisto_btagerr_pe.SetBinContent(i, j, btagerr_pe)
            
            lepup_pe = abs(nominal - lepup) / nominal
            wHisto_lepup_pe.SetBinContent(i, j, lepup_pe)

            lepdown_pe = abs(nominal - lepdown) / nominal
            wHisto_lepdown_pe.SetBinContent(i, j, lepdown_pe)

            leperr_pe = (lepup_pe + lepdown_pe) / 2.
            wHisto_leperr_pe.SetBinContent(i, j, leperr_pe)
  
            isrup_pe = abs(nominal - isrup) / nominal
            wHisto_isrup_pe.SetBinContent(i, j, isrup_pe)

            isrdown_pe = abs(nominal - isrdown) / nominal
            wHisto_isrdown_pe.SetBinContent(i, j, isrdown_pe)

            isrerr_pe = (isrup_pe + isrdown_pe) / 2.
            wHisto_isrerr_pe.SetBinContent(i, j, isrerr_pe)
  
            print btagdown_pe, btagup_pe, btagerr_pe, JESdown_pe, JESup_pe, JESerr_pe, pdferr_pe, lepdown_pe, lepup_pe, leperr_pe, isrdown_pe, isrup_pe, isrerr_pe
            
    numEntries = data.numEntries()
    if Min < 0: Min = 0
    if Max < 0: Max = numEntries
    
    rdata = data.reduce(rt.RooFit.EventRange(Min,Max))
    if write:
        writeTree2DataSet([rdata,nLooseElectrons,nLooseMuons,nLooseTaus,
                           wHisto, wHisto_JESup, wHisto_JESdown, wHisto_pdfcen, wHisto_pdferr, wHisto_btagup, wHisto_btagdown, wHisto_lepup, wHisto_lepdown,wHisto_isrup, wHisto_isrdown, wHisto_JESup_pe, wHisto_JESdown_pe, wHisto_JESerr_pe, wHisto_pdferr_pe, wHisto_btagup_pe, wHisto_btagdown_pe, wHisto_btagerr_pe, wHisto_lepup_pe, wHisto_lepdown_pe, wHisto_leperr_pe, wHisto_isrup_pe, wHisto_isrdown_pe, wHisto_isrerr_pe],
                          outputDir, outputFile, '%s.root' % filter.name, rMin, mRmin, mstop, mlsp)
        
    return rdata

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('--max',dest="max",type="int",default=-1,
                  help="The last event to take from the input Dataset")
    parser.add_option('--min',dest="min",type="int",default=0,
                  help="The first event to take from the input Dataset")  
    parser.add_option('-b','--box',dest="box",type="string",default="",
                  help="box to run")     
    parser.add_option('-e','--eff',dest="eff",default=False,action='store_true',
                  help="Calculate the MC efficiencies")
    parser.add_option('-f','--flavour',dest="flavour",default='TTj',
                  help="The flavour of MC used as input")
    parser.add_option('-r','--run',dest="run",default=-1,type=float,
                  help="The minimum run number")
    parser.add_option('-d','--dir',dest="outdir",default="./",type="string",
                  help="Output directory to store datasets")
 ##    parser.add_option('-x','--box',dest="box",default=None,type="string",
##                   help="Specify only one box")
    parser.add_option('--name',dest="name",default='RMRTree',type="string",
                  help="The name of the TTree to use")
    parser.add_option('--mstop',dest="mstop",default=650,type=float,
                  help="The name of the TTree to use")
    parser.add_option('--mlsp',dest="mlsp",default=0,type=float,
                  help="The name of the TTree to use")

      
    (options,args) = parser.parse_args()
    
    if options.config is None:
        import inspect, os
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(convertTree2Dataset)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    box = options.box
    outputDir = options.outdir
    
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


    #for doing all the crap with btags and scale factors
    tagger = BTag('T2tt')
    muonScaling = MuSFUtil()
    eleScaling  = EleSFUtil()

    if box == "BJetHS" :
        convertTree2Dataset(chain, outputDir, fName, cfg,options.min,options.max,BJetBoxLS(CalcBDT(chain)),options.run, options.mstop, options.mlsp)
    elif box == "BJetLS" :
        convertTree2Dataset(chain, outputDir, fName, cfg,options.min,options.max,BJetBoxHS(CalcBDT(chain)),options.run, options.mstop, options.mlsp)
    elif box == "Mu" :
        convertTree2Dataset(chain, outputDir, fName, cfg,options.min,options.max,MuBox(None),options.run, options.mstop, options.mlsp)
    else :
        convertTree2Dataset(chain, outputDir, fName, cfg,options.min,options.max,EleBox(None),options.run, options.mstop, options.mlsp)
   


