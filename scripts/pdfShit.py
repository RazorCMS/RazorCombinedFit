import ROOT as rt
import math
from array import array

# return histogram with max and min variations value
def GetCenAndErr(hLIST,  ibinx, xarray, ibiny, yarray, relative):

    ibinx = hLIST[0].GetXaxis().GetNbins()
    minx = hLIST[0].GetXaxis().GetXmin()
    maxx = hLIST[0].GetXaxis().GetXmax()

    ibiny = hLIST[0].GetYaxis().GetNbins()
    miny = hLIST[0].GetYaxis().GetXmin()    
    maxy = hLIST[0].GetYaxis().GetXmax()

    hCEN = rt.TH2D("hCEN", "hCEN", ibinx, xarray, ibiny, yarray)
    hSIG = rt.TH2D("hSIG", "hSIG", ibinx, xarray, ibiny, yarray)
    
    for i in xrange(1,ibinx+1):
        for j in xrange(1,ibiny+1):
            MAX = hLIST[0].GetBinContent(i,j)
            MIN = hLIST[0].GetBinContent(i,j)
            if MAX != MAX: MAX = 0.
            if MIN != MIN: MIN = 0.
            for k in xrange(1,len(hLIST)):
                if hLIST[k].GetBinContent(i,j) > MAX and hLIST[k].GetBinContent(i,j) == hLIST[k].GetBinContent(i,j): MAX = hLIST[k].GetBinContent(i,j)
                if hLIST[k].GetBinContent(i,j) < MIN and hLIST[k].GetBinContent(i,j) == hLIST[k].GetBinContent(i,j): MIN = hLIST[k].GetBinContent(i,j)
            hCEN.SetBinContent(i, j, (MAX+MIN)/2.)
            if relative == True:
                if math.fabs(MAX+MIN) > 0.: hSIG.SetBinContent(i, j, (MAX-MIN)/(MAX+MIN))
                else: hSIG.SetBinContent(i, j, 0.)
            else: hSIG.SetBinContent(i, j, (MAX-MIN)/2)
    return hCEN, hSIG

def GetErrAbs(w, w2, wALL, selectedEvents_, originalEvents_):
    originalAcceptance = float(selectedEvents_)/float(originalEvents_)
    acc_central = 0.
    if w[0]>0: acc_central = w[0]/wALL[0]

    xi = acc_central-originalAcceptance
    return math.fabs(xi/originalAcceptance)

def GetErrEigen(w, w2, wALL, selectedEvents_, originalEvents_, PDFSET):
    CTEQ = False
    if PDFSET.find("CTEQ") != -1: CTEQ = True
    NNPDF = False
    if PDFSET.find("NNPDF") != -1: NNPDF = True

    nmembers = len(w)
    npairs = (nmembers-1)/2
    wplus = 0.
    wminus = 0.
    nplus = 0
    nminus = 0
    events_central = w[0]
    events2_central = w2[0]

    if events_central == 0: return 0,0
    for j in xrange(0,npairs):           
        wa = w[2*j+1]/events_central-1.
        wb = w[2*j+2]/events_central-1.
        if NNPDF:
            if wa>0.:
                wplus += wa*wa
                nplus+=1
            else:
                wminus += wa*wa
                nminus+=1       
            if wb>0.:
                wplus += wb*wb
                nplus+=1
            else:
                wminus += wb*wb
                nminus+=1
        else:
            if wa>wb:
                if wa<0.: wa = 0.
                if wb>0.: wb = 0.
                wplus += wa*wa
                wminus += wb*wb
            else: 
                if wb<0.: wb = 0.
                if wa>0.: wa = 0.
                wplus += wb*wb
                wminus += wa*wa

    if wplus>0: wplus = math.sqrt(wplus)
    if wminus>0: wminus = math.sqrt(wminus)
    if wplus != math.fabs(wplus): wplus = 0.
    if wminus != math.fabs(wminus): wminus = 0.
    if NNPDF:
        if nplus>0: wplus *= 1./math.sqrt(nplus);
        if nminus>0: wminus *= 1./math.sqrt(nminus);            
    if CTEQ:
        #cen = (wplus+wminus)/2.
        #err = math.fabs(wplus-wminus)/2.
        wplus = wplus/1.6
        wminus = wminus/1.6
  
    return wminus,wplus

def GetErrEigenEff(w, w2, wALL, PDFSET):
    # w = array of yields for events passing cuts and weighted by w_i
    # w2 = array of yields for events passing cuts and weighted by w_i*w_i
    # wALL = array of yields for events before cuts and weighted by w_i
    # selectedEvents_ = unweighted yield for events passing ths cuts
    # originalEvents_ = unweighted yield for events before the cuts
    # PDFSET = label for pdf set

    CTEQ = False
    if PDFSET.find("CTEQ") != -1: CTEQ = True
    NNPDF = False
    if PDFSET.find("NNPDF") != -1: NNPDF = True

    nmembers = len(w)
    npairs = (nmembers-1)/2
    wplus = 0.
    wminus = 0.
    nplus = 0
    nminus = 0
    acc_central = 0.
    acc2_central = 0.
    
    if w[0]>0 and wALL[0]>0:
        acc_central = w[0]/wALL[0]
        acc2_central = w2[0]/wALL[0]

    for j in xrange(0,npairs):
        wa = 0.
        wb = 0.
        if acc_central!=0:
            if wALL[2*j+1]>0: wa = (w[2*j+1]/wALL[2*j+1])/acc_central-1.
            if wALL[2*j+2]>0: wb = (w[2*j+2]/wALL[2*j+2])/acc_central-1.
        if NNPDF:
            if wa>0.:
                wplus += wa*wa
                nplus+=1
            else:
                wminus += wa*wa
                nminus+=1
            if wb>0.:
                wplus += wb*wb 
                nplus+=1
            else:
                wminus += wb*wb
                nminus+=1
        else:
            if wa>wb:
                if wa<0.: wa = 0.
                if wb>0.: wb = 0.
                wplus += wa*wa
                wminus += wb*wb
            else: 
                if wb<0.: wb = 0.
                if wa>0.: wa = 0.
                wplus += wb*wb
                wminus += wa*wa

    if wplus>0: wplus = math.sqrt(wplus)
    if wminus>0: wminus = math.sqrt(wminus)
    if wplus != math.fabs(wplus): wplus = 0.
    if wminus != math.fabs(wminus): wminus = 0.
    if NNPDF:
        if nplus>0: wplus *= 1./math.sqrt(nplus);
        if nminus>0: wminus *= 1./math.sqrt(nminus);
    if CTEQ:
        #cen = (wplus+wminus)/2.
        #err = math.fabs(wplus-wminus)/2.
        wplus = wplus/1.6
        wminus = wminus/1.6
  
    return acc_central*(1-wminus)*wALL[0],acc_central*(1+wplus)*wALL[0]


def makePDFPlotCONDARRAY(tree, histo, ibinx, xarray, ibiny, yarray, condition, relative, histoFileName, outputFile):
    # for PDFs
    hCTEQ66_EIGENP = rt.TH2D("hCTEQ66_EIGENP",   "hCTEQ66_EIGENP", ibinx, xarray, ibiny, yarray)
    hCTEQ66_EIGENM = rt.TH2D("hCTEQ66_EIGENM", "hCTEQ66_EIGENM", ibinx, xarray, ibiny, yarray)
    
    hMRST2006NNLO_EIGENP = rt.TH2D("hMRST2006NNLO_EIGENP",   "hMRST2006NNLO_EIGENP", ibinx, xarray, ibiny, yarray)
    hMRST2006NNLO_EIGENM = rt.TH2D("hMRST2006NNLO_EIGENM", "hMRST2006NNLO_EIGENM", ibinx, xarray, ibiny, yarray)
    
    # hNNPDF10100_EIGENP = rt.TH2D("hNNPDF10100_EIGENP",   "hNNPDF10100_EIGENP", ibinx, xarray, ibiny, yarray)
    # hNNPDF10100_EIGENM = rt.TH2D("hNNPDF10100_EIGENM",   "hNNPDF10100_EIGENM", ibinx, xarray, ibiny, yarray)
    
    hwCTEQ66 = []
    hwCTEQ66SQ = []
    for i in xrange(0, 45):
        #make histogram for this weight
        wCTEQ66 = rt.TH2D("wCTEQ66_%i" %i,"wCTEQ66_%i" %i, ibinx, xarray, ibiny, yarray)
        tree.Project("wCTEQ66_%i" %i, "RSQ:MR", 'CTEQ66_W[%i]*%s' % (i, condition))
        wCTEQ66SQ = rt.TH2D("wCTEQ66SQ_%i" %i,"wCTEQ66SQ_%i", ibinx, xarray, ibiny, yarray)
        tree.Project("wCTEQ66SQ_%i" %i, "RSQ:MR", 'pow(CTEQ66_W[%i],2.)*%s' % (i, condition))
        hwCTEQ66.append(wCTEQ66)
        hwCTEQ66SQ.append(wCTEQ66SQ)
        
    hwMRST2006NNLO = []
    hwMRST2006NNLOSQ = []
    for i in xrange(0,31):
        #make histogram for this weight
        wMRST2006NNLO = rt.TH2D("wMRST2006NNLO_%i" %i,"wMRST2006NNLO_%i" %i, ibinx, xarray, ibiny, yarray)
        tree.Project("wMRST2006NNLO_%i" %i, "RSQ:MR", 'MRST2006NNLO_W[%i]*%s' % (i, condition))
        wMRST2006NNLOSQ = rt.TH2D("wMRST2006NNLOSQ_%i" %i,"wMRST2006NNLOSQ_%i", ibinx, xarray, ibiny, yarray)
        tree.Project("wMRST2006NNLOSQ_%i" %i,"RSQ:MR",'pow(MRST2006NNLO_W[%i],2.)*%s' % (i, condition))
        hwMRST2006NNLO.append(wMRST2006NNLO)
        hwMRST2006NNLOSQ.append(wMRST2006NNLOSQ)

    # hwNNPDF10100 = []
    # hwNNPDF10100SQ = []
    # for i in xrange(0,101):
    #     #make histogram for this weight
    #     wNNPDF10100 = rt.TH2D("wNNPDF10100_%i" %i,"wNNPDF10100_%i" %i, ibinx, xarray, ibiny, yarray)
    #     tree.Project("wNNPDF10100_%i" %i, "RSQ:MR", 'NNPDF10100_W[%i]*%s' % (i, condition))
    #     wNNPDF10100SQ = rt.TH2D("wNNPDF10100SQ_%i" %i,"wNNPDF10100SQ_%i", ibinx, xarray, ibiny, yarray)
    #     tree.Project("wNNPDF10100SQ_%i" %i, "RSQ:MR", 'pow(NNPDF10100_W[%i],2.)*%s' % (i, condition))
    #     hwNNPDF10100.append(wNNPDF10100)
    #     hwNNPDF10100SQ.append(wNNPDF10100SQ)


    MGstringstart = outputFile.find("MG")+3
    MGstringend = outputFile.find("MCHI")-1
    MCHIstringstart = MGstringend+6
    MCHIstringend = MCHIstringstart+7
    MG = float(outputFile[MGstringstart:MGstringend])
    MCHI = float(outputFile[MCHIstringstart:MCHIstringend])

    histoFile = rt.TFile.Open(histoFileName)
    for i in xrange(1, ibinx+1):
        for j in xrange(1, ibiny+1):
            w = []
            hw = []
            hw2 = []
            for k in xrange(0,45):
                htemp = histoFile.Get("SMSWCTEQ_%i"%k)
                w.append(htemp.GetBinContent(htemp.FindBin(MG,MCHI)))
                hw.append(hwCTEQ66[k].GetBinContent(i,j))
                hw2.append(hwCTEQ66SQ[k].GetBinContent(i,j))
            if histo.GetBinContent(i,j) != 0 and  histo.Integral() != 0.:
                GetErrEigenM, GetErrEigenP = GetErrEigenEff(hw, hw2, w, "CTEQ")
                # we store the absolute values (not the relative deviation returned by the function)
                hCTEQ66_EIGENP.SetBinContent(i, j, GetErrEigenP/w[0])
                hCTEQ66_EIGENM.SetBinContent(i, j, GetErrEigenM/w[0])
    del hwCTEQ66, hwCTEQ66SQ
    
    for i in xrange(1, ibinx+1):
        for j in xrange(1, ibiny+1):
            w = []
            hw = []
            hw2 = []
            for k in xrange(0,31):
                htemp = histoFile.Get("SMSWMRST_%i"%k)
                w.append(htemp.GetBinContent(htemp.FindBin(MG,MCHI)))
                hw.append(hwMRST2006NNLO[k].GetBinContent(i,j))
                hw2.append(hwMRST2006NNLOSQ[k].GetBinContent(i,j))
            if histo.GetBinContent(i,j) != 0 and  histo.Integral() != 0.:
                GetErrEigenM, GetErrEigenP = GetErrEigenEff(hw, hw2, w, "MRST")
                hMRST2006NNLO_EIGENP.SetBinContent(i, j,  GetErrEigenP/w[0])
                hMRST2006NNLO_EIGENM.SetBinContent(i, j,  GetErrEigenM/w[0])
    del hwMRST2006NNLO, hwMRST2006NNLOSQ

    # for i in xrange(1, ibinx+1):
    #     for j in xrange(1, ibiny+1):
    #         w = []
    #         hw = []
    #         hw2 = []
    #         for k in xrange(0,101):
    #             htemp = histoFile.Get("SMSWNNPDF_%i"%k)
    #             w.append(htemp.GetBinContent(htemp.FindBin(MG,MCHI)))
    #             hw.append(hwNNPDF10100[k].GetBinContent(i,j))
    #             hw2.append(hwNNPDF10100SQ[k].GetBinContent(i,j))
    #         if histo.GetBinContent(i,j) != 0 and  histo.Integral() != 0.:    
    #             GetErrEigenM, GetErrEigenP = GetErrEigenEff(hw, hw2, w, "NNPDF")
    #             hNNPDF10100_EIGENP.SetBinContent(i, j,  GetErrEigenP/w[0])
    #             hNNPDF10100_EIGENM.SetBinContent(i, j,  GetErrEigenM/w[0])
    # del hwNNPDF10100, hwNNPDF10100SQ

    histoFile.Close()
    del histoFile
    # compute the central value and error (relative or not)
    # taking the absolute values as input
    #Cen,Error = GetCenAndErr([hMRST2006NNLO_EIGENP, hMRST2006NNLO_EIGENM, hCTEQ66_EIGENP, hCTEQ66_EIGENM, hNNPDF10100_EIGENP, hNNPDF10100_EIGENM], ibinx, xarray, ibiny, yarray,  relative)
    #del hMRST2006NNLO_EIGENP, hMRST2006NNLO_EIGENM, hCTEQ66_EIGENP, hCTEQ66_EIGENM, hNNPDF10100_EIGENP, hNNPDF10100_EIGENM
    Cen,Error = GetCenAndErr([hMRST2006NNLO_EIGENP, hMRST2006NNLO_EIGENM, hCTEQ66_EIGENP, hCTEQ66_EIGENM], ibinx, xarray, ibiny, yarray,  relative)
    del hMRST2006NNLO_EIGENP, hMRST2006NNLO_EIGENM, hCTEQ66_EIGENP, hCTEQ66_EIGENM
    return Cen,Error

def makePDFPlotCOND2D(tree, histo, condition, relative):
    ibinx = histo.GetXaxis().GetNbins()
    minx = histo.GetXaxis().GetXmin()
    maxx = histo.GetXaxis().GetXmax()

    ibiny = histo.GetYaxis().GetNbins()
    miny = histo.GetYaxis().GetXmin()
    maxy = histo.GetYaxis().GetXmax()

    myX = []
    for i in xrange (0,ibinx+1):
        myX.append(minx+ (maxx-minx)/ibinx*i)
    myXarray = array("d",myX)
    myY = []
    for i in xrange (0,ibiny+1): myY.append(miny+ (maxy-miny)/ibiny*i)
    myYarray = array("d", myY)
    Cen,Error = makePDFPlotCONDARRAY(tree, histo, ibinx, myXarray, ibiny, myYarray, condition, relative)
    del myXarray, myYarray
    return Cen,Error

def makePDFPlotCOND3D(tree, histo, condition, relative, BTAGNOM, histoFileName, outputFile):
    ibinx = histo.GetXaxis().GetNbins()
    minx = histo.GetXaxis().GetXmin()
    maxx = histo.GetXaxis().GetXmax()

    ibiny = histo.GetYaxis().GetNbins()
    miny = histo.GetYaxis().GetXmin()
    maxy = histo.GetYaxis().GetXmax()

    ibinz = histo.GetZaxis().GetNbins()
    minz = histo.GetZaxis().GetXmin()
    maxz = histo.GetZaxis().GetXmax()
    myX = []
    for i in xrange (1,ibinx+2):
        myX.append(histo.GetXaxis().GetBinLowEdge(i))
    myXarray = array("d",myX)
    myY = []
    for j in xrange (1,ibiny+2):
        myY.append(histo.GetYaxis().GetBinLowEdge(j))
    myYarray = array("d", myY)
    # call the 2D function for each bin of the z axis
    Cen = histo.Clone(histo.GetName()+"_pdferr_nom")
    Cen.SetTitle(histo.GetName()+"_pdferr_nom")
    Error = histo.Clone(histo.GetName()+"_pdferr_pe")
    Error.SetTitle(histo.GetName()+"_pdferr_pe")
    print "IN PDF CODE: minz = %i, maxz = %i"%(minz,maxz)
    for k in xrange(1,ibinz+1):
        btagbin = histo.GetZaxis().GetBinLowEdge(k)
        condition_btag = condition.replace("%s >= 1"%BTAGNOM,"%s == %i"%(BTAGNOM,btagbin))
        histo2D = rt.TH2D("histo2D_%i"%k,"histo2D_%i"%k, ibinx, myXarray, ibiny, myYarray)
        tree.Project("histo2D_%i"%k,"RSQ:MR","%s"%condition_btag)
        TMPCen,TMPError = makePDFPlotCONDARRAY(tree, histo2D, ibinx, myXarray, ibiny, myYarray, condition_btag, relative, histoFileName, outputFile)        
        for i in xrange(1,ibinx+1):
            for j in xrange(1,ibiny+1):
                Cen.SetBinContent(i,j,k,TMPCen.GetBinContent(i,j))
                Error.SetBinContent(i,j,k,TMPError.GetBinContent(i,j))
    del myXarray, myYarray
    return Cen,Error

def makePDFPlot(tree, histo, condition, relative = False, BTAGNOM = "btag_nom", histoFileName = "T1bbbb_histo.root", outputFile = "none"):
    if histo.InheritsFrom("TH3"): return makePDFPlotCOND3D(tree, histo, condition, relative, BTAGNOM, histoFileName, outputFile)
    else: return makePDFPlotCOND2D(tree, histo, condition, relative)
