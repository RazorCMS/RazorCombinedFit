from optparse import OptionParser
import os
import math
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from array import *
from pdfShit import *
import sys

def getCutString(box, fitRegion):
    if box in ["Jet2b","MultiJet"]:
        if fitRegion=="FULL":
            return "(MR>=400.&&Rsq>=0.25&&(MR>=450.||Rsq>=0.3))"
        else:
            return "(MR>=550.&&Rsq>=0.3)"
    else:
        if fitRegion=="FULL":
            return "(MR>=300.&&Rsq>=0.15&&(MR>=350.||Rsq>=0.2))"
        else:
            return "(MR>=450.&&Rsq>=0.2)"
                
def passCut(MRVal, RsqVal, box, fitRegion):
    if box in ["Jet2b","MultiJet"]:
        if fitRegion=="FULL":
            if MRVal >= 400. and RsqVal >= 0.25 and (MRVal >= 450. or RsqVal >= 0.3): return True
        else:
            if MRVal >= 550. and RsqVal >= 0.3: return True
    else:
        if fitRegion=="FULL":
            if MRVal >= 300. and RsqVal >= 0.15 and (MRVal >= 350. or RsqVal >= 0.2): return True
        else:
            if MRVal >= 450. and RsqVal >= 0.2: return True

    return False
        
def rebin3d(oldhisto, x, y, z, box, fitRegion):
    newhisto = rt.TH3D(oldhisto.GetName()+"_rebin",oldhisto.GetTitle()+"_rebin",len(x)-1,x,len(y)-1,y,len(z)-1,z)
    for i in range(1,oldhisto.GetNbinsX()+1):
        for j in range(1,oldhisto.GetNbinsY()+1):
            for k in range(1,oldhisto.GetNbinsZ()+1):
                xold = oldhisto.GetXaxis().GetBinCenter(i)
                yold = oldhisto.GetYaxis().GetBinCenter(j)
                zold = oldhisto.GetZaxis().GetBinCenter(k)
                if not passCut(xold, yold, box, fitRegion): continue
                oldbincontent = oldhisto.GetBinContent(i,j,k)
                newhisto.Fill(xold, yold, zold, max(0.,oldbincontent))                
    return newhisto
    
def writeDataCard(box,model,txtfileName,bkgs,paramNames,histos1d,workspace,sigma):
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
            txtfile.write("rate            %.3f		%.3f	\n"%
                          (histos1d[box,model].Integral(),histos1d[box,bkgs[0]].Integral()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			    lnN	1.044       1.00\n")
            txtfile.write("lepton			lnN	1.03       1.00\n")
            txtfile.write("trigger			lnN	1.05       1.00\n")
            txtfile.write("Pdf			shape	%.2f       -\n"%(1./sigma))
            txtfile.write("Jes			shape	%.2f       -\n"%(1./sigma))
            txtfile.write("Btag			shape	%.2f       -\n"%(1./sigma))
            txtfile.write("Isr			shape	%.2f       -\n"%(1./sigma))
            normErr = 1.+(workspace.var("Ntot_TTj1b").getError()/workspace.var("Ntot_TTj1b").getVal())
            txtfile.write("bgnorm%s%s  	lnN   	1.00       %.3f\n"%
                          (box,bkgs[0],normErr))
            for paramName in paramNames:
                txtfile.write("%s_%s	shape	-	   %.2f\n"%(paramName,box,(1./sigma)))
        elif box=="Jet2b":
            txtfile.write("bin		bin1			bin1			bin1\n")
            txtfile.write("process		%s_%s 	%s_%s	%s_%s\n"%
                          (box,model,box,bkgs[0],box,bkgs[1]))
            txtfile.write("process        	0          		1			2\n")
            txtfile.write("rate            %.3f		%.3f		%.3f\n"%
                          (histos1d[box,model].Integral(),histos1d[box,bkgs[0]].Integral(),
                           histos1d[box,bkgs[1]].Integral()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			    lnN	1.044       1.00	1.00\n")
            txtfile.write("lepton			lnN	1.03       1.00	1.00\n")
            txtfile.write("trigger			lnN	1.05       1.00	1.00\n")
            txtfile.write("Pdf			shape	%.2f       -	-\n"%(1./sigma))
            txtfile.write("Jes			shape	%.2f       -	-\n"%(1./sigma))
            txtfile.write("Btag			shape	%.2f       -	-\n"%(1./sigma))
            txtfile.write("Isr			shape	%.2f       -	-\n"%(1./sigma))
            normErr = 1.+(workspace.var("Ntot_TTj2b").getError()/workspace.var("Ntot_TTj2b").getVal())
            txtfile.write("bgnorm%s%s  	lnN   	1.00       %.3f	1.00\n"%
                          (box,bkgs[0],normErr))
            normErr = 1.+rt.TMath.Sqrt(rt.TMath.Power(workspace.var("Ntot_TTj2b").getError()/workspace.var("Ntot_TTj2b").getVal(),2.) + rt.TMath.Power(workspace.var("f3_TTj2b").getError()/workspace.var("f3_TTj2b").getVal(),2.))
            txtfile.write("bgnorm%s%s  	lnN   	1.00       1.00	%.3f\n"%
                          (box,bkgs[1],normErr))
            for paramName in paramNames:
                txtfile.write("%s_%s	shape	-	   %.2f	%.2f\n"%(paramName,box,(1./sigma),(1./sigma)))
        else:
            txtfile.write("bin		bin1			bin1			bin1			bin1\n")
            txtfile.write("process		%s_%s 	%s_%s	%s_%s	%s_%s\n"%
                          (box,model,box,bkgs[0],box,bkgs[1],box,bkgs[2]))
            txtfile.write("process        	0          		1			2			3\n")
            txtfile.write("rate            %.3f		%.3f		%.3f		%.3f\n"%
                          (histos1d[box,model].Integral(),histos1d[box,bkgs[0]].Integral(),
                           histos1d[box,bkgs[1]].Integral(),histos1d[box,bkgs[2]].Integral()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			lnN	1.044      1.00	1.00	1.00\n")
            txtfile.write("lepton			lnN	1.03       1.00	1.00	1.00\n")
            txtfile.write("trigger			lnN	1.05       1.00	1.00	1.00\n")
            txtfile.write("Pdf			shape	%.2f       -	-	-\n"%(1./sigma))
            txtfile.write("Jes			shape	%.2f       -	-	-\n"%(1./sigma))
            txtfile.write("Btag			shape	%.2f       -	-	-\n"%(1./sigma))
            txtfile.write("Isr			shape	%.2f       -	-	-\n"%(1./sigma))
            normErr = 1.+(workspace.var("Ntot_TTj1b").getError()/workspace.var("Ntot_TTj1b").getVal())
            txtfile.write("bgnorm%s%s  	lnN   	1.00       %.3f	1.00	1.00\n"%
                          (box,bkgs[0],normErr))
            normErr = 1.+(workspace.var("Ntot_TTj2b").getError()/workspace.var("Ntot_TTj2b").getVal())
            txtfile.write("bgnorm%s%s  	lnN   	1.00       1.00	%.3f	1.00\n"%
                          (box,bkgs[1],normErr))
            normErr = 1.+rt.TMath.Sqrt(rt.TMath.Power(workspace.var("Ntot_TTj2b").getError()/workspace.var("Ntot_TTj2b").getVal(),2.) + rt.TMath.Power(workspace.var("f3_TTj2b").getError()/workspace.var("f3_TTj2b").getVal(),2.))
            txtfile.write("bgnorm%s%s  	lnN   	1.00       1.00	1.00	%.3f\n"%
                          (box,bkgs[2],normErr))
            for paramName in paramNames:
                txtfile.write("%s_%s	shape	-	   %.2f	%.2f	%.2f\n"%(paramName,box,(1./sigma),(1./sigma),(1./sigma)))
        txtfile.close()

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

            
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('-d','--dir',dest="outdir",default="./",type="string",
                  help="Output directory to store datasets")
    parser.add_option('-b','--box',dest="box",default=None,type="string",
                  help="Specify only one box")
    parser.add_option('-i','--input',dest="input", default=None,metavar='FILE',
                  help="An input file to read fit results and workspaces from")
    parser.add_option('-x','--xsec',dest="refXsec", default=100,type="float",
                  help="Reference signal cross section in fb to define mu (signal strength)")
    parser.add_option('-l','--lumi',dest="lumi", default=19.3,type="float",
                  help="Nominal luminosity in fb^-1")
    parser.add_option('-s','--sigma',dest="sigma", default=0.5,type="float",
                  help="Number of sigmas to fluctuate systematic uncertainties")
    parser.add_option('-m','--model',dest="model", default="T2tt",type="string",
                  help="SMS model string")
    parser.add_option('-f','--fit-region',dest="fitRegion", default="FULL",type="string",
                  help="fit region = FULL, Sideband")

    (options,args) = parser.parse_args()
    
    if options.config is None:
        print "You need to specify a config"   
        sys.exit()
    if options.input is None:
        print "You need a input razor fit result file"   
        sys.exit()  
    if options.box is None:
        print "You need to specify a box"
        sys.exit()
        
    print 'INFO: input file is %s' % ', '.join(args)
    
    cfg = Config.Config(options.config)
    
    rt.gSystem.Load("../lib/libRazor")
    
    box = options.box
    model = options.model
    infile = rt.TFile.Open(options.input,"READ")
    sigFile = rt.TFile.Open(args[0],"READ")
    refXsec = options.refXsec
    lumi = options.lumi
    outdir = options.outdir
    sigma = options.sigma
    fitRegion = options.fitRegion
            
    histos = {}
    histos1d = {}

    x = array('d', cfg.getBinning(box)[0])
    y = array('d', cfg.getBinning(box)[1])
    z = array('d', cfg.getBinning(box)[2])
    
    if box in ["MuEle", "EleEle", "MuMu"]:
        initialBkgs = ["TTj1b"]
    elif box == "Jet2b":
        initialBkgs = ["TTj2b", "TTj3b"]
    else:
        initialBkgs = ["TTj1b", "TTj2b", "TTj3b"]
        
    print "\nINFO: retreiving %s box workspace\n"%box
    workspace = infile.Get("%s/Box%s_workspace"%(box,box))
    data = workspace.data("RMRTree")
    fr = workspace.obj("independentFR")

    #get the background nuisance parmeter names 
    parList = fr.floatParsFinal()
    paramNames = []
    for p in RootTools.RootIterator.RootIterator(parList):
        paramNames.append(p.GetName())

    print "INFO: background nuisnace parameters are", paramNames

    bkgs = []
    bkgs.extend(initialBkgs)
    for bkg in initialBkgs:
        for paramName in paramNames:
            for syst in ["Up","Down"]:
                bkgs.append("%s_%s_%s%s"%(bkg,paramName,box,syst))
    for bkg in bkgs:
        histos[box,bkg] = rt.TH3D("%s_%s_3d"%(box,bkg),"%s_%s_3d"%(box,bkg),len(x)-1,x,len(y)-1,y,len(z)-1,z)
    histos[box,model] = rt.TH3D("%s_%s_3d"%(box,model),"%s_%s_3d"%(box,model),len(x)-1,x,len(y)-1,y,len(z)-1,z)
    histos[box,"data"] = rt.TH3D("%s_%s_3d"%(box,"data"),"%s_%s_3d"%(box,"data"),len(x)-1,x,len(y)-1,y,len(z)-1,z)
        
    
    print "\nINFO: retreiving %s box covariance matrix\n"%box
    covMatrix = fr.covarianceMatrix()
    covMatrix.Print("")
    paramList = rt.RooArgList()
    for paramName in paramNames:
        paramList.add(workspace.var(paramName))
        
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
    for j in range(0,len(paramNames)):
        variation.append([eigenVal[j]*eigenVect[i][j] for i in range(0,len(paramNames))])
        
    cen = [workspace.var(paramName).getVal() for paramName in paramNames]
        
    MR = workspace.var("MR")
    Rsq = workspace.var("Rsq")
    nBtag = workspace.var("nBtag")

    variables = rt.RooArgSet(MR,Rsq)
        
    MRRsqnBtag = rt.RooArgSet("MRRsqnBtag")
    MRRsqnBtag.add(MR)
    MRRsqnBtag.add(Rsq)
    MRRsqnBtag.add(nBtag)
    
    var_names = [v.GetName() for v in RootTools.RootIterator.RootIterator(workspace.set('variables'))]
        
    data_obs = data.reduce(MRRsqnBtag)
    data_obs = data_obs.reduce(getCutString(box,fitRegion))
    data_obs.SetName("data_obs")
    
    data_obs.fillHistogram(histos[box,"data"],rt.RooArgList(MR,Rsq,nBtag))
        
    for bkg in initialBkgs:
        if bkgs=="TTj3b": continue
        for i in xrange(1,len(x)):
            for j in xrange(1,len(y)):
                for k in xrange(1, len(z)):
                    if not passCut(x[i-1],y[j-1], box, fitRegion): continue
                    bin_events = getBinEvents(i,j,k,x,y,z,workspace)
                    if (bkg.find("1b")!=-1 and z[k-1]==1) :
                        histos[box,bkg].SetBinContent(i,j,k,bin_events)
                    elif (bkg.find("2b")!=-1 and z[k-1]==2) : 
                        histos[box,bkg].SetBinContent(i,j,k,bin_events)
                    elif (bkg.find("2b")!=-1 and z[k-1]==3) : 
                        histos[box,"TTj3b"].SetBinContent(i,j,k,bin_events)

    sign = {}
    sign["Up"] = sigma
    sign["Down"] = -sigma
    for bkg in initialBkgs:
        for p in range(0,len(paramNames)):
            print "\nINFO: Now varying parameter\n"
            print "variation #", p
            var_name = paramNames[p]
            for syst in ["Up","Down"]:
                for q in range(0,len(paramNames)):
                    paramName = paramNames[q]
                    relErr = sign[syst]*variation[p][q]/(workspace.var(paramName).getError())
                    print paramName, syst, " = ", cen[q]+sign[syst]*variation[p][q], " -> ", "%.2fsigma"%(relErr)
                    workspace.var(paramName).setVal(cen[q]+sign[syst]*variation[p][q])
                for i in xrange(1,len(x)):
                    for j in xrange(1,len(y)):
                        for k in xrange(1,len(z)):
                            if not passCut(x[i-1],y[j-1], box, fitRegion): continue
                            bin_events = getBinEvents(i,j,k,x,y,z,workspace)
                            if (bkg.find("1b")!=-1 and z[k-1]==1) :
                                histos[box,"%s_%s_%s%s"%(bkg,var_name,box,syst)].SetBinContent(i,j,k,bin_events)
                            elif (bkg.find("2b")!=-1 and z[k-1]==2) : 
                                histos[box,"%s_%s_%s%s"%(bkg,var_name,box,syst)].SetBinContent(i,j,k,bin_events)
                            elif (bkg.find("3b")!=-1 and z[k-1]==3) : 
                                histos[box,"%s_%s_%s%s"%(bkg,var_name,box,syst)].SetBinContent(i,j,k,bin_events)
                for q in range(0,len(paramNames)):
                    paramName = paramNames[q]
                    workspace.var(paramName).setVal(cen[q])
                    
    for bkg in initialBkgs:
        for paramName in paramNames:
            for syst in ['Up','Down']:
                if histos[box,"%s_%s_%s%s"%(bkg,paramName,box,syst)].Integral() > 0:
                    histos[box,"%s_%s_%s%s"%(bkg,paramName,box,syst)].Scale( histos[box,"%s"%(bkg)].Integral()/histos[box,"%s_%s_%s%s"%(bkg,paramName,box,syst)].Integral())
                else: print "ERROR: histogram for %s_%s_%s%s has zero integral!"%(bkg,paramName,box,syst)
        
    wHisto = sigFile.Get('wHisto_pdferr_nom')
    btag =  sigFile.Get('wHisto_btagerr_pe')
    jes =  sigFile.Get('wHisto_JESerr_pe')
    pdf =  sigFile.Get('wHisto_pdferr_pe')
    isr =  sigFile.Get('wHisto_ISRerr_pe')

    # adding signal shape systematics
    print "\nINFO: Now obtaining signal shape systematics\n"
    
    isrUp = wHisto.Clone("%s_%s_IsrUp_3d"%(box,model))
    isrUp.SetTitle("%s_%s_IsrUp_3d"%(box,model))
    isrDown = wHisto.Clone("%s_%s_IsrDown_3d"%(box,model))
    isrDown.SetTitle("%s_%s_IsrDown_3d"%(box,model))
    isrAbs = isr.Clone("IsrAbs_3d")
    isrAbs.Multiply(wHisto)
    isrUp.Add(isrAbs,sign["Up"])
    isrDown.Add(isrAbs,sign["Down"])
    histos[(box,"%s_IsrUp"%(model))] = rebin3d(isrUp,x,y,z, box, fitRegion)
    histos[(box,"%s_IsrDown"%(model))] = rebin3d(isrDown,x,y,z, box, fitRegion)
    
    btagUp = wHisto.Clone("%s_%s_BtagUp_3d"%(box,model))
    btagUp.SetTitle("%s_%s_BtagUp_3d"%(box,model))
    btagDown = wHisto.Clone("%s_%s_BtagDown_3d"%(box,model))
    btagDown.SetTitle("%s_%s_BtagDown_3d"%(box,model))
    btagAbs = btag.Clone("BtagAbs_3d")
    btagAbs.Multiply(wHisto)
    btagUp.Add(btagAbs,sign["Up"])
    btagDown.Add(btagAbs,sign["Down"])
    histos[(box,"%s_BtagUp"%(model))] = rebin3d(btagUp,x,y,z, box, fitRegion)
    histos[(box,"%s_BtagDown"%(model))] = rebin3d(btagDown,x,y,z, box, fitRegion)

    jesUp = wHisto.Clone("%s_%s_JesUp_3d"%(box,model))
    jesUp.SetTitle("%s_%s_JesUp_3d"%(box,model))
    jesDown = wHisto.Clone("%s_%s_JesDown_3d"%(box,model))
    jesDown.SetTitle("%s_%s_JesDown_3d"%(box,model))
    jesAbs = jes.Clone("JesAbs_3d")
    jesAbs.Multiply(wHisto)
    jesUp.Add(jesAbs,sign["Up"])
    jesDown.Add(jesAbs,sign["Down"])
    histos[(box,"%s_JesUp"%(model))] = rebin3d(jesUp,x,y,z, box, fitRegion)
    histos[(box,"%s_JesDown"%(model))] = rebin3d(jesDown,x,y,z, box, fitRegion)
    
    pdfUp = wHisto.Clone("%s_%s_PdfUp_3d"%(box,model))
    pdfUp.SetTitle("%s_%s_PdfUp_3d"%(box,model))
    pdfDown = wHisto.Clone("%s_%s_PdfDown_3d"%(box,model))
    pdfDown.SetTitle("%s_%s_PdfDown_3d"%(box,model))
    pdfAbs = pdf.Clone("PdfAbs_3d")
    pdfAbs.Multiply(wHisto)
    pdfUp.Add(pdfAbs,sign["Up"])
    pdfDown.Add(pdfAbs,sign["Down"])
    histos[(box,"%s_PdfUp"%(model))] = rebin3d(pdfUp,x,y,z, box, fitRegion)
    histos[(box,"%s_PdfDown"%(model))] = rebin3d(pdfDown,x,y,z, box, fitRegion)
    
    #set the per box eff value
    sigNorm = wHisto.Integral()
    sigEvents = sigNorm*lumi*refXsec
    print "\nINFO: now multiplying:  efficiency x lumi x refXsec = %f x %f x %f = %f"%(sigNorm,lumi,refXsec,sigEvents)
    
    histos[box,model] = rebin3d(wHisto.Clone("%s_%s_3d"%(box,model)), x, y, z, box, fitRegion)
    histos[box,model].SetTitle("%s_%s_3d"%(box,model))
    histos[box,model].Scale(lumi*refXsec)
    
    for paramName in ["Jes","Isr","Btag","Pdf"]:
        for syst in ['Up','Down']:
            if histos[box,"%s_%s%s"%(model,paramName,syst)].Integral() > 0:
                histos[box,"%s_%s%s"%(model,paramName,syst)].Scale( histos[box,model].Integral()/histos[box,"%s_%s%s"%(model,paramName,syst)].Integral())
                
    outFile = rt.TFile.Open("%s/razor_combine_%s_%s.root"%(outdir,box,model),"RECREATE")

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
    writeDataCard(box,model,"%s/razor_combine_%s_%s.txt"%(outdir,box,model),initialBkgs,paramNames,histos1d,workspace,sigma)
    os.system("cat %s/razor_combine_%s_%s.txt \n"%(outdir,box,model)) 
    outFile.Close()
