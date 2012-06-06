import os
import ROOT as rt
import sys

def CalcUL(h, CL):
    prob = 0.
    probOLD = 0
    integralval = h.Integral() 
    for i in range(1,h.GetXaxis().GetNbins()+1):
        prob += h.GetBinContent(i)/integralval
        if probOLD < CL and prob > CL: return h.GetXaxis().GetBinCenter(i)
        probOLD = prob
    return 0.

def fileIN(hname):
    f = rt.TFile.Open(hname)
    h_i = f.Get("Histo").Clone()
    h_i.SetName(hname.replace(" ","").replace("outFile_","").replace(".root",""))
    return (h_i,f)

def ObservedYield(filename, hname):
    f = rt.TFile.Open(filename)
    alldata = f.Get("RMRTree")
    cuts = hname.split("_")
    y = alldata.reduce("MR>= %s && MR < %s && Rsq >= %s && Rsq < %s" %(cuts[0], cuts[1], cuts[2],cuts[3])).numEntries()
    f.Close()
    return y

def getLimit(sigeff, output):

    e = map(float,sigeff)
    h = [fileIN("outFile_3000_4000_0.0300_0.0375.root"),
         fileIN("outFile_ 800_4000_0.0375_0.0900.root"),
         fileIN("outFile_ 650_4000_0.0900_0.2000.root"),
         fileIN("outFile_ 600_4000_0.2000_0.3000.root"),
         fileIN("outFile_ 550_4000_0.3000_0.5000.root"),
         fileIN("outFile_ 500_4000_0.5000_1.0000.root")]

    n = []
    for i in range(0,6): n.append(ObservedYield("/Users/wreece/Documents/workspace/RazorCombinedFit/MultiJet-Run2011A-05Aug2011-v1-wreece_130312_MR500.0_R0.173205080757_BJet.root",h[i][0].GetName()))

    ibin = 100
    minbin = 0.0
    maxbin = 0.1
    lumi = 4980.
    xsecH = rt.TH1D("xsecH", "xsecH", ibin, minbin, maxbin)
    for i in range(1,101):
        xsec_val = minbin + (i-0.5)/ibin*(maxbin-minbin)
        prob = 1.
        for j in range(0,len(e)):
            s_i = xsec_val*lumi*e[j]
            prob = prob*h[j][0].GetBinContent(h[j][0].FindBin(max(n[j]-s_i,0.)))
        xsecH.SetBinContent(i,prob)
    outFile = rt.TFile(output, "recreate")
    xsec = CalcUL(xsecH, 0.95)
    xsecH.Write()
    outFile.Close()
    
    for hh in h:
        hh[1].Close()
    
    return xsec


if __name__ == '__main__':
    
    print "Xsec UL: %f pb-1 @95 Prob." % getLimit(sys.argv[1:],'outProb.root')
