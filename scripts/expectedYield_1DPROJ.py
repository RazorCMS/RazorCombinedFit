from optparse import OptionParser
import ROOT as rt
import sys
from array import *

if __name__ == '__main__':

    myTree = rt.TTree("myTree", "myTree")

    # define the tree structures as two structures.

    # read inputs
    ScaleFactor = int(sys.argv[1])
    label = sys.argv[2]
    Box = sys.argv[3]

    # bins in mR
    MRbins = [450, 500, 550, 650, 800, 1000, 1500, 2000, 2800, 3500]
    #if Box == "Had":
    #MRbins = [500, 550, 650, 800, 1000, 1500, 2000, 2800, 3500]
    RsqMin = 0.3
    x = array("d",MRbins)

    # first structure
    stringMyStruct1= "struct MyStruct1{"
    for iBinX in range(0,len(MRbins)-1):
        stringMyStruct1 = stringMyStruct1+"Double_t b%i;" %(iBinX)            
    rt.gROOT.ProcessLine(stringMyStruct1+"}")
    from ROOT import MyStruct1

    # fills the bins list and associate the bins to the corresponding variables in the structure
    s1 = MyStruct1()
    for ix in range(0, len(MRbins)-1):
        varName = "b%i" %(ix) 
        branchName = "b%s_%i" %(Box,ix) 
        myTree.Branch(branchName, rt.AddressOf(s1,varName),'%s/D' %varName)

    treeName = "RMRTree"
    for i in range(4,len(sys.argv)):
        myfile = rt.TFile(sys.argv[i])
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("RooDataSet") != True: continue
        # fill the tree
        for iBinX in range(0,len(MRbins)-1):
            dataTMP = gdata.reduce("MR>=%f && MR<%f && Rsq>=%f && Rsq<0.5" %(MRbins[iBinX],MRbins[iBinX+1],RsqMin))
            value = setattr(s1, "b%i" %(iBinX), float(dataTMP.numEntries())/ScaleFactor)
            del dataTMP
        myTree.Fill()
        del gdata
        myfile.Close()        
        continue

    fileOut = rt.TFile.Open("%s" %label, "recreate")
    myTree.Write()
    fileOut.Close()
        
