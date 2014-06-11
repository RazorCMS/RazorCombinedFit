from optparse import OptionParser
import os, sys
from array import array
import pickle
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from SingleBoxFit.RazorBox import *
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

def writeTree2DataSet(data,outputDir, outputFile, box, rMin, mRmin, label, args, jes_pe, pdf_pe, btag_pe, isr_pe, lep_pe, nominal, pdf_cen, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down, lep_up, lep_down, mstop, mlsp):

    # Load the file with the SMS number of total events per each point
    file = open(('T3/RMRTrees/'
                 'T2tt/SMS-T2tt_mStop-Combo.0_8TeV-Pythia6Z-Summer12-START52_'
                 'V9_FSIM-v1-SUSY.pkl'), 'rb')
    # file = open(('/tmp/SMS-T2tt_mStop-Combo.0_8TeV-Pythia6Z-Summer12-START52_'
    #              'V9_FSIM-v1-SUSY.pkl'), 'rb')
    # Get the original event weight, which is 1/nevts for a given process
    point = (mstop, mlsp)
    norms = pickle.load(file)
    weight = 1./(norms[point])
    print weight

    #for d in data:

    for histo in [nominal, pdf_cen, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down, lep_up, lep_down]:
        histo.Scale(weight)

    print "signal efficiency from nominal     = %f"%nominal.Integral()
    print "signal efficiency from pdf nominal = %f"%pdf_cen.Integral()
    print "integral of pdf relative errors = %f"%pdf_pe.Integral()

    #clear underflow and overflow bins in b-tags
    for histo in [jes_pe, pdf_pe, btag_pe, isr_pe, lep_pe, nominal, pdf_cen, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down, lep_up, lep_down]:
        for i in xrange(1,histo.GetXaxis().GetNbins()+1):
            for j in xrange(1,histo.GetYaxis().GetNbins()+1):
                #clear underflow and overflow bins in b-tags
                k = 0
                histo.SetBinContent(i,j,k,0)
                k = histo.GetZaxis().GetNbins()+1
                histo.SetBinContent(i,j,k,0)

    #histoFile.Close()
    print "signal efficiency from nominal     = %f"%nominal.Integral()
    print "signal efficiency from pdf nominal = %f"%pdf_cen.Integral()

    output = rt.TFile.Open(outputDir +'/'+outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+str(mstop)+'_'+str(mlsp)+'_'+box+'.root','RECREATE')
    print "writing dataset to", output.GetName()

    data.Write()

    for histo in [jes_pe, pdf_pe, btag_pe, isr_pe, lep_pe, nominal, pdf_cen, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down, lep_up, lep_down]:
        histo.Write()

    output.Close()

def convertTree2Dataset(tree, outputDir, outputFile, config, Min, Max, filter, run, mstop, mlsp, write = True):
    """This defines the format of the RooDataSet"""

    box = filter.name
    workspace = rt.RooWorkspace(box)
    variables = config.getVariablesRange(box,"variables",workspace)
    workspace.factory('W[0,0,+INF]')

    # if filter.dumper is not None:
    #     for h in filter.dumper.sel.headers_for_MVA():
    #         workspace.factory('%s[0,-INF,+INF]' % h)

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

    events = {}

    MRbins    = getBinning(box, 'MR'   , 'Btag')
    Rsqbins   = getBinning(box, 'Rsq'  , 'Btag')
    nBtagbins = getBinning(box, 'nBtag', 'Btag')

    x = array("d",MRbins)
    y = array("d",Rsqbins)
    z = array("d",nBtagbins)
    zprime = array("d",[0.,1.,2.,3.,4.])

    # Book the histograms
    jes_pe    = rt.TH3D("wHisto_JESerr_pe"   , "wHisto_JESerr_pe"   , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_pe   = rt.TH3D("wHisto_btagerr_pe"  , "wHisto_btagerr_pe"  , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    isr_pe    = rt.TH3D("wHisto_ISRerr_pe"   , "wHisto_ISRerr_pe"   , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    lep_pe    = rt.TH3D("wHisto_LEPerr_pe"   , "wHisto_LEPerr_pe"   , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    pdf_pe    = rt.TH3D("wHisto_PDFerr_pe"   , "wHisto_PDFerr_pe"   , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)

    jes_up    = rt.TH3D("wHisto_JESerr_up"   , "wHisto_JESerr_up"   , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    jes_down  = rt.TH3D("wHisto_JESerr_down" , "wHisto_JESerr_down" , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)

    btag_up   = rt.TH3D("wHisto_btagerr_up"  , "wHisto_btagerr_up"  , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_down = rt.TH3D("wHisto_btagerr_down", "wHisto_btagerr_down", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins), zprime )

    isr_up    = rt.TH3D("wHisto_ISRerr_up"   , "wHisto_ISRerr_up"   , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    isr_down  = rt.TH3D("wHisto_ISRerr_down" , "wHisto_ISRerr_down" , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)

    lep_up    = rt.TH3D("wHisto_LEPerr_up"   , "wHisto_LEPerr_up"   , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    lep_down  = rt.TH3D("wHisto_LEPerr_down" , "wHisto_LEPerr_down" , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)

    nominal   = rt.TH3D("wHisto"             , "wHisto"             , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)

    pdf_cen   = rt.TH3D("pdf_cen"            , "pdf_cen"            , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    pdf_err   = rt.TH3D("pdf_err"            , "pdf_err"            , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)


    # Book histograms for PDFs:
    #---------------

    vwHisto_pdfCTEQ = []
    vwHisto_pdfNNPDF = []

    for icteq in range(45):
        wHisto_pdfCTEQ = rt.TH3D("wHisto_pdfCTEQ_%s" % icteq  , "wHisto_pdfCTEQ_%s" % icteq         , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
        vwHisto_pdfCTEQ.append(wHisto_pdfCTEQ)

    for innpdf in range(101):
        wHisto_pdfNNPDF = rt.TH3D("wHisto_pdfNNPDF_%s" % innpdf, "wHisto_pdfNNPDF_%s" % innpdf      , len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
        vwHisto_pdfNNPDF.append(wHisto_pdfNNPDF)

    print 'Number of entries:', tree.GetEntries()


    for entry in xrange(tree.GetEntries()):
        tree.GetEntry(entry)

        # if entry > 10000.:
        #     break

        if entry % 50000 == 0:
            print entry

        if mstop != tree.mStop or mlsp != tree.mLSP:
            continue

        #apply the box based filter class
        if not filter(tree):
            continue
        bdt = -9999.
        if filter.dumper is not None:
            bdt = filter.dumper.bdt()

        #filter out duplicate events in case there are any
        e = (tree.run,tree.lumi,tree.event)
        if e in events:
            continue
        events[e] = None

     ##    if filter.dumper is not None:
##             for h in filter.dumper.sel.headers_for_MVA():
##                 a.setRealValue(h,getattr(filter.dumper.sel,h)())
##                 data.add(a)

        a = rt.RooArgSet(args)

        a.setRealValue('MR', tree.MR, True)
        a.setRealValue('Rsq', tree.RSQ, True)
        a.setRealValue('nBtag', tree.nCSVM)
        a.setRealValue('nJet', tree.nJetNoLeptons)

        # a.Print('V')
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

        #DEBUG
        btag_nominal = 1.+findBTagProb(jets, 'data')/bt_prob_fast

        btag_SF_bc_up  = findBTagProb(jets, efftype='data', SFerrdir=+1)/bt_prob_fast
        btag_SF_bc_Eup = abs(btag_nominal - btag_SF_bc_up)
        btag_SF_bc_dw  = findBTagProb(jets, efftype='data', SFerrdir=-1)/bt_prob_fast
        btag_SF_bc_Edw = abs(btag_nominal - btag_SF_bc_dw)
     
        btag_SF_lt_up = findBTagProb(jets, efftype='data', SFerrdir=+1, doLight=True)/bt_prob_fast
        btag_SF_lt_Eup = abs(btag_nominal - btag_SF_lt_up)
        btag_SF_lt_dw = findBTagProb(jets, efftype='data', SFerrdir=-1, doLight=True)/bt_prob_fast
        btag_SF_lt_Edw = abs(btag_nominal - btag_SF_lt_dw)
     
        btag_CF_up = findBTagProb(jets, efftype='data', CFerrdir=+1)/bt_prob_fast
        btag_CF_Eup = abs(btag_nominal - btag_CF_up)
        btag_CF_dw = findBTagProb(jets, efftype='data', CFerrdir=-1)/bt_prob_fast
        btag_CF_Edw = abs(btag_nominal - btag_CF_dw)
      
        btag_Eup = rt.TMath.Sqrt(btag_SF_bc_Eup**2 + min(btag_SF_lt_Eup, btag_SF_lt_Edw)**2 + btag_CF_Edw**2)
        btag_Edw = rt.TMath.Sqrt(btag_SF_bc_Edw**2 + min(btag_SF_lt_Eup, btag_SF_lt_Edw)**2 + btag_CF_Eup**2)

        btagw_up = btag_nominal + btag_Eup
        btagw_dw = btag_nominal - btag_Edw

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

        MR  = tree.MR
        RSQ = tree.RSQ

        weight = 0.95

        nominal.Fill(MR, RSQ, btag_nominal, weight*btag_nominal*lepw_nominal*isrw_nominal)
        # print 'btag dw', MR              , RSQ              , btagw_dw    , weight*btagw_dw*lepw_nominal*isrw_nominal
        #err
        jes_up.Fill   (tree.MR_JES_UP  , tree.RSQ_JES_UP  , btag_nominal, weight*btag_nominal*lepw_nominal*isrw_nominal)
        jes_down.Fill (tree.MR_JES_DOWN, tree.RSQ_JES_DOWN, btag_nominal, weight*btag_nominal*lepw_nominal*isrw_nominal)
        btag_up.Fill  (MR              , RSQ              , btagw_up    , weight*btagw_up*lepw_nominal*isrw_nominal    )
        btag_down.Fill(MR              , RSQ              , btagw_up    , weight*btagw_dw*lepw_nominal*isrw_nominal    )
        isr_up.Fill   (MR              , RSQ              , btag_nominal, weight*isrw_up*btag_nominal*lepw_nominal     )
        isr_down.Fill (MR              , RSQ              , btag_nominal, weight*isrw_dw*btag_nominal*lepw_nominal     )
        lep_up.Fill   (MR              , RSQ              , btag_nominal, weight*lepw_up*btag_nominal*isrw_nominal     )
        lep_down.Fill (MR              , RSQ              , btag_nominal, weight*lepw_dw*btag_nominal*isrw_nominal     )

        # PDFs:
        CTEQ66_W = tree.CTEQ66_W
        NNPDF_W = tree.MRST2006NNLO_W

        for icteq in range(45):
            vwHisto_pdfCTEQ[icteq].Fill(MR, RSQ, btag_nominal, weight*btag_nominal*lepw_nominal*CTEQ66_W[icteq])
        for innpdf in range(101):
           vwHisto_pdfNNPDF[innpdf].Fill(MR, RSQ, btag_nominal, weight*btag_nominal*lepw_nominal*NNPDF_W[innpdf])

    #end of the tree loop
    # Make the overall PDF histograms:

    # evaluate CTEQ:
    # Following are the histogrrams storing +- % error on the PDF center:
    for i in range(1, len(MRbins)+1):
        for j in range(1, len(Rsqbins)+1):
            for k in range(1, len(nBtagbins)+1):
                pdfcenters = []
                pdferrors = []
                if nominal.GetBinContent(i,j,k) != 0 and nominal.Integral() != 0.:
                    w = []
                    for p in range(0,45):
                         w.append(vwHisto_pdfCTEQ[p].GetBinContent(i,j, k))
                    pdfCTEQcen, pdfCTEQerr = GetPDFCenErr(w, 'CTEQ')
                    pdfcenters.append(pdfCTEQcen)
                    pdferrors.append(pdfCTEQerr)
                    #print 'orig central:', wHisto.GetBinContent(i,j), hw[0]
                    w = []
                    for p in range(0,101):
                        w.append(vwHisto_pdfNNPDF[p].GetBinContent(i,j,k))
                    pdfNNPDFcen, pdfNNPDFerr = GetPDFCenErr(w, 'NNPDF')
                    pdfcenters.append(pdfNNPDFcen)
                    pdferrors.append(pdfNNPDFerr)
                    #print 'pdfcenters, pdferrors'
                    print pdfcenters, pdferrors
                    pdfcen, pdferr = GetPDFEnvelope(pdfcenters, pdferrors)
                    pdf_cen.SetBinContent(i,j,k,pdfcen)
                    pdf_err.SetBinContent(i,j,k,pdferr)
                    #print 'pdfcen, pdferr, err/cen', pdfcen, pdferr#, pdferr/pdfcen

    # PDFs done

    # Percent error histograms:
    ###### JES ######
    #using (UP - DOWN)/2:
    jes_pe.Add(jes_up, 0.5)
    jes_pe.Add(jes_down, -0.5)

    #divide by (UP + NOM + DOWN)/3:
    jes_denom = rt.TH3D("wHisto_JESerr_denom", "wHisto_JESerr_denom", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    jes_denom.Add(jes_up, 1.0/3.0)
    jes_denom.Add(pdf_cen, 1.0/3.0)
    jes_denom.Add(jes_down, 1.0/3.0)

    jes_pe.Divide(jes_denom)

    ###### BTAG ######
    #using (UP - DOWN)/2:
    btag_pe.Add(btag_up,0.5)
    btag_pe.Add(btag_down,-0.5)

    #divide by (UP + NOM + DOWN)/3
    btag_denom = rt.TH3D("wHisto_btagerr_denom", "wHisto_btagerr_denom", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    btag_denom.Add(btag_up,1.0/3.0)
    btag_denom.Add(pdf_cen,1.0/3.0)
    btag_denom.Add(btag_down,1.0/3.0)

    btag_pe.Divide(btag_denom)

    ###### ISR ######
    #using (UP - DOWN)/2:
    isr_pe.Add(isr_up, 0.5)
    isr_pe.Add(isr_down, -0.5)

    #divide by (UP + NOM + DOWN)/3
    isr_denom = rt.TH3D("wHisto_ISRerr_denom", "wHisto_ISRerr_denom", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
    isr_denom.Add(isr_up,1.0/3.0)
    isr_denom.Add(pdf_cen,1.0/3.0)
    isr_denom.Add(isr_down,1.0/3.0)

    isr_pe.Divide(isr_denom)

    ####### PDF #######
    pdf_up = pdf_err.Clone("wHisto_pdferr_up")
    pdf_up.SetTitle("wHisto_pdferr_up")
    pdf_up.Multiply(pdf_cen)
    pdf_up.Add(pdf_cen)

    pdf_down = pdf_pe.Clone("wHisto_pdferr_down") 
    pdf_down.SetTitle("wHisto_pdferr_down") 
    pdf_down.Multiply(pdf_cen)
    pdf_down.Scale(-1.0)
    pdf_down.Add(pdf_cen)

    pdf_pe = pdf_err.Clone("wHisto_pdferr_pe")
    pdf_pe.SetTitle("wHisto_pdferr_pe") 
    pdf_pe.Divide(pdf_cen)

    print "after PDF"

    numEntries = data.numEntries()
    if Min < 0: Min = 0
    if Max < 0: Max = numEntries

    label = ""
    writeTree2DataSet(data, outputDir, outputFile, box, rMin, mRmin, label, args, jes_pe, pdf_pe, btag_pe, isr_pe, lep_pe, nominal, pdf_cen, jes_up, jes_down, pdf_up, pdf_down, btag_up, btag_down, isr_up, isr_down, lep_up, lep_down, mstop, mlsp)


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
    eleScaling = EleSFUtil()

    if box == "BJetLS":
        convertTree2Dataset(chain, outputDir, fName, cfg, options.min, options.max, BJetBoxLS(CalcBDT(chain)), options.run, options.mstop, options.mlsp)
    elif box == "BJetHS":
        convertTree2Dataset(chain, outputDir, fName, cfg, options.min, options.max, BJetBoxHS(CalcBDT(chain)), options.run, options.mstop, options.mlsp)
    elif box == "Mu":
        convertTree2Dataset(chain, outputDir, fName, cfg, options.min, options.max, MuBox(None), options.run, options.mstop, options.mlsp)
    else:
        convertTree2Dataset(chain, outputDir, fName, cfg, options.min, options.max, EleBox(None), options.run, options.mstop, options.mlsp)

