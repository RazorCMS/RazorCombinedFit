import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os
from array import *
from getGChiPairs import *

def getLnQDataAll(boxes,boxDict):
    print 'INFO: retreiving lnQ on Data'
    lnQDataBox = []
    for box in boxes:
        #fileName = getFileName("B",mg,mchi,xsec,box,model,directory)
        fileName = boxDict[box][0]
        lnQDataBox.append(getLnQData(box, fileName))
    lnQData = sum(lnQDataBox)
    return lnQData
    
def getLnQData(box,fileName):
    dataTree = rt.TChain("myDataTree")
    addToChain = fileName+"/"+box+"/myDataTree"
    dataTree.Add(addToChain)

    dataTree.Draw('>>elist','','entrylist')
    elist = rt.gDirectory.Get('elist')
    entry = elist.Next()
    dataTree.GetEntry(entry)
    lnQData = 2*eval('dataTree.LzSR_%s'%box)
    return max(0.,lnQData)


def getLnQToys(box,fileName):
    hypoTree = rt.TChain("myTree")
    addToChain = fileName.replace("//","/")+"_*.root"+"/"+box+"/myTree"
    print "adding to chain: %s"% addToChain
    hypoTree.Add(addToChain)
    hypoTree.Draw('>>elist','','entrylist')
    elist = rt.gDirectory.Get('elist')
    
    entry = -1
    lnQToy = []
    while True:
        entry = elist.Next()
        if entry == -1: break
        hypoTree.GetEntry(entry)
        lnQToys.append(eval('hypoTree.LzSR_%s'%box))
    return lnQToys

def sortkey(fileName):
    toyStart = fileName.split("_")[-1].split("-")[0]
    return int(toyStart)
    
def getDataSet(boxes,hypo,LzCut, boxDict,Xmin):
    print "INFO: getting dataset hypo=%s"%hypo
    sumName = "2*("
    for box in boxes:
        sumName+="LzSR_%s+"%(box)
        
    sumName = sumName[:-1]+")"
    
    lnQBox = []
    hypoDataSetBox = []
    
    boxSet = {}
    for box in boxes:
        fileName = getFileName(hypo,mg,mchi,xsec,box,model,directory)
        #boxDict[box] = sorted(glob.glob(fileName.replace("//","/")+"_*.root"),key=sortkey)
        boxSet[box] = set([newFileName.replace(box,"box") for newFileName in boxDict[box]])
        
    totalSet = boxSet[box]
    for box in boxes:
        totalSet = totalSet & boxSet[box]
    for box in boxes:
        boxSet[box] = [newFileName.replace("_box_","_"+box+"_") for newFileName in totalSet]
    for box in boxes:
        boxDict[box] = sorted(list(boxSet[box]),key=sortkey)
        
    if all([not boxDict[box] for box in boxes]):
        print "INFO: the overlap between boxes is empty, moving on to next point!"
        return 0, 0, 0, 0
        
    for box in boxes:
        hypoTreeBox = rt.TChain("myTree")
        for addToChain in boxDict[box]:
            addToChain+="/"+box+"/myTree"
            #print "adding to chain: %s"% addToChain
            hypoTreeBox.Add(addToChain)
            #hypoTreeBox.Print("V")
        iToy = rt.RooRealVar("iToy","iToy",0.)
        h0covQual = rt.RooRealVar("H0covQual_%s"%box,"H0covQual_%s"%box,0.)
        h1covQual = rt.RooRealVar("H1covQual_%s"%box,"H1covQual_%s"%box,0.)
        lnQBox.append(rt.RooRealVar("LzSR_%s"%box,"LzSR_%s"%box,0.))
        hypoSetBox = rt.RooArgSet("hypoSet_%s"%box)  
        hypoSetBox.add(iToy) 
        hypoSetBox.add(h0covQual)
        hypoSetBox.add(h1covQual)
        hypoSetBox.add(lnQBox[-1])
        #hypoTreeBox.Print("V")
        hypoDataSetBox.append(rt.RooDataSet("hypoDataSet_%s"%box,"hypoDataSet_%s"%box,hypoTreeBox,hypoSetBox))
        #hypoDataSetBox[-1].Print("v")
        #rt.gROOT.ProcessLine("myTree->Delete;")
        #rt.gROOT.ProcessLine("delete myTree;")
    hypoDataSet = hypoDataSetBox[0].Clone("hypoDataSet")
    hypoDataSet.SetTitle("hypoDataSet")
    for i in xrange(1,len(hypoDataSetBox)):
        hypoDataSet.merge(hypoDataSetBox[i])
    
    hypoSet= rt.RooArgSet("hypoSet")
    hypoList = rt.RooArgList("hypoList")
    for lnQb in lnQBox:
        hypoSet.add(lnQb)
        hypoList.add(lnQb)
        
    
    lnQFunc = rt.RooFormulaVar("lnQ","LzSR_%s"%('_'.join(boxes)),sumName,hypoList)
    lnQ = hypoDataSet.addColumn(lnQFunc)
    
    hypoDataSetCut = hypoDataSet.reduce(LzCut)
    
    print "INFO: for mg=%.0f, mchi=%.0f, xsec=%.4f, hypo=%s"%(mg,mchi,xsec,hypo)
    print "      number of entries =     %i"%(hypoDataSet.numEntries())
    print "      number of cut entries = %i"%(hypoDataSetCut.numEntries())
    lowest = array('d',[0])
    highest = array('d',[0])
    hypoDataSetCut.getRange(lnQ,lowest,highest)

    XmaxTest = highest[0]
    Xmax = highest[0]
    
    totalEntries = float(hypoDataSetCut.numEntries())
    if totalEntries==0:
        print "INFO: the fit quality cut killed all entries, moving on to next point!"
        return 0, 0, 0, 0

    numAttempts = 0
    while float(hypoDataSetCut.sumEntries("lnQ>%f && lnQ<%f"%(XmaxTest,Xmax)))/totalEntries < 0.01 and numAttempts < 100:
        numAttempts += 1
        XmaxTest = Xmin + float(XmaxTest-Xmin)*0.95
    Xmax = XmaxTest
    
    return lnQ, hypoDataSet, Xmax, totalEntries

def getFunc(lnQ, hypo, hypoDataSet, LzCut, Xmin, Xmax, totalEntries):
    print "INFO: getting KDE hypo=%s"%hypo

    hypoDataSetCut = hypoDataSet.reduce(LzCut)
    lnQ.setRange(Xmin,Xmax)
    hypoHisto = rt.TH1D("histo","histo",50,Xmin,Xmax)
    hypoDataSetCut.fillHistogram(hypoHisto,rt.RooArgList(lnQ),LzCut)
    hypoHisto.SetDirectory(0)

    hypoSumSet = rt.RooArgSet("hypoSumSet")
    hypoSumSet.add(lnQ)
    hypoSumList = rt.RooArgList("hypoSumList")
    hypoSumList.add(lnQ)

    Xmean = hypoHisto.GetMean()
    Xrms = hypoHisto.GetRMS()
    print "Xmean = ", Xmean
    print "totalEntries = ", totalEntries
    print "Xrms = ", Xrms
    if Xrms < 10.0:
        rho = 0.001
    else:
        rho = 0.01

    hypoPdf = rt.RooKeysPdf("hypoPdf","hypoPdf",lnQ, hypoDataSetCut,rt.RooKeysPdf.NoMirror, rho)
    #hypoFunc = hypoPdf.asTF(hypoSumList,rt.RooArgList(),hypoSumSet)
    hypoFunc = hypoPdf.asTF(hypoSumList,rt.RooArgList())
    #frame = lnQ.frame()
    #hypoDataSetCut.plotOn(frame)
    #hypoPdf.plotOn(frame)
    #d = rt.TCanvas("d","d",500,400)
    #hypoHisto.Scale(hypoFunc.GetMaximum()/hypoHisto.GetMaximum())
    #hypoHisto.Draw("")
    #hypoFunc.Draw("same")
    #frame.Draw()
    #d.Print("hypoHisto.pdf")
    
    return hypoPdf, hypoHisto, hypoFunc

def getQuantilesFromDataSet(dataset,quantiles,LzCut,Xmax):
    totalEntries = float(dataset.sumEntries("%s"%LzCut)) 
    Xvals = array('d',[])
    for q in quantiles:
        fraction = 0.
        Xcut = 0.
        n = 0
        while abs(fraction-q) > 0.01:
            if (n>20): break
            n += 1
            Xcut += copysign(1.0,q-fraction)*Xmax/pow(2.0,n)
            cutEntries = float(dataset.sumEntries("%s&&lnQ<%f"%(LzCut,Xcut)))
            fraction = cutEntries/totalEntries
        Xvals.append(Xcut)
    return Xvals
        
    
def getOneSidedPValueFromDataSet(Xobs,boxes,LzCut,dataset):
    totalEntries = float(dataset.sumEntries("%s"%LzCut))
    cutEntries = float(dataset.sumEntries("%s&&lnQ>%f"%(LzCut,Xobs)))
    return cutEntries/totalEntries

def getOneSidedPValueFromKDE(Xobs,Xmin,Xmax,func):
    #return getLeftSidedPValueFromKDE(Xobs,Xmin,Xmax,func)
    return getRightSidedPValueFromKDE(Xobs,Xmin,Xmax,func)
            
def getRightSidedPValueFromKDE(Xobs,Xmin,Xmax,func):
    pValKDE = 1.0
    if func.Integral(Xmin,Xmax) != 0:
        pValKDE = func.Integral(Xobs,Xmax)/func.Integral(Xmin,Xmax)
    
    # DRAWING FUNCTION AND FILLS
    ic = rt.TColor(1398, 0.75, 0.92, 0.68,"")
    func.SetLineColor(ic.GetColor(0.1, .85, 0.5))
    funcFillRight = func.Clone("funcFillRight")
    funcFillRight.SetRange(Xmin,Xobs)
    funcFillRight.SetFillColor(ic.GetColor(0.1, .85, 0.5))
    funcFillRight.SetLineColor(ic.GetColor(0.1, .85, 0.5))
    funcFillRight.SetFillStyle(3002)
    funcFillLeft = func.Clone("funcFillLeft")
    funcFillLeft.SetRange(Xobs,Xmax)
    funcFillLeft.SetFillColor(ic.GetColor(0.5, .1, 0.85))
    funcFillLeft.SetLineColor(ic.GetColor(0.5, .1, 0.85))
    funcFillLeft.SetFillStyle(3002)
    
    return pValKDE, funcFillRight, funcFillLeft

def getLeftSidedPValueFromKDE(Xobs,Xmin,Xmax,func):
    funcObs = func.Eval(Xobs)
    pValKDE = 1
    if func.Integral(Xmin,Xmax) != 0:
        pValKDE = func.Integral(Xmin,Xobs)/func.Integral(Xmin,Xmax)
    
    # DRAWING FUNCTION AND FILLS
    ic = rt.TColor(1398, 0.75, 0.92, 0.68,"")
    func.SetLineColor(ic.GetColor(0.1, .85, 0.5))
    funcFillRight = func.Clone("funcFillRight")
    funcFillRight.SetRange(Xmin,Xobs)
    funcFillRight.SetFillColor(ic.GetColor(0.1, .85, 0.5))
    funcFillRight.SetLineColor(ic.GetColor(0.1, .85, 0.5))
    funcFillRight.SetFillStyle(3002)
    funcFillLeft = func.Clone("funcFillLeft")
    funcFillLeft.SetRange(Xobs,Xmax)
    funcFillLeft.SetFillColor(ic.GetColor(0.5, .1, 0.85))
    funcFillLeft.SetLineColor(ic.GetColor(0.5, .1, 0.85))
    funcFillLeft.SetFillStyle(3002)
    
    return pValKDE,funcFillRight, funcFillLeft

def calcCLs(lzValues_sb,lzValues_b,Box):
    BoxName, lzCrit = Box
    CLsb = float(len([lz for lz in lzValues_sb if lz < lzCrit]))/len(lzValues_sb)
    CLb = float(len([lz for lz in lzValues_b if lz < lzCrit]))/len(lzValues_b)
    
    CLs = -9999999999
    if CLb!= 0: CLs = CLsb / CLb
    print "Critical Value for %s box is %f" % (BoxName,lzCrit)
    print "Using %i b entries, %i s+b entries" % (len(lzValues_b), len(lzValues_sb))
    print "CLs+b = %f" %CLsb
    print "CLb = %f" %CLb
    print "CLs = %f" %CLs
    
    return CLs

def calcCLsExp(lzValues_sb,lzValues_b,Box):
    CLbValues = [0.16, 0.5, 0.84]
    lzValues_b.sort()
    lzValues_sb.sort()
    lzCritValues = [lzValues_b[int(sigma*len(lzValues_b)+0.5)] for sigma in CLbValues]
    CLsbValues = [float(len([lz for lz in lzValues_sb if lz < lzCrit]))/len(lzValues_sb) for lzCrit in lzCritValues]
    CLsExpValues = [CLsb/CLb for CLsb,CLb in zip(CLsbValues,CLbValues)]
    print "Expected for %s box"%Box[0]
    print "CLsExp+ = %f" %CLsExpValues[0]
    print "CLsExp  = %f" %CLsExpValues[1]
    print "CLsExp- = %f" %CLsExpValues[2]
    return CLsExpValues

def getFileName(hypo, mg, mchi, xsec, box, model, directory):
    hybridLimit = "Razor2013HybridLimit"
    modelPoint = "MG_%f_MCHI_%f"%(mg,mchi)
    xsecString = str(xsec).replace(".","p")
    fileName = "%s/%s_%s_%s_%s_%s_%s"%(directory,hybridLimit,model,modelPoint,box,xsecString,hypo)
    return fileName

    
def writeXsecTree(box, directory, mg, mchi, xsecULObs, xsecULExpPlus2, xsecULExpPlus, xsecULExp, xsecULExpMinus, xsecULExpMinus2):
    outputFileName = "%s/xsecUL_mg_%s_mchi_%s_%s.root" %(directory, mg, mchi, '_'.join(boxes))
    print "INFO: xsec UL values being written to %s"%outputFileName
    fileOut = rt.TFile.Open(outputFileName, "recreate")
    
    xsecTree = rt.TTree("xsecTree", "xsecTree")
    myStructCmd = "struct MyStruct{Double_t mg;Double_t mchi;"
    ixsecUL = 0
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+0)
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+1)
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+2)
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+3)
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+4)
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+5)
    ixsecUL+=6
    myStructCmd += "}"
    rt.gROOT.ProcessLine(myStructCmd)
    from ROOT import MyStruct

    s = MyStruct()
    xsecTree.Branch("mg", rt.AddressOf(s,"mg"),'mg/D')
    xsecTree.Branch("mchi", rt.AddressOf(s,"mchi"),'mchi/D')
    
    s.mg = mg
    s.mchi = mchi
    
    ixsecUL = 0
    xsecTree.Branch("xsecULObs_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+0)),'xsecUL%i/D'%(ixsecUL+0))
    xsecTree.Branch("xsecULExpPlus2_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+1)),'xsecUL%i/D'%(ixsecUL+1))
    xsecTree.Branch("xsecULExpPlus_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+2)),'xsecUL%i/D'%(ixsecUL+2))
    xsecTree.Branch("xsecULExp_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+3)),'xsecUL%i/D'%(ixsecUL+3))
    xsecTree.Branch("xsecULExpMinus_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+4)),'xsecUL%i/D'%(ixsecUL+4))
    xsecTree.Branch("xsecULExpMinus2_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+5)),'xsecUL%i/D'%(ixsecUL+5))
    exec 's.xsecUL%i = xsecULObs[ixsecUL]'%(ixsecUL+0)
    exec 's.xsecUL%i = xsecULExpPlus2[ixsecUL]'%(ixsecUL+1)
    exec 's.xsecUL%i = xsecULExpPlus[ixsecUL]'%(ixsecUL+2)
    exec 's.xsecUL%i = xsecULExp[ixsecUL]'%(ixsecUL+3)
    exec 's.xsecUL%i = xsecULExpMinus[ixsecUL]'%(ixsecUL+4)
    exec 's.xsecUL%i = xsecULExpMinus2[ixsecUL]'%(ixsecUL+5)
    ixsecUL += 4

    xsecTree.Fill()

    fileOut.cd()
    xsecTree.Write()
    
    fileOut.Close()
    
    return outputFileName

def erfcInv(prob):
    return rt.Math.normal_quantile_c(prob/2,1.0)/rt.TMath.Sqrt(2) # = TMath::ErfcInverse(prob)
    
def getXsecUL(CL, rootFileName, mg, mchi, box):
    rootFile = rt.TFile.Open(rootFileName)
    clTree = rootFile.Get("clTree")

    erfcMethod = True
    logMethod = False
    
    totalEntries = clTree.Draw('>>elist','mg==%f && mchi==%f'%(mg,mchi),'entrylist')
    if totalEntries==long(0):
        rootFile.Close()
        return 1e-4

    
    elist = rt.gDirectory.Get('elist')
    entry = -1
    xsecVals = array('d')
    CLVals = array('d')
    xsecList = []
    clList  =[]
    while True:
        entry = elist.Next()
        if entry == -1: break
        clTree.GetEntry(entry)
        testxsecVal = clTree.xsec
        testCLVal = eval('clTree.%s_%s'%(CL,box))
        xsecVals.append(testxsecVal)
        xsecList.append(testxsecVal)
        if testCLVal==0 and erfcMethod:
            testCLVal = 1e-4
        CLVals.append(testCLVal)
        clList.append(testCLVal)
        
    if not xsecVals:
        print "INFO: no xsecVals! moving on to next point!"
        rootFile.Close()
        return 1e-4
    
    xsecList, clList = (list(q) for q in zip(*sorted(zip(xsecList, clList))))

    CLVals = array('d',clList)
    xsecVals = array('d',xsecList)

    
    slope = [(CLVals[j]-CLVals[j-1])/(xsecVals[j]-xsecVals[j-1]) for j in xrange(1,len(CLVals))]
    while any([slope[j]>0 for j in xrange(0, len(slope))]):
        i = 1  
        while i < len(CLVals):
            if slope[i-1] > 0:
                CLVals.pop(i)
                xsecVals.pop(i)
            i+=1
        slope = [(CLVals[j]-CLVals[j-1])/(xsecVals[j]-xsecVals[j-1]) for j in xrange(1,len(CLVals))]
        
    
    # # xsecVals.reverse()
    # CLVals.reverse()
    # xsecVals.append(0)
    # CLVals.append(1.0)
    # xsecVals.reverse()
    # CLVals.reverse()

    print "INFO: number of xsec vals", len(xsecVals)
    print "      xsecVals =", xsecVals
    print "      CLVals =", CLVals

    # now extrapolating using tgraph of transformed CLs values
    erfcInvVals = array('d',[erfcInv(min(CLs,1.0)) for CLs in CLVals])
    logXsecVals = array('d',[rt.TMath.Log(xsec) for xsec in xsecVals])
    
    erfcInvTGraph = rt.TGraph(len(xsecVals),erfcInvVals,xsecVals)
    
    # now extrapolating using tgraph of CLs values
    if logMethod:
        clsTGraph = rt.TGraph(len(logXsecVals),CLVals,logXsecVals)
    else:
        clsTGraph = rt.TGraph(len(xsecVals),CLVals,xsecVals)
    
    if erfcMethod:
        xsecUL = erfcInvTGraph.Eval(erfcInv(0.05),0)
    elif logMethod:
        xsecUL = rt.TMath.Exp(clsTGraph.Eval(0.05,0))
    else:
        xsecUL = clsTGraph.Eval(0.05,0)
        
    #this is to be able to see the usual CLs vs. sigma plot
    xsecTGraph = rt.TGraph(len(xsecVals),xsecVals,CLVals)
    erfcTGraph = rt.TGraph(len(xsecVals),xsecVals,erfcInvVals)
    
    # making the lines that show the extrapolation
    lines = []
    if erfcMethod:
        lines.append(rt.TLine(min(xsecVals), erfcInv(0.05),  xsecUL, erfcInv(0.05)))
        lines.append(rt.TLine(xsecUL, min(erfcInvVals), xsecUL, erfcInv(0.05)))
    else:
        lines.append(rt.TLine(min(xsecVals), 0.05, xsecUL, 0.05))
        lines.append(rt.TLine(xsecUL, 0, xsecUL, 0.05))
    
    [line.SetLineColor(rt.kBlue) for line in lines]
    [line.SetLineWidth(2) for line in lines]
    
    # plotting things so you can see if anything went wrong 
    d = rt.TCanvas("d","d",500,400)
    if logMethod:
        d.SetLogx()

    if erfcMethod:
        erfcTGraph.SetLineWidth(2)
        erfcTGraph.Draw("al*")
    else:   
        xsecTGraph.SetLineWidth(2)
        xsecTGraph.Draw("al*")
        
    [line.Draw("lsame") for line in lines]

    modelPoint = "MG_%f_MCHI_%f"%(mg,mchi)

    rt.gStyle.SetOptTitle(0)
    l = rt.TLatex()
    l.SetTextAlign(12)
    l.SetTextSize(0.05)
    l.SetTextFont(42)
    l.SetNDC()
    if model=="T2tt":
        l.DrawLatex(0.2,0.955,"m_{#tilde{t}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; %s Box"%(mg,mchi,box))
    elif model in ["T1bbbb","T1tttt"]:
        l.DrawLatex(0.2,0.955,"m_{#tilde{g}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; %s Box"%(mg,mchi,box))
    elif model in ["T2bb","T6bbHH"]:
        l.DrawLatex(0.2,0.955,"m_{#tilde{b}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; %s Box"%(mg,mchi,box))
    l.DrawLatex(0.25,0.8,"#sigma^{95%%CL} = %.4f pb"%(xsecUL))
    erfcTGraph.GetYaxis().SetTitle("Erfc^{-1}(CL_{s})")
    erfcTGraph.GetXaxis().SetTitle("#sigma [pb]")
    xsecTGraph.GetYaxis().SetTitle("CL_{s}")
    xsecTGraph.GetXaxis().SetTitle("#sigma [pb]")
    
    d.Print("%s/xsecUL%s_%s_%s_%s.pdf"%(directory,CL,model,modelPoint,box))
    del d
    
    rootFile.Close()

    #if xsecUL < min(xsecVals): return 1111
    #if xsecUL > max(xsecVals): return 9999
    
    return xsecUL
    
def getCLs(mg, mchi, xsec, boxes, model, directory, boxDictB, boxDictSpB):
    print "INFO: now running mg = %i, mchi = %i, xsec = %f for boxes %s" % (mg, mchi, xsec, " & ".join(boxes))
    Xmin = 0
    LzCut = ""
    for box in boxes:
        LzCut+="H0covQual_%s>=2&&H1covQual_%s>=3&&LzSR_%s>=0.&&"%(box,box,box)
    LzCut = LzCut[:-2]
    
    lnQSpB, SpBDataSet, XmaxSpB, totalEntriesSpB = getDataSet(boxes,"SpB",LzCut,boxDictSpB, Xmin)
    if not SpBDataSet:
        return [],[]
    lnQB, BDataSet, XmaxB, totalEntriesB = getDataSet(boxes,"B",LzCut,boxDictB, Xmin)
    if not BDataSet:
        return [],[]
    
    lnQData = getLnQDataAll(boxes, boxDictB)
    
    Xmax  = max([XmaxB, XmaxSpB, 1.1*lnQData])
    
    #SpBPdf, SpBHisto, SpBFunc = getFunc(lnQSpB, "SpB", SpBDataSet, LzCut, Xmin, Xmax, totalEntriesSpB)
    #BPdf, BHisto, BFunc = getFunc(lnQB, "B", BDataSet, LzCut, Xmin, Xmax, totalEntriesB)
    
    #CLbKDE, BFuncFill, dummyFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, BFunc)
    #CLsbKDE, dummyFill, SpBFuncFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, SpBFunc)

    #CLb = CLbKDE
    #CLsb = CLsbKDE
    
    CLbDS = getOneSidedPValueFromDataSet(lnQData,boxes,LzCut,BDataSet)
    CLsbDS = getOneSidedPValueFromDataSet(lnQData,boxes,LzCut,SpBDataSet)

    CLb = CLbDS
    CLsb = CLsbDS
    
    CLs = 1.
    if CLb > 0.:
        CLs = CLsb/CLb

    if CLsb==0: "WARNING: CLsb is zero!!!!"

        
    #CLbExp = array("d",[0.023,0.159,0.500,0.841,0.977])
    CLbExp = array("d",[0.159,0.500,0.841])

    #lnQExp = array("d",[0.,0.,0.,0.,0.])
    #BFunc.GetQuantiles(5,lnQExp,CLbExp)

    lnQExp = getQuantilesFromDataSet(BDataSet,CLbExp,LzCut,XmaxB)
    
    #CLsbExp = [ getOneSidedPValueFromKDE(thislnQ,Xmin,Xmax, SpBFunc)[0] for thislnQ in lnQExp]
    #CLsExp = [max(thisCLsb/thisCLb,0.) for thisCLsb, thisCLb in zip(CLsbExp,CLbExp)]
    
    CLsbExp = [ getOneSidedPValueFromDataSet(thislnQ,boxes,LzCut, SpBDataSet) for thislnQ in lnQExp]
    CLsExp = [thisCLsb/thisCLb for thisCLsb, thisCLb in zip(CLsbExp,CLbExp)]
    for myarray in [CLsExp,lnQExp]:
        myarray.reverse()
        myarray.append(0)
        myarray.reverse()
        myarray.append(0)
    
    print "###########################"
    print "Box           = %s"%('_'.join(boxes))
    print "mg            = %.0f"%mg
    print "mchi          = %.0f"%mchi
    print "xsec          = %.4f pb-1"%xsec
    print "###########################"
    print "lnQ on Data   = %.3f"%lnQData
    print "lnQ max B     = %.3f"%XmaxB
    print "lnQ max S+B   = %.3f"%XmaxSpB
    print "CLb           = %.5f"%CLb
    print "CLs+b         = %.5f"%CLsb
    print "CLs           = %.5f"%CLs
    print "###########################"
    print "lnQExp+2sigma = %.5f"%lnQExp[0]
    print "lnQExp+1sigma = %.5f"%lnQExp[1]
    print "lnQExp        = %.5f"%lnQExp[2]
    print "lnQExp-1sigma = %.5f"%lnQExp[3]
    print "lnQExp-2sigma = %.5f"%lnQExp[4]
    print "CLsExp+2sigma = %.5f"%CLsExp[0]
    print "CLsExp+1sigma = %.5f"%CLsExp[1]
    print "CLsExp        = %.5f"%CLsExp[2]
    print "CLsExp-1sigma = %.5f"%CLsExp[3]
    print "CLsExp-2sigma = %.5f"%CLsExp[4]
    print "###########################"

    c = rt.TCanvas("c","c",500,400)
    lnQ = rt.RooRealVar("lnQ","q_{#sigma}= -2log(L_{s+b}(#sigma,#hat{#theta}_{#sigma}) / L_{s+b}(#hat{#sigma},#hat{#theta})", Xmin, Xmin,Xmax)
    frame = lnQ.frame(rt.RooFit.Name("frame"), rt.RooFit.Title("m_{#tilde{g}} = %.0f GeV, m_{#tilde{#chi}} = %.0f GeV, #sigma = %.4f pb, CL_{s} = #frac{%.4f}{%.4f} = %.4f"%(mg,mchi,xsec,CLsb,CLb,CLs)))
    BDataSet.plotOn(frame, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.MarkerSize(0.75), rt.RooFit.MarkerColor(rt.kBlue), rt.RooFit.Rescale(1./BDataSet.numEntries()))
    SpBDataSet.plotOn(frame, rt.RooFit.LineColor(rt.kRed), rt.RooFit.MarkerSize(0.75),  rt.RooFit.MarkerColor(rt.kRed), rt.RooFit.Rescale(1./SpBDataSet.numEntries()))
    # #BFunc.GetXaxis().SetTitle("#lambda = log(L_{s+b}/L_{b})")
    
    #for hypoFunc in [BFunc, SpBFunc]:
    #     if hypoFunc.GetMaximum()>maxVal:
    #         maxFunc = hypoFunc
    #         maxVal =  maxFunc.GetMaximum()
    #     hypoFunc.GetXaxis().SetTitle("q_{#sigma} = -2log(L_{s+b}(#sigma,#hat{#theta}_{#sigma}) / L_{s+b}(#hat{#sigma},#hat{#theta})")
    # BHisto.Scale(BFunc.GetMaximum()/BHisto.GetMaximum())
    # BFunc.SetLineColor(rt.kBlue)
    # BHisto.SetLineColor(rt.kBlue)
    # SpBHisto.Scale(SpBFunc.GetMaximum()/SpBHisto.GetMaximum())
    # SpBFunc.SetLineColor(rt.kRed)
    # SpBHisto.SetLineColor(rt.kRed)
    # maxFunc.Draw("")
    # BHisto.Draw("histosame")
    # BFuncFill.Draw("fsame")
    # BFunc.Draw("same")
    # SpBHisto.Draw("histosame")
    # SpBFuncFill.Draw("fsame")
    # SpBFunc.Draw("same")
    # #for profile
    c.SetLogy()
    frame.SetMaximum(1.)
    maxVal = 1.
    
    hybridLimit = "Razor2013HybridLimit"
    modelPoint = "MG_%f_MCHI_%f"%(mg,mchi)
    xsecString = str(xsec).replace(".","p")
    #l = rt.TLatex()
    #l.SetTextAlign(12)
    #l.SetTextSize(0.05)
    #l.SetTextFont(42)
    #l.SetNDC()
    #l.DrawLatex(0.10,0.955,"m_{#tilde{g}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; #sigma = %.4f pb; %s Box"%(mg,mchi,xsec,"_".join(boxes)))
    #l.DrawLatex(0.55,0.8,"CL_{s} = %.4f"%(CLs))

    frame.Draw()
    line = rt.TLine(lnQData, 0, lnQData, maxVal)
    line.SetLineWidth(2)
    line.Draw("same")

    expline = []
    for i in xrange(1,4):
        expline.append(rt.TLine(lnQExp[i],0,lnQExp[i],maxVal))
        expline[i-1].SetLineWidth(2)
        expline[i-1].Draw("same")
        expline[i-1].SetLineColor(rt.kBlue)
    
    rt.gStyle.SetErrorX(0.25)
    leg = rt.TLegend(0.65,0.7,0.9,0.9)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    SpBHist = rt.TH1D("SpBHist","SpBHist",1, 0, 1)
    SpBHist.SetMarkerStyle(20)
    SpBHist.SetMarkerSize(0.75)
    SpBHist.SetMarkerColor(rt.kRed)
    SpBHist.SetLineColor(rt.kRed)
    BHist = rt.TH1D("BHist","BHist",1, 0, 1)
    BHist.SetMarkerStyle(20)
    BHist.SetMarkerSize(0.75)
    BHist.SetMarkerColor(rt.kBlue)
    BHist.SetLineColor(rt.kBlue)
    
    leg.AddEntry(SpBHist, "S+B toys","pe")
    leg.AddEntry(BHist, "B-only toys","pe")
    #leg.AddEntry(SpBFuncFill, "CL_{s+b}","f")
    #leg.AddEntry(BFuncFill, "1-CL_{b}","f")
    # #leg.AddEntry(line, "#lambda on Data","l")
    leg.AddEntry(line, "q_{#sigma} on Data","l")
    leg.AddEntry(expline[0], "q_{#sigma} Expected#pm1#sigma","l")
            
    leg.Draw("same")
    c.Print("%s/lnQ_%s_%s_%s_%s.pdf"%(directory,model,modelPoint,xsecString,'_'.join(boxes)))
    del c

    return CLs, CLsExp

def writeCLTree(mg,mchi,xsec, box, model, directory, CLs, CLsExp):
    clTree = rt.TTree("clTree", "clTree")
    myStructCmd = "struct MyStruct{Double_t mg;Double_t mchi;Double_t xsec;"
    iCL = 0
    myStructCmd+= "Double_t CL%i;"%(iCL+0)
    myStructCmd+= "Double_t CL%i;"%(iCL+1)
    myStructCmd+= "Double_t CL%i;"%(iCL+2)
    myStructCmd+= "Double_t CL%i;"%(iCL+3)
    myStructCmd+= "Double_t CL%i;"%(iCL+4)
    myStructCmd+= "Double_t CL%i;"%(iCL+5)
    iCL+=6
    myStructCmd += "}"
    rt.gROOT.ProcessLine(myStructCmd)
    from ROOT import MyStruct

    s = MyStruct()
    clTree.Branch("mg", rt.AddressOf(s,"mg"),'mg/D')
    clTree.Branch("mchi", rt.AddressOf(s,"mchi"),'mchi/D')
    clTree.Branch("xsec", rt.AddressOf(s,"xsec"),'xsec/D')
    
    s.mg = mg
    s.mchi = mchi
    s.xsec = xsec
    
    iCL = 0
    clTree.Branch("CLs_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+0)),'CL%i/D'%(iCL+0))
    clTree.Branch("CLsExpPlus2_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+1)),'CL%i/D'%(iCL+1))
    clTree.Branch("CLsExpPlus_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+2)),'CL%i/D'%(iCL+2))
    clTree.Branch("CLsExp_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+3)),'CL%i/D'%(iCL+3))
    clTree.Branch("CLsExpMinus_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+4)),'CL%i/D'%(iCL+4))
    clTree.Branch("CLsExpMinus2_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+5)),'CL%i/D'%(iCL+5))
    exec 's.CL%i = CLs[iCL]'%(iCL+0)
    exec 's.CL%i = CLsExp[iCL][0]'%(iCL+1)
    exec 's.CL%i = CLsExp[iCL][1]'%(iCL+2)
    exec 's.CL%i = CLsExp[iCL][2]'%(iCL+3)
    exec 's.CL%i = CLsExp[iCL][3]'%(iCL+4)
    exec 's.CL%i = CLsExp[iCL][4]'%(iCL+5)
    iCL += 6

    clTree.Fill()

    xsecString = str(xsec).replace(".","p")
    outputFileName = "%s/CLs_mg_%s_mchi_%s_xsec_%s_%s.root" %(directory, mg, mchi, xsecString,'_'.join(boxes))
    print "CLs values being written to %s"%outputFileName
    fileOut = rt.TFile.Open(outputFileName, "recreate")
    clTree.Write()
    
    fileOut.Close()
    return outputFileName

if __name__ == '__main__':

    boxInput = sys.argv[1]
    model = sys.argv[2]
    directory = sys.argv[3]

    #rt.RooMsgService.instance().Print()
    rt.RooMsgService.instance().getStream(1).removeTopic(rt.RooFit.Eval)
    rt.RooMsgService.instance().getStream(1).removeTopic(rt.RooFit.Integration)
    #rt.RooMsgService.instance().Print()

    gchipairs = getGChiPairs(model)
    gchipairs = reversed(gchipairs)
        
    boxes = boxInput.split("_")
        
    
    doAll = (len(boxes)>0)
    
    rootFileName = "%s/CLs_%s.root"%(directory,'_'.join(boxes))
    print "INFO: is output CLs file %s present?"%rootFileName
    calcCLsMode = (not glob.glob(rootFileName))
    
    if calcCLsMode:
        print "INFO: output CLs file not present: entering calculate CLs mode"
        outputFileNames = []
        for mg, mchi in gchipairs:
            xsecRange = getXsecRange(model,mchi,mg)
            for xsec in xsecRange:
                print "INFO: now checking for output file"
                print "      for mg = %i, mchi = %i, xsec = %f"%(mg, mchi, xsec)
                print "      for boxes %s" % ("+".join(boxes))
                xsecString = str(xsec).replace(".","p")
                outputFilePresent = glob.glob("%s/CLs_mg_%i_mchi_%i_xsec_%s_%s.root"%(directory,mg, mchi, xsecString,'_'.join(boxes)))
                
                if outputFilePresent:
                    print "ERROR: output file is there! moving on to next point!"
                    continue

                print "INFO: now checking for files missing "
                print "      for mg = %i, mchi = %i, xsec = %f"%(mg, mchi, xsec)
                print "      for boxes %s" % ("+".join(boxes))
                anyfilesNotFound = []
                SpBAllBoxList =  glob.glob(getFileName("SpB",mg,mchi,xsec,"*",model,directory)+"*")
                BAllBoxList = glob.glob(getFileName("B",mg,mchi,xsec,"*",model,directory)+"*")
                print "INFO: %i files found for B, %i files found for SpB" % (len(BAllBoxList), len(SpBAllBoxList))
                boxDictSpB = {}
                boxDictB = {}
                for box in boxes:
                    boxDictSpB[box] = sorted([fileName for fileName in SpBAllBoxList if fileName.find("_%s_"%box)!=-1],key=sortkey)
                    boxDictB[box] = sorted([fileName for fileName in BAllBoxList if fileName.find("_%s_"%box)!=-1],key=sortkey)
                    anyfilesNotFound.append(not boxDictSpB[box])
                    anyfilesNotFound.append(not boxDictB[box])
                if any(anyfilesNotFound):
                    print "ERROR: at least one box missing all files! moving on to next point!"
                    continue
                CLs = []
                CLsExp = []
                CLsBox,CLsExpBox  = getCLs(mg, mchi, xsec, boxes, model, directory, boxDictB, boxDictSpB)
                if CLsBox==[] and CLsExpBox==[]:
                    continue
                CLs.append(CLsBox)
                CLsExp.append(CLsExpBox)
                outputFileNames.append(writeCLTree(mg, mchi, xsec,'_'.join(boxes), model,directory, CLs, CLsExp))
        haddCmd = "hadd -f %s %s"%(rootFileName,' '.join(outputFileNames))
        print haddCmd
        os.system(haddCmd)
    else:
        print "INFO: output CLs file present: entering calculate Xsec Upper Limit mode"
        outputFileNames = []
        for mg, mchi in gchipairs:
            xsecULObs = []
            xsecULExpPlus2 = []
            xsecULExpPlus = []
            xsecULExp = []
            xsecULExpMinus = []
            xsecULExpMinus2 = []
            box = '_'.join(boxes)
            try:
                xsecULObsVal = getXsecUL("CLs", rootFileName, mg, mchi, box)
                xsecULExpPlusVal = getXsecUL("CLsExpPlus", rootFileName, mg, mchi, box)
                xsecULExpVal = getXsecUL("CLsExp", rootFileName, mg, mchi, box)
                xsecULExpMinusVal = getXsecUL("CLsExpMinus", rootFileName, mg, mchi, box)
                if xsecULObsVal==1e-4 and xsecULExpPlusVal==1e-4 and xsecULExpVal==1e-4 and xsecULExpMinusVal==1e-4:
                    print "INFO: no cross section upper limits; moving to next point"
                    continue
                xsecULObs.append(max(1e-4,xsecULObsVal))
                xsecULExpPlus2.append(1e-4)
                xsecULExpPlus.append(max(1e-4,xsecULExpPlusVal))
                xsecULExp.append(max(1e-4,xsecULExpVal))
                xsecULExpMinus.append(max(1e-4,xsecULExpMinusVal))
                xsecULExpMinus2.append(1e-4)
                outputFileNameVal = writeXsecTree(box, directory, mg, mchi, xsecULObs, xsecULExpPlus2, xsecULExpPlus, xsecULExp, xsecULExpMinus, xsecULExpMinus2)
                outputFileNames.append(outputFileNameVal)
            except TypeError:
                print "INFO: TypeError"
                continue
        xsecFileName = "%s/xsecUL_%s.root"%(directory,'_'.join(boxes))
        haddCmd = "hadd -f %s %s"%(xsecFileName,' '.join(outputFileNames))
        print "INFO: now executing hadd on xsec trees: ", haddCmd
        os.system(haddCmd)
    
