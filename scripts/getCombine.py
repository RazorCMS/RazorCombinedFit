import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os
from array import *
from getGChiPairs import *

def getFileName(mg, mchi, box, model, directory,fitRegion,method):
    hybridLimit = "higgsCombine"
    modelPoint = "MG_%f_MCHI_%f"%(mg,mchi)
    fileName = "%s/%s%s_%s_%s_%s.%s.mH120.root"%(directory,hybridLimit,model,modelPoint,fitRegion,box,method)
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

if __name__ == '__main__':

    boxInput = sys.argv[1]
    model = sys.argv[2]
    directory = sys.argv[3]

    fitRegion="FULL"
    refXsec = 100 #fb
    doHybridNew = False
    refXsecFile = None
    for i in xrange(4,len(sys.argv)):
        if sys.argv[i].find("--fit-region")!=-1: fitRegion = sys.argv[i+1]
        if sys.argv[i].find("--xsec")!=-1: refXsec = float(sys.argv[i+1])
        if sys.argv[i].find("--xsec-file")!=-1: refXsecFile = sys.argv[i+1]
        if sys.argv[i].find("--toys")!=-1: doHybridNew = True

    if refXsecFile is not None:
        print "INFO: Input ref xsec file!"
        gluinoFile = rt.TFile.Open(refXsecFile,"READ")
        gluinoHistName = refXsecFile.split("/")[-1].split(".")[0]
        gluinoHist = gluinoFile.Get(gluinoHistName)
        refXsec = 1.e3*gluinoHist.GetBinContent(gluinoHist.FindBin(mGluino))
        print "INFO: ref xsec taken to be: %s mass %d, xsec = %f fb"%(gluinoHistName, mGluino, refXsec)
        
    gchipairs = getGChiPairs(model)
        
    boxes = boxInput.split("_")

    #output = rt.TFile.Open("%s/combine_%s_%s.root"%(directory,model,boxInput),"RECREATE")
    #rt.TTree("combine","combine")

    haddOutputs = []
    for mg, mchi in gchipairs:
        if not glob.glob(getFileName(mg,mchi,boxInput,model,directory,fitRegion,"Asymptotic")): continue
        if doHybridNew and not glob.glob(getFileName(mg,mchi,boxInput,model,directory,fitRegion,"HybridNew")): continue

        print getFileName(mg,mchi,boxInput,model,directory,fitRegion,"Asymptotic")
        tFile = rt.TFile.Open(getFileName(mg,mchi,boxInput,model,directory,fitRegion,"Asymptotic"))
        limit = tFile.Get("limit")
        if limit.GetEntries() < 6: continue
        limit.Draw('>>elist','','entrylist')
        elist = rt.gDirectory.Get('elist')
        entry = elist.Next()
        limit.GetEntry(entry)
        limits = []
        while True:
            if entry == -1: break
            limit.GetEntry(entry)
            limits.append(refXsec*(1.e-3)*limit.limit)
            entry = elist.Next()
        if len(limits) < 6: continue
        tFile.cd()
        tFile.Close()

        if doHybridNew:
            print getFileName(mg,mchi,boxInput,model,directory,fitRegion,"HybridNew")
            tFile = rt.TFile.Open(getFileName(mg,mchi,boxInput,model,directory,fitRegion,"HybridNew"))
            limit = tFile.Get("limit")
            if limit.GetEntries() < 1: continue
            limit.Draw('>>elist','','entrylist')
            elist = rt.gDirectory.Get('elist')
            entry = elist.Next()
            limit.GetEntry(entry)
            hybridNew = 0
            while True:
                if entry == -1: break
                limit.GetEntry(entry)
                hybridNew = refXsec*(1.e-3)*limit.limit
                entry = elist.Next()
                tFile.cd()
                tFile.Close()
            limits[5] = hybridNew
            
        limits.reverse()
        print mg, mchi
        print limits
        

        haddOutput = writeXsecTree(boxInput, directory, mg, mchi, [limits[0]],[limits[1]],[limits[2]],[limits[3]],[limits[4]],[limits[5]])
        haddOutputs.append(haddOutput)

    os.system("hadd -f %s/xsecUL_%s.root %s"%(directory,boxInput," ".join(haddOutputs)))

    
