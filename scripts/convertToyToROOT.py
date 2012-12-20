from optparse import OptionParser
import ROOT as rt
import sys
    
if __name__ == '__main__':
    
    MR = rt.RooRealVar("MR", "MR", 450., 4000.)
    Rsq = rt.RooRealVar("Rsq", "Rsq", 0.03, 1.)
    dir = sys.argv[1] 
    # to add the category
    for i in range(0,2000):
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"RMRTree\");")
        tree = rt.TTree("RMRTree","RMRTree")
        filename = sys.argv[1]+"_"+str(i)+".txt"
        tree.ReadFile(filename,"MR/D:Rsq/D")
        if tree.GetEntries() <1: continue
        myfile = rt.TFile.Open("%s_%i.root" %(dir, i), "recreate")
        tree.Write()
        myfile.Close()
        del tree
	del myfile
        continue


        
        
