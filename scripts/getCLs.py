import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os
from array import *


def useThisRho(minX,maxX):
    #rho = 0.1
    rho = 2.0
    return rho
    
def getLnQData(box,fileName):
    dataTree = rt.TChain("myDataTree")
    addToChain = fileName.replace("//","/")+"_*.root"+"/"+box+"/myDataTree"
    print "adding to chain: %s"% addToChain
    dataTree.Add(addToChain)

    dataTree.Draw('>>elist','','entrylist')
    elist = rt.gDirectory.Get('elist')
    entry = elist.Next()
    dataTree.GetEntry(entry)
    lnQData = dataTree.LzSR
    
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
        lnQToys.append(hypoTree.LzSR)
    return lnQToys

def getMinMax(box,BfileName,SpBfileName):
    hypoTree = rt.TChain("myTree")
    addToChain = BfileName.replace("//","/")+"_*.root"+"/"+box+"/myTree"
    hypoTree.Add(addToChain)
    addToChain = SpBfileName.replace("//","/")+"_*.root"+"/"+box+"/myTree"
    hypoTree.Add(addToChain)
    hypoTree.Draw("LzSR")
    
    htemp = rt.gPad.GetPrimitive("htemp")
    Xmin = htemp.GetXaxis().GetXmin()
    Xmax = htemp.GetXaxis().GetXmax()
    
    XmaxBin = htemp.GetXaxis().FindBin(Xmax)
    XmaxTest = Xmax
    XmaxTestBin = htemp.GetXaxis().FindBin(XmaxTest)
    while htemp.Integral(XmaxTestBin,XmaxBin)/htemp.Integral() < 0.005:
       XmaxTest = Xmin + float(XmaxTest-Xmin)*0.95
       XmaxTestBin = htemp.GetXaxis().FindBin(XmaxTest)
    Xmax = XmaxTest

    return Xmin, Xmax

def getFuncKDE(box,fileName,Xmin,Xmax):
    hypoTree = rt.TChain("myTree")
    addToChain = fileName.replace("//","/")+"_*.root"+"/"+box+"/myTree"
    print "adding to chain: %s"% addToChain
    hypoTree.Add(addToChain)
    
    hypoHisto = rt.TH1D("histo","histo",50,Xmin,Xmax)
    hypoTree.Project(hypoHisto.GetName(),"LzSR")

    hypoHisto.SetDirectory(0)
    hypoHisto.Scale(1./hypoHisto.Integral())
    
    lnQ = rt.RooRealVar("LzSR","LzSR",Xmin,Xmax)
    
    hypoSet = rt.RooArgSet("hypoSet")
    hypoSet.add(lnQ)
    hypoList = rt.RooArgList("hypoList")
    hypoList.add(lnQ)

    hypoDataSet= rt.RooDataSet("hypoDataSet","hypoDataSet",hypoTree,hypoSet)

    
    rho = useThisRho(Xmin,Xmax)
    hypoPdf = rt.RooKeysPdf("hypoPdf","hypoPdf",lnQ,hypoDataSet,rt.RooKeysPdf.NoMirror,rho)
    hypoFunc = hypoPdf.asTF(hypoList,rt.RooArgList(),hypoSet)

    return lnQ, hypoPdf, hypoDataSet, hypoHisto, hypoFunc

def getOneSidedPValueFromKDE(Xobs,Xmin,Xmax,func):
    funcObs = func.Eval(Xobs)

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

def getFileName(hypo, mg, mchi, xsec, box,directory):
    model = "T1bbbb"
    hybridLimit = "Razor2012HybridLimit"
    modelPoint = "MG_%f_MCHI_%f"%(mg,mchi)
    xsecString = str(xsec).replace(".","p")
    fileName = "%s/%s_%s_%s_%s_%s_%s"%(directory,hybridLimit,model,modelPoint,box,xsecString,hypo)
    return fileName

    
def writeXsecTree(boxes, directory, mg, mchi, xsecULObs, xsecULExpPlus, xsecULExp, xsecULExpMinus):
    xsecTree = rt.TTree("xsecTree", "xsecTree")
    myStructCmd = "struct MyStruct{Double_t mg;Double_t mchi;"
    ixsecUL = 0
    for box in boxes: 
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
    for box in boxes:
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

    outputFileName = "%s/xsecUL_mg_%s_mchi_%s_%s.root" %(directory, mg, mchi, '_'.join(boxes))
    print "xsec UL values being written to %s"%outputFileName
    fileOut = rt.TFile.Open(outputFileName, "recreate")
    xsecTree.Write()
    
    fileOut.Close()
    return outputFileName


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
        
    erfcInvVals = array('d',[rt.TMath.ErfcInverse(min(CLs,1.0))for CLs in CLVals])
    i = 0
    while  i < len(CLVals):
        if CLVals[i]>=1:
            CLVals.pop(i)
            erfcInvVals.pop(i)
            xsecVals.pop(i)
        i+=1

    lessXsecVals = array('d')
    lessErfcInvVals = array('d')
    for i in xrange(0,len(xsecVals)):
        if erfcInvVals[i] < rt.TMath.ErfcInverse(0.05):
            lessXsecVals.append(xsecVals[i])
            lessErfcInvVals.append(erfcInvVals[i])
    
    erfcTGraph = rt.TGraph(len(xsecVals),erfcInvVals,xsecVals)
    
    polyPars = array('d',[0,0])
    fPoly = rt.TF1("fPoly","[0] +[1]*x",0, rt.TMath.ErfcInverse(0.05))
    fPoly.SetParameter(0,polyPars[0])
    fPoly.SetParameter(1,polyPars[1])

    
    if len(lessXsecVals) > 1:
        lessErfcTGraph = rt.TGraph(len(lessXsecVals),lessErfcInvVals,lessXsecVals)
        lessErfcTGraph.Fit(fPoly, "","",0, rt.TMath.ErfcInverse(0.05))
        xsecULFit = fPoly.Eval(rt.TMath.ErfcInverse(0.05))

    erfcTSpilne = rt.TSpline3("spline3",erfcInvVals,xsecVals,len(xsecVals))
    xsecULSpline = erfcTGraph.Eval(rt.TMath.ErfcInverse(0.05),0,"S")
    xsecULPolyLine = erfcTGraph.Eval(rt.TMath.ErfcInverse(0.05),0)
    
    if len(lessXsecVals) <= 1:
        xsecUL = xsecULPolyLine
    else:
        xsecUL = xsecULFit
        
    lines = []
    lines.append(rt.TLine(rt.TMath.ErfcInverse(0.05), 0, rt.TMath.ErfcInverse(0.05), xsecUL))
    lines.append(rt.TLine(erfcTGraph.GetXaxis().GetXmin(), xsecUL, rt.TMath.ErfcInverse(0.05), xsecUL))
    [line.SetLineColor(rt.kBlue) for line in lines]
    [line.SetLineWidth(2) for line in lines]
    d = rt.TCanvas("d","d",500,400)
    erfcTGraph.SetLineWidth(2)
    erfcTGraph.Draw("al*")
    erfcTSpilne.SetLineWidth(2)
    erfcTSpilne.SetLineColor(rt.kGreen+2)
    #erfcTSpilne.Draw("acsame")
    if len(lessXsecVals) > 1: fPoly.Draw("csame")
    [line.Draw("lsame") for line in lines]
    model = "T1bbbb"
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
    
def getCLs(mg, mchi, xsec, box, directory):
    SpBFileName = getFileName("SpB",mg,mchi,xsec,box,directory)
    BFileName = getFileName("B",mg,mchi,xsec,box,directory)
    
    Xmin, Xmax = getMinMax(box,BFileName,SpBFileName)
    
    lnQSpB, SpBPdf, SpBDataSet, SpBHisto, SpBFunc = getFuncKDE(box,SpBFileName,Xmin,Xmax)
    lnQB,     BPdf,   BDataSet,   BHisto,   BFunc = getFuncKDE(box,  BFileName,Xmin,Xmax)

    lnQData = getLnQData(box,BFileName)


    CLb, dummyFill, BFuncFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, BFunc)
    
    CLsb, SpBFuncFill, dummyFill = getOneSidedPValueFromKDE(lnQData,Xmin,Xmax, SpBFunc)

    CLs = CLsb/CLb

    lnQExp = array("d",[0.,0.,0.])
    CLbExp = array("d",[0.159,0.500,0.841])
    BFunc.GetQuantiles(3,lnQExp,CLbExp)
    # WE MUST REVERSE THE ORDER OF lnQExp,
    # otherwise we'll swap CLb <=> 1-CLb
    CLsbExp = [ getOneSidedPValueFromKDE(thislnQ,Xmin,Xmax, SpBFunc)[0] for thislnQ in reversed(lnQExp)]
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
    print "lnQExp+1sigma = %.3f"%lnQExp[0]
    print "lnQExp        = %.3f"%lnQExp[1]
    print "lnQExp-1sigma = %.3f"%lnQExp[2]
    print "CLsExp+1sigma = %.3f"%CLsExp[0]
    print "CLsExp        = %.3f"%CLsExp[1]
    print "CLsExp-1sigma = %.3f"%CLsExp[2]
    print "###########################"

    c = rt.TCanvas("c","c",500,400)
    BFunc.GetXaxis().SetTitle("log(Q) = log(L_{s+b}/L_{b})")
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
    #c.SetLogy()
    
    model = "T1bbbb"
    hybridLimit = "Razor2012HybridLimit"
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
    leg.AddEntry(line, "log(Q) on Data","l")
    leg.Draw("same")
    c.Print("%s/lnQ_%s_%s_%s_%s.pdf"%(directory,model,modelPoint,xsecString,box))
    del c

    return CLs, CLsExp

def writeCLTree(mg,mchi,xsec, boxes, directory, CLs, CLsExp):
    clTree = rt.TTree("clTree", "clTree")
    myStructCmd = "struct MyStruct{Double_t mg;Double_t mchi;Double_t xsec;"
    iCL = 0
    for box in boxes: 
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
    for box in boxes:
        clTree.Branch("CLs_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+0)),'CL%i/D'%(iCL+0))
        clTree.Branch("CLsExpPlus_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+1)),'CL%i/D'%(iCL+1))
        clTree.Branch("CLsExp_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+2)),'CL%i/D'%(iCL+2))
        clTree.Branch("CLsExpMinus_%s"%box, rt.AddressOf(s,"CL%i"%(iCL+3)),'CL%i/D'%(iCL+3))
        exec 's.CL%i = CLs[iCL]'%(iCL+0)
        exec 's.CL%i = CLsExp[iCL][0]'%(iCL+1)
        exec 's.CL%i = CLsExp[iCL][1]'%(iCL+2)
        exec 's.CL%i = CLsExp[iCL][2]'%(iCL+3)
        iCL += 4

    clTree.Fill()

    xsecString = str(xsec).replace(".","p")
    outputFileName = "%s/CLs_mg_%s_mchi_%s_xsec_%s_%s.root" %(directory, mg, mchi, xsecString,'_'.join(boxes))
    print "CLs values being written to %s"%outputFileName
    fileOut = rt.TFile.Open(outputFileName, "recreate")
    clTree.Write()
    
    fileOut.Close()
    return outputFileName

def getXsecMax(mg, mchi):
    name = "T1bbbb"
    label = "MR400.0_R0.5"
    massPoint = "MG_%f_MCHI_%f"%(mg, mchi)
    signalFile = rt.TFile("SMS/"+name+"_"+massPoint+"_"+label+"_"+box+".root")
    wHisto = signalFile.Get("wHisto")
    mrMean = wHisto.GetMean(1)
    stop_xs = 0.0
    yield_at_xs = [(stop_xs,0.0)]
    #with 15 signal events, we *should* be able to set a limit
    print "deciding xsec range based on signal mrMean = %f"%mrMean
    if mrMean < 800:
        eventsToExclude = 150
        poi_max = 1.
    elif mrMean < 1000:
        eventsToExclude = 100
        poi_max = 0.5
    elif mrMean < 1600:
        eventsToExclude = 50
        poi_max = 0.2
    else:
        eventsToExclude = 25
        poi_max = 0.05
    return poi_max

if __name__ == '__main__':
    gluinopoints = range(425,2025,200)
    #gluinopoints = [425]
    neutralinopoints = [0]
    
    xsecsteps = [0.01,0.05,0.1,0.5,1.0]
    
    box = sys.argv[1]
    directory = sys.argv[2]
    if box == 'All':
        boxes = ["Jet","MultiJet"]
    else:
        boxes = [box]

        
    rootFileName = "%s/CLs_%s.root"%(directory,'_'.join(boxes))
    if not glob.glob(rootFileName):
        outputFileNames = []
        for mg in gluinopoints:
            for mchi in neutralinopoints:
                for xsecstep in xsecsteps:
                    xsec = xsecstep * getXsecMax(mg,mchi)
                    if not glob.glob(getFileName("SpB",mg,mchi,xsec,box,directory)+"*"): continue
                    if not glob.glob(getFileName("B",mg,mchi,xsec,box,directory)+"*"): continue
                    if box!="All":
                        CLs = []
                        CLsExp = []
                        CLsBox,CLsExpBox  = getCLs(mg, mchi, xsec, box, directory)
                        CLs.append(CLsBox)
                        CLsExp.append(CLsExpBox)
                        outputFileNames.append(writeCLTree(mg, mchi, xsec, boxes, directory, CLs, CLsExp))

                    else:
                        print 'WORKING ON ALL STILL'
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
                for box in boxes:
                    xsecULObs.append(max(1e-3,getXsecUL("CLs", rootFileName, mg, mchi, box)))
                    xsecULExpPlus.append(max(1e-3,getXsecUL("CLsExpPlus", rootFileName, mg, mchi, box)))
                    xsecULExp.append(max(1e-3,getXsecUL("CLsExp", rootFileName, mg, mchi, box)))
                    xsecULExpMinus.append(max(1e-3,getXsecUL("CLsExpMinus", rootFileName, mg, mchi, box)))
                outputFileNames.append(writeXsecTree(boxes, directory, mg, mchi, xsecULObs, xsecULExpPlus, xsecULExp, xsecULExpMinus))
        xsecFileName = "%s/xsecUL_%s.root"%(directory,'_'.join(boxes))
        haddCmd = "hadd -f %s %s"%(xsecFileName,' '.join(outputFileNames))
        print haddCmd
        os.system(haddCmd)
    
