from optparse import OptionParser
import ROOT as rt
from array import *
import sys

def find68ProbRange(hToy):
    # get the bin contents
    probsList = []
    for  i in range(1, hToy.GetNbinsX()):
        probsList.append(hToy.GetBinContent(i)/hToy.Integral())
    probsList.sort()
    probsList.reverse()
    prob = 0
    prob68 = 0
    found = False
    for i in range(0,len(probsList)):
        prob = prob + probsList[i]
        if prob >= 0.68 and not found:
            prob68 = probsList[i]
            found = True

    foundMin = False
    foundMax = False
    for  i in range(0, hToy.GetNbinsX()):
        if not foundMin and hToy.GetBinContent(i+1) >= prob68:
            minVal = hToy.GetBinCenter(i+1)
            foundMin = True
        if not foundMax and hToy.GetBinContent(hToy.GetNbinsX()-i) >= prob68:
            maxVal = hToy.GetBinCenter(hToy.GetNbinsX()-i)
            foundMax = True
    return minVal,maxVal

def getPValue(n, hToy):
    # find the probability of the bin corresponding to the observed n
    Prob_n = hToy.GetBinContent(hToy.FindBin(n))
    Prob = 0
    for i in range(1, hToy.GetNbinsX()+1):
        if hToy.GetBinContent(i)< Prob_n: Prob += hToy.GetBinContent(i)
    Prob = Prob/hToy.Integral()
    return Prob
    
if __name__ == '__main__':
    Box = sys.argv[1]
    fileName = sys.argv[2]
    datafileName = sys.argv[3]

    # the "temperature" plot for the pvalue
    h =  rt.TH2D("h","h", 10, 300, 2000., 7, 0.09, 0.5);
    mybins = sorted([300.,350.,400.,450.,650.,800.,1000.,1250.,1500.,2000.])
    x = array("d",mybins)
    h.GetXaxis().Set(len(x)-1,x)
    mybinsy = sorted([0.09, 0.16, 0.2, 0.3, 0.4, 0.45, 0.5])
    y = array("d",mybinsy)
    h.GetYaxis().Set(len(y)-1,y)
    
    h.GetXaxis().SetTitle("M_{R}[GeV]")
    h.GetYaxis().SetTitle("R^{2}")
    h.SetMaximum(1.)
    h.SetMinimum(0.)
    
    # bins in mR
    MRbins = [300, 350, 400, 450, 650, 800, 1000, 1250, 1500, 7000]
    # bins in R^2
    Rsqbins = [0.09, 0.16, 0.20, 0.30, 0.40, 0.45, 0.50]
    # min bin in the signal region, for each bin or R^2
    # This depends on the box
    minMR = []
    if Box == "Had":    minMR = [8,5,4,3,3,2]
    if Box == "Mu":     minMR = [5,5,4,3,3,2]
    if Box == "Ele":    minMR = [5,5,4,3,3,2]
    if Box == "MuMu":   minMR = [4,4,3,1,1,1]
    if Box == "MuEle":  minMR = [4,4,3,1,1,1]
    if Box == "EleEle": minMR = [4,4,3,1,1,1]
    
    binList = []

    fileIn = rt.TFile.Open(fileName)
    myTree = fileIn.Get("myTree")
    dataFile = rt.TFile.Open(datafileName)
    alldata = dataFile.Get("RMRTree")

    fileOUT = rt.TFile.Open("pvalue_%s.root" %Box, "recreate")

    print "%s Box & Observed & Predicted 68 Prob. & \"p-value\" \\\\" %Box
    # loop over Bins
    for ix in range(0, len(MRbins)-1):
        for iy in range(0, len(Rsqbins)-1):
            if ix < minMR[iy]: continue
            varName = "b%s_%i_%i" %(Box, ix, iy) 
            # make an histogram of the expected yield
            myhisto = rt.TH1D("h_%s" %varName, "h_%s" %varName, 2500, 0., 2500.)
            myTree.Project("h_"+varName, varName)
            if myhisto.GetEntries() != 0: 
                # get the observed number of events
                data = alldata.reduce("MR> %f && MR< %f && Rsq > %f && Rsq < %f" %(MRbins[ix], MRbins[ix+1], Rsqbins[iy], Rsqbins[iy+1]))
                nObs = data.numEntries()
                pval = getPValue(nObs, myhisto)
                nsigma = getSigma(nObs, myhisto)
                h.SetBinContent(ix+1, iy+1, pval)
                hNS.SetBinContent(ix+1, iy+1, nsigma)
                rangeMin,rangeMax = find68ProbRange(myhisto)
                if pval >0.99: pval = 0.99 
                print "%s & %i & $[%i, %i]$ & 0.%i \\\\" %(varName, nObs, int(rangeMin), int(rangeMax), int(pval*100))
                myhisto.GetXaxis().SetRangeUser(0., rangeMax*2.)
                myhisto.Write()
                del data
    h.Write()
    hNS.Write()
    fileOUT.Close()

    xLines = []
    yLines = []

    for i in range(0,5):
        xLines.append(rt.TLine(x[0], y[i+1], x[9], y[i+1]))
        xLines[i].SetLineStyle(2);
        xLines[i].SetLineColor(rt.kBlack);
        

    for i in range(0,8):
        yLines.append(rt.TLine(x[i+1], y[0], x[i+1], y[6]))
        yLines[i].SetLineStyle(2)
        yLines[i].SetLineColor(rt.kBlack)
                      
    c1 = rt.TCanvas("c1","c1", 900, 600)
    h.Draw("colz")
    for i in range(0,5): xLines[i].Draw()
    for i in range(0,8): yLines[i].Draw()
    c1.SaveAs("pValue_%s.C" %Box)
    c1.SaveAs("pValue_%s.pdf" %Box)

    c2 = rt.TCanvas("c2","c2", 900, 600)
    colors = []
    takeOut = [0,4,7,9,10]
    #add the red (darker to lighter)
    for i in range(0,6): colors.append(rt.kRed-takeOut[i])
    # add the white
    colors.append(rt.kWhite)
    #add the blue (lighter to darker)
    for i in range(0,6): colors.append(rt.kBlue-5+takeOut[i])
    rt.gStyle.SetPalette(11,colors)
    hNS.Draw("colz")
    hNS.SetMaximum(5.5)
    hNS.SetMinimum(-5.5)
    for i in range(0,12): hNS.SetContoueLevel(i,-5.5 +i*11.)
    for i in range(0,5): xLines[i].Draw()
    for i in range(0,8): yLines[i].Draw()
    c1.SaveAs("nSigma_%s.C" %Box)
    c1.SaveAs("nSigma_%s.pdf" %Box)
