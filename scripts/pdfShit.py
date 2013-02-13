import ROOT as rt
import math
from array import array

# return histogram with max and min variations value
def GetCenAndErr(hLIST, relative):
    ibinx = hLIST[0].GetNbinsX()
    ibiny = hLIST[0].GetNbinsY()    
    for i in range(1,ibinx+1):
        for j in range(1,ibiny+1):
            MAX = hLIST[0].GetBinContent(i,j)
            MIN = hLIST[0].GetBinContent(i,j)
            if MAX != MAX: MAX = 0.
            if MIN != MIN: MIN = 0.
            for k in range(1,len(hLIST)):
                if hLIST[k].GetBinContent(i,j) > MAX and hLIST[k].GetBinContent(i,j) == hLIST[k].GetBinContent(i,j): MAX = hLIST[k].GetBinContent(i,j)
                if hLIST[k].GetBinContent(i,j) < MIN and hLIST[k].GetBinContent(i,j) == hLIST[k].GetBinContent(i,j): MIN = hLIST[k].GetBinContent(i,j)
            hLIST[0].SetBinContent(i, j, (MAX+MIN)/2.)
            if relative == True:
                if math.fabs(MAX+MIN) > 0.: hLIST[1].SetBinContent(i, j, (MAX-MIN)/(MAX+MIN))
                else: hLIST[1].SetBinContent(i, j, 0.)
            else: hLIST[1].SetBinContent(i, j, (MAX-MIN)/2.)            
    return hLIST[0], hLIST[1]

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

def makePDFPlotCONDARRAY(tree, histo, ibinx, xarray, ibiny, yarray, condition, relative):
    
    # for PDFs
    hCTEQ66_EIGENP = rt.TH2D("hCTEQ66_EIGENP",   "hCTEQ66_EIGENP", ibinx, xarray, ibiny, yarray)
    hCTEQ66_EIGENM = rt.TH2D("hCTEQ66_EIGEN", "hCTEQ66_EIGEN", ibinx, xarray, ibiny, yarray)
    
    hMRST2006NNLO_EIGENP = rt.TH2D("hMRST2006NNLO_EIGENP",   "hMRST2006NNLO_EIGENP", ibinx, xarray, ibiny, yarray)
    hMRST2006NNLO_EIGENM = rt.TH2D("hMRST2006NNLO_EIGEN", "hMRST2006NNLO_EIGEN", ibinx, xarray, ibiny, yarray)
    
    #hNNPDF10100_EIGENP = rt.TH2D("hNNPDF10100_EIGENP",   "hNNPDF10100_EIGENP", ibinx, xarray, ibiny, yarray)
    #hNNPDF10100_EIGENM = rt.TH2D("hNNPDF10100_EIGENM",   "hNNPDF10100_EIGENM", ibinx, xarray, ibiny, yarray)

    hwCTEQ66 = []
    hwCTEQ66SQ = []
    for i in range(0, 45):
        #make histogram for this weight
        wCTEQ66 = rt.TH2D("wCTEQ66_%i" %i,"wCTEQ66_%i" %i, ibinx, xarray, ibiny, yarray)
        tree.Project("wCTEQ66_%i" %i, "RSQ:MR", 'CTEQ66_W[%i]*(%s)' % (i, condition))
        wCTEQ66SQ = rt.TH2D("wCTEQ66SQ_%i" %i,"wCTEQ66SQ_%i", ibinx, xarray, ibiny, yarray)
        tree.Project("wCTEQ66SQ_%i" %i, "RSQ:MR", 'pow(CTEQ66_W[%i],2.)*(%s)' % (i, condition))
        hwCTEQ66.append(wCTEQ66)
        hwCTEQ66SQ.append(wCTEQ66SQ)
        
    hwMRST2006NNLO = []
    hwMRST2006NNLOSQ = []
    for i in range(0,31):
        #make histogram for this weight
        wMRST2006NNLO = rt.TH2D("wMRST2006NNLO_%i" %i,"wMRST2006NNLO_%i" %i, ibinx, xarray, ibiny, yarray)
        tree.Project("wMRST2006NNLO_%i" %i, "RSQ:MR", 'MRST2006NNLO_W[%i]*(%s)' % (i,condition))
        wMRST2006NNLOSQ = rt.TH2D("wMRST2006NNLOSQ_%i" %i,"wMRST2006NNLOSQ_%i", ibinx, xarray, ibiny, yarray)
        tree.Project("wMRST2006NNLOSQ_%i" %i,"RSQ:MR",'pow(MRST2006NNLO_W[%i],2.)*(%s)' % (i,condition))
        hwMRST2006NNLO.append(wMRST2006NNLO)
        hwMRST2006NNLOSQ.append(wMRST2006NNLOSQ)

    #hwNNPDF10100 = []
    #hwNNPDF10100SQ = []
    #for i in range(0,1):
    #    #make histogram for this weight
    #    wNNPDF10100 = rt.TH2D("wNNPDF10100_%i" %i,"wNNPDF10100_%i" %i, ibinx, xarray, ibiny, yarray)
    #    tree.Project("wNNPDF10100_%i" %i, "RSQ:MR", 'NNPDF10100_W[%i]*(%s)' % (i,condition))
    #    wNNPDF10100SQ = rt.TH2D("wNNPDF10100SQ_%i" %i,"wNNPDF10100SQ_%i", ibinx, xarray, ibiny, yarray)
    #    tree.Project("wNNPDF10100SQ_%i" %i, "RSQ:MR", 'pow(NNPDF10100_W[%i],2.)*(%s)' % (i, condition))
    #    hwNNPDF10100.append(wNNPDF10100)
    #    hwNNPDF10100SQ.append(wNNPDF10100SQ)

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
    del hwCTEQ66, hwCTEQ66SQ
    
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
    del hwMRST2006NNLO, hwMRST2006NNLOSQ

    #for i in range(1, ibinx+1):
    #    for j in range(1, ibiny+1):
    #        hw = []
    #        hw2 = []
    #        for k in range(0,101):
    #            w.append(hwNNPDF10100[k].Integral())
    #            hw.append(hwNNPDF10100[k].GetBinContent(i,j))
    #            hw2.append(hwNNPDF10100SQ[k].GetBinContent(i,j))
    #        if histo.GetBinContent(i,j) != 0 and  histo.Integral() != 0.:    
    #            GetErrEigenM, GetErrEigenP = GetErrEigen(hw, hw2, w, histo.GetBinContent(i,j), histo.Integral(), False)
    #            hNNPDF10100_EIGENP.SetBinContent(i, j, GetErrEigenP)
    #            hNNPDF10100_EIGENM.SetBinContent(i, j, GetErrEigenM)    
    #del hwNNPDF10100, hwNNPDF10100SQ
    
    #Cen,Error = GetCenAndErr([hMRST2006NNLO_EIGENP, hMRST2006NNLO_EIGENM, hCTEQ66_EIGENP, hCTEQ66_EIGENM, hNNPDF10100_EIGENP, hNNPDF10100_EIGENM], relative)
    #del hMRST2006NNLO_EIGENP, hMRST2006NNLO_EIGENM, hCTEQ66_EIGENP, hCTEQ66_EIGENM, hNNPDF10100_EIGENP, hNNPDF10100_EIGENM
    Cen,Error = GetCenAndErr([hMRST2006NNLO_EIGENP, hMRST2006NNLO_EIGENM, hCTEQ66_EIGENP, hCTEQ66_EIGENM], relative)
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
    for i in range (0,ibinx+1):
        myX.append(minx+ (maxx-minx)/ibinx*i)
        print minx+ (maxx-minx)/ibinx*i
    myXarray = array("d",myX)
    myY = []
    for i in range (0,ibiny+1): myY.append(miny+ (maxy-miny)/ibiny*i)
    myYarray = array("d", myY)
    Cen,Error = makePDFPlotCONDARRAY(tree, histo, ibinx, myXarray, ibiny, myYarray, condition, relative)
    del myXarray, myYarray
    return Cen,Error

def makePDFPlotCOND3D(tree, histo, condition, relative):
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
    for i in range (1,ibinx+2):
        myX.append(histo.GetXaxis().GetBinLowEdge(i))
    myXarray = array("d",myX)
    myY = []
    for j in range (1,ibiny+2):
        myY.append(histo.GetYaxis().GetBinLowEdge(j))
    myYarray = array("d", myY)

    # call the 2D function for each bin of the z axis
    Cen = histo.Clone(histo.GetName()+"_pdferr_nom")
    Cen.SetTitle(histo.GetName()+"_pdferr_nom")
    Error = histo.Clone(histo.GetName()+"_pdferr_pe")
    Error.SetTitle(histo.GetName()+"_pdferr_pe")
    for k in range(1,ibinz+1):
        condition = "("+condition+")&&(btag_nom==%i)"%k
        TMPCen,TMPError = makePDFPlotCONDARRAY(tree, histo, ibinx, myXarray, ibiny, myYarray, condition, relative)        
        for i in range(1,ibinx+1):
            for j in range(1,ibiny+1):
                Cen.SetBinContent(i,j,k,TMPCen.GetBinContent(i,j))
                Error.SetBinContent(i,j,k,TMPError.GetBinContent(i,j))
    del myXarray, myYarray
    return Cen,Error

def makePDFPlot(tree, histo, condition, relative = False):
    if histo.InheritsFrom("TH3"): return makePDFPlotCOND3D(tree, histo, condition, relative)
    else: return makePDFPlotCOND2D(tree, histo, condition, relative)
