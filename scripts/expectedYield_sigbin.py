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

    if Box == "TauTau" or Box == "Had":
        MRbins = [400.0, 450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 800, 900, 1000, 1200, 1600, 2000, 2600, 4500.0]
        Rsqbins = [0.18, 0.21, 0.24, 0.27, 0.3, 0.35, 0.4, 0.5, 0.65, 0.80, 1.5]
    else:
        MRbins = [300, 350, 400, 450, 500, 550, 600, 700, 800, 1000, 1200, 1600, 2500, 4500]
        Rsqbins = [0.11, 0.13, 0.15, 0.18, 0.21, 0.24, 0.27, 0.3, 0.35, 0.4, 0.5, 0.65, 0.8, 1.5]

    #MRbins = [400.0, 450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 800, 900, 1000, 1200, 1600, 2000, 2600, 4500.0]
    #Rsqbins = [0.18, 0.21, 0.24, 0.27, 0.3, 0.35, 0.4, 0.5, 0.65, 0.80, 1.5]

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
    for i in range(4,len(sys.argv)):
        myfile = rt.TFile(sys.argv[i])
        #myfile = rt.TFile("%s_%i.root" %(sys.argv[4],i))
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

    fileOut = rt.TFile.Open("%s" %label, "recreate")
    myTree.Write()
    fileOut.Close()
    
