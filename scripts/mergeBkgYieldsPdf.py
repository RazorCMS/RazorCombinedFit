import ROOT as rt
import sys

dilepSigRegions = [["S1", 50, 0, 100], ["S2", 25, 0, 50], ["S3", 25, 0, 50]]
lepSigRegions = [["hS1",8, 0, 16], ["hS2", 10, 0, 20], ["hS3", 9, 0., 18],["hS4", 20, 0, 40],["hS5", 7, 0,14]]
hadSigRegions = [["hS1", 15, 0, 30], ["hS2", 40, 0, 80], ["hS3", 30, 0., 60], ["hS4", 30, 10, 70], ["hS5", 10, 0., 20]]

Box = sys.argv[1]

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
                                                    
# get the roodataset
data = rt.RooDataSet("BKG", "BKG", ws.set("vars"))
for i in range(2,len(sys.argv)):
    myFile = rt.TFile.Open(sys.argv[i])
    data.append(myFile.Get("BKG"))
    #hadHistDataset.add(myFile.Get("%sBkgData" %Box))
    myFile.Close()

# create the roohistdataset and the roohistpdf
hadBkgPdf = rt.RooHistPdf()
hadHistDataset = rt.RooDataHist()
if Box == "ELE" or  Box == "MU" or Box == "HAD":
    hadHistDataset = rt.RooDataHist("%sBkgData" %Box, "%sBkgData" %Box, rt.RooArgSet(ws.var("b_%s_hS1" %Box), ws.var("b_%s_hS2" %Box), ws.var("b_%s_hS3" %Box), ws.var("b_%s_hS4" %Box), ws.var("b_%s_hS5" %Box)), data)
    hadBkgPdf = rt.RooHistPdf("%sBkgPdf" %Box, "%sBkgPdf" %Box, rt.RooArgSet(ws.var("b_%s_hS1" %Box), ws.var("b_%s_hS2" %Box), ws.var("b_%s_hS3" %Box), ws.var("b_%s_hS4" %Box), ws.var("b_%s_hS5" %Box)), hadHistDataset)
else:
    hadHistDataset = rt.RooDataHist("%sBkgData" %Box, "%sBkgData" %Box, rt.RooArgSet(ws.var("b_%s_S1" %Box), ws.var("b_%s_S2" %Box), ws.var("b_%s_S3" %Box)), data)
    hadBkgPdf = rt.RooHistPdf("%sBkgPdf" %Box, "%sBkgPdf" %Box, rt.RooArgSet(ws.var("b_%s_S1" %Box), ws.var("b_%s_S2" %Box), ws.var("b_%s_S3" %Box)), hadHistDataset)

myOutFile = rt.TFile.Open("bkg_%s.root" %Box,"recreate")
data.Write()
hadHistDataset.Write()
hadBkgPdf.Write()
myOutFile.Close()
