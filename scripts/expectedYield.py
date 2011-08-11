from optparse import OptionParser
import ROOT as rt
import sys
    
if __name__ == '__main__':

    myTree = rt.TTree("myTree", "myTree")

    # THIS IS CRAZY !!!!
    rt.gROOT.ProcessLine(
        "struct MyStruct{\
        Double_t var1;\
        Double_t var2;\
        Double_t var3;\
        Double_t var4;\
        Double_t var5;\
        };")
    from ROOT import MyStruct

    sigRegions = []
    sigRegions.append(["S1", 650., 7000., 0.09, 0.50])
    sigRegions.append(["S2", 450.,  650., 0.20, 0.50])
    sigRegions.append(["S3", 350.,  450., 0.30, 0.50])

    lepSigRegions = []
    lepSigRegions.append(["hS1", 1500., 7000., 0.09, 0.50])
    lepSigRegions.append(["hS2", 1000., 1500., 0.20, 0.50])
    lepSigRegions.append(["hS3",  800., 1500., 0.30, 0.50])
    lepSigRegions.append(["hS4",  450.,  800., 0.45, 0.50])
    lepSigRegions.append(["hS5",  350.,  450., 0.49, 0.50])

    hadSigRegions = []
    hadSigRegions.append(["hS1", 1500., 7000., 0.16, 0.50])
    hadSigRegions.append(["hS2", 1000., 1500., 0.20, 0.50])
    hadSigRegions.append(["hS3",  800., 1500., 0.30, 0.50])
    hadSigRegions.append(["hS4",  450.,  800., 0.45, 0.50])
    hadSigRegions.append(["hS5",  400.,  450., 0.49, 0.50])

    label = sys.argv[1]
    Box = sys.argv[2]
    Regions = sigRegions
    if Box == "ELE" or  Box == "MU":
        Regions = lepSigRegions
    elif Box == "HAD":
        Regions = hadSigRegions

    s = MyStruct()
    myTree.Branch("b_"+Box+"_"+Regions[0][0], rt.AddressOf(s,'var1'),'var1/D')
    myTree.Branch("b_"+Box+"_"+Regions[1][0], rt.AddressOf(s,'var2'),'var2/D')
    myTree.Branch("b_"+Box+"_"+Regions[2][0], rt.AddressOf(s,'var3'),'var3/D')
    if Box == "ELE" or  Box == "MU" or Box == "HAD":
        myTree.Branch("b_"+Box+"_"+Regions[3][0], rt.AddressOf(s,'var4'),'var4/D')
        myTree.Branch("b_"+Box+"_"+Regions[4][0], rt.AddressOf(s,'var5'),'var5/D')
    
    treeName = "RMRTree"
    argc = len(sys.argv)
    for i in range(3,argc):
        myfile = rt.TFile(sys.argv[i])
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("RooDataSet") != True: continue
        s.var1 = float(gdata.reduce("MR>%s" %Regions[0][1]).reduce("MR<=%s" %Regions[0][2]).reduce("Rsq>%s" %Regions[0][3]).reduce("Rsq<=%s" %Regions[0][4]).numEntries())
        s.var2 = float(gdata.reduce("MR>%s" %Regions[1][1]).reduce("MR<=%s" %Regions[1][2]).reduce("Rsq>%s" %Regions[1][3]).reduce("Rsq<=%s" %Regions[1][4]).numEntries())
        s.var3 = float(gdata.reduce("MR>%s" %Regions[2][1]).reduce("MR<=%s" %Regions[2][2]).reduce("Rsq>%s" %Regions[2][3]).reduce("Rsq<=%s" %Regions[2][4]).numEntries())
        if Box == "ELE" or  Box == "MU" or Box == "HAD":
            s.var4 = float(gdata.reduce("MR>%s" %Regions[3][1]).reduce("MR<=%s" %Regions[3][2]).reduce("Rsq>%s" %Regions[3][3]).reduce("Rsq<=%s" %Regions[3][4]).numEntries())
            s.var5 = float(gdata.reduce("MR>%s" %Regions[4][1]).reduce("MR<=%s" %Regions[4][2]).reduce("Rsq>%s" %Regions[4][3]).reduce("Rsq<=%s" %Regions[4][4]).numEntries())
        myTree.Fill()
        del gdata
        myfile.Close()
        continue

    dilepSigRegions = [["S1", 50, 0, 100], ["S2", 25, 0, 50], ["S3", 25, 0, 50]]
    lepSigRegions = [["hS1",8, 0, 16], ["hS2", 10, 0, 20], ["hS3", 9, 0., 18],["hS4", 20, 0, 40],["hS5", 7, 0,14]]
    hadSigRegions = [["hS1", 15, 0, 30], ["hS2", 40, 0, 80], ["hS3", 30, 0., 60], ["hS4", 30, 10, 70], ["hS5", 10, 0., 20]]

    Regions = dilepSigRegions
    if Box == "ELE" or  Box == "MU": Regions = lepSigRegions
    if Box == "HAD": Regions = hadSigRegions
    
    ws = rt.RooWorkspace("myws")
    ws.defineSet("vars","")
    for i in range(0, len(Regions)):
        regionName = Box+"_"+Regions[i][0]
        min = float(Regions[i][2])
        max = float(Regions[i][3])
        ws.factory("b_%s[%f,%f,%f]" %(regionName, min, min, max))
        ws.extendSet("vars","b_%s" %regionName)
        ws.var("b_%s" %regionName).setBins(int(Regions[i][1]))
        

    data = rt.RooDataSet("BKG", "BKG", myTree, ws.set("vars"))    
    hadHistDataset = rt.RooDataHist()
    if Box == "ELE" or  Box == "MU" or Box == "HAD":
        hadHistDataset = rt.RooDataHist("%sBkgData" %Box, "%sBkgData" %Box, rt.RooArgSet(ws.var("b_%s_hS1" %Box), ws.var("b_%s_hS2" %Box), ws.var("b_%s_hS3" %Box), ws.var("b_%s_hS4" %Box), ws.var("b_%s_hS5" %Box)), data)
    else:
        hadHistDataset = rt.RooDataHist("%sBkgData" %Box, "%sBkgData" %Box, rt.RooArgSet(ws.var("b_%s_S1" %Box), ws.var("b_%s_S2" %Box), ws.var("b_%s_S3" %Box)), data)
    
    fileOut = rt.TFile.Open("%s" %label, "recreate")
    data.Write()
    hadHistDataset.Write()
    fileOut.Close()

        
        
