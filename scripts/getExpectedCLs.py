import ROOT as rt
import sys
import RootTools
import glob
import getCLs

def ComputeMedian(myHisto):
    integral = 0.
    median = -99999999999;
    plus = -99999999999;
    minus = -99999999999;
    for i in range(1, myHisto.GetNbisX()+1):
        if integral < 0.50 and integral + myHisto.GetBinContent(i) > 0.50: median = myHisto.GetBinCenter(i)
        if integral < 0.16 and integral + myHisto.GetBinContent(i) > 0.16: median = myHisto.GetBinCenter(i)
        if integral < 0.84 and integral + myHisto.GetBinContent(i) > 0.84: median = myHisto.GetBinCenter(i)
        integral += myHisto.GetBinContent(i)
    return median, plus,minus

if __name__ == '__main__':
    fileName = sys.argv[1]
    BoxName = sys.argv[2]

    m0 = fileName.split("_")[2]
    m12 = fileName.split("_")[4]

    fileInput = rt.TFile.Open(fileName)
    SpB = fileInput.Get("SpB_%s" %BoxName)
    B = fileInput.Get("B_%s" %BoxName)

    myCLs = []
    for i in range(0, 1000):
        # sample the critical value for a bkg-only toy sample
        myCriticalValue = B.GetRandom()
        # compute The CLs value for the critical value
        myCLs.append(calcCLs(SpB, B, myCriticalValue))

    myCLs.sort()
    myCLsHisto = rt.TH1D("ExpectedCLs_%s" %BoxName, 100, min(myCLs), max(myCLs))
    for thisCLs in myCLs: myCLsHisto.Fill(thisCLs)
        
    clExpectedTree = rt.TTree("clExpectedTree", "clExpectedTree")
    rt.gROOT.ProcessLine(
        "struct MyStruct{\
        Double_t m0;\
        Double_t m12;\
        Double_t CLexp;\
        Double_t CLexpPlus;\
        Double_t CLexpMinus;};")
    from ROOT import MyStruct

    s = MyStruct()
    clTree.Branch("m0", rt.AddressOf(s,"m0"),'m0/D')
    clTree.Branch("m12", rt.AddressOf(s,"m12"),'m12/D')
    clTree.Branch("CLexp_%s" %BoxName, rt.AddressOf(s,"CLexp"),'CLexp/D')
    clTree.Branch("CLexpPlus_%s" %BoxName, rt.AddressOf(s,"CLexpPlus"),'CLexpPlus/D')
    clTree.Branch("CLexpMinus_%s" %BoxName, rt.AddressOf(s,"CLexpMinus"),'CLexpMinus/D')

    s.m0 = m0
    s.m12 = m12
    s.CLexp, s.CLexpPlus, s.CLexpMinus = ComputeMedian(myCLsHisto)
    clExpectedTree.Fill()
    
    outFile = rt.TFile(fileName.split(".root")[0]+"_expected.root", "recreate")
    clExpectedTree.Fill()
    myCLsHisto.Fill()
    outFile.Close()
