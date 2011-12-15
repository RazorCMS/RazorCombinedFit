from optparse import OptionParser
import ROOT as rt
import sys

if __name__ == '__main__':

    myTree = rt.TTree("myTree", "myTree")

    # define the tree structures as two structures.

    # first structure
    stringMyStruct1= "struct MyStruct1{"
    for iBinX in range(0,16):
        for iBinY in range(0,5):
            stringMyStruct1 = stringMyStruct1+"Double_t b%i_%i;" %(iBinX,iBinY)            
    rt.gROOT.ProcessLine(stringMyStruct1+"}")
    from ROOT import MyStruct1

    # read inputs
    ScaleFactor = int(sys.argv[1])
    label = sys.argv[2]
    Box = sys.argv[3]

    # bins in mR
    MRbins = [300, 350, 400, 450, 500, 550, 600, 650, 700, 800, 900, 1000, 1200, 1600, 2000, 2800, 3500]
    # bins in R^2
    Rsqbins =  [0.09, 0.16, 0.20, 0.30, 0.40, 0.50]

    # fills the bins list and associate the bins to the corresponding variables in the structure
    s1 = MyStruct1()
    for ix in range(0, len(MRbins)-1):
        for iy in range(0, len(Rsqbins)-1):
            varName = "b%i_%i" %(ix, iy) 
            branchName = "b%s_%i_%i" %(Box,ix, iy) 
            myTree.Branch(branchName, rt.AddressOf(s1,varName),'%s/D' %varName)
    
    treeName = "RMRTree"
    for i in range(4,len(sys.argv)):
        myfile = rt.TFile(sys.argv[i])
        #myfile = rt.TFile("%s_%i.root" %(sys.argv[4],i))
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("RooDataSet") != True: continue
        iBinX = 0
        iBinY = 0
        # fill the tree
        for iBinY in range(0,5):
            for iBinX in range(0,16):
                dataTMP = gdata.reduce("MR>=%f" %MRbins[iBinX]).reduce("MR<%f" %MRbins[iBinX+1]).reduce("Rsq>=%f" %Rsqbins[iBinY]).reduce("Rsq<%f" %Rsqbins[iBinY+1])
                value = setattr(s1, "b%i_%i" %(iBinX,iBinY), float(dataTMP.numEntries())/ScaleFactor)
                del dataTMP
        myTree.Fill()
        del gdata
        myfile.Close()        
        continue

    fileOut = rt.TFile.Open("%s" %label, "recreate")
    myTree.Write()
    fileOut.Close()
    
