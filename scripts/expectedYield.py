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
    hadSigRegions.append(["hS5",  350.,  450., 0.49, 0.50])
    #hadSigRegions.append(["hC1",  650., 7000., 0.09, 0.20])
    #hadSigRegions.append(["hC2",  450., 1000., 0.20, 0.30])
    #hadSigRegions.append(["hC3",  350.,  800., 0.30, 0.45])
    #hadSigRegions.append(["hC4",  350.,  450., 0.45, 0.49])

    Box = sys.argv[1]
    Regions = sigRegions
    if Box == "Had" or  Box == "Ele" or  Box == "Mu": Regions = hadSigRegions
    histos = []
    for Region in Regions:
        if Region[0].find("hS") != -1:
            histos.append([Box, Region, rt.TH1D("%s_%s" %(Region[0], Box), "%s_%s" %(Region[0], Box), 80, 0., 80.)])
        else:
            histos.append([Box, Region, rt.TH1D("%s_%s" %(Region[0], Box), "%s_%s" %(Region[0], Box), 1000, 0., 1000.)])
            
    treeName = "RMRTree"
    argc = len(sys.argv)
    for i in range(2,argc):
        myfile = rt.TFile(sys.argv[i])
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("RooDataSet") != True: continue
        for histo in histos:
            histo[2].Fill(gdata.reduce("MR>%s" %histo[1][1]).reduce("MR<=%s" %histo[1][2]).reduce("Rsq>%s" %histo[1][3]).reduce("Rsq<=%s" %histo[1][4]).numEntries())
            continue
        continue

    print "Box        Expected Range"
    # print the result and write it to out
    fileOut = rt.TFile.Open("expectedYield_%s.root" %Box, "recreate")
    for histo in histos:
        print "%s_%s        %f +/- %f" %(histo[1][0], histo[0], histo[2].GetMean(), histo[2].GetRMS())
        histo[2].Write()
    fileOut.Close()

        
        
