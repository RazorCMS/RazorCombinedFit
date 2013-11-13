from optparse import OptionParser
import ROOT as rt
import sys
import random
from array import *
import makeBluePlot
import os

def getTree2D(MRbins,Rsqbins,listfileName):
    x = array("d",MRbins)
    y = array("d",Rsqbins)
    # first structure
    stringMyStruct1= "struct MyStruct1{"
    for iBinX in range(0,len(MRbins)-1):
        for iBinY in range(0,len(Rsqbins)-1):
            stringMyStruct1 = stringMyStruct1+"float b%i_%i;" %(iBinX,iBinY)
    print stringMyStruct1
    rt.gROOT.ProcessLine(stringMyStruct1+"}")
    from ROOT import MyStruct1

    # fills the bins list and associate the bins to the corresponding variables in the structure
    s1 = MyStruct1()
    for ix in range(0, len(MRbins)-1):
        for iy in range(0, len(Rsqbins)-1):
            varName = "b%i_%i" %(ix, iy) 
            branchName = "b%i_%i" %(ix, iy) 
            myTree.Branch(branchName, rt.AddressOf(s1,varName),'%s/F' %varName)
    
    treeName = "RMRTree"
    
    listfile = open(listfileName)
    for line in listfile:
        filename = line.split('\n')[0]
        myfile = rt.TFile(filename)
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("TTree") != True: continue
        h =  rt.TH2D("h","h", len(MRbins)-1, x, len(Rsqbins)-1, y)
        gdata.Project("h", "Rsq:MR")
        iBinX = 0
        iBinY = 0
        # fill the tree
        for iBinY in range(0,len(Rsqbins)-1):
            for iBinX in range(0,len(MRbins)-1):
                value = setattr(s1, "b%i_%i" %(iBinX,iBinY), float(h.GetBinContent(iBinX+1, iBinY+1)/ScaleFactor))
        myTree.Fill()
        del gdata
        del h
        myfile.Close()        
        continue
    listfile.close()
    return myTree


def getTree3D(MRbins,Rsqbins,nBtagbins,listfileName):
    x = array("d",MRbins)
    y = array("d",Rsqbins)
    z = array("d",nBtagbins)
    # first structure
    stringMyStruct1= "{struct MyStruct1{"
    for iBinX in range(0,len(MRbins)-1):
        for iBinY in range(0,len(Rsqbins)-1):
            for iBinZ in range(0,len(nBtagbins)-1):
                BinZVal = nBtagbins[iBinZ]
                stringMyStruct1 = stringMyStruct1+"float b%i_%i_%i;" %(iBinX,iBinY,BinZVal)
    print stringMyStruct1+"};}"
    rando = random.randint(1,999999)
    tempMacro = open("tempMacro_%d.C"%rando,"w")
    tempMacro.write(stringMyStruct1+"};}")
    tempMacro.close()
    rt.gROOT.Macro("tempMacro_%d.C"%rando)
    #rt.gROOT.ProcessLine(stringMyStruct1+"};")
    from ROOT import MyStruct1

    # fills the bins list and associate the bins to the corresponding variables in the structure
    s1 = MyStruct1()
    for ix in range(0, len(MRbins)-1):
        for iy in range(0, len(Rsqbins)-1):
            for iz in range(0,len(nBtagbins)-1):
                zVal = nBtagbins[iz]
                varName = "b%i_%i_%i" %(ix, iy, zVal) 
                branchName = "b%i_%i_%i" %(ix, iy, zVal) 
                myTree.Branch(branchName, rt.AddressOf(s1,varName),'%s/F' %varName)
    
    treeName = "RMRTree"
    
    listfile = open(listfileName)
    for line in listfile:
        filename = line.split('\n')[0]
        myfile = rt.TFile(filename)
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("TTree") != True: continue
        h =  rt.TH3D("h","h", len(MRbins)-1, x, len(Rsqbins)-1, y, len(nBtagbins)-1, z)
        gdata.Project("h", "nBtag:Rsq:MR")
        iBinX = 0
        iBinY = 0
        iBinZ = 0
        # fill the tree
        for iBinY in range(0,len(Rsqbins)-1):
            for iBinX in range(0,len(MRbins)-1):
                for iBinZ in range(0,len(nBtagbins)-1):
                    BinZVal = nBtagbins[iBinZ]
                    value = setattr(s1, "b%i_%i_%i" %(iBinX,iBinY,BinZVal), float(h.GetBinContent(iBinX+1, iBinY+1, iBinZ+1)/ScaleFactor))
        myTree.Fill()
        del gdata
        del h
        myfile.Close()        
        continue
    listfile.close()
    os.system("rm tempMacro_%d.C"%rando)
    return myTree


if __name__ == '__main__':
    # read inputs
    ScaleFactor = int(sys.argv[1])
    label = sys.argv[2]
    Box = sys.argv[3]
    listfileName = sys.argv[4]
    noBtag = False
    fit3D = False
    
    # output file
    fileOut = rt.TFile.Open("%s" %label, "recreate")
    # define tree
    myTree = rt.TTree("myTree", "myTree")
    
    for i in range(5,len(sys.argv)):
        if sys.argv[i] == "--noBtag": noBtag = True
        if sys.argv[i] == "--3D": fit3D = True

    #MRbins, Rsqbins, nBtagbins = makeBluePlot.Binning(Box, noBtag)
    from RazorBox import getBinning
    MRbins    = getBinning(Box, "MR"   , "Btag")
    Rsqbins   = getBinning(Box, "Rsq"  , "Btag")
    nBtagbins = getBinning(Box, "nBtag", "Btag")
   
    if fit3D:
        myTree = getTree3D(MRbins,Rsqbins,nBtagbins,listfileName)
    else:
        myTree = getTree2D(MRbins,Rsqbins,listfileName)
        
    fileOut.cd()
    myTree.Write()
    fileOut.Close()
    
