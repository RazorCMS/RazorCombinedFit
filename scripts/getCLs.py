import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os
from array import *

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
    
    while float(hypoDataSetCut.sumEntries("lnQ>%f && lnQ<%f"%(XmaxTest,Xmax)))/totalEntries < 0.01:
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
    
    totalEntries = clTree.Draw('>>elist','mg==%f && mchi==%f'%(mg,mchi),'entrylist')
    if totalEntries==long(0):
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
        if testCLVal==0:
            testCLVal = 1e-4
        CLVals.append(testCLVal)
        clList.append(testCLVal)
        
    if not xsecVals:
        print "INFO: no xsecVals! moving on to next point!"
        return 1e-4
    

    xsecList, clList = (list(q) for q in zip(*sorted(zip(xsecList, clList))))

    CLVals = array('d',clList)
    xsecVals = array('d',xsecList)
    
    slope = [(CLVals[j]-CLVals[j-1])/(xsecVals[j]-xsecVals[j-1]) for j in xrange(1,len(CLVals))]
    while any([slope[j]>0 for j in xrange(0, len(slope))]):
        i = 1  
        while i< len(CLVals):
            if slope[i-1] > 0:
                CLVals.pop(i)
                xsecVals.pop(i)
            i+=1
        slope = [(CLVals[j]-CLVals[j-1])/(xsecVals[j]-xsecVals[j-1]) for j in xrange(1,len(CLVals))]
        

    xsecVals.reverse()
    CLVals.reverse()
    xsecVals.append(0)
    CLVals.append(1.0)
    xsecVals.reverse()
    CLVals.reverse()

        
    print "INFO: number of xsec vals", len(xsecVals)
    print "      xsecVals =", xsecVals
    print "      CLVals =", CLVals
    

    # now making array of erfc inv vals
    erfcInvVals = array('d',[erfcInv(min(CLs,1.0)) for CLs in CLVals])
        
    erfcTGraph = rt.TGraph(len(xsecVals),erfcInvVals,xsecVals)

    #this is to be able to see the usual CLs vs. sigma plot
    xsecTGraph = rt.TGraph(len(xsecVals),xsecVals,CLVals)
    
    xsecULPolyLine = erfcTGraph.Eval(erfcInv(0.05),0)

    xsecUL = xsecULPolyLine
    
    # making the lines that show the extrapolation
    lines = []
    lines.append(rt.TLine(erfcInv(0.05), 0, erfcInv(0.05), xsecUL))
    lines.append(rt.TLine(erfcTGraph.GetXaxis().GetXmin(), xsecUL, erfcInv(0.05), xsecUL))
    #lines.append(rt.TLine(0, 0.05, xsecUL, 0.05))
    #lines.append(rt.TLine(xsecUL, 0, xsecUL, 0.05))
    [line.SetLineColor(rt.kBlue) for line in lines]
    [line.SetLineWidth(2) for line in lines]
    
    # plotting things so you can see if anything went wrong 
    d = rt.TCanvas("d","d",500,400)
    #xsecTGraph.SetLineWidth(2)
    #xsecTGraph.Draw("al*")
    
    erfcTGraph.SetLineWidth(2)
    erfcTGraph.Draw("al*")
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
    l.DrawLatex(0.25,0.8,"#sigma^{95%%CL} = %.4f pb"%(xsecUL))
    erfcTGraph.GetXaxis().SetTitle("Erfc(CL_{s})")
    erfcTGraph.GetYaxis().SetTitle("#sigma [pb]")
    
    d.Print("%s/xsecUL%s_%s_%s_%s.pdf"%(directory,CL,model,modelPoint,box))
    del d
    
    rootFile.Close()

    return xsecUL
    
def getCLs(mg, mchi, xsec, boxes, model, directory, boxDictB, boxDictSpB):
    print "INFO: now running mg = %i, mchi = %i, xsec = %f for boxes %s" % (mg, mchi, xsec, " & ".join(boxes))
    Xmin = 0
    LzCut = ""
    for box in boxes:
        myCut = "H0covQual_%s>=2&&H1covQual_%s>=2&&LzSR_%s>=0."%(box,box,box)
        LzCut+="H0covQual_%s>=2&&H1covQual_%s>=2&&LzSR_%s>=0.&&"%(box,box,box)
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





def getXsecRange(model,neutralinoMass,gluinoMass):
    if model=="T1bbbb":
        mDelta = (pow(gluinoMass,2) - pow(neutralinoMass,2))/gluinoMass
        print "mDelta = ", mDelta
        if mDelta < 150:
            xsecRange = [0.005, 0.01, 0.05, 0.1, 0.5, 1., 5., 10., 50.]
        if mDelta < 400:
            xsecRange = [0.005, 0.01, 0.05, 0.1, 0.5, 1.]
        elif mDelta < 800:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
        else:
            xsecRange = [0.0005, 0.001, 0.005, 0.01, 0.05]
    elif model=="T2tt":
        topMass = 175.
        mDelta = 2.*sqrt(pow( (pow(gluinoMass,2) - pow(neutralinoMass,2) + pow(topMass,2) )/(2.*gluinoMass) , 2) - pow(topMass,2))
        print "mDelta = ", mDelta
        if mDelta < 300:
            xsecRange = [0.1, 0.5, 1., 5., 10., 50., 100.]
        elif mDelta < 400:
            xsecRange = [0.05, 0.1, 0.5, 1., 5., 10., 50.]
        elif mDelta < 500:
            xsecRange = [0.005,0.01, 0.05, 0.1, 0.5, 1., 5.]
        else:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
    elif model=="T1tttt":
        topMass = 175.
        mDelta = 2.*sqrt(pow( (pow(gluinoMass,2) - pow(neutralinoMass,2) + pow(2.*topMass,2) )/(2.*gluinoMass) , 2) - pow(2.*topMass,2))
        print "mDelta = ", mDelta
        if mDelta < 700:
            xsecRange = [0.05, 0.1, 0.5, 1., 5., 10.]
        elif mDelta < 800:
            xsecRange = [0.01, 0.05, 0.1, 0.5, 1.0]
        else:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1]
    elif model=="T6bbHH":
        higgsMass = 125.
        mDelta = 2*sqrt(pow( (pow(gluinoMass,2) - pow(neutralinoMass,2) + pow(2.*higgsMass,2) )/(2.*gluinoMass) , 2) - pow(2.*higgsMass,2))
        print "mDelta = ", mDelta
        if mDelta < 250:
            xsecRange = [0.1, 0.5, 1., 5., 10., 50., 100.]
        elif mDelta < 400:
            xsecRange = [0.05, 0.1, 0.5, 1., 5., 10., 50.]
        elif mDelta < 500:
            xsecRange = [0.005,0.01, 0.05, 0.1, 0.5, 1., 5.]
        else:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
    elif model=="T2bb":
            # Probably don't need the last entry of each xsec scan!!!
        mDelta = (pow(gluinoMass,2) - pow(neutralinoMass,2))/gluinoMass
        print "mDelta = ", mDelta
        if mDelta < 150:
            xsecRange = [0.05, 0.1, 0.5, 1., 5., 10., 50., 100., 500., 1000., 5000.]
        elif mDelta < 200:
            xsecRange = [0.05,0.1, 0.5, 1., 5., 10., 50., 100.]
        elif mDelta < 400:
            xsecRange = [0.01,0.05, 0.1, 0.5, 1., 5., 10., 50.]
        elif mDelta < 500:
            xsecRange = [0.001,0.005,0.01, 0.05, 0.1, 0.5, 1., 5.]
        else:
            xsecRange = [0.0005,0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
        
    return xsecRange


if __name__ == '__main__':

    boxInput = sys.argv[1]
    model = sys.argv[2]
    directory = sys.argv[3]

    #rt.RooMsgService.instance().Print()
    rt.RooMsgService.instance().getStream(1).removeTopic(rt.RooFit.Eval)
    rt.RooMsgService.instance().getStream(1).removeTopic(rt.RooFit.Integration)
    #rt.RooMsgService.instance().Print()

    
    if model=="T1bbbb":
        gchipairs = [(400, 50), (400, 200), (400, 300),
                     (450, 50), (450, 200), (450, 300), (450, 400),
                     (500, 50), (500, 200), (500, 300), (500, 400), (500, 450), 
                     (550, 50), (550, 200), (550, 300), (550, 400), (550, 450), (550, 500),
                     (600, 50), (600, 200), (600, 300), (600, 400), (600, 450), (600, 500), (600, 550),
                     (650, 50), (650, 200), (650, 300), (650, 400), (650, 450), (650, 500), (650, 550), (650, 600),
                     (700, 50), (700, 200), (700, 300), (700, 400), (700, 450), (700, 500), (700, 550), (700, 600), (700, 650),
                     (750, 200), (750, 300), (750, 400), (750, 450), (750, 500), (750, 550), (750, 600), (750, 650), (750, 700),
                     (775, 50), (775, 200), (775, 300), (775, 400), (775, 450), (775, 500), (775, 525), (775, 550), (775, 600), (775, 625), (775, 650), (775, 700), (775, 750),
                     (800, 550), (800, 600), (800, 650), (800, 700),
                     (825, 50), (825, 200), (825, 300), (825, 400), (825, 450), (825, 500), (825, 525), (825, 550), (825, 600), (825, 625), (825, 650), (825, 700), (825, 750), (825, 800),
                     (850, 550), (850, 600), (850, 650), (850, 700), 
                     (875, 50), (875, 200), (875, 300), (875, 400), (875, 450), (875, 500), (875, 525), (875, 550), (875, 600), (875, 625), (875, 650), (875, 700), (875, 750), (875, 800), (875, 850),
                     (900, 550), (900, 600), (900, 650),
                     (925, 50), (925, 200), (925, 300), (925, 400), (925, 450), (925, 500), (925, 525), (925, 550), (925, 600), (925, 625), (925, 650), (925, 700), (925, 750), (925, 800), (925, 850), (925, 875), (925, 900),
                     (950, 525), (950, 550), (950, 600), (950, 625), (950, 650), (950, 700), (950, 750), (950, 800), (950, 850), (950, 900), (950, 925),
                     (1000, 525), (1000, 550), (1000, 600), (1000, 625), (1000, 650), (1000, 700), (1000, 750), (1000, 800), (1000, 850),  (1000, 900), (1000, 950), (1000, 975),
                     (1025, 50), (1025, 200), (1025, 300), (1025, 400), (1025, 450), (1025, 500), (1025, 525), (1025, 550), (1025, 600), (1025, 625), (1025, 650), (1025, 700), (1025, 750), (1025, 800), (1025, 850), (1025, 900), (1025, 950), (1025, 1000),
                     (1050, 550), (1050, 600), (1050, 650), (1050, 700), (1050, 750), (1050, 800), (1050, 825), (1050, 850), (1050, 900), (1050, 950), (1050, 1000), (1050, 1025),
                     (1075, 50), (1075, 200), (1075, 300), (1075, 400), (1075, 450), (1075, 500), (1075, 525), (1075, 550), (1075, 600), (1075, 625), (1075, 650), (1075, 700), (1075, 750), (1075, 800), (1075, 850), (1075, 900), (1075, 950),  (1075, 1000),  (1075, 1050),
                     (1100, 550), (1100, 600), (1100, 650), (1100, 700), (1100, 750), (1100, 800), (1100, 850), (1100, 900), (1100, 950), (1100, 1000), (1100, 1050), (1100, 1075),
                     (1125, 50), (1125, 200), (1125, 300), (1125, 400), (1125, 450), (1125, 500), (1125, 525), (1125, 550), (1125, 600), (1125, 625), (1125, 650), (1125, 700), (1125, 750), (1125, 800), (1125, 850), (1125, 900), (1125, 950), (1125, 1000), (1125, 1050), (1125, 1100),
                     (1150, 550), (1150, 600), (1150, 650), (1150, 700), (1150, 750), (1150, 800), (1150, 850),
                     (1225, 50), (1225, 200), (1225, 300), (1225, 400), (1225, 450), (1225, 500), (1225, 525), (1225, 550), (1225, 600), (1225, 625), (1225, 650), (1225, 700), (1225, 750), (1225, 800), (1225, 850), (1225, 900), (1225, 950), (1225, 1000), (1225, 1050), (1225, 1100), (1225, 1150), (1225, 1200), 
                     (1275, 900), (1275, 950), (1275, 1000), (1275, 1050), (1275, 1100), (1275, 1150), (1275, 1200), (1275, 1250),
                     (1325, 50), (1325, 200), (1325, 300), (1325, 400), (1325, 450), (1325, 500), (1325, 525), (1325, 550), (1325, 600), (1325, 625), (1325, 650), (1325, 700), (1325, 750), (1325, 800), (1325, 850), (1325, 900), (1325, 950), (1325, 1000), (1325, 1050), (1325, 1100), (1325, 1150), (1325, 1200), (1325, 1250), (1325, 1300),
                     (1375, 50), (1375, 200), (1375, 300), (1375, 400), (1375, 450), (1375, 500), (1375, 525), (1375, 550), (1375, 600), (1375, 625), (1375, 650), (1375, 700), (1375, 750), (1375, 800), (1375, 850), (1375, 900), (1375, 950), (1375, 1000), (1375, 1050), (1375, 1100), (1375, 1150), (1375, 1200), (1375, 1250), (1375, 1300), (1375, 1350)]

                     
    if model=="T2tt":
        gchipairs = [(150, 50),
                     (200, 50),
                     (250, 50), (250, 150),
                     (300, 50), (300, 150),
                     (350, 50), (350, 150), (350, 250),
                     (400, 50), (400, 150), (400, 250),
                     (450, 50), (450, 150), (450, 250), (450, 350),
                     (500, 50), (500, 150), (500, 250), (500, 350),
                     (550, 50), (550, 150), (550, 250), (550, 350), (550, 450),
                     (600, 50), (600, 150), (600, 250), (600, 350), (600, 450),
                     (650, 50), (650, 150), (650, 250), (650, 350), (650, 450), (650, 550),
                     (700, 50), (700, 150), (700, 250), (700, 350), (700, 450), (700, 550),
                     (750, 50), (750, 150), (750, 250), (750, 350), (750, 450), (750, 550), (750, 650),
                     (800, 50), (800, 150), (800, 250), (800, 350), (800, 450), (800, 550), (800, 650)]
        
    if model=="T1tttt":
        gchipairs = [(400, 1), (400, 25), (400, 125),
                     (450, 1), (450, 25), (450, 125), (450, 225),
                     (500, 1), (500, 25), (500, 125), (500, 225),
                     (550, 1), (550, 25), (550, 125), (550, 225), (550, 325),
                     (600, 1), (600, 25), (600, 125), (600, 225), (600, 325),
                     (650, 1), (650, 25), (650, 125), (650, 225), (650, 325), (650, 425),
                     (700, 1), (700, 25), (700, 125), (700, 225), (700, 325), (700, 425),
                     (750, 1), (750, 25), (750, 125), (750, 225), (750, 325), (750, 425), (750, 525),
                     (800, 1), (800, 525),
                     (850, 1), (850, 525), (850, 625),
                     (900, 1), (950, 1),
                     (1000, 1), (1000, 525), (1000, 625), (1000, 725),
                     (1050, 1), (1050, 525), (1050, 625), (1050, 725), (1050, 825),
                     (1100, 1), (1100, 125), (1100, 225), (1100, 325), (1100, 425), (1100, 525), (1100, 625), (1100, 725), (1100, 825),
                     (1150, 1), (1150, 125), (1150, 225), (1150, 325), (1150, 425), (1150, 525), (1150, 625), (1150, 725), (1150, 825), (1150, 925),
                     (1200, 1), (1200, 125), (1200, 225), (1200, 325), (1200, 425), (1200, 525), (1200, 625), (1200, 725), (1200, 825), (1200, 925),
                     (1250, 1), (1250, 125), (1250, 225), (1250, 325), (1250, 425), (1250, 525), (1250, 625), (1250, 725), (1250, 825), (1250, 925), (1250, 1025),
                     (1300, 1), (1300, 125), (1300, 225), (1300, 325), (1300, 425), (1300, 525), (1300, 625), (1300, 725), (1300, 825), (1300, 925), (1300, 1025),
                     (1350, 1), (1350, 125), (1350, 225), (1350, 325), (1350, 425), (1350, 525), (1350, 625), (1350, 725), (1350, 825), (1350, 925), (1350, 1025), (1350, 1125),
                     (1400, 1)]
        
    if model=="T6bbHH":
        gchipairs = [(325, 25),
                     (350, 25), (350, 50),
                     (375, 25), (375, 50), (375, 75),
                     (400, 25), (400, 50), (400, 75), (400, 100),
                     (425, 25), (425, 50), (425, 75), (425, 100), (425, 125),
                     (450, 25), (450, 50), (450, 75), (450, 100), (450, 125), (450, 150),
                     (475, 25), (475, 50), (475, 75), (475, 100), (475, 125), (475, 150), (475, 175),
                     (500, 25), (500, 50), (500, 75), (500, 100), (500, 125), (500, 150), (500, 175), (500, 200),
                     (525, 25), (525, 50), (525, 75), (525, 100), (525, 125), (525, 150), (525, 175), (525, 200), (525, 225),
                     (550, 25), (550, 50), (550, 75), (550, 100), (550, 125), (550, 150), (550, 175), (550, 200), (550, 225), (550, 250),
                     (575, 25), (575, 50), (575, 75), (575, 100), (575, 125), (575, 150), (575, 175), (575, 200), (575, 225), (575, 250), (575, 275),
                     (600, 25), (600, 50), (600, 75), (600, 100), (600, 125), (600, 150), (600, 175), (600, 200), (600, 225), (600, 250), (600, 275), (600, 300),
                     (625, 25), (625, 50), (625, 75), (625, 100), (625, 125), (625, 150), (625, 175), (625, 200), (625, 225), (625, 250), (625, 275), (625, 300), (625, 325),
                     (650, 25), (650, 50), (650, 75), (650, 100), (650, 125), (650, 150), (650, 175), (650, 200), (650, 225), (650, 250), (650, 275), (650, 300), (650, 325), (650, 350),
                     (675, 25), (675, 50), (675, 75), (675, 100), (675, 150), (675, 225), (675, 250), (675, 275), (675, 300), (675, 325), (675, 350), (675, 375),
                     (700, 25), (700, 50), (700, 75), (700, 100), (700, 125), (700, 150), (700, 175), (700, 200), (700, 225), (700, 250), (700, 275), (700, 300), (700, 325), (700, 350), (700, 375), (700, 400)]
        
    
    if model=="T2bb":
        gchipairs = [(100, 1), (100, 50),
                     #(125, 1), (125, 50),
                     (150, 1), (150, 50), (150, 100),
                     #(175, 1), (175, 50), (175, 100),
                     (200, 1), (200, 50), (200, 100), (200, 150),
                     #(225, 1), (225, 50), (225, 100), (225, 150),
                     (250, 1), (250, 50), (250, 100), (250, 150), (250, 200),
                     #(275, 1), (275, 50), (275, 100), (275, 150), (275, 200),
                     (300, 1), (300, 50), (300, 100), (300, 150), (300, 200), (300, 250),
                     #(325, 1), (325, 50), (325, 100), (325, 150), (325, 200), (325, 250),
                     (350, 1), (350, 50), (350, 100), (350, 150), (350, 200), (350, 250), (350, 300),
                     #(375, 1), (375, 50), (375, 100), (375, 150), (375, 200), (375, 250), (375, 300),
                     (400, 1), (400, 50), (400, 100), (400, 150), (400, 200), (400, 250), (400, 300), (400, 350),
                     #(425, 1), (425, 50), (425, 100), (425, 150), (425, 200), (425, 250), (425, 300), (425, 350),
                     (450, 1), (450, 50), (450, 100), (450, 150), (450, 200), (450, 250), (450, 300), (450, 350), (450, 400),
                     #(475, 1), (475, 50), (475, 100), (475, 150), (475, 200), (475, 250), (475, 300), (475, 350), (475, 400),
                     (500, 1), (500, 50), (500, 100), (500, 150), (500, 200), (500, 250), (500, 300), (500, 350), (500, 400), (500, 450),
                     #(525, 1), (525, 50), (525, 100), (525, 150), (525, 200), (525, 250), (525, 300), (525, 350), (525, 400), (525, 450),
                     (550, 1), (550, 50), (550, 100), (550, 150), (550, 200), (550, 250), (550, 300), (550, 350), (550, 400), (550, 450), (550, 500),
                     #(575, 1), (575, 50), (575, 100), (575, 150), (575, 200), (575, 250), (575, 300), (575, 350), (575, 400), (575, 450), (575, 500),
                     (600, 1), (600, 50), (600, 100), (600, 150), (600, 200), (600, 250), (600, 300), (600, 350), (600, 400), (600, 450), (600, 500), (600, 550),
                     #(625, 1), (625, 50), (625, 100), (625, 150), (625, 200), (625, 250), (625, 300), (625, 350), (625, 400), (625, 450), (625, 500), (625, 550),
                     (650, 1), (650, 50), (650, 100), (650, 150), (650, 200), (650, 250), (650, 300), (650, 350), (650, 400), (650, 450), (650, 500), (650, 550), (650, 600),
                     #(675, 1), (675, 50), (675, 100), (675, 150), (675, 200), (675, 250), (675, 300), (675, 350), (675, 400), (675, 450), (675, 500), (675, 550), (675, 600),
                     (700, 1), (700, 50), (700, 100), (700, 150), (700, 200), (700, 250), (700, 300), (700, 350), (700, 400), (700, 450), (700, 500), (700, 550), (700, 600), (700, 650),
                     #(725, 1), (725, 50), (725, 100), (725, 150), (725, 200), (725, 250), (725, 300), (725, 350), (725, 400), (725, 450), (725, 500), (725, 550), (725, 600), (725, 650),
                     (750, 1), (750, 50), (750, 100), (750, 150), (750, 200), (750, 250), (750, 300), (750, 350), (750, 400), (750, 450), (750, 500), (750, 550), (750, 600), (750, 650), (750, 700),
                     (775, 1), (775, 50), (775, 100), (775, 150), (775, 200), (775, 250), (775, 300), (775, 350), (775, 400), (775, 450), (775, 500), (775, 550), (775, 600), (775, 650), (775, 700), (775, 725)]

        
    boxes = boxInput.split("_")
        
    gchipairs = reversed(gchipairs)
    
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
                if glob.glob("%s/CLs_mg_%i_mchi_%i_xsec_%s_%s.root"%(directory,mg, mchi, xsecString,'_'.join(boxes))):
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
    
