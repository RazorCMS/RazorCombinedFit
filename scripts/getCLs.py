import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os
from array import *

def getLnQDataAll(boxes):
    lnQDataBox = []
    for box in boxes:
        getLnQData
        fileName = getFileName("B",mg,mchi,xsec,box,model,directory)
        lnQDataBox.append(getLnQData(box, fileName))
    lnQData = sum(lnQDataBox)
    return lnQData
    
def getLnQData(box,fileName):
    dataTree = rt.TChain("myDataTree")
    addToChain = fileName.replace("//","/")+"_*.root"+"/"+box+"/myDataTree"
    print "adding to chain: %s"% addToChain
    dataTree.Add(addToChain)

    dataTree.Draw('>>elist','','entrylist')
    elist = rt.gDirectory.Get('elist')
    entry = elist.Next()
    dataTree.GetEntry(entry)
    lnQData = eval('dataTree.LzSR_%s'%box)
    return lnQData


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

def getMinMax(box,BfileName,SpBfileName,LzCut):
    hypoTree = rt.TChain("myTree")
    addToChain = BfileName.replace("//","/")+"_*.root"+"/"+box+"/myTree"
    hypoTree.Add(addToChain)
    addToChain = SpBfileName.replace("//","/")+"_*.root"+"/"+box+"/myTree"
    hypoTree.Add(addToChain)
    addToChain = BfileName.replace("//","/")+"_*.root"+"/"+box+"/myDataTree"
    hypoTree.Add(addToChain)
    hypoTree.Draw("LzSR_%s"%box,LzCut)
    
    htemp = rt.gPad.GetPrimitive("htemp")
    Xmin = htemp.GetXaxis().GetXmin()
    Xmax = htemp.GetXaxis().GetXmax()
    rms = htemp.GetRMS()
    mean = htemp.GetMean()
    
    Xmin = 0
    Xmax = mean+5*rms

    # XmaxBin = htemp.GetXaxis().FindBin(Xmax)
    # XmaxTest = Xmax
    # XmaxTestBin = htemp.GetXaxis().FindBin(XmaxTest)
    # while htemp.Integral(XmaxTestBin,XmaxBin)/htemp.Integral() < 0.005:
    #     XmaxTest = Xmin + float(XmaxTest-Xmin)*0.95
    #     XmaxTestBin = htemp.GetXaxis().FindBin(XmaxTest)
    # Xmax = XmaxTest

    return Xmin, Xmax

def sortkey(fileName):
    toyStart = fileName.split("_")[-1].split("-")[0]
    return int(toyStart)
    
def getFuncKDEAll(boxes,hypo,Xmin,Xmax):
    LzCut = ""
    sumName = ""
    for box in boxes:
        LzCut+="H0covQual_%s==3&&H1covQual_%s==3&&LzSR_%s>=0.&&"%(box,box,box)
        sumName+="LzSR_%s+"%(box)
    LzCut = LzCut[:-2]
    sumName = sumName[:-1]
    
    lnQBox = []
    hypoDataSetBox = []
    boxDict = {}
    boxSet = {}
    for box in boxes:
        fileName = getFileName(hypo,mg,mchi,xsec,box,model,directory)
        boxDict[box] = sorted(glob.glob(fileName.replace("//","/")+"_*.root"),key=sortkey)
        boxSet[box] = set([newFileName.replace(box,"box") for newFileName in boxDict[box]])
        
    totalSet = boxSet[box]
    for box in boxes:
        totalSet = totalSet & boxSet[box]
    for box in boxes:
        boxSet[box] = [newFileName.replace("_box_","_"+box+"_") for newFileName in totalSet]
    for box in boxes:
        boxDict[box] = sorted(list(boxSet[box]),key=sortkey)
        
    
    for box in boxes:
        hypoTreeBox = rt.TChain("myTree")
        for addToChain in boxDict[box]:
            addToChain+="/"+box+"/myTree"
            #print "adding to chain: %s"% addToChain
            hypoTreeBox.Add(addToChain)
        iToy = rt.RooRealVar("iToy","iToy",0.)
        h0covQual = rt.RooRealVar("H0covQual_%s"%box,"H0covQual_%s"%box,0.)
        h1covQual = rt.RooRealVar("H1covQual_%s"%box,"H1covQual_%s"%box,0.)
        lnQBox.append(rt.RooRealVar("LzSR_%s"%box,"LzSR_%s"%box,0.))
        hypoSetBox = rt.RooArgSet("hypoSet_%s"%box)  
        hypoSetBox.add(iToy) 
        hypoSetBox.add(h0covQual)
        hypoSetBox.add(h1covQual)
        hypoSetBox.add(lnQBox[-1])
        hypoDataSetBox.append(rt.RooDataSet("hypoDataSet_%s"%box,"hypoDataSet_%s"%box,hypoTreeBox,hypoSetBox))
        #rt.gROOT.ProcessLine("myTree->Delete;")
        #rt.gROOT.ProcessLine("delete myTree;")
        #hypoDataSetBox[-1].Print("v")
    hypoDataSet = hypoDataSetBox[0].Clone("hypoDataSet")
    hypoDataSet.SetTitle("hypoDataSet")
    for i in xrange(1,len(hypoDataSetBox)):
        hypoDataSet.merge(hypoDataSetBox[i])

    
    
    hypoSet= rt.RooArgSet("hypoSet")
    hypoList = rt.RooArgList("hypoList")
    for lnQb in lnQBox:
        hypoSet.add(lnQb)
        hypoList.add(lnQb)
        
    
    lnQFunc = rt.RooFormulaVar("LzSR_%s"%('_'.join(boxes)),"LzSR_%s"%('_'.join(boxes)),sumName,hypoList)
    lnQ = hypoDataSet.addColumn(lnQFunc)

    lnQ.setRange(Xmin,Xmax)
    
    
    rho = 1.0
    hypoDataSetCut = hypoDataSet.reduce(LzCut)
    
    hypoHisto = rt.TH1D("histo","histo",50,Xmin,Xmax)
    hypoDataSetCut.fillHistogram(hypoHisto,rt.RooArgList(lnQ),LzCut)
    hypoHisto.SetDirectory(0)
    hypoHisto.Scale(1./hypoHisto.GetMaximum())

    
    hypoSumSet = rt.RooArgSet("hypoSumSet")
    hypoSumSet.add(lnQ)
    hypoSumList = rt.RooArgList("hypoSumList")
    hypoSumList.add(lnQ)
    
    hypoPdf = rt.RooKeysPdf("hypoPdf","hypoPdf",lnQ, hypoDataSetCut,rt.RooKeysPdf.NoMirror,rho)
    hypoFunc = hypoPdf.asTF(hypoSumList,rt.RooArgList(),hypoSumSet)

    
    return lnQ, hypoPdf, hypoDataSet, hypoHisto, hypoFunc

def getFuncKDE(box,fileName,LzCut,Xmin,Xmax):
    hypoTree = rt.TChain("myTree")
    addToChain = fileName.replace("//","/")+"_*.root"+"/"+box+"/myTree"
    print "adding to chain: %s"% addToChain
    hypoTree.Add(addToChain)
    
    hypoHisto = rt.TH1D("histo","histo",50,Xmin,Xmax)
    hypoTree.Project(hypoHisto.GetName(),"LzSR_%s"%box,LzCut)

    hypoHisto.SetDirectory(0)
    hypoHisto.Scale(1./hypoHisto.Integral())
    
    lnQ = rt.RooRealVar("LzSR_%s"%box,"LzSR_%s"%box,Xmin,Xmax)
    
    hypoSet = rt.RooArgSet("hypoSet")
    hypoSet.add(lnQ)
    hypoList = rt.RooArgList("hypoList")
    hypoList.add(lnQ)

    hypoDataSet= rt.RooDataSet("hypoDataSet","hypoDataSet",hypoTree,hypoSet)
    
    rho = 1.0
    hypoPdf = rt.RooKeysPdf("hypoPdf","hypoPdf",lnQ,hypoDataSet,rt.RooKeysPdf.NoMirror,rho)
    hypoFunc = hypoPdf.asTF(hypoList,rt.RooArgList(),hypoSet)

    return lnQ, hypoPdf, hypoDataSet, hypoHisto, hypoFunc


def getOneSidedPValueFromKDE(Xobs,Xmin,Xmax,func):
    #return getLeftSidedPValueFromKDE(Xobs,Xmin,Xmax,func)
    return getRightSidedPValueFromKDE(Xobs,Xmin,Xmax,func)
            
def getRightSidedPValueFromKDE(Xobs,Xmin,Xmax,func):
    funcObs = func.Eval(Xobs)
    pValKDE = 1
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
    print fileName
    return fileName

    
def writeXsecTree(box, directory, mg, mchi, xsecULObs, xsecULExpPlus2, xsecULExpPlus, xsecULExp, xsecULExpMinus, xsecULExpMinus2):
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

    outputFileName = "%s/xsecUL_mg_%s_mchi_%s_%s.root" %(directory, mg, mchi, '_'.join(boxes))
    print "xsec UL values being written to %s"%outputFileName
    fileOut = rt.TFile.Open(outputFileName, "recreate")
    xsecTree.Write()
    
    fileOut.Close()
    return outputFileName

def erfcInv(prob):
    return rt.Math.normal_quantile_c(prob/2,1.0)/rt.TMath.Sqrt(2) # = TMath::ErfcInverse(prob)
    
def getXsecUL(CL, rootFileName, mg, mchi, box):
    rootFile = rt.TFile.Open(rootFileName)
    clTree = rootFile.Get("clTree")
    
    clTree.Draw('>>elist','mg==%f && mchi==%f'%(mg,mchi),'entrylist')

    
    elist = rt.gDirectory.Get('elist')
    entry = -1
    xsecVals = array('d')
    CLVals = array('d')
    while True:
        entry = elist.Next()
        if entry == -1: break
        clTree.GetEntry(entry)
        xsecVals.append(clTree.xsec)
        exec 'CLVals.append(clTree.%s_%s)'%(CL,box)
        
    
    # removing points that are out of order
    i = 0
    while i<len(CLVals):
        if CLVals[i]==0:
            CLVals.pop(i)
            xsecVals.pop(i)
        i+=1
     
    #print "number of xsec vals", len(xsecVals)
    #print xsecVals
    #print CLVals
    
    i = 0
    j = 1
    poppedOne = True
    while len(CLVals) > 1 and poppedOne:
        poppedOne = False
        if CLVals[1]>=CLVals[0]:
            CLVals.pop(0)
            xsecVals.pop(0)
            poppedOne = True
        j+=1
    
    i = 0
    while  i < len(CLVals):
        j = i+1
        while  j < len(CLVals):
            if CLVals[j]>=CLVals[i]:
                CLVals.pop(j)
                xsecVals.pop(j)
            j+=1
        i+=1

        
    #print "number of xsec vals", len(xsecVals)
    #print xsecVals
    #print CLVals

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
    l.DrawLatex(0.2,0.955,"m_{#tilde{g}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; %s Box"%(mg,mchi,box))
    l.DrawLatex(0.25,0.8,"#sigma^{95%%CL} = %.4f pb"%(xsecUL))
    erfcTGraph.GetXaxis().SetTitle("Erfc(CL_{s})")
    erfcTGraph.GetYaxis().SetTitle("#sigma [pb]")
    
    d.Print("%s/xsecUL%s_%s_%s_%s.pdf"%(directory,CL,model,modelPoint,box))
    del d
    
    rootFile.Close()

    return xsecUL
    
def getCLsAll(mg, mchi, xsec, boxes, model, directory):
    Xmin = 0
    Xmax = 0
    for box in boxes:
        LzCut = "H0covQual_%s==3&&H1covQual_%s==3&&LzSR_%s>=0."%(box,box,box)
        SpBFileName = getFileName("SpB",mg,mchi,xsec,box,model,directory)
        BFileName = getFileName("B",mg,mchi,xsec,box,model,directory)
        XminTEST, XmaxTEST = getMinMax(box,BFileName,SpBFileName,LzCut)
        Xmax+= XmaxTEST
        
    
    print SpBFileName
    print BFileName
    lnQSpB, SpBPdf, SpBDataSet, SpBHisto, SpBFunc = getFuncKDEAll(boxes,"SpB",Xmin,Xmax)
    lnQB,     BPdf,   BDataSet,   BHisto,   BFunc = getFuncKDEAll(boxes,"B",Xmin,Xmax)

    lnQData = getLnQDataAll(boxes)
    
    CLb, BFuncFill, dummyFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, BFunc)
    CLsb, dummyFill, SpBFuncFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, SpBFunc)

    if CLb==0:
        CLs = 1.0
    else:
        CLs = CLsb/CLb

    lnQExp = array("d",[0.,0.,0.,0.,0.])
    CLbExp = array("d",[0.023, 0.159,0.500,0.841,0.977])
    BFunc.GetQuantiles(5,lnQExp,CLbExp)
    # WE MUST REVERSE THE ORDER OF lnQExp IN LEP,
    # otherwise we'll swap CLb <=> 1-CLb
    CLsbExp = [ getOneSidedPValueFromKDE(thislnQ,Xmin,Xmax, SpBFunc)[0] for thislnQ in lnQExp]
    CLsExp = [thisCLsb/thisCLb for thisCLsb, thisCLb in zip(CLsbExp,CLbExp)]
    
    
    print "###########################"
    print "Box           = %s"%('_'.join(boxes))
    print "mg            = %.0f"%mg
    print "mchi          = %.0f"%mchi
    print "xsec          = %.4f pb-1"%xsec
    print "###########################"
    print "lnQ on Data   = %.3f"%lnQData
    print "CLb           = %.3f"%CLb
    print "CLs+b         = %.3f"%CLsb
    print "CLs           = %.3f"%CLs
    print "###########################"
    print "lnQExp+2sigma = %.3f"%lnQExp[0]
    print "lnQExp+1sigma = %.3f"%lnQExp[1]
    print "lnQExp        = %.3f"%lnQExp[2]
    print "lnQExp-1sigma = %.3f"%lnQExp[3]
    print "lnQExp-2sigma = %.3f"%lnQExp[4]
    print "CLsExp+2sigma = %.3f"%CLsExp[0]
    print "CLsExp+1sigma = %.3f"%CLsExp[1]
    print "CLsExp        = %.3f"%CLsExp[2]
    print "CLsExp-1sigma = %.3f"%CLsExp[3]
    print "CLsExp-2sigma = %.3f"%CLsExp[4]
    print "###########################"

    c = rt.TCanvas("c","c",500,400)
    #BFunc.GetXaxis().SetTitle("#lambda = log(L_{s+b}/L_{b})")
    BFunc.GetXaxis().SetTitle("q_{#sigma} = -2log(L_{s+b}(#sigma,#hat{#theta}_{#sigma}) / L_{s+b}(#hat{#sigma},#hat{#theta})")
    BHisto.Scale(BFunc.GetMaximum()/BHisto.GetMaximum())
    BFunc.SetLineColor(rt.kBlue)
    BHisto.SetLineColor(rt.kBlue)
    SpBHisto.Scale(SpBFunc.GetMaximum()/SpBHisto.GetMaximum())
    SpBFunc.SetLineColor(rt.kRed)
    SpBHisto.SetLineColor(rt.kRed)
    BFunc.Draw("")
    BHisto.Draw("histosame")
    BFuncFill.Draw("fsame")
    BFunc.Draw("same")
    SpBHisto.Draw("histosame")
    SpBFuncFill.Draw("fsame")
    SpBFunc.Draw("same")
    #for profile
    c.SetLogy()
    
    hybridLimit = "Razor2013HybridLimit"
    modelPoint = "MG_%f_MCHI_%f"%(mg,mchi)
    xsecString = str(xsec).replace(".","p")
    l = rt.TLatex()
    l.SetTextAlign(12)
    l.SetTextSize(0.05)
    l.SetTextFont(42)
    l.SetNDC()
    l.DrawLatex(0.10,0.955,"m_{#tilde{g}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; #sigma = %.4f pb; %s Box"%(mg,mchi,xsec,"All"))
    l.DrawLatex(0.55,0.8,"CL_{s} = %.4f"%(CLs))
    
    line = rt.TLine(lnQData, 0, lnQData, BHisto.GetMaximum())
    line.SetLineWidth(2)
    line.Draw("same")
    leg = rt.TLegend(0.55,0.49,0.8,0.67)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.AddEntry(SpBFuncFill, "CL_{s+b}","f")
    leg.AddEntry(BFuncFill, "1-CL_{b}","f")
    #leg.AddEntry(line, "#lambda on Data","l")
    leg.AddEntry(line, "q_{#sigma} on Data","l")
    leg.Draw("same")
    c.Print("%s/lnQ_%s_%s_%s_%s.pdf"%(directory,model,modelPoint,xsecString,'_'.join(boxes)))
    del c

    return CLs, CLsExp

def getCLs(mg, mchi, xsec, box, model, directory):
    LzCut = "H0covQual_%s==3&&H1covQual_%s==3&&LzSR_%s>=0."%(box,box,box)
    
    SpBFileName = getFileName("SpB",mg,mchi,xsec,box,model,directory)
    BFileName = getFileName("B",mg,mchi,xsec,box,model,directory)
    
    Xmin, Xmax = getMinMax(box,BFileName,SpBFileName,LzCut)

    lnQSpB, SpBPdf, SpBDataSet, SpBHisto, SpBFunc = getFuncKDE(box,SpBFileName,LzCut,Xmin,Xmax)
    lnQB,     BPdf,   BDataSet,   BHisto,   BFunc = getFuncKDE(box,BFileName,LzCut,Xmin,Xmax)

    lnQData = getLnQData(box,BFileName)
    # for Hybrid CLs
    # CLb, dummyFill, BFuncFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, BFunc)
    # CLsb, SpBFuncFill, dummyFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, SpBFunc)

    CLb, BFuncFill, dummyFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, BFunc)
    CLsb, dummyFill, SpBFuncFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, SpBFunc)
    
    if CLb==0:
        CLs = 1.0
    else:
        CLs = CLsb/CLb

    lnQExp = array("d",[0.,0.,0.,0.,0.])
    CLbExp = array("d",[0.023, 0.159,0.500,0.841,0.977])
    BFunc.GetQuantiles(5,lnQExp,CLbExp)
    # WE MUST REVERSE THE ORDER OF lnQExp IN LEP,
    # otherwise we'll swap CLb <=> 1-CLb
    CLsbExp = [ getOneSidedPValueFromKDE(thislnQ,Xmin,Xmax, SpBFunc)[0] for thislnQ in lnQExp]
    CLsExp = [thisCLsb/thisCLb for thisCLsb, thisCLb in zip(CLsbExp,CLbExp)]
    
    
    print "###########################"
    print "Box           = %s"%box
    print "mg            = %.0f"%mg
    print "mchi          = %.0f"%mchi
    print "xsec          = %.4f pb-1"%xsec
    print "###########################"
    print "lnQ on Data   = %.3f"%lnQData
    print "CLb           = %.3f"%CLb
    print "CLs+b         = %.3f"%CLsb
    print "CLs           = %.3f"%CLs
    print "###########################"
    print "lnQExp+2sigma = %.3f"%lnQExp[0]
    print "lnQExp+1sigma = %.3f"%lnQExp[1]
    print "lnQExp        = %.3f"%lnQExp[2]
    print "lnQExp-1sigma = %.3f"%lnQExp[3]
    print "lnQExp-2sigma = %.3f"%lnQExp[4]
    print "CLsExp+2sigma = %.3f"%CLsExp[0]
    print "CLsExp+1sigma = %.3f"%CLsExp[1]
    print "CLsExp        = %.3f"%CLsExp[2]
    print "CLsExp-1sigma = %.3f"%CLsExp[3]
    print "CLsExp-2sigma = %.3f"%CLsExp[4]
    print "###########################"

    c = rt.TCanvas("c","c",500,400)
    #BFunc.GetXaxis().SetTitle("#lambda = log(L_{s+b}/L_{b})")
    BFunc.GetXaxis().SetTitle("q_{#sigma} = -2log(L_{s+b}(#sigma,#hat{#theta}_{#sigma}) / L_{s+b}(#hat{#sigma},#hat{#theta})")
    BHisto.Scale(BFunc.GetMaximum()/BHisto.GetMaximum())
    BFunc.SetLineColor(rt.kBlue)
    BHisto.SetLineColor(rt.kBlue)
    SpBHisto.Scale(SpBFunc.GetMaximum()/SpBHisto.GetMaximum())
    SpBFunc.SetLineColor(rt.kRed)
    SpBHisto.SetLineColor(rt.kRed)
    BFunc.Draw("")
    BHisto.Draw("histosame")
    BFuncFill.Draw("fsame")
    BFunc.Draw("same")
    SpBHisto.Draw("histosame")
    SpBFuncFill.Draw("fsame")
    SpBFunc.Draw("same")
    #for profile
    c.SetLogy()
    
    hybridLimit = "Razor2013HybridLimit"
    modelPoint = "MG_%f_MCHI_%f"%(mg,mchi)
    xsecString = str(xsec).replace(".","p")
    l = rt.TLatex()
    l.SetTextAlign(12)
    l.SetTextSize(0.05)
    l.SetTextFont(42)
    l.SetNDC()
    l.DrawLatex(0.10,0.955,"m_{#tilde{g}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; #sigma = %.4f pb; %s Box"%(mg,mchi,xsec,box))
    l.DrawLatex(0.55,0.8,"CL_{s} = %.4f"%(CLs))
    
    line = rt.TLine(lnQData, 0, lnQData, BHisto.GetMaximum())
    line.SetLineWidth(2)
    line.Draw("same")
    leg = rt.TLegend(0.55,0.49,0.8,0.67)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.AddEntry(SpBFuncFill, "CL_{s+b}","f")
    leg.AddEntry(BFuncFill, "1-CL_{b}","f")
    #leg.AddEntry(line, "#lambda on Data","l")
    leg.AddEntry(line, "q_{#sigma} on Data","l")
    leg.Draw("same")
    c.Print("%s/lnQ_%s_%s_%s_%s.pdf"%(directory,model,modelPoint,xsecString,box))
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



def getXsecRange(model,neutralinopoint,gluinopoint):
    mDelta = (gluinopoint*gluinopoint - neutralinopoint*neutralinopoint)/gluinopoint
    
    if model=="T1bbbb":
        if mDelta < 400:
            xsecRange = [0.005, 0.01, 0.05, 0.1, 0.5, 1., 5.]
        elif mDelta < 800:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
        else:
            xsecRange = [0.0005, 0.001, 0.005, 0.01, 0.05]
    elif model=="T2tt":
        if mDelta < 500:
            xsecRange = [0.01, 0.05, 0.1, 0.5, 1.]
        else:
            xsecRange = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]

    return xsecRange

if __name__ == '__main__':

    boxInput = sys.argv[1]
    model = sys.argv[2]
    directory = sys.argv[3]

    
    if model=="T1bbbb":
        gchipairs = [( 775,  50), ( 825,  50), ( 925,  50), ( 950,  50), (1025,  50), (1075,  50), (1125,  50), (1225,  50), (1325,  50), (1375,  50),
                     ( 775, 200), ( 825, 200), ( 925, 200), ( 950, 200), (1025, 200), (1075, 200), (1125, 200), (1225, 200), (1325, 200), (1375, 200),
                     #( 775, 300), ( 825, 300), ( 925, 300), ( 950, 300), (1025, 300), (1075, 300), (1125, 300), (1225, 300), (1325, 300), (1375, 300),
                     ( 775, 400), ( 825, 400), ( 925, 400), ( 950, 400), (1025, 400), (1075, 400), (1125, 400), (1225, 400), (1325, 400), (1375, 400),
                     ( 775, 525), ( 825, 525), ( 925, 525), ( 950, 525), (1025, 525), (1075, 525), (1125, 525), (1225, 525), (1325, 525), (1375, 525),
                     ( 775, 600), ( 825, 600), ( 925, 600),  (950, 600), (1025, 600), (1075, 600), (1125, 600), (1225, 600), (1325, 600), (1375, 600),
                     ( 775, 650), ( 825, 650), ( 925, 650), ( 950, 650), (1025, 650), (1075, 650), (1125, 650), (1225, 650), (1325, 650), (1375, 650),
                     ( 775, 700), ( 825, 700), ( 925, 700), ( 950, 700), (1025, 700), (1075, 700), (1125, 700), (1225, 700), (1325, 700), (1375, 700)]
                     #( 925, 800), (1025, 800), (1125, 800), (1225, 800), (1325, 800)]
    elif model=="T2tt":
        gchipairs = [(150, 50), (200, 50), (250, 50), (300, 50), (350, 50), (400, 50), (450, 50),
                     (500, 50), (550, 50), (600, 50), (650, 50), (700, 50), (750, 50), (800, 50)]
    

    
    #boxes = ["MultiJet","TauTauJet","Jet"]
    boxes = boxInput.split("_")
        

    doAll = (len(boxes)>1)
    if not doAll:
        box = boxes[0]
    
    rootFileName = "%s/CLs_%s.root"%(directory,'_'.join(boxes))
    if not glob.glob(rootFileName):
        outputFileNames = []
        for mg, mchi in gchipairs:
            xsecRange = getXsecRange(model,mchi,mg)
            for xsec in xsecRange:
                if not doAll:
                    if not glob.glob(getFileName("SpB",mg,mchi,xsec,box,model,directory)+"*"): continue
                    if not glob.glob(getFileName("B",mg,mchi,xsec,box,model,directory)+"*"): continue
                    CLs = []
                    CLsExp = []
                    CLsBox,CLsExpBox  = getCLs(mg, mchi, xsec, box, model, directory)
                    CLs.append(CLsBox)
                    CLsExp.append(CLsExpBox)
                    outputFileNames.append(writeCLTree(mg, mchi, xsec, box, model, directory, CLs, CLsExp))
                else:
                    anyfilesNotFound = []
                    for box in boxes:
                        anyfilesNotFound.append(not glob.glob(getFileName("SpB",mg,mchi,xsec,box,model,directory)+"*") )
                        anyfilesNotFound.append(not glob.glob(getFileName("B",mg,mchi,xsec,box,model,directory)+"*"))
                    if any(anyfilesNotFound): continue
                    xsecString = str(xsec).replace(".","p")
                    if glob.glob("%s/CLs_mg_%i_mchi_%i_xsec_%s_%s.root"%(directory,mg, mchi, xsecString,'_'.join(boxes))): continue
                    CLs = []
                    CLsExp = []
                    CLsBox,CLsExpBox  = getCLsAll(mg, mchi, xsec, boxes, model, directory)
                    CLs.append(CLsBox)
                    CLsExp.append(CLsExpBox)
                    outputFileNames.append(writeCLTree(mg, mchi, xsec,'_'.join(boxes), model,directory, CLs, CLsExp))

        haddCmd = "hadd -f %s %s"%(rootFileName,' '.join(outputFileNames))
        print haddCmd
        os.system(haddCmd)
    else:
        outputFileNames = []
        for mg, mchi in gchipairs:
            xsecULObs = []
            xsecULExpPlus2 = []
            xsecULExpPlus = []
            xsecULExp = []
            xsecULExpMinus = []
            xsecULExpMinus2 = []
            if doAll: box = '_'.join(boxes)
            try:
                xsecULObs.append(max(1e-4,getXsecUL("CLs", rootFileName, mg, mchi, box)))
                xsecULExpPlus2.append(max(1e-4,getXsecUL("CLsExpPlus2", rootFileName, mg, mchi, box)))
                xsecULExpPlus.append(max(1e-4,getXsecUL("CLsExpPlus", rootFileName, mg, mchi, box)))
                xsecULExp.append(max(1e-4,getXsecUL("CLsExp", rootFileName, mg, mchi, box)))
                xsecULExpMinus.append(max(1e-4,getXsecUL("CLsExpMinus", rootFileName, mg, mchi, box)))
                xsecULExpMinus2.append(max(1e-4,getXsecUL("CLsExpMinus2", rootFileName, mg, mchi, box)))
                outputFileNames.append(writeXsecTree(box, directory, mg, mchi, xsecULObs, xsecULExpPlus2, xsecULExpPlus, xsecULExp, xsecULExpMinus, xsecULExpMinus2))
            except TypeError: continue
        xsecFileName = "%s/xsecUL_%s.root"%(directory,'_'.join(boxes))
        haddCmd = "hadd -f %s %s"%(xsecFileName,' '.join(outputFileNames))
        print haddCmd
        os.system(haddCmd)
    
