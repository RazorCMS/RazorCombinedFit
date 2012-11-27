from optparse import OptionParser
import ROOT as rt
import sys
    
if __name__ == '__main__':
    
    MR = rt.RooRealVar("MR", "MR", 350., 2500.)
    Rsq = rt.RooRealVar("Rsq", "Rsq", 0.11, 1.5)
    dir = sys.argv[1] 
    # to add the category
    for i in range(0,2000):
        tree = rt.TTree()
        filename = sys.argv[1]+"_"+str(i)+".txt"
        tree.ReadFile(filename,"MR/D:Rsq/D")
        if tree.GetEntries() <1: continue
        myfile = rt.TFile.Open("%s_%i.root" %(dir, i), "recreate")
        tree.SetName("RMRTree")
        tree.Write()
        myfile.Close()
	tree.Delete()
	myfile.Delete()
        del tree
	del myfile
        continue


        
        
