from optparse import OptionParser
import ROOT as rt
import sys

if __name__ == '__main__':

    myTree = rt.TTree("myTree", "myTree")

    # bins in mR
    MRbins = [300, 350, 400, 450, 650, 800, 1000, 1250, 1500, 7000]
    # bins in R^2
    Rsqbins = [0.09, 0.16, 0.20, 0.30, 0.40, 0.45, 0.50]

    # create magic string
    magicString= "struct MyStruct{"
    for ix in range(0, len(MRbins)-1):
        for iy in range(0, len(Rsqbins)-1):
            magicString += "Double_t bin_%i_%i;"%(ix,iy)
    magicString += "};"
    #print magicString

    # THIS IS CRAZY !!!!
    rt.gROOT.ProcessLine(magicString)
    from ROOT import MyStruct

    # read inputs
    ScaleFactor = int(sys.argv[1])
    label = sys.argv[2]
    Box = sys.argv[3]

    # associate the bins to the corresponding variables in the structure
    s = MyStruct()
    for ix in range(0, len(MRbins)-1):
        for iy in range(0, len(Rsqbins)-1):
            myBin = ["b%s_%i_%i" %(Box,ix,iy), MRbins[ix], MRbins[ix+1], Rsqbins[iy], Rsqbins[iy+1]]
            varName = "bin_%i_%i" %(ix, iy) 
            # only the signal-region bins go in the Tree
            myTree.Branch(myBin[0], rt.AddressOf(s,varName),'%s/D' %varName)
    
    treeName = "RMRTree"
    for i in range(4,len(sys.argv)):
        print "processing file: ", sys.argv[i]
        myfile = rt.TFile(sys.argv[i])
        #myfile = rt.TFile("%s_%i.root" %(sys.argv[4],i))
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("RooDataSet") != True: continue
        for ix in range(0, len(MRbins)-1):
            for iy in range(0, len(Rsqbins)-1):
                # fill the tree. THIS SUCKS!!!
                dataTMP = gdata.reduce("MR>%f && MR<=%f && Rsq>%f && Rsq<=%f" % (MRbins[ix],MRbins[ix+1], Rsqbins[iy],Rsqbins[iy+1]))
                setattr(s,"bin_%i_%i"%(ix,iy), float(dataTMP.numEntries())/ScaleFactor )
                del dataTMP
        myTree.Fill()
        del gdata
        myfile.Close()        
        continue

    
    fileOut = rt.TFile.Open("%s" %label, "recreate")
    #data.Write()
    #hadHistDataset.Write()
    myTree.Write()
    fileOut.Close()

        
        
