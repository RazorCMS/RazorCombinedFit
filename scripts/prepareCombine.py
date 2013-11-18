from optparse import OptionParser
import os
import math
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from array import *
from pdfShit import *
import sys


def rebin3d(oldhisto, x,y,z, MRcut, Rsqcut):
    newhisto = rt.TH3D(oldhisto.GetName(),oldhisto.GetTitle(),len(x)-1,x,len(y)-1,y,len(z)-1,z)
    for i in range(1,oldhisto.GetNbinsX()+1):
        for j in range(1,oldhisto.GetNbinsY()+1):
            for k in range(1,oldhisto.GetNbinsZ()+1):
                xold = oldhisto.GetXaxis().GetBinCenter(i)
                yold = oldhisto.GetYaxis().GetBinCenter(j)
                zold = oldhisto.GetZaxis().GetBinCenter(k)
                if xold < MRcut and  yold < Rsqcut: continue
                oldbincontent = oldhisto.GetBinContent(i,j,k)
                newhisto.Fill(xold, yold, zold, max(0.,oldbincontent))                
    return newhisto
    
def writeDataCard(box,model,txtfileName,bkgs,param_names,histos1d,workspace):
        txtfile = open(txtfileName,"w")
        txtfile.write("imax 1 number of channels\n")
        if box in ["MuEle","MuMu","EleEle"]:
            txtfile.write("jmax 1 number of backgrounds\n")
            txtfile.write("kmax 13 number of nuisnace parameters\n")
        elif box=="Jet2b":
            txtfile.write("jmax 2 number of backgrounds\n")
            txtfile.write("kmax 15 number of nuisnace parameters\n")
        else:
            txtfile.write("jmax 3 number of backgrounds\n")
            txtfile.write("kmax 21 number of nuisnace parameters\n")
        txtfile.write("------------------------------------------------------------\n")
        txtfile.write("observation	%i\n"%
                      histos1d[box,"data"].Integral())
        txtfile.write("------------------------------------------------------------\n")
        txtfile.write("shapes * * razor_combine_%s_%s.root $PROCESS $PROCESS_$SYSTEMATIC\n"%
                      (box,model))
        txtfile.write("------------------------------------------------------------\n")
        if box in ["MuEle","MuMu","EleEle"]:
            txtfile.write("bin		bin1			bin1		\n")
            txtfile.write("process		%s_%s 	%s_%s\n"%
                          (box,model,box,bkgs[0]))
            txtfile.write("process        	0          		1\n")
            txtfile.write("rate            %f		%f	\n"%
                          (histos1d[box,model].Integral(),histos1d[box,bkgs[0]].Integral()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			    lnN	1.044       1.00\n")
            txtfile.write("lepton			lnN	1.03       1.00\n")
            txtfile.write("trigger			lnN	1.05       1.00\n")
            txtfile.write("Pdf			shape	2.00       -\n")
            txtfile.write("Jes			shape	2.00       -\n")
            txtfile.write("Btag			shape	2.00       -\n")
            txtfile.write("Isr			shape	2.00       -\n")
            norm_err = 1.+(workspace.var("Ntot_TTj1b").getError()/workspace.var("Ntot_TTj1b").getVal())
            txtfile.write("bgnorm%s%s  	lnN   	1.00       %f\n"%
                          (box,bkgs[0],norm_err))
            for param_name in param_names:
                txtfile.write("%s_%s	shape	-	   2.00\n"%(param_name,box))
        elif box=="Jet2b":
            txtfile.write("bin		bin1			bin1			bin1\n")
            txtfile.write("process		%s_%s 	%s_%s	%s_%s\n"%
                          (box,model,box,bkgs[0],box,bkgs[1]))
            txtfile.write("process        	0          		1			2\n")
            txtfile.write("rate            %f		%f		%f\n"%
                          (histos1d[box,model].Integral(),histos1d[box,bkgs[0]].Integral(),
                           histos1d[box,bkgs[1]].Integral()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			    lnN	1.044       1.00	1.00\n")
            txtfile.write("lepton			lnN	1.03       1.00	1.00\n")
            txtfile.write("trigger			lnN	1.05       1.00	1.00\n")
            txtfile.write("Pdf			shape	2.00       -	-\n")
            txtfile.write("Jes			shape	2.00       -	-\n")
            txtfile.write("Btag			shape	2.00       -	-\n")
            txtfile.write("Isr			shape	2.00       -	-\n")
            norm_err = 1.+(workspace.var("Ntot_TTj2b").getError()/workspace.var("Ntot_TTj2b").getVal())
            txtfile.write("bgnorm%s%s  	lnN   	1.00       %f	1.00\n"%
                          (box,bkgs[0],norm_err))
            norm_err = 1.+rt.TMath.Sqrt(rt.TMath.Power(workspace.var("Ntot_TTj2b").getError()/workspace.var("Ntot_TTj2b").getVal(),2.) + rt.TMath.Power(workspace.var("f3_TTj2b").getError()/workspace.var("f3_TTj2b").getVal(),2.))
            txtfile.write("bgnorm%s%s  	lnN   	1.00       1.00	%s\n"%
                          (box,bkgs[1],norm_err))
            for param_name in param_names:
                txtfile.write("%s_%s	shape	-	   2.00	2.00\n"%(param_name,box))
        else:
                
            txtfile.write("bin		bin1			bin1			bin1			bin1\n")
            txtfile.write("process		%s_%s 	%s_%s	%s_%s	%s_%s\n"%
                          (box,model,box,bkgs[0],box,bkgs[1],box,bkgs[2]))
            txtfile.write("process        	0          		1			2			3\n")
            txtfile.write("rate            %f		%f		%f		%f\n"%
                          (histos1d[box,model].Integral(),histos1d[box,bkgs[0]].Integral(),
                           histos1d[box,bkgs[1]].Integral(),histos1d[box,bkgs[2]].Integral()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			lnN	1.044      1.00	1.00	1.00\n")
            txtfile.write("lepton			lnN	1.03       1.00	1.00	1.00\n")
            txtfile.write("trigger			lnN	1.05       1.00	1.00	1.00\n")
            txtfile.write("Pdf			shape	2.00       -	-	-\n")
            txtfile.write("Jes			shape	2.00       -	-	-\n")
            txtfile.write("Btag			shape	2.00       -	-	-\n")
            txtfile.write("Isr			shape	2.00       -	-	-\n")
            norm_err = 1.+(workspace.var("Ntot_TTj1b").getError()/workspace.var("Ntot_TTj1b").getVal())
            txtfile.write("bgnorm%s%s  	lnN   	1.00       %f	1.00	1.00\n"%
                          (box,bkgs[0],norm_err))
            norm_err = 1.+(workspace.var("Ntot_TTj2b").getError()/workspace.var("Ntot_TTj2b").getVal())
            txtfile.write("bgnorm%s%s  	lnN   	1.00       1.00	%s	1.00\n"%
                          (box,bkgs[1],norm_err))
            norm_err = 1.+rt.TMath.Sqrt(rt.TMath.Power(workspace.var("Ntot_TTj2b").getError()/workspace.var("Ntot_TTj2b").getVal(),2.) + rt.TMath.Power(workspace.var("f3_TTj2b").getError()/workspace.var("f3_TTj2b").getVal(),2.))
            txtfile.write("bgnorm%s%s  	lnN   	1.00       1.00	1.00	%f\n"%
                          (box,bkgs[2],norm_err))
            for param_name in param_names:
                txtfile.write("%s_%s	shape	-	   2.00	2.00	2.00\n"%(param_name,box))
        txtfile.close()

# def find68ProbRange(hToy, probVal=0.6827):
#     minVal = 0.
#     maxVal = 100000.
#     if hToy.Integral()<=0: return hToy.GetBinCenter(hToy.GetMaximumBin()),max(minVal,0.),maxVal
#     # get the bin contents
#     probsList = []
#     for  iX in range(1, hToy.GetNbinsX()+1):
#         probsList.append(hToy.GetBinContent(iX)/hToy.Integral())
#     probsList = reversed(sorted(probsList))
#     prob = 0
#     found = False
#     range68 = 0
#     counter = 0
#     for prob_inc in probsList:
#         counter += 1
#         if prob+prob_inc >= probVal and not found:
#             range68 = counter
#             found = True
#         prob += prob_inc
#     range68 = range68 * hToy.GetBinWidth(1)
#     mode = hToy.GetBinLowEdge(hToy.GetMaximumBin())
#     #print "mode +- range68 = %i +- %i"%(mode,range68)
#     return mode,range68

def find68ProbRange(hToy, probVal=0.6827):
    minVal = 0.
    maxVal = 100000.
    if hToy.Integral()<=0: return hToy.GetBinCenter(hToy.GetMaximumBin()),max(minVal,0.),maxVal
    # get the bin contents
    probsList = []
    for iX in range(1, hToy.GetNbinsX()+1):
        probsList.append(hToy.GetBinContent(iX)/hToy.Integral())
    probsList.sort()
    prob = 0
    prob68 = 0
    found = False
    for iX in range(0,len(probsList)):
        if prob+probsList[iX] >= 1-probVal and not found:
            frac = (1-probVal-prob)/probsList[iX]
            prob68 = probsList[iX-1]+frac*(probsList[iX]-probsList[iX-1])
            found = True
        prob = prob + probsList[iX]

    foundMin = False
    foundMax = False
    for  iX in range(0, hToy.GetNbinsX()):
        if not foundMin and hToy.GetBinContent(iX+1) >= prob68:
            fraction = (prob68-hToy.GetBinContent(iX))/(hToy.GetBinContent(iX+1)-hToy.GetBinContent(iX))
            minVal = hToy.GetBinLowEdge(iX)+hToy.GetBinWidth(iX)*fraction
            foundMin = True
        if not foundMax and hToy.GetBinContent(hToy.GetNbinsX()-iX) >= prob68:
            fraction = (prob68-hToy.GetBinContent(hToy.GetNbinsX()-iX+1))/(hToy.GetBinContent(hToy.GetNbinsX()-iX)-hToy.GetBinContent(hToy.GetNbinsX()-iX+1))
            maxVal = hToy.GetBinLowEdge(hToy.GetNbinsX()-iX)+hToy.GetBinWidth(hToy.GetNbinsX()-iX)*(1-fraction)
            foundMax = True

    range68 = (maxVal-max(minVal,0.))/2.
    return hToy.GetBinCenter(hToy.GetMaximumBin()),range68

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
    if Y0 > ymin: Y0 = ymin-0.05
    if X0 > xmin: X0 = xmin-100
    total_integral = (N/rt.TMath.Power(B*N,N))*(Gfun(xmin,ymin,X0,Y0,B,N)-Gfun(xmin,ymax,X0,Y0,B,N)-Gfun(xmax,ymin,X0,Y0,B,N)+Gfun(xmax,ymax,X0,Y0,B,N))

    xmin  = x[0]
    xmax  = x[3]
    ymin  = y[0]
    ymax  = y[1]
    excl_integral = (N/rt.TMath.Power(B*N,N))*(Gfun(xmin,ymin,X0,Y0,B,N)-Gfun(xmin,ymax,X0,Y0,B,N)-Gfun(xmax,ymin,X0,Y0,B,N)+Gfun(xmax,ymax,X0,Y0,B,N))

    xmin  = x[i-1]
    xmax  = x[i]
    ymin  = y[j-1]
    ymax  = y[j]
    integral = (N/rt.TMath.Power(B*N,N))*(Gfun(xmin,ymin,X0,Y0,B,N)-Gfun(xmin,ymax,X0,Y0,B,N)-Gfun(xmax,ymin,X0,Y0,B,N)+Gfun(xmax,ymax,X0,Y0,B,N))

    if (z[k-1]==1) :
        bin_events =  NTOT*integral/total_integral
    elif (z[k-1]==2) : 
        bin_events = (1.-F3)*NTOT*integral/total_integral
    elif (z[k-1]==3) : 
        bin_events =  F3*NTOT*integral/total_integral

    if bin_events <0:
        print "\nERROR: bin razor pdf integral =", integral
        print "\nERROR: total razor pdf integral =", total_integral
        return 0.
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
    while zeroIntegral:
        argList = fr.randomizePars()
        for p in RootTools.RootIterator.RootIterator(argList):
            workspace.var(p.GetName()).setVal(p.getVal())
            workspace.var(p.GetName()).setError(p.getError())
            # check how many error messages we have before evaluating pdfs
            errorCountBefore = rt.RooMsgService.instance().errorCount()
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
                # check how many error messages we have after evaluating pdfs
            zeroIntegral = any(badPars)
            if not zeroIntegral:
                for component in componentsOn:
                    pdfComp = workspace.pdf("%s_%s"%(pdfname,component))
                    pdfValV = pdfComp.getValV(myvars)
                    errorCountAfter = rt.RooMsgService.instance().errorCount()
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
            return [0.15, 0.2, 0.25,0.3,0.35,0.41,0.52,0.64,0.8,1.5]
            #return [0.15,0.20,0.30,0.41,0.52,0.64,0.80,1.5]
    elif varName == "nBtag" :
        if boxName in ["Jet2b"]:
            return [2.,3.,4.]
        elif boxName in ["MuEle","EleEle","MuMu"]:
            return [1.,4.]
        else:
            return [1.,2.,3.,4.]
            
if __name__ == '__main__':

    rt.gSystem.Load("../lib/libRazor")
    
    boxes = ["MultiJet","Jet2b","EleMultiJet","MuMultiJet","MuJet","EleJet","MuEle","EleEle","MuMu"]
    box = sys.argv[1]
    model = sys.argv[2]
    infile = rt.TFile.Open(sys.argv[3],"READ")
    sigFile = rt.TFile.Open(sys.argv[4])

    
    lumi = 19.3 # luminosity in fb^-1
    ref_xsec = 100. # reference cross section in fb
    for i in xrange(5,len(sys.argv)):
        if sys.argv[i].find("--xsec")!=-1: ref_xsec = float(sys.argv[i+1])
        if sys.argv[i].find("--lumi")!=-1: lumi = float(sys.argv[i+1])
            
    w = rt.RooWorkspace("w")
    histos = {}
    histos1d = {}
    if box in ["MuEle", "EleEle", "MuMu"]:
        param_names = ["MR0_TTj1b", "Ntot_TTj1b", "R0_TTj1b", "b_TTj1b", "n_TTj1b"]
        initialbkgs = ["TTj1b"]
    elif box == "Jet2b":
        param_names = ["MR0_TTj2b", "Ntot_TTj2b", "R0_TTj2b", "b_TTj2b", "f3_TTj2b", "n_TTj2b"]
        initialbkgs = ["TTj2b", "TTj3b"]
    else:
        initialbkgs = ["TTj1b", "TTj2b", "TTj3b"]
        param_names = ["MR0_TTj1b", "MR0_TTj2b", "Ntot_TTj1b", "Ntot_TTj2b", "R0_TTj1b", "R0_TTj2b", "b_TTj1b", "b_TTj2b", "f3_TTj2b", "n_TTj1b", "n_TTj2b"]

    x = array('d', getBinning(box, "MR"))
    y = array('d', getBinning(box, "Rsq"))
    z = array('d', getBinning(box, "nBtag"))

    bkgs = []
    bkgs.extend(initialbkgs)
    for bkg in initialbkgs:
        for param_name in param_names:
            for syst in ["Up","Down"]:
                bkgs.append("%s_%s_%s%s"%(bkg,param_name,box,syst))
    for bkg in bkgs:
        histos[box,bkg] = rt.TH3D("%s_%s_3d"%(box,bkg),"%s_%s_3d"%(box,bkg),len(x)-1,x,len(y)-1,y,len(z)-1,z)
    histos[box,model] = rt.TH3D("%s_%s_3d"%(box,model),"%s_%s_3d"%(box,model),len(x)-1,x,len(y)-1,y,len(z)-1,z)
    histos[box,"data"] = rt.TH3D("%s_%s_3d"%(box,"data"),"%s_%s_3d"%(box,"data"),len(x)-1,x,len(y)-1,y,len(z)-1,z)
        
    print "\nINFO: retreiving %s box workspace\n"%box
    workspace = infile.Get("%s/Box%s_workspace"%(box,box))
    data = workspace.data("RMRTree")
    fr = workspace.obj("independentFR")
    print "\nINFO: retreiving %s box covariance matrix\n"%box
    covMatrix = fr.covarianceMatrix()
    covMatrix.Print("")
    paramList = rt.RooArgList()
    for param_name in param_names:
        paramList.add(workspace.var(param_name))
        
    covMatrixE = rt.TMatrixDSymEigen(covMatrix)
    eigenVal = covMatrixE.GetEigenValues()
    eigenVect = covMatrixE.GetEigenVectors()
        
    eigenVectT = eigenVect.Clone()
    eigenVectT.Transpose(eigenVect)

    print "\nINFO: diagonalizing covariance matrix\n"
    diag = eigenVectT * (covMatrix *  eigenVect)
    eigenVal.Print("")
    
    
    print "\nINFO: %s box fit result!\n"%box
    fr.Print("v")
    eigenVal.Sqrt()

    rotEigenVal =  eigenVal.Clone()
    rotEigenVal *=  eigenVect
        
    variation = []
    for j in range(0,len(param_names)):
        variation.append([eigenVal[j]*eigenVect[i][j] for i in range(0,len(param_names))])
        
    cen = [workspace.var(param_name).getVal() for param_name in param_names]
        
    MR = workspace.var("MR")
    Rsq = workspace.var("Rsq")
    nBtag = workspace.var("nBtag")

    variables = rt.RooArgSet(MR,Rsq)
        
    MRRsqnBtag = rt.RooArgSet("MRRsqnBtag")
    MRRsqnBtag.add(MR)
    MRRsqnBtag.add(Rsq)
    MRRsqnBtag.add(nBtag)
    
    var_names = [v.GetName() for v in RootTools.RootIterator.RootIterator(workspace.set('variables'))]
        
    x = array('d', getBinning(box, "MR"))
    y = array('d', getBinning(box, "Rsq"))
    z = array('d', getBinning(box, "nBtag"))

    MRcut = x[3]
    Rsqcut = y[1]
        
    data_obs = data.reduce(MRRsqnBtag)
    data_obs = data_obs.reduce("MR>=%i || Rsq>=%f"%(MRcut,Rsqcut))
    data_obs.SetName("data_obs")
    
    data_obs.fillHistogram(histos[box,"data"],rt.RooArgList(MR,Rsq,nBtag))
        
    for bkg in initialbkgs:
        if bkgs=="TTj3b": continue
        for i in xrange(1,len(x)):
            for j in xrange(1,len(y)):
                for k in xrange(1, len(z)):
                    if x[i-1] < MRcut and y[j-1] < Rsqcut: continue
                    bin_events = getBinEvents(i,j,k,x,y,z,workspace)
                    if (bkg.find("1b")!=-1 and z[k-1]==1) :
                        histos[box,bkg].SetBinContent(i,j,k,bin_events)
                    elif (bkg.find("2b")!=-1 and z[k-1]==2) : 
                        histos[box,bkg].SetBinContent(i,j,k,bin_events)
                    elif (bkg.find("2b")!=-1 and z[k-1]==3) : 
                        histos[box,"TTj3b"].SetBinContent(i,j,k,bin_events)

    sign = {}
    sign["Up"] = 0.5
    sign["Down"] = -0.5
    for bkg in initialbkgs:
        for p in range(0,len(param_names)):
            print "\nINFO: Now varying parameter\n"
            print "variation #", p
            var_name = param_names[p]
            for syst in ["Up","Down"]:
                for q in range(0,len(param_names)):
                    param_name = param_names[q]
                    rel_err = sign[syst]*variation[p][q]/(workspace.var(param_name).getError())
                    print param_name, syst, " = ", cen[q]+sign[syst]*variation[p][q], " -> ", "%.2fsigma"%(rel_err)
                    workspace.var(param_name).setVal(cen[q]+sign[syst]*variation[p][q])
                for i in xrange(1,len(x)):
                    for j in xrange(1,len(y)):
                        for k in xrange(1,len(z)):
                            if x[i-1] < MRcut and y[j-1] < Rsqcut: continue
                            bin_events = getBinEvents(i,j,k,x,y,z,workspace)
                            if (bkg.find("1b")!=-1 and z[k-1]==1) :
                                histos[box,"%s_%s_%s%s"%(bkg,var_name,box,syst)].SetBinContent(i,j,k,bin_events)
                            elif (bkg.find("2b")!=-1 and z[k-1]==2) : 
                                histos[box,"%s_%s_%s%s"%(bkg,var_name,box,syst)].SetBinContent(i,j,k,bin_events)
                            elif (bkg.find("3b")!=-1 and z[k-1]==3) : 
                                histos[box,"%s_%s_%s%s"%(bkg,var_name,box,syst)].SetBinContent(i,j,k,bin_events)
                for q in range(0,len(param_names)):
                    param_name = param_names[q]
                    workspace.var(param_name).setVal(cen[q])
                    
    for bkg in initialbkgs:
        for param_name in param_names:
            for syst in ['Up','Down']:
                if histos[box,"%s_%s_%s%s"%(bkg,param_name,box,syst)].Integral() > 0:
                    histos[box,"%s_%s_%s%s"%(bkg,param_name,box,syst)].Scale( histos[box,"%s"%(bkg)].Integral()/histos[box,"%s_%s_%s%s"%(bkg,param_name,box,syst)].Integral())
                else: print "ERROR: histogram for %s_%s_%s%s has zero integral!"%(bkg,param_name,box,syst)
        
    wHisto = sigFile.Get('wHisto_pdferr_nom')
    btag =  sigFile.Get('wHisto_btagerr_pe')
    jes =  sigFile.Get('wHisto_JESerr_pe')
    pdf =  sigFile.Get('wHisto_pdferr_pe')
    isr =  sigFile.Get('wHisto_ISRerr_pe')

    # adding signal shape systematics
    print "\nINFO: Now obtaining signal shape systematics\n"
    
    isrUp = wHisto.Clone("%s_%s_IsrUp"%(box,model))
    isrUp.SetTitle("%s_%s_IsrUp"%(box,model))
    isrDown = wHisto.Clone("%s_%s_IsrDown"%(box,model))
    isrDown.SetTitle("%s_%s_IsrDown"%(box,model))
    isrAbs = isr.Clone("IsrAbs")
    isrAbs.Multiply(wHisto)
    isrUp.Add(isrAbs,sign["Up"])
    isrDown.Add(isrAbs,sign["Down"])
    histos[(box,"%s_IsrUp"%(model))] = rebin3d(isrUp,x,y,z, MRcut, Rsqcut)
    histos[(box,"%s_IsrDown"%(model))] = rebin3d(isrDown,x,y,z, MRcut, Rsqcut)
    
    btagUp = wHisto.Clone("%s_%s_BtagUp"%(box,model))
    btagUp.SetTitle("%s_%s_BtagUp"%(box,model))
    btagDown = wHisto.Clone("%s_%s_BtagDown"%(box,model))
    btagDown.SetTitle("%s_%s_BtagDown"%(box,model))
    btagAbs = btag.Clone("BtagAbs")
    btagAbs.Multiply(wHisto)
    btagUp.Add(btagAbs,sign["Up"])
    btagDown.Add(btagAbs,sign["Down"])
    histos[(box,"%s_BtagUp"%(model))] = rebin3d(btagUp,x,y,z, MRcut, Rsqcut)
    histos[(box,"%s_BtagDown"%(model))] = rebin3d(btagDown,x,y,z, MRcut, Rsqcut)

    jesUp = wHisto.Clone("%s_%s_JesUp"%(box,model))
    jesUp.SetTitle("%s_%s_JesUp"%(box,model))
    jesDown = wHisto.Clone("%s_%s_JesDown"%(box,model))
    jesDown.SetTitle("%s_%s_JesDown"%(box,model))
    jesAbs = jes.Clone("JesAbs")
    jesAbs.Multiply(wHisto)
    jesUp.Add(jesAbs,sign["Up"])
    jesDown.Add(jesAbs,sign["Down"])
    histos[(box,"%s_JesUp"%(model))] = rebin3d(jesUp,x,y,z, MRcut, Rsqcut)
    histos[(box,"%s_JesDown"%(model))] = rebin3d(jesDown,x,y,z, MRcut, Rsqcut)
    
    pdfUp = wHisto.Clone("%s_%s_PdfUp"%(box,model))
    pdfUp.SetTitle("%s_%s_PdfUp"%(box,model))
    pdfDown = wHisto.Clone("%s_%s_PdfDown"%(box,model))
    pdfDown.SetTitle("%s_%s_PdfDown"%(box,model))
    pdfAbs = pdf.Clone("PdfAbs")
    pdfAbs.Multiply(wHisto)
    pdfUp.Add(pdfAbs,sign["Up"])
    pdfDown.Add(pdfAbs,sign["Down"])
    histos[(box,"%s_PdfUp"%(model))] = rebin3d(pdfUp,x,y,z, MRcut, Rsqcut)
    histos[(box,"%s_PdfDown"%(model))] = rebin3d(pdfDown,x,y,z, MRcut, Rsqcut)
    
    #set the per box eff value
    sigNorm = wHisto.Integral()
    sigEvents = sigNorm*lumi*ref_xsec
    print "\nINFO: now multiplying:  efficiency x lumi x ref_xsec = %f x %f x %f = %f"%(sigNorm,lumi,ref_xsec,sigEvents)
    
    histos[box,model] = rebin3d(wHisto.Clone("%s_%s_3d"%(box,model)), x, y, z, MRcut, Rsqcut )
    histos[box,model].SetTitle("%s_%s_3d"%(box,model))
    histos[box,model].Scale(lumi*ref_xsec)
    
    for param_name in ["Jes","Isr","Btag","Pdf"]:
        for syst in ['Up','Down']:
            if histos[box,"%s_%s%s"%(model,param_name,syst)].Integral() > 0:
                histos[box,"%s_%s%s"%(model,param_name,syst)].Scale( histos[box,model].Integral()/histos[box,"%s_%s%s"%(model,param_name,syst)].Integral())
                
    outFile = rt.TFile.Open("razor_combine_%s_%s.root"%(box,model),"RECREATE")

    #unroll histograms 3D -> 1D
    print "\nINFO: Now Unrolling 3D histograms\n" 
    
    for index, histo in histos.iteritems():
        box, bkg = index
        print box, bkg
        totalbins = (len(x)-1)*(len(y)-1)*(len(z)-1)
        if bkg=="data":
            histos1d[box,bkg] = rt.TH1D("data_obs","data_obs",totalbins, 1, totalbins+1)
        else:
            histos1d[box,bkg] = rt.TH1D("%s_%s"%(box,bkg),"%s_%s"%(box,bkg),totalbins, 1, totalbins+1)
            
        totalbins = histos1d[box,bkg].GetNbinsX()
        newbin = 0
        for i in xrange(1,histo.GetNbinsX()+1):
            for j in xrange(1,histo.GetNbinsY()+1):
                for k in xrange(1,histo.GetNbinsZ()+1):
                    newbin += 1
                    histos1d[box,bkg].SetBinContent(newbin,histo.GetBinContent(i,j,k))
                        
        histos1d[box,bkg].Write()

    print "\nINFO: Now writing data card\n"
    writeDataCard(box,model,"razor_combine_%s_%s.txt"%(box,model),initialbkgs,param_names,histos1d,workspace)
    os.system("cat razor_combine_%s_%s.txt \n"%(box,model)) 
    outFile.Close()
