from optparse import OptionParser
import ROOT as rt
import sys
    
if __name__ == '__main__':
    
    MR = rt.RooRealVar("MR", "MR", 350., 2500.)
    Rsq = rt.RooRealVar("Rsq", "Rsq", 0.11, 1.5)
    nBtag = rt.RooRealVar("nBtag", "nBtag", 1.0, 5.0)
    dir = sys.argv[1] 
    # to add the category
    for i in range(0,3225):
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"RMRTree\");")
        tree = rt.TTree("RMRTree","RMRTree")
        filename = sys.argv[1]+"_"+str(i)+".txt"
        tree.ReadFile(filename,"MR/D:Rsq/D:nBtag/D")
        if tree.GetEntries() <1: continue
        myfile = rt.TFile.Open("%s_%i.root" %(dir, i), "recreate")
        tree.Write()
        myfile.Close()
        del tree
	del myfile
        continue


        
        
