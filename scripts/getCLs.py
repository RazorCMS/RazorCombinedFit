import ROOT as rt
import sys
import glob
import os
from array import array

def getXsecRange(neutralinopoint,gluinopoint):


    if gluinopoint == 200:
        return [0.1, 0.4, 1.0, 2.0, 5.0, 8.0, 10.0]
    # elif gluinopoint == 300:
    #     return [0.01, 0.05, 0.1, 0.2, 0.4, 0.5, 0.8, 1.0]#, 2.0, 5.0, 6.0]
    # elif gluinopoint == 400:
    #     return [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.5, 1.0, 2.0, 3.0]
    # elif gluinopoint == 500:
    #     return [0.001, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7]
    # elif gluinopoint == 550:
    #     return [0.001, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7]
    # elif gluinopoint == 600:
    #     return [0.005, 0.01, 0.1, 0.2, 0.3]
    # elif gluinopoint == 650:
    #     return [0.01, 0.02, 0.05, 0.08, 0.1, 0.2, 0.3]
    # elif gluinopoint == 700:
    #     return [0.001, 0.01, 0.02, 0.05, 0.08, 0.1, 0.2]
    # elif gluinopoint == 800:
    #     return [0.001, 0.005, 0.01, 0.02, 0.05, 0.08, 0.1]
    else:
        # return [0.01, 0.05, 0.1, 0.5]
        return [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]

def useThisRho(minX,maxX, type):
    if type=="LHC":
        rho = 1.0
    if type=="LEP":
        rho = 2.0
    return rho

def getLnQDataAll(boxes):
    lnQDataBox = []
    for box in boxes:
        getLnQData
        fileName = getFileName("B",mg,mchi,xsecstep,box,directory)
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

def getMinMax(box,BfileName,SpBfileName,LzCut,type):
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

    if type=="LHC":
        print "LHC"
        Xmin = 0
        Xmax = mean+5*rms
    if type=="LEP":
        XmaxBin = htemp.GetXaxis().FindBin(Xmax)
        XmaxTest = Xmax
        XmaxTestBin = htemp.GetXaxis().FindBin(XmaxTest)
        while htemp.Integral(XmaxTestBin,XmaxBin)/htemp.Integral() < 0.005:
            XmaxTest = Xmin + float(XmaxTest-Xmin)*0.95
            XmaxTestBin = htemp.GetXaxis().FindBin(XmaxTest)
        Xmax = XmaxTest

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
        fileName = getFileName(hypo,mg,mchi,xsecstep,box,directory)
        boxDict[box] = sorted(glob.glob(fileName.replace("//","/")+"_*.root"),key=sortkey)
        boxSet[box] = set([newFileName.replace(box,"box") for newFileName in boxDict[box]])
        for addToChain in boxDict[box]:
            addToChain+="/%s/myTree"%(box)
            # print "adding to chain: %s"% addToChain

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
            # print "adding to chain: %s"% addToChain
            hypoTreeBox.Add(addToChain)
        #lnQBox.append(rt.RooRealVar("LzSR_%s"%box,"LzSR_%s"%box,Xmin,Xmax))
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

    hypoDataSet = hypoDataSetBox[0].Clone("hypoDataSet")
    hypoDataSet.SetTitle("hypoDataSet")
    for i in xrange(1,len(hypoDataSetBox)):
        # print hypoDataSet, hypoDataSetBox[i]
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

def getFuncKDE(box,fileName,LzCut,Xmin,Xmax,type):
    if box=="All":
        return getFuncKDEAll(boxes,fileName,LzCut,Xmin,Xmax)
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

    rho = useThisRho(Xmin,Xmax,type)
    hypoPdf = rt.RooKeysPdf("hypoPdf","hypoPdf",lnQ,hypoDataSet,rt.RooKeysPdf.NoMirror,rho)
    hypoFunc = hypoPdf.asTF(hypoList,rt.RooArgList(),hypoSet)

    return lnQ, hypoPdf, hypoDataSet, hypoHisto, hypoFunc

def getOneSidedPValueFromKDE(Xobs,Xmin,Xmax,func,type="LEP"):
    if type=="LEP":
        return getLeftSidedPValueFromKDE(Xobs,Xmin,Xmax,func)
    if type =="LHC":
        return getRightSidedPValueFromKDE(Xobs,Xmin,Xmax,func)

def getRightSidedPValueFromKDE(Xobs,Xmin,Xmax,func):
    # funcObs = func.Eval(Xobs)
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

    return pValKDE,funcFillRight, funcFillLeft

def getLeftSidedPValueFromKDE(Xobs,Xmin,Xmax,func):
    # funcObs = func.Eval(Xobs)

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

def getFileName(hypo, mg, mchi, xsec, box,directory):
    model = "T2tt"
    hybridLimit = "Razor2012HybridLimit"
    modelPoint = "%.1f_%.1f"%(mg,mchi)
    xsecString = str(xsec).replace(".","p")
    fileName = "%s/%s_%s_%s_%s_%s_%s"%(directory,hybridLimit,model,modelPoint,box,xsecString,hypo)
    # fileName = "%s/%s_%s_%s_%s_%s"%(directory,hybridLimit,modelPoint,box,xsecString,hypo)
    print fileName
    return fileName

def writeXsecTree(box, directory, mg, mchi, xsecULObs, xsecULExpPlus, xsecULExp, xsecULExpMinus):
    xsecTree = rt.TTree("xsecTree", "xsecTree")
    myStructCmd = "struct MyStruct{Double_t mg;Double_t mchi;"
    ixsecUL = 0
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+0)
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+1)
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+2)
    myStructCmd+= "Double_t xsecUL%i;"%(ixsecUL+3)
    ixsecUL+=4
    myStructCmd += "}"
    rt.gROOT.ProcessLine(myStructCmd)
    from ROOT import MyStruct

    s = MyStruct()
    xsecTree.Branch("mg", rt.AddressOf(s,"mg"),'mg/D')
    xsecTree.Branch("mchi", rt.AddressOf(s,"mchi"),'mchi/D')

    s.mg = mg
    s.mchi = mchi

    ixsecUL = 0
    # for box in boxes:
    xsecTree.Branch("xsecULObs_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+0)),'xsecUL%i/D'%(ixsecUL+0))
    xsecTree.Branch("xsecULExpPlus_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+1)),'xsecUL%i/D'%(ixsecUL+1))
    xsecTree.Branch("xsecULExp_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+2)),'xsecUL%i/D'%(ixsecUL+2))
    xsecTree.Branch("xsecULExpMinus_%s"%box, rt.AddressOf(s,"xsecUL%i"%(ixsecUL+3)),'xsecUL%i/D'%(ixsecUL+3))
    exec 's.xsecUL%i = xsecULObs[ixsecUL]'%(ixsecUL+0)
    exec 's.xsecUL%i = xsecULExpPlus[ixsecUL]'%(ixsecUL+1)
    exec 's.xsecUL%i = xsecULExp[ixsecUL]'%(ixsecUL+2)
    exec 's.xsecUL%i = xsecULExpMinus[ixsecUL]'%(ixsecUL+3)
    ixsecUL += 4

    xsecTree.Fill()

    outputFileName = "%s_plots/xsecUL_mg_%s_mchi_%s_%s.root" %(directory, mg, mchi, '_'.join(boxes))
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
    xsecList = []
    clList  =[]
    while True:
        entry = elist.Next()
        if entry == -1: break
        clTree.GetEntry(entry)
        xsecVals.append(clTree.xsec)
        xsecList.append(clTree.xsec)
        CLVals.append(eval('clTree.%s_%s'%(CL,box)))
        clList.append(eval('clTree.%s_%s'%(CL,box)))

    print "number of xsec vals", len(xsecVals)
    print xsecVals
    print CLVals

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

    print "number of xsec vals", len(xsecVals)
    print xsecVals
    print CLVals

    # now making array of erfc inv vals
    erfcInvVals = array('d',[erfcInv(min(CLs,1.0)) for CLs in CLVals])
    erfcTGraph = rt.TGraph(len(xsecVals),erfcInvVals,xsecVals)

    #this is to be able to see the usual CLs vs. sigma plot
    # xsecTGraph = rt.TGraph(len(xsecVals),xsecVals,CLVals)
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
    model = "T2tt"
    if model=="T2tt":
        l.DrawLatex(0.2,0.955,"m_{#tilde{t}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; %s Box"%(mg,mchi,box))
    elif model=="T1bbbb":
        l.DrawLatex(0.2,0.955,"m_{#tilde{g}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; %s Box"%(mg,mchi,box))
    l.DrawLatex(0.25,0.8,"#sigma^{95%%CL} = %.4f pb"%(xsecUL))
    erfcTGraph.GetXaxis().SetTitle("Erfc(CL_{s})")
    erfcTGraph.GetYaxis().SetTitle("#sigma [pb]")

    d.Print("%s/xsecUL%s_%s_%s_%s.pdf"%(directory,CL,model,modelPoint,box))
    del d

    rootFile.Close()

    return xsecUL

def getCLsAll(mg, mchi, xsec, boxes, directory,type):
    Xmin = 0
    Xmax = 0
    for box in boxes:
        LzCut = "H0covQual_%s==3&&H1covQual_%s==3&&LzSR_%s>=0."%(box,box,box)
        SpBFileName = getFileName("SpB",mg,mchi,xsec,box,directory)
        BFileName = getFileName("B",mg,mchi,xsec,box,directory)
        XminTEST, XmaxTEST = getMinMax(box,BFileName,SpBFileName,LzCut,type)
        Xmax+= XmaxTEST

    lnQSpB, SpBPdf, SpBDataSet, SpBHisto, SpBFunc = getFuncKDEAll(boxes,"SpB",Xmin,Xmax)
    lnQB,     BPdf,   BDataSet,   BHisto,   BFunc = getFuncKDEAll(boxes,"B",Xmin,Xmax)

    lnQData = getLnQDataAll(boxes)

    if type=="LHC":
        CLb, BFuncFill, dummyFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, BFunc,type=type)
        CLsb, dummyFill, SpBFuncFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, SpBFunc,type=type)

    if CLb==0:
        CLs = 1.0
    else:
        CLs = CLsb/CLb

    lnQExp = array("d",[0.,0.,0.,0.,0.])
    CLbExp = array("d",[0.023, 0.159,0.500,0.841,0.977])
    BFunc.GetQuantiles(5,lnQExp,CLbExp)
    # WE MUST REVERSE THE ORDER OF lnQExp IN LEP,
    # otherwise we'll swap CLb <=> 1-CLb
    CLsbExp = [ getOneSidedPValueFromKDE(thislnQ,Xmin,Xmax, SpBFunc,type=type)[0] for thislnQ in lnQExp]
    CLsExp = [thisCLsb/thisCLb for thisCLsb, thisCLb in zip(CLsbExp,CLbExp)]


    print "###########################"
    print "Box           = %s"%('_'.join(boxes))
    print "mg            = %.0f"%mg
    print "mchi          = %.0f"%mchi
    print "xsec          = %.4f pb"%xsec
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
    if type=="LEP":
        BFunc.GetXaxis().SetTitle("#lambda = log(L_{s+b}/L_{b})")
    if type =="LHC":
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
    if type=="LHC":
        c.SetLogy()

    model = "T2tt"
    # hybridLimit = "Razor2012HybridLimit"
    modelPoint = "%.1f_%.1f"%(mg,mchi)
    xsecString = str(xsec).replace(".","p")
    l = rt.TLatex()
    l.SetTextAlign(12)
    l.SetTextSize(0.05)
    l.SetTextFont(42)
    l.SetNDC()
    l.DrawLatex(0.10,0.955,"m_{#tilde{t}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; #sigma = %.4f pb; %s Box"%(mg,mchi,xsec,box))
    l.DrawLatex(0.55,0.8,"CL_{s} = %.4f"%(CLs))

    line = rt.TLine(lnQData, 0, lnQData, BHisto.GetMaximum())
    line.SetLineWidth(2)
    line.Draw("same")
    leg = rt.TLegend(0.55,0.49,0.8,0.67)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.AddEntry(SpBFuncFill, "CL_{s+b}","f")
    leg.AddEntry(BFuncFill, "1-CL_{b}","f")
    if type=="LEP":
        leg.AddEntry(line, "#lambda on Data","l")
    if type=="LHC":
        leg.AddEntry(line, "q_{#sigma} on Data","l")
    leg.Draw("same")
    c.Print("%s/lnQ_%s_%s_%s_%s.pdf"%(directory,model,modelPoint,xsecString,'_'.join(boxes)))
    del c

    return CLs, CLsExp

def getCLs(mg, mchi, xsec, box, directory, type):
    LzCut = "H0covQual_%s==3&&H1covQual_%s==3&&LzSR_%s>=0."%(box,box,box)
    print "Entering getCLs"


    SpBFileName = getFileName("SpB",mg,mchi,xsec,box,directory)
    BFileName = getFileName("B",mg,mchi,xsec,box,directory)

    Xmin, Xmax = getMinMax(box,BFileName,SpBFileName,LzCut,type)

    lnQSpB, SpBPdf, SpBDataSet, SpBHisto, SpBFunc = getFuncKDE(box,SpBFileName,LzCut,Xmin,Xmax,type)
    lnQB,     BPdf,   BDataSet,   BHisto,   BFunc = getFuncKDE(box,  BFileName,LzCut,Xmin,Xmax,type)

    lnQData = getLnQData(box,BFileName)


    # for Hybrid CLs
    if type=="LEP":
        CLb, dummyFill, BFuncFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, BFunc,type=type)
        CLsb, SpBFuncFill, dummyFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, SpBFunc,type=type)

    if type=="LHC":
        CLb, BFuncFill, dummyFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, BFunc,type=type)
        CLsb, dummyFill, SpBFuncFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, SpBFunc,type=type)

    if CLb==0:
        CLs = 1.0
    else:
        CLs = CLsb/CLb

    lnQExp = array("d",[0.,0.,0.,0.,0.])
    CLbExp = array("d",[0.023,0.159,0.500,0.841,0.977])
    BFunc.GetQuantiles(5,lnQExp,CLbExp)
    # WE MUST REVERSE THE ORDER OF lnQExp,
    # otherwise we'll swap CLb <=> 1-CLb
    CLsbExp = [ getOneSidedPValueFromKDE(thislnQ,Xmin,Xmax, SpBFunc,type=type)[0] for thislnQ in lnQExp]
    CLsExp = [thisCLsb/thisCLb for thisCLsb, thisCLb in zip(CLsbExp,CLbExp)]

    print "###########################"
    print "Box           = %s"%box
    print "mg            = %.0f"%mg
    print "mchi          = %.0f"%mchi
    print "xsec          = %.4f pb"%xsec
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
    if type=="LEP":
        BFunc.GetXaxis().SetTitle("#lambda = log(L_{s+b}/L_{b})")
    if type =="LHC":
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
    if type == "LHC":
        c.SetLogy()

    model = "T2tt"
    # hybridLimit = "Razor2012HybridLimit"
    modelPoint = "%.1f_%.1f"%(mg,mchi)
    xsecString = str(xsec).replace(".","p")
    l = rt.TLatex()
    l.SetTextAlign(12)
    l.SetTextSize(0.05)
    l.SetTextFont(42)
    l.SetNDC()
    l.DrawLatex(0.10,0.955,"m_{#tilde{t}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV; #sigma = %.4f pb; %s Box"%(mg,mchi,xsec,box))
    l.DrawLatex(0.55,0.8,"CL_{s} = %.4f"%(CLs))

    line = rt.TLine(lnQData, 0, lnQData, BHisto.GetMaximum())
    line.SetLineWidth(2)
    line.Draw("same")
    leg = rt.TLegend(0.55,0.49,0.8,0.67)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.AddEntry(SpBFuncFill, "CL_{s+b}","f")
    leg.AddEntry(BFuncFill, "1-CL_{b}","f")
    if type == "LEP":
        leg.AddEntry(line, "#lambda on Data","l")
    if type == "LHC":
        leg.AddEntry(line, "q_{#sigma} on Data","l")
    leg.Draw("same")
    c.Print("%s_plots/lnQ_%s_%s_%s_%s.pdf"%(directory,model,modelPoint,xsecString,box))
    del c

    return CLs, CLsExp

def writeCLTree(mg,mchi,xsec, box, directory, CLs, CLsExp):
    clTree = rt.TTree("clTree", "clTree")
    myStructCmd = "struct MyStruct{Double_t mg;Double_t mchi;Double_t xsec;"
    iCL = 0
    myStructCmd+= "Double_t CL%i;"%(iCL+0)
    myStructCmd+= "Double_t CL%i;"%(iCL+1)
    myStructCmd+= "Double_t CL%i;"%(iCL+2)
    myStructCmd+= "Double_t CL%i;"%(iCL+3)
    iCL+=4
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
    clTree.Branch("CLsExpPlus_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+1)),'CL%i/D'%(iCL+1))
    clTree.Branch("CLsExp_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+2)),'CL%i/D'%(iCL+2))
    clTree.Branch("CLsExpMinus_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+3)),'CL%i/D'%(iCL+3))
    exec 's.CL%i = CLs[iCL]'%(iCL+0)
    exec 's.CL%i = CLsExp[iCL][1]'%(iCL+1)
    exec 's.CL%i = CLsExp[iCL][2]'%(iCL+2)
    exec 's.CL%i = CLsExp[iCL][3]'%(iCL+3)
    iCL += 4

    clTree.Fill()

    xsecString = str(xsec).replace(".","p")
    outputFileName = "%s_plots/CLs_mg_%s_mchi_%s_xsec_%s_%s.root" %(directory, mg, mchi, xsecString,'_'.join(boxes))
    print "CLs values being written to %s"%outputFileName
    fileOut = rt.TFile.Open(outputFileName, "recreate")
    clTree.Write()

    fileOut.Close()
    return outputFileName

if __name__ == '__main__':
    # gluinopoints = [200, 300, 400, 500, 550, 600, 650, 700, 800]
    # gluinopoints = [ 500, 525, 550, 575, 600, 625, 650]
    gluinopoints = [ 525, 550, 575, 600, 625, 650]

    neutralinopoints = [0]

    boxInput = sys.argv[1]
    directory = sys.argv[2]
    type = sys.argv[3]

    os.system("mkdir %s_plots" %directory)

    boxes = boxInput.split("_")
    print boxes
    doAll = (len(boxes)>1)
    if not doAll:
        box = boxInput

    rootFileName = "%s_plots/CLs_%s.root"%(directory,'_'.join(boxes))
    if not glob.glob(rootFileName):
        outputFileNames = []
        for mg in gluinopoints:
            for mchi in neutralinopoints:
                xsecRange = getXsecRange(mchi,mg)
                for xsecstep in xsecRange:
                    print xsecstep
                    if not doAll:
                        if not glob.glob(getFileName("SpB",mg,mchi,xsecstep,box,directory)+"*"): continue
                        if not glob.glob(getFileName("B",mg,mchi,xsecstep,box,directory)+"*"): continue
                        CLs = []
                        CLsExp = []
                        CLsBox,CLsExpBox  = getCLs(mg, mchi, xsecstep, box, directory, type=type)
                        if CLsBox > 0.001:
                            CLs.append(CLsBox)
                            CLsExp.append(CLsExpBox)
                            print 'This is CLsBox:', CLsBox
                            outputFileNames.append(writeCLTree(mg, mchi, xsecstep, box, directory, CLs, CLsExp))
                    else:
                        anyfilesNotFound = []
                        for box in boxes:
                            anyfilesNotFound.append(not glob.glob(getFileName("SpB",mg,mchi,xsecstep,box,directory)+"*") )
                            anyfilesNotFound.append(not glob.glob(getFileName("B",mg,mchi,xsecstep,box,directory)+"*"))
                            if any(anyfilesNotFound): continue
                        CLs = []
                        CLsExp = []
                        CLsBox,CLsExpBox  = getCLsAll(mg, mchi, xsecstep, boxes, directory,type=type)
                        if CLsBox > 0.001:
                            CLs.append(CLsBox)
                            CLsExp.append(CLsExpBox)
                            outputFileNames.append(writeCLTree(mg, mchi, xsecstep,'_'.join(boxes), directory, CLs, CLsExp))

        haddCmd = "hadd -f %s %s"%(rootFileName,' '.join(outputFileNames))
        print haddCmd
        os.system(haddCmd)
    else:
        outputFileNames = []
        for mg in gluinopoints:
            for mchi in neutralinopoints:
                xsecULObs = []
                xsecULExpPlus = []
                xsecULExp = []
                xsecULExpMinus = []
                if doAll: box = '_'.join(boxes)
                try:
                    xsecULObs.append(max(1e-4,getXsecUL("CLs", rootFileName, mg, mchi, box)))
                    xsecULExpPlus.append(max(1e-4,getXsecUL("CLsExpPlus", rootFileName, mg, mchi, box)))
                    xsecULExp.append(max(1e-4,getXsecUL("CLsExp", rootFileName, mg, mchi, box)))
                    xsecULExpMinus.append(max(1e-4,getXsecUL("CLsExpMinus", rootFileName, mg, mchi, box)))
                    outputFileNames.append(writeXsecTree(box, directory, mg, mchi, xsecULObs, xsecULExpPlus, xsecULExp, xsecULExpMinus))
                except TypeError:continue
        xsecFileName = "%s_plots/xsecUL_%s.root"%(directory,'_'.join(boxes))
        haddCmd = "hadd -f %s %s"%(xsecFileName,' '.join(outputFileNames))
        print haddCmd
        os.system(haddCmd)
