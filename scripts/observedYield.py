from optparse import OptionParser
import ROOT as rt
import sys
    
if __name__ == '__main__':

    sigRegions = []
    sigRegions.append(["S1", 650., 7000., 0.09, 0.50])
    sigRegions.append(["S2", 450.,  650., 0.20, 0.50])
    sigRegions.append(["S3", 350.,  450., 0.30, 0.50])

    hadSigRegions = []
    hadSigRegions.append(["hS1", 1500., 7000., 0.16, 0.50])
    hadSigRegions.append(["hS2", 1000., 1500., 0.20, 0.50])
    hadSigRegions.append(["hS3",  800., 1500., 0.30, 0.50])
    hadSigRegions.append(["hS4",  450.,  800., 0.45, 0.50])
    hadSigRegions.append(["hS5",  400.,  450., 0.49, 0.50])
    #hadSigRegions.append(["hC1",  650., 7000., 0.09, 0.20])
    #hadSigRegions.append(["hC2",  450., 1000., 0.20, 0.30])
    #hadSigRegions.append(["hC3",  350.,  800., 0.30, 0.45])
    #hadSigRegions.append(["hC4",  350.,  450., 0.45, 0.49])

    lepSigRegions = []
    lepSigRegions.append(["hS1", 1500., 7000., 0.09, 0.50])
    lepSigRegions.append(["hS2", 1000., 1500., 0.20, 0.50])
    lepSigRegions.append(["hS3",  800., 1500., 0.30, 0.50])
    lepSigRegions.append(["hS4",  450.,  800., 0.45, 0.50])
    lepSigRegions.append(["hS5",  350.,  450., 0.49, 0.50])
    #lepSigRegions.append(["hC1",  650., 7000., 0.09, 0.20])
    #lepSigRegions.append(["hC2",  450., 1000., 0.20, 0.30])
    #lepSigRegions.append(["hC3",  350.,  800., 0.30, 0.45])
    #lepSigRegions.append(["hC4",  350.,  450., 0.45, 0.49])
    
    myfile = rt.TFile.Open(sys.argv[2])
    Box = sys.argv[1]
    Regions = sigRegions
    if Box == "Had": Regions = hadSigRegions
    if Box == "Ele" or  Box == "Mu": Regions = lepSigRegions

    tree = myfile.Get("RMRTree")
    for region in Regions:
        nEv = tree.reduce("MR > %f && MR < %f && Rsq > %f && Rsq < %f" % (region[1], region[2], region[3], region[4])).numEntries()
        print "%s_%s  %i" %(region[0], Box, nEv)
                          
        
        
