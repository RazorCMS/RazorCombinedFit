from optparse import OptionParser
import ROOT as rt
import sys
    
if __name__ == '__main__':
    
    MR = rt.RooRealVar("MR", "MR", 450., 4000.)
    Rsq = rt.RooRealVar("Rsq", "Rsq", 0.03, 1.)
    dir = sys.argv[1] 
    # to add the category
    #argc = len(sys.argv)
    #argc = int(sys.argv[2]) 
    for i in range(0,2000):
        tree = rt.TTree()
        #tree.ReadFile(sys.argv[i],"MR/D:Rsq/D")
        filename = sys.argv[1]+"_"+str(i)+".txt"
        tree.ReadFile(filename,"MR/D:Rsq/D")
        if tree.GetEntries() <1: continue
        mydata =  rt.RooDataSet("RMRTree","RMRTree",tree, rt.RooArgSet(MR, Rsq))
        myfile = rt.TFile.Open("%s_%i.root" %(dir, i), "recreate")
        mydata.Write()
        myfile.Close()
        del tree
        del mydata
        continue


        
        
