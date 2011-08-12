from optparse import OptionParser
import ROOT as rt
import sys
    
if __name__ == '__main__':

    myTree = rt.TTree("myTree", "myTree")

    # THIS IS CRAZY !!!!
    rt.gROOT.ProcessLine(
        "struct MyStruct{\
        Double_t bin_0_0;\
        Double_t bin_0_1;\
        Double_t bin_0_2;\
        Double_t bin_0_3;\
        Double_t bin_0_4;\
        Double_t bin_0_5;\
        Double_t bin_1_0;\
        Double_t bin_1_1;\
        Double_t bin_1_2;\
        Double_t bin_1_3;\
        Double_t bin_1_4;\
        Double_t bin_1_5;\
        Double_t bin_2_0;\
        Double_t bin_2_1;\
        Double_t bin_2_2;\
        Double_t bin_2_3;\
        Double_t bin_2_4;\
        Double_t bin_2_5;\
        Double_t bin_3_0;\
        Double_t bin_3_1;\
        Double_t bin_3_2;\
        Double_t bin_3_3;\
        Double_t bin_3_4;\
        Double_t bin_3_5;\
        Double_t bin_4_0;\
        Double_t bin_4_1;\
        Double_t bin_4_2;\
        Double_t bin_4_3;\
        Double_t bin_4_4;\
        Double_t bin_4_5;\
        Double_t bin_5_0;\
        Double_t bin_5_1;\
        Double_t bin_5_2;\
        Double_t bin_5_3;\
        Double_t bin_5_4;\
        Double_t bin_5_5;\
        Double_t bin_6_0;\
        Double_t bin_6_1;\
        Double_t bin_6_2;\
        Double_t bin_6_3;\
        Double_t bin_6_4;\
        Double_t bin_6_5;\
        Double_t bin_7_0;\
        Double_t bin_7_1;\
        Double_t bin_7_2;\
        Double_t bin_7_3;\
        Double_t bin_7_4;\
        Double_t bin_7_5;\
        Double_t bin_8_0;\
        Double_t bin_8_1;\
        Double_t bin_8_2;\
        Double_t bin_8_3;\
        Double_t bin_8_4;\
        Double_t bin_8_5;};")
    from ROOT import MyStruct

    # read inputs
    ScaleFactor = int(sys.argv[1])
    label = sys.argv[2]
    Box = sys.argv[3]

    minMR = []
    # bins in mR
    MRbins = [300, 350, 400, 450, 650, 800, 1000, 1250, 1500, 7000]
    # bins in R^2
    Rsqbins = [0.09, 0.16, 0.20, 0.30, 0.40, 0.45, 0.50]
    # min bin in the signal region, for each bin or R^2
    # This depends on the box
    minMR = []
    if Box == "Had":    minMR = [9,5,4,5,5,2]
    if Box == "Mu":     minMR = [5,5,4,5,5,2]
    if Box == "Ele":    minMR = [5,5,4,5,5,2]
    if Box == "MuMu":   minMR = [4,4,3,1,1,1]
    if Box == "MuEle":  minMR = [4,4,3,1,1,1]
    if Box == "EleEle": minMR = [4,4,3,1,1,1]

    binList = []
    # fille the bins list and associate the bins to the corresponding variables in the structure
    s = MyStruct()
    for ix in range(0, len(MRbins)-1):
        for iy in range(0, len(Rsqbins)-1):
            myBin = ["b%s_%i_%i" %(Box,ix,iy), MRbins[ix], MRbins[ix+1], Rsqbins[iy], Rsqbins[iy+1]]
            varName = "bin_%i_%i" %(ix, iy) 
            binList.append(myBin)
            # only the signal-region bins go in the Tree
            if ix >= minMR[iy]: myTree.Branch(myBin[0], rt.AddressOf(s,varName),'%s/D' %varName)
    
    treeName = "RMRTree"
    for i in range(4,len(sys.argv)):
        print sys.argv[i]
        myfile = rt.TFile(sys.argv[i])
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("RooDataSet") != True: continue
        iBin = 0
        # fill the tree. THIS SUCKS!!!
        s.bin_0_0 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_0_1 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_0_2 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_0_3 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_0_4 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_0_5 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_1_0 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_1_1 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_1_2 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_1_3 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_1_4 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_1_5 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_2_0 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_2_1 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_2_2 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_2_3 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_2_4 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_2_5 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_3_0 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_3_1 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_3_2 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_3_3 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_3_4 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_3_5 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_4_0 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_4_1 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_4_2 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_4_3 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_4_4 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_4_5 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_5_0 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_5_1 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_5_2 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_5_3 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_5_4 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_5_5 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_6_0 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_6_1 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_6_2 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_6_3 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_6_4 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_6_5 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_7_0 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_7_1 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_7_2 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_7_3 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_7_4 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_7_5 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_8_0 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_8_1 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_8_2 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_8_3 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_8_4 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        iBin = iBin +1 
        s.bin_8_5 = float(gdata.reduce("MR>%f" %binList[iBin][1]).reduce("MR<=%f" %binList[iBin][2]).reduce("Rsq>%f" %binList[iBin][3]).reduce("Rsq<=%f" %binList[iBin][4]).numEntries()/ScaleFactor)
        myTree.Fill()
        del gdata
        myfile.Close()
        continue

    #dilepSigRegions = [["S1", 50, 0, 100], ["S2", 25, 0, 50], ["S3", 25, 0, 50]]
    #lepSigRegions = [["hS1",8, 0, 16], ["hS2", 10, 0, 20], ["hS3", 9, 0., 18],["hS4", 20, 0, 40],["hS5", 7, 0,14]]
    #hadSigRegions = [["hS1", 15, 0, 30], ["hS2", 40, 0, 80], ["hS3", 30, 0., 60], ["hS4", 30, 10, 70], ["hS5", 10, 0., 20]]

    #Regions = dilepSigRegions
    #if Box == "ELE" or  Box == "MU": Regions = lepSigRegions
    #if Box == "HAD": Regions = hadSigRegions
    
    #ws = rt.RooWorkspace("myws")
    #ws.defineSet("vars","")
    #for i in range(0, len(binList)):
    #    regionName = binList[i][0]
    #    min = float(Regions[i][2])
    #    max = float(Regions[i][3])
    #    ws.factory("b_%s[%f,%f,%f]" %(regionName, min, min, max))
    #    ws.extendSet("vars","b_%s" %regionName)
    #    ws.var("b_%s" %regionName).setBins(int(Regions[i][1]))
        

    #data = rt.RooDataSet("BKG", "BKG", myTree, ws.set("vars"))    
    #hadHistDataset = rt.RooDataHist()
    #if Box == "ELE" or  Box == "MU" or Box == "HAD":
    #    hadHistDataset = rt.RooDataHist("%sBkgData" %Box, "%sBkgData" %Box, rt.RooArgSet(ws.var("b_%s_hS1" %Box), ws.var("b_%s_hS2" %Box), ws.var("b_%s_hS3" %Box), ws.var("b_%s_hS4" %Box), ws.var("b_%s_hS5" %Box)), data)
    #else:
    #    hadHistDataset = rt.RooDataHist("%sBkgData" %Box, "%sBkgData" %Box, rt.RooArgSet(ws.var("b_%s_S1" %Box), ws.var("b_%s_S2" %Box), ws.var("b_%s_S3" %Box)), data)
    
    fileOut = rt.TFile.Open("%s" %label, "recreate")
    #data.Write()
    #hadHistDataset.Write()
    myTree.Write()
    fileOut.Close()

        
        
