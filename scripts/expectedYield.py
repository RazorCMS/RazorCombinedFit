from optparse import OptionParser
import ROOT as rt
import sys
    
if __name__ == '__main__':

    sigRegions = []
    sigRegions.append(["S1", 650., 7000., 0.09, 0.50])
    sigRegions.append(["S2", 450.,  650., 0.20, 0.50])
    sigRegions.append(["S3", 350.,  450., 0.30, 0.50])

    hadSigRegions = []
    hadSigRegions.append(["hS1", 1500., 7000., 0.09, 0.50])
    hadSigRegions.append(["hS2", 1000., 1500., 0.20, 0.50])
    hadSigRegions.append(["hS3",  800., 1500., 0.30, 0.50])
    hadSigRegions.append(["hS4",  450.,  800., 0.45, 0.50])
    hadSigRegions.append(["hS5",  350.,  500., 0.49, 0.50])
    hadSigRegions.append(["hC1",  650., 7000., 0.09, 0.20])
    hadSigRegions.append(["hC2",  450., 1000., 0.20, 0.30])
    hadSigRegions.append(["hC3",  350.,  800., 0.30, 0.45])
    hadSigRegions.append(["hC4",  350.,  450., 0.45, 0.49])

    Boxes = ["Mu", "Ele", "MuMu", "MuEle", "EleEle"]
    histos = []
    for Box in Boxes:
        Regions = sigRegions
        if Box == Had: hadSigRegions = sigRegions
        for Region in Regions:
            histos.append([Box, Region, rt.TH1D("%s_%s" %(Region, Box), "%s_%s" %(Region, Box), 2000, 0., 2000.)])
    
    treeName = "RMRTree"
    argc = len(sys.argv)
    for i in range(1,argc):
        myfile = rt.TFile(sys,argv[i])
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("RooDataSet") != True: continue
        for histos in histo:
            histos[2].Fill(gdata.reduce("MR>%f" %histos[1].[0]).reduce("MR<=%f" %histos[1].[1]).reduce("Rsq>%f" %histos[1].[2]).reduce("Rsq<=%f" %histos[1].[3]))
            continue
        continue

    print "Box        Expected Range"
    # print the result and write it to out
    fileOut = rt.Tfile.Open("expectedYield.root", "recreate")
    for histos in histo:
        print "%s        %f +/- %f" %(histos[0], histos[2].GetMean(), histos[2].GetRMS())
        histos[2].Write()
    fileOut.Close()

        
        
