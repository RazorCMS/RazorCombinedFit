import ROOT as rt
import math

# return histogram with max and min variations value
def GetCenAndErr(h1, h2, h3, h4):
    ibinx = h1.GetNbinsX()
    ibiny = h1.GetNbinsY()
    
    for i in range(1,ibinx+1):
        for j in range(1,ibiny+1):
            MAX = h1.GetBinContent(i,j)
            MIN = h1.GetBinContent(i,j)
            if MAX != MAX: MAX = 0.
            if MIN != MIN: MIN = 0.
            if h2.GetBinContent(i,j) > MAX and h2.GetBinContent(i,j) == h2.GetBinContent(i,j): MAX = h2.GetBinContent(i,j)
            if h3.GetBinContent(i,j) > MAX and h3.GetBinContent(i,j) == h3.GetBinContent(i,j): MAX = h3.GetBinContent(i,j)
            if h4.GetBinContent(i,j) > MAX and h4.GetBinContent(i,j) == h4.GetBinContent(i,j): MAX = h4.GetBinContent(i,j)
            if h2.GetBinContent(i,j) < MIN and h2.GetBinContent(i,j) == h2.GetBinContent(i,j): MIN = h2.GetBinContent(i,j)
            if h3.GetBinContent(i,j) < MIN and h3.GetBinContent(i,j) == h3.GetBinContent(i,j): MIN = h3.GetBinContent(i,j)
            if h4.GetBinContent(i,j) < MIN and h4.GetBinContent(i,j) == h4.GetBinContent(i,j): MIN = h4.GetBinContent(i,j)
            h1.SetBinContent(i, j, (MAX+MIN)/2.)
            h2.SetBinContent(i, j, (MAX-MIN)/2.)            
    return h1,h2

def GetErrAbs(w, w2, wALL, selectedEvents_, originalEvents_):
    originalAcceptance = float(selectedEvents_)/float(originalEvents_)
    acc_central = 0.
    if w[0]>0: acc_central = w[0]/wALL[0]

    xi = acc_central-originalAcceptance
    return math.fabs(xi/originalAcceptance)

def GetErrEigen(w, w2, wALL, selectedEvents_, originalEvents_, CTEQ=False):

    nmembers = len(w)
    npairs = (nmembers-1)/2
    wplus = 0.
    wminus = 0.
    nplus = 0
    nminus = 0
    events_central = w[0]
    events2_central = w2[0]

    if events_central == 0: return 0,0

    for j in range(0,npairs):
        wa = w[2*j+1]/events_central-1.
        wb = w[2*j+2]/events_central-1.
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
    if CTEQ:
        cen = (wplus+wminus)/2.
        err = math.fabs(wplus-wminus)/2.
        wplus = cen+err/1.6
        wminus = cen-err/1.6
  
    return wminus,wplus

def GetErrEigenEff(w, w2, wALL, selectedEvents_, originalEvents_, CTEQ=False):

    nmembers = len(w)
    npairs = (nmembers-1)/2
    wplus = 0.
    wminus = 0.
    nplus = 0
    nminus = 0
    originalAcceptance = float(selectedEvents_)/float(originalEvents_)
    acc_central = 0.
    acc2_central = 0.
    if w[0]>0:
        acc_central = w[0]/wALL[0]
        acc2_central = w2[0]/wALL[0]

    for j in range(0,npairs):
        wa = 0.
        if wALL[2*j+1]>0: wa = (w[2*j+1]/wALL[2*j+1])/acc_central-1.
        wb = 0.
        if w[2*j+2]>0: wb = (w[2*j+2]/wALL[2*j+2])/acc_central-1.
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
    if CTEQ:
        cen = (wplus+wminus)/2.
        err = math.fabs(wplus-wminus)/2.
        wplus = cen+err/1.6
        wminus = cen-err/1.6
  
    return wminus,wplus

def makePDFPlotCOND(tree, histo, ibinx, minx, maxx, ibiny, miny, maxy, box):
    
    # for PDFs
    hCTEQ66_EIGENP = rt.TH2D("hCTEQ66_EIGENP",   "hCTEQ66_EIGENP", ibinx, minx, maxx, ibiny, miny, maxy)
    hCTEQ66_EIGENM = rt.TH2D("hCTEQ66_EIGEN", "hCTEQ66_EIGEN", ibinx, minx, maxx, ibiny, miny, maxy)
    
    hMRST2006NNLO_EIGENP = rt.TH2D("hMRST2006NNLO_EIGENP",   "hMRST2006NNLO_EIGENP", ibinx, minx, maxx, ibiny, miny, maxy)
    hMRST2006NNLO_EIGENM = rt.TH2D("hMRST2006NNLO_EIGEN", "hMRST2006NNLO_EIGEN", ibinx, minx, maxx, ibiny, miny, maxy)
    
    hMRST2007lomod_ABS = rt.TH2D("hMRST2007lomod_ABS",   "hMRST2007lomod_ABS", ibinx, minx, maxx, ibiny, miny, maxy)
    
    hwCTEQ66 = []
    hwCTEQ66SQ = []

    for i in range(0, 45):
        #make histogram for this weight
        wCTEQ66 = rt.TH2D("wCTEQ66_%i" %i,"wCTEQ66_%i" %i, ibinx, minx, maxx, ibiny, miny, maxy)
        tree.Project("wCTEQ66_%i" %i, "RSQ:MR", 'LEP_W*W*CTEQ66_W[%i]*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (%s))' % (i, minx,maxx,miny,maxy,box))
        wCTEQ66SQ = rt.TH2D("wCTEQ66SQ_%i" %i,"wCTEQ66SQ_%i", ibinx, minx, maxx, ibiny, miny, maxy)
        tree.Project("wCTEQ66SQ_%i" %i, "RSQ:MR", 'LEP_W*W*pow(CTEQ66_W[%i],2.)*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (%s))' % (i, minx,maxx,miny,maxy,box))
        hwCTEQ66.append(wCTEQ66)
        hwCTEQ66SQ.append(wCTEQ66SQ)
        
    hwMRST2006NNLO = []
    hwMRST2006NNLOSQ = []
    for i in range(0,31):
        #make histogram for this weight
        wMRST2006NNLO = rt.TH2D("wMRST2006NNLO_%i" %i,"wMRST2006NNLO_%i" %i, ibinx, minx, maxx, ibiny, miny, maxy)
        tree.Project("wMRST2006NNLO_%i" %i, "RSQ:MR", 'LEP_W*W*MRST2006NNLO_W[%i]*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (%s))' % (i, minx,maxx,miny,maxy,box))
        wMRST2006NNLOSQ = rt.TH2D("wMRST2006NNLOSQ_%i" %i,"wMRST2006NNLOSQ_%i", ibinx, minx, maxx, ibiny, miny, maxy)
        tree.Project("wMRST2006NNLOSQ_%i" %i,"RSQ:MR",'LEP_W*W*pow(MRST2006NNLO_W[%i],2.)*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (%s))' % (i, minx,maxx,miny,maxy,box))
        hwMRST2006NNLO.append(wMRST2006NNLO)
        hwMRST2006NNLOSQ.append(wMRST2006NNLOSQ)

    hwMRST2007lomod = []
    hwMRST2007lomodSQ = []

    for i in range(0,1):
        #make histogram for this weight
        wMRST2007lomod = rt.TH2D("wMRST2007lomod_%i" %i,"wMRST2007lomod_%i" %i, ibinx, minx, maxx, ibiny, miny, maxy)
        tree.Project("wMRST2007lomod_%i" %i, "RSQ:MR", 'LEP_W*W*MRST2007lomod_W[%i]*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (%s))' % (i, minx,maxx,miny,maxy,box))
        wMRST2007lomodSQ = rt.TH2D("wMRST2007lomodSQ_%i" %i,"wMRST2007lomodSQ_%i", ibinx, minx, maxx, ibiny, miny, maxy)
        tree.Project("wMRST2007lomodSQ_%i" %i, "RSQ:MR", 'LEP_W*W*pow(MRST2007lomod_W[%i],2.)*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (%s))' % (i, minx,maxx,miny,maxy,box))
        hwMRST2007lomod.append(wMRST2007lomod)
        hwMRST2007lomodSQ.append(wMRST2007lomodSQ)

    for i in range(1, ibinx+1):
        for j in range(1, ibiny+1):
            w = []
            hw = []
            hw2 = []
            for k in range(0,45):
                w.append(hwCTEQ66[k].Integral())
                hw.append(hwCTEQ66[k].GetBinContent(i,j))
                hw2.append(hwCTEQ66SQ[k].GetBinContent(i,j))
            if histo.GetBinContent(i,j) != 0 and  histo.Integral() != 0.:
                GetErrEigenM, GetErrEigenP = GetErrEigen(hw, hw2, w, histo.GetBinContent(i,j), histo.Integral(), True)
                hCTEQ66_EIGENP.SetBinContent(i, j, GetErrEigenP)
                hCTEQ66_EIGENM.SetBinContent(i, j, GetErrEigenM)
    
    for i in range(1, ibinx+1):
        for j in range(1, ibiny+1):
            hw = []
            hw2 = []
            for k in range(0,31):
                w.append(hwMRST2006NNLO[k].Integral())
                hw.append(hwMRST2006NNLO[k].GetBinContent(i,j))
                hw2.append(hwMRST2006NNLOSQ[k].GetBinContent(i,j))
            if histo.GetBinContent(i,j) != 0 and  histo.Integral() != 0.:
                GetErrEigenM, GetErrEigenP = GetErrEigen(hw, hw2, w, histo.GetBinContent(i,j), histo.Integral(), False)
                hMRST2006NNLO_EIGENP.SetBinContent(i, j, GetErrEigenP)
                hMRST2006NNLO_EIGENM.SetBinContent(i, j, GetErrEigenM)      

    for i in range(1, ibinx+1):
        for j in range(1, ibiny+1):
            hw = []
            hw2 = []
            for k in range(0,1):
                w.append(hwMRST2007lomod[k].Integral())
                hw.append(hwMRST2007lomod[k].GetBinContent(i,j))
                hw2.append(hwMRST2007lomodSQ[k].GetBinContent(i,j))
            if histo.GetBinContent(i,j) != 0 and  histo.Integral() != 0.:    
                hMRST2007lomod_ABS.SetBinContent(i, j, GetErrAbs(hw, hw2, w, histo.GetBinContent(i,j), histo.Integral()))

    return GetCenAndErr(hMRST2006NNLO_EIGENP, hMRST2006NNLO_EIGENM, hCTEQ66_EIGENP, hCTEQ66_EIGENM)

def makePDFPlot(tree, histo, ibinx, minx, maxx, ibiny, miny, maxy, box):
    makePDFPlotCOND(tree, histo, ibinx, minx, maxx, ibiny, miny, maxy, "BOX_NUM == %i" %box)
