from optparse import OptionParser
import os
import math
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from array import *
from pdfShit import *
import sys

def find68ProbRange(hToy, probVal=0.6827):
    minVal = 0.
    maxVal = 100000.
    if hToy.Integral()<=0: return hToy.GetBinCenter(hToy.GetMaximumBin()),max(minVal,0.),maxVal
    # get the bin contents
    probsList = []
    for  iX in range(1, hToy.GetNbinsX()+1):
        probsList.append(hToy.GetBinContent(iX)/hToy.Integral())
    probsList = reversed(sorted(probsList))
    prob = 0
    found = False
    range68 = 0
    counter = 0
    for prob_inc in probsList:
        counter += 1
        if prob+prob_inc >= probVal and not found:
            range68 = counter
            found = True
        prob += prob_inc
    
    mode = hToy.GetBinLowEdge(hToy.GetMaximumBin())
    #print "mode +- range68 = %i +- %i"%(mode,range68)
    return mode,range68


def getBinEvents(i, j, k, x, y, z, workspace):
    if z[k-1]==3:
        bkg = "TTj2b"
    else:
        bkg = "TTj%ib"%z[k-1]
    B = workspace.var("b_%s"%bkg).getVal()
    N = workspace.var("n_%s"%bkg).getVal()
    X0 = workspace.var("MR0_%s"%bkg).getVal()
    Y0 = workspace.var("R0_%s"%bkg).getVal()
    NTOT = workspace.var("Ntot_%s"%bkg).getVal()
    F3 = workspace.var("f3_%s"%bkg).getVal()
    
    xmin  = x[0]
    xmax  = x[-1]
    ymin  = y[0]
    ymax  = y[-1]
    total_integral = (N/rt.TMath.Power(B*N,N))*(Gfun(xmin,ymin,X0,Y0,B,N)-Gfun(xmin,ymax,X0,Y0,B,N)-Gfun(xmax,ymin,X0,Y0,B,N)+Gfun(xmax,ymax,X0,Y0,B,N))

    
    xmin  = x[i-1]
    xmax  = x[i]
    ymin  = y[j-1]
    ymax  = y[j]
    integral = (N/rt.TMath.Power(B*N,N))*(Gfun(xmin,ymin,X0,Y0,B,N)-Gfun(xmin,ymax,X0,Y0,B,N)-Gfun(xmax,ymin,X0,Y0,B,N)+Gfun(xmax,ymax,X0,Y0,B,N))

    bin_events =  NTOT*integral/total_integral
    
    if (z[k-1]==2) : 
        bin_events =  (1.-F3)*bin_events
    elif (z[k-1]==3) : 
        bin_events =  F3*bin_events

    return bin_events

def getRandomPars(fr, workspace):
    zeroIntegral = True
    randomizeAttempts = 0
    
    xmin =  workspace.var('MR').getMin()
    xmax = workspace.var('MR').getMax()
    ymin =  workspace.var('Rsq').getMin()
    ymax = workspace.var('Rsq').getMax()
    components = ['TTj1b','TTj2b','Vpj']
    componentsOn = [comp for comp in components if workspace.var('Ntot_%s'%comp).getVal()]
    #print "The components on are ", componentsOn
    while zeroIntegral:
        argList = fr.randomizePars()
        for p in RootTools.RootIterator.RootIterator(argList):
            workspace.var(p.GetName()).setVal(p.getVal())
            workspace.var(p.GetName()).setError(p.getError())
            #print "RANDOMIZE PARAMETER %s = %f +- %f"%(p.GetName(),p.getVal(),p.getError())
            # check how many error messages we have before evaluating pdfs
            errorCountBefore = rt.RooMsgService.instance().errorCount()
            #print "RooMsgService ERROR COUNT BEFORE = %i"%errorCountBefore
            # evaluate each pdf, assumed to be called "RazPDF_{component}"
            pdfname = "RazPDF"
            badPars = []
            myvars = rt.RooArgSet(workspace.var('MR'),workspace.var('Rsq'))
            for component in componentsOn:
                B = workspace.var("b_%s"%component).getVal()
                N = workspace.var("n_%s"%component).getVal()
                X0 = workspace.var("MR0_%s"%component).getVal()
                Y0 = workspace.var("R0_%s"%component).getVal()
                NTOT = workspace.var("Ntot_%s"%component).getVal()
                F3 = workspace.var("f3_%s"%component).getVal()
                
                badPars.append(N <= 0)
                badPars.append(B <= 0)
                badPars.append(X0 >= xmin)
                badPars.append(Y0 >= ymin)
                total_integral = (N/rt.TMath.Power(B*N,N))*(Gfun(xmin,ymin,X0,Y0,B,N)-Gfun(xmin,ymax,X0,Y0,B,N)-Gfun(xmax,ymin,X0,Y0,B,N)+Gfun(xmax,ymax,X0,Y0,B,N))
                badPars.append(total_integral <= 0)
                #print badPars
                # check how many error messages we have after evaluating pdfs
            zeroIntegral = any(badPars)
            if not zeroIntegral:
                for component in componentsOn:
                    pdfComp = workspace.pdf("%s_%s"%(pdfname,component))
                    pdfValV = pdfComp.getValV(myvars)
                    errorCountAfter = rt.RooMsgService.instance().errorCount()
                    #print "RooMsgService ERROR COUNT AFTER  = %i"%errorCountAfter
                    zeroIntegral = (errorCountAfter>errorCountBefore) or any(badPars)
            randomizeAttempts+=1
    return argList
def Gamma(a, x):
    return rt.TMath.Gamma(a) * rt.Math.inc_gamma_c(a,x)

def Gfun(x, y, X0, Y0, B, N):
    return Gamma(N,B*N*rt.TMath.Power((x-X0)*(y-Y0),1/N))

def getBinning(boxName, varName):
    if varName == "MR" :
        if boxName in ["MultiJet", "Jet2b"]:
            return [400, 450, 500, 550, 600, 650, 700, 800, 900, 1000,1200, 1600, 2000, 2500, 4000]
            #return [400, 450, 550, 700, 900, 1200, 1600, 2500, 4000]
        else:
            return [300, 350, 400, 450, 500, 550, 600, 650, 700, 800, 900, 1000,1200, 1600, 2000, 2500, 4000]
            #return [300, 350, 450, 550, 700, 900, 1200, 1600, 2500, 4000]
    elif varName == "Rsq" : 
        if boxName in ["MultiJet", "Jet2b"]:
            return [0.25,0.30,0.35,0.41,0.52,0.64,0.80,1.5]
            #return [0.25,0.30,0.41,0.52,0.64,0.80,1.5]
        else:
            return [0.15, 0.20, 0.25,0.30,0.35,0.41,0.52,0.64,0.80,1.5]
            #return [0.15,0.20,0.30,0.41,0.52,0.64,0.80,1.5]
    elif varName == "nBtag" :
        if boxName in ["Jet2b"]:
            return [2.,3.,4.]
        else:
            return [1.,2.,3.,4.]
            
if __name__ == '__main__':

    boxes = ["MultiJet","Jet2b","EleMultiJet","MuMultiJet","MuJet","EleJet","MuEle","EleEle","MuMu"]
    boxes = [sys.argv[1]]
    infile = rt.TFile.Open("FULLFits2012ABCD.root","READ")
    histos = {}
    histos1d = {}
    for box in boxes:
        x = array('d', getBinning(box, "MR"))
        y = array('d', getBinning(box, "Rsq"))
        z = array('d', getBinning(box, "nBtag"))
        for bkg in ["TTj1b", "TTj2b", "TTj3b", "TTj1b_shape%sTTj1bUp"%box, "TTj1b_shape%sTTj1bDown"%box, "TTj2b_shape%sTTj2bUp"%box, "TTj2b_shape%sTTj2bDown"%box, "TTj3b_shape%sTTj2bUp"%box, "TTj3b_shape%sTTj2bDown"%box]:
            histos[box,bkg] = rt.TH3D("%s_%s_3d"%(box,bkg),"%s_%s_3d"%(box,bkg),len(x)-1,x,len(y)-1,y,len(z)-1,z)
            totalbins = (len(x)-1)*(len(y)-1)*(len(z)-1)
            histos1d[box,bkg] = rt.TH1D("%s_%s"%(box,bkg),"%s_%s"%(box,bkg),totalbins, 1, totalbins+1)
        
        histos[box,"T2tt"] = rt.TH3D("%s_%s_3d"%(box,"T2tt"),"%s_%s_3d"%(box,"T2tt"),len(x)-1,x,len(y)-1,y,len(z)-1,z)
        totalbins = (len(x)-1)*(len(y)-1)*(len(z)-1)
        histos1d[box,"T2tt"] = rt.TH1D("%s_%s"%(box,"T2tt"),"%s_%s"%(box,"T2tt"),totalbins, 1, totalbins+1)
        
        histos[box,"data"] = rt.TH3D("%s_%s_3d"%(box,"data"),"%s_%s_3d"%(box,"data"),len(x)-1,x,len(y)-1,y,len(z)-1,z)
        histos1d[box,"data"] = rt.TH1D("data_obs","data_obs",totalbins, 1, totalbins+1)
    for box in boxes:
        workspace = infile.Get("%s/Box%s_workspace"%(box,box))
        data = workspace.data("RMRTree")
        fr = workspace.obj("independentFR")

            
        MR = workspace.var("MR")
        Rsq = workspace.var("Rsq")
        nBtag = workspace.var("nBtag")
        data.fillHistogram(histos[box,"data"],rt.RooArgList(MR,Rsq,nBtag))
        
        x = array('d', getBinning(box, "MR"))
        y = array('d', getBinning(box, "Rsq"))
        z = array('d', getBinning(box, "nBtag"))
        
        for bkg in ["TTj1b", "TTj2b"]:
            for i in xrange(1,len(x)):
                for j in xrange(1,len(y)):
                    for k in xrange(1, len(z)):
                        if i==1 and j==1: continue
                        bin_events = getBinEvents(i,j,k,x,y,z,workspace)
                        if (bkg.find("1b")!=-1 and z[k-1]==1) :
                            histos[box,bkg].SetBinContent(i,j,k,bin_events)
                        elif (bkg.find("2b")!=-1 and z[k-1]==2) : 
                            histos[box,bkg].SetBinContent(i,j,k,bin_events)
                        elif (bkg.find("2b")!=-1 and z[k-1]==3) : 
                            histos[box,"TTj3b"].SetBinContent(i,j,k,bin_events)

        binHistos = {}
        for i in xrange(1,len(x)):
            for j in xrange(1,len(y)):
                for k in xrange(1, len(z)):
                    if i==1 and j==1: continue
                    binMax = int(2*histos[box,"data"].GetBinContent(histos[box,"data"].GetMaximumBin()))
                    binHistos[i,j,k] = rt.TH1D("hist_%i_%i_%i"%(i,j,k),"hist_%i_%i_%i"%(i,j,k),binMax,0,binMax)
                    
        for iToy in xrange(0, 3000):
            randomPars = getRandomPars(fr, workspace)
            if iToy%50==0: print "toy #", iToy
            #for p in RootTools.RootIterator.RootIterator(randomPars):
            #    print p.GetName(), "=", p.getVal(), "+-", p.getError()
            for i in xrange(1,len(x)):
                for j in xrange(1,len(y)):
                    for k in xrange(1, len(z)):
                        if i==1 and j==1 : continue
                        bin_events = getBinEvents(i,j,k,x,y,z,workspace)
                        binHistos[i,j,k].Fill(bin_events)
                    
        for bkg in ["TTj1b", "TTj2b"]:
            for i in xrange(1,len(x)):
                for j in xrange(1,len(y)):
                    for k in xrange(1, len(z)):
                        if i==1 and j==1 : continue
                        mode, range68 = find68ProbRange(binHistos[i,j,k])
                        if (bkg.find("1b")!=-1 and z[k-1]==1) :
                            nom = histos[box,bkg].GetBinContent(i,j,k)
                            histos[box,"%s_shape%s%sUp"%(bkg,box,bkg)].SetBinContent(i,j,k,nom + range68/2.)
                            histos[box,"%s_shape%s%sDown"%(bkg,box,bkg)].SetBinContent(i,j,k,max(0.,nom - range68/2.))
                        elif (bkg.find("2b")!=-1 and z[k-1]==2) : 
                            nom = histos[box,bkg].GetBinContent(i,j,k)
                            histos[box,"%s_shape%s%sUp"%(bkg,box,bkg)].SetBinContent(i,j,k,nom + range68/2.)
                            histos[box,"%s_shape%s%sDown"%(bkg,box,bkg)].SetBinContent(i,j,k,max(0.,nom - range68/2.))
                        elif (bkg.find("2b")!=-1 and z[k-1]==3) : 
                            nom = histos[box,"TTj3b"].GetBinContent(i,j,k)
                            histos[box,"%s_shape%s%sUp"%("TTj3b",box,bkg)].SetBinContent(i,j,k,nom + range68/2.)
                            histos[box,"%s_shape%s%sDown"%("TTj3b",box,bkg)].SetBinContent(i,j,k,max(0.,nom - range68/2.))
                        
        
        
        
        sigFile = rt.TFile.Open("SMS/T2tt_MG_750.000000_MCHI_50.000000_MR300.0_R0.387298334621_%s.root"%box)
        sigHist = sigFile.Get("wHisto_pdferr_nom")
        histos[box,"T2tt"] = sigHist.Clone("%s_%s"%(box,"T2tt"))
        histos[box,"T2tt"].SetTitle("%s_%s"%(box,"T2tt"))
        lumi = 19.3 # luminosity in fb^-1
        xsec = 6.23244 # cross section in fb at 725
        xsec_err = .188796 # percent error on cross section at 725
        xsec = 5.32605 # at 740
        xsec_err = .191995 # at 740
        histos[box,"T2tt"].Scale(lumi*xsec)
        outFile = rt.TFile.Open("razor_combine_%s.root"%box,"RECREATE")

        #unroll histograms 3D -> 1D
        for index, histo in histos.iteritems():
            box, bkg = index
            histo1d = histos1d[(box,bkg)]
            totalbins = histo1d.GetNbinsX()
            newbin = 0
            for i in xrange(1,histo.GetNbinsX()+1):
                for j in xrange(1,histo.GetNbinsY()+1):
                    for k in xrange(1,histo.GetNbinsZ()+1):
                        newbin += 1
                        histo1d.SetBinContent(newbin,histo.GetBinContent(i,j,k))
            histo.Write()
            histo1d.Write()
        outFile.Close()
