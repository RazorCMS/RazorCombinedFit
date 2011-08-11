from optparse import OptionParser
import ROOT as rt
import sys
    
if __name__ == '__main__':
    
    MR = rt.RooRealVar("MR", "MR", 300., 7000.)
    Rsq = rt.RooRealVar("Rsq", "Rsq", 0.09, 0.5)
    dir = sys.argv[1] 
    # to add the category
    argc = len(sys.argv)
    for i in range(2,argc):
        tree = rt.TTree()
        tree.ReadFile(sys.argv[i],"MR/D:Rsq/D")
        if tree.GetEntries() <1: continue
        mydata =  rt.RooDataSet("RMRTree","RMRTree",tree, rt.RooArgSet(MR, Rsq))
        myfile = rt.TFile.Open("%s_%i.root" %(dir, i), "recreate")
        mydata.Write()
        myfile.Close()
        continue


        
        
