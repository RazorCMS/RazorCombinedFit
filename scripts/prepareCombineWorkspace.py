from optparse import OptionParser
import os
import math
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
from array import *
from pdfShit import *
import glob
import sys

def getCutString(box, signalRegion):
    if box in ["Jet2b","MultiJet"]:
        if signalRegion=="FULL":
            return "(MR>=400.&&Rsq>=0.25&&(MR>=450.||Rsq>=0.3))"
        elif signalRegion=="HighMR":
            return "(MR>=550.&&Rsq>=0.3)"
    else:
        if signalRegion=="FULL":
            return "(MR>=300.&&Rsq>=0.15&&(MR>=350.||Rsq>=0.2))"
        elif signalRegion=="HighMR":
            return "(MR>=450.&&Rsq>=0.2)"
                
def passCut(MRVal, RsqVal, box, signalRegion):
    if box in ["Jet2b","MultiJet"]:
        if signalRegion=="FULL":
            if MRVal >= 400. and RsqVal >= 0.25 and (MRVal >= 450. or RsqVal >= 0.3): return True
        elif signalRegion=="HighMR":
            if MRVal >= 550. and RsqVal >= 0.3: return True
    else:
        if signalRegion=="FULL":
            if MRVal >= 300. and RsqVal >= 0.15 and (MRVal >= 350. or RsqVal >= 0.2): return True
        elif signalRegion=="HighMR":
            if MRVal >= 450. and RsqVal >= 0.2: return True

    return False
        
def rebin3d(oldhisto, x, y, z, box, signalRegion):
    newhisto = rt.TH3D(oldhisto.GetName()+"_rebin",oldhisto.GetTitle()+"_rebin",len(x)-1,x,len(y)-1,y,len(z)-1,z)
    for i in range(1,oldhisto.GetNbinsX()+1):
        for j in range(1,oldhisto.GetNbinsY()+1):
            for k in range(1,oldhisto.GetNbinsZ()+1):
                xold = oldhisto.GetXaxis().GetBinCenter(i)
                yold = oldhisto.GetYaxis().GetBinCenter(j)
                zold = oldhisto.GetZaxis().GetBinCenter(k)
                if not passCut(xold, yold, box, signalRegion): continue
                oldbincontent = oldhisto.GetBinContent(i,j,k)
                newhisto.Fill(xold, yold, zold, max(0.,oldbincontent))                
    return newhisto
    
def writeDataCard(box,model,massPoint,txtfileName,bkgs,paramNames,w,lumi_uncert,trigger_uncert,lepton_uncert):
        txtfile = open(txtfileName,"w")
        txtfile.write("imax 1 number of channels\n")
        if box in ["MuEle","MuMu","EleEle"]:
            nBkgd = 1
            nNuis = 12
            txtfile.write("jmax %i number of backgrounds\n"%nBkgd)
            txtfile.write("kmax %i number of nuisance parameters\n"%nNuis)
        elif box in ["Jet2b"]:
            nBkgd = 2
            nNuis = 13
            txtfile.write("jmax %i number of backgrounds\n"%nBkgd)
            txtfile.write("kmax %i number of nuisance parameters\n"%nNuis)
        else:
            nBkgd = 3
            nNuis = 18
            txtfile.write("jmax %i number of backgrounds\n"%nBkgd)
            txtfile.write("kmax %i number of nuisance parameters\n"%nNuis)
        txtfile.write("------------------------------------------------------------\n")
        txtfile.write("observation	%i\n"%
                      w.data("data_obs").sumEntries())
        txtfile.write("------------------------------------------------------------\n")
        txtfile.write("shapes * * razor_combine_%s_%s_%s.root w%s:$PROCESS w%s:$PROCESS_$SYSTEMATIC\n"%
                      (box,model,massPoint,box,box))
        txtfile.write("------------------------------------------------------------\n")
        if box in ["MuEle","MuMu","EleEle"]:
            txtfile.write("bin		%s			%s		\n"%(box,box))
            txtfile.write("process		%s_%s 	%s_%s\n"%
                          (box,model,box,bkgs[0]))
            txtfile.write("process        	0          		1\n")
            txtfile.write("rate            %.3f		%.3f	\n"%
                          (w.data("%s_%s"%(box,model)).sumEntries(),w.var("Ntot_%s_%s"%("TTj1b",box)).getVal()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			lnN	%.3f       1.00\n"%lumi_uncert)
            txtfile.write("lepton			lnN	%.3f       1.00\n"%lepton_uncert)
            txtfile.write("trigger			lnN	%.3f       1.00\n"%trigger_uncert)
            txtfile.write("Pdf			shape	%.2f       -\n"%(1./1.))
            txtfile.write("Jes			shape	%.2f       -\n"%(1./1.))
            txtfile.write("Btag			shape	%.2f       -\n"%(1./1.))
            txtfile.write("Isr			shape	%.2f       -\n"%(1./1.))
            normErr = 1.
            normErr += 2.*(w.var("Ntot_%s_%s"%("TTj1b",box)).getError()/w.var("Ntot_%s_%s"%("TTj1b",box)).getVal())
            txtfile.write("bgNorm_%s_%s  	lnN   	1.00       %.3f\n"%
                          (bkgs[0],box,normErr))
            for paramName in paramNames:
                if paramName.find("Ntot")!=-1 or paramName.find("f3")!=-1: continue
                txtfile.write("%s_%s	param	%e    %e\n"%(paramName,box,w.var("%s_%s"%(paramName,box)).getVal(), 2.*w.var("%s_%s"%(paramName,box)).getError()))
        elif box in ["Jet2b"]:
            txtfile.write("bin		%s			%s			%s\n"%(box,box,box))
            txtfile.write("process		%s_%s 	%s_%s	%s_%s\n"%
                          (box,model,box,bkgs[0],box,bkgs[1]))
            txtfile.write("process        	0          		1			2\n")
            txtfile.write("rate            %.3f		%.3f		%.3f\n"%
                          (w.data("%s_%s"%(box,model)).sumEntries(),w.var("Ntot_%s_%s"%("TTj2b",box)).getVal(),
                           w.var("Ntot_%s_%s"%("TTj2b",box)).getVal()*w.var("f3_%s_%s"%("TTj2b",box)).getVal()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			lnN	%.3f       1.00 1.00\n"%lumi_uncert)
            txtfile.write("lepton			lnN	%.3f       1.00 1.00\n"%lepton_uncert)
            txtfile.write("trigger			lnN	%.3f       1.00 1.00\n"%trigger_uncert)
            txtfile.write("Pdf			shape	%.2f       -	-\n"%(1./1.))
            txtfile.write("Jes			shape	%.2f       -	-\n"%(1./1.))
            txtfile.write("Btag			shape	%.2f       -	-\n"%(1./1.))
            txtfile.write("Isr			shape	%.2f       -	-\n"%(1./1.))
            normErr = 1.
            normErr += 2.*w.var("Ntot_%s_%s"%("TTj2b",box)).getError()/w.var("Ntot_%s_%s"%("TTj2b",box)).getVal()
            txtfile.write("bgNorm_%s_%s  	lnN   	1.00       %.3f	1.00\n"%
                          (bkgs[0],box,normErr))
            normErr = 1.
            quadErr = rt.TMath.Power(w.var("Ntot_%s_%s"%("TTj2b",box)).getError()/w.var("Ntot_%s_%s"%("TTj2b",box)).getVal(),2.) 
            quadErr += rt.TMath.Power(w.var("f3_%s_%s"%("TTj2b",box)).getError()/w.var("f3_%s_%s"%("TTj2b",box)).getVal(),2.)
            normErr += 2.*rt.TMath.Sqrt(quadErr)
            txtfile.write("bgNorm_%s_%s  	lnN   	1.00       1.00	%.3f\n"%
                          (bkgs[1],box,normErr))
            
            for paramName in paramNames:
                if paramName.find("Ntot")!=-1 or paramName.find("f3")!=-1: continue
                txtfile.write("%s_%s	param	%e    %e\n"%(paramName,box,w.var("%s_%s"%(paramName,box)).getVal(), 2.*w.var("%s_%s"%(paramName,box)).getError()))
        else:
            txtfile.write("bin		%s			%s			%s			%s\n"%(box,box,box,box))
            txtfile.write("process		%s_%s 	%s_%s	%s_%s	%s_%s\n"%
                          (box,model,box,bkgs[0],box,bkgs[1],box,bkgs[2]))
            txtfile.write("process        	0          		1			2			3\n")
            txtfile.write("rate            %.3f		%.3f		%.3f		%.3f\n"%
                          (w.data("%s_%s"%(box,model)).sumEntries(),w.var("Ntot_%s_%s"%("TTj1b",box)).getVal(),
                           w.var("Ntot_%s_%s"%("TTj2b",box)).getVal(),
                           w.var("Ntot_%s_%s"%("TTj2b",box)).getVal()*w.var("f3_%s_%s"%("TTj2b",box)).getVal()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			lnN	%.3f       1.00	1.00 1.00\n"%lumi_uncert)
            txtfile.write("lepton			lnN	%.3f       1.00	1.00 1.00\n"%lepton_uncert)
            txtfile.write("trigger			lnN	%.3f       1.00	1.00 1.00\n"%trigger_uncert)
            txtfile.write("Pdf			shape	%.2f       -	-	-\n"%(1./1.))
            txtfile.write("Jes			shape	%.2f       -	-	-\n"%(1./1.))
            txtfile.write("Btag			shape	%.2f       -	-	-\n"%(1./1.))
            txtfile.write("Isr			shape	%.2f       -	-	-\n"%(1./1.))
            normErr = 1.
            normErr += 2.*w.var("Ntot_%s_%s"%("TTj1b",box)).getError()/w.var("Ntot_%s_%s"%("TTj1b",box)).getVal()
            txtfile.write("bgNorm_%s_%s  	lnN   	1.00       %.3f	1.00	1.00\n"%
                          (bkgs[0],box,normErr))
            normErr = 1.
            normErr += 2.*w.var("Ntot_%s_%s"%("TTj2b",box)).getError()/w.var("Ntot_%s_%s"%("TTj2b",box)).getVal()
            txtfile.write("bgNorm_%s_%s  	lnN   	1.00       1.00	%.3f	1.00\n"%
                          (bkgs[1],box,normErr))
            normErr = 1.
            quadErr = rt.TMath.Power(w.var("Ntot_%s_%s"%("TTj2b",box)).getError()/w.var("Ntot_%s_%s"%("TTj2b",box)).getVal(),2.) 
            quadErr += rt.TMath.Power(w.var("f3_%s_%s"%("TTj2b",box)).getError()/w.var("f3_%s_%s"%("TTj2b",box)).getVal(),2.)
            normErr += 2.*rt.TMath.Sqrt(quadErr)
            txtfile.write("bgNorm_%s_%s  	lnN   	1.00       1.00	1.00	%.3f\n"%
                          (bkgs[2],box,normErr))
            for paramName in paramNames:
                if paramName.find("Ntot")!=-1 or paramName.find("f3")!=-1: continue
                txtfile.write("%s_%s	param	%e    %e\n"%(paramName,box,w.var("%s_%s"%(paramName,box)).getVal(), 2.*w.var("%s_%s"%(paramName,box)).getError()))
            
        txtfile.close()

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
    parser.add_option('-f','--xsec-file',dest="refXsecFile", default=None,metavar='FILE',
                  help="Reference signal cross section file")
    parser.add_option('-s','--sigma',dest="sigma", default=1.0,type="float",
                  help="Number of sigmas to fluctuate systematic uncertainties")
    parser.add_option('-m','--model',dest="model", default="T2tt",type="string",
                  help="SMS model string")
    parser.add_option('-r','--signal-region',dest="signalRegion", default="FULL",type="string",
                  help="signal region = FULL, HighMR")

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
    
    if glob.glob("../../lib/slc5_amd64_gcc472/libHiggsAnalysisCombinedLimit.so"):
        rt.gSystem.Load("../../lib/slc5_amd64_gcc472/libHiggsAnalysisCombinedLimit.so")
    else: 
        print "WARNING: NO HIGGS LIBRARY"
    if glob.glob("lib/libRazor.so"):
        rt.gSystem.Load("lib/libRazor.so")
    else: 
        print "WARNING: NO RAZOR LIBRARY"
        

    seed = 314159
    rt.RooRandom.randomGenerator().SetSeed(seed)
    box = options.box
    model = options.model
    infile = rt.TFile.Open(options.input,"READ")
    sigFile = rt.TFile.Open(args[0],"READ")
    mGluino = float(args[0].split("_")[-6])
    mLSP = float(args[0].split("_")[-4])
    massPoint = "MG_%f_MCHI_%f"%(mGluino, mLSP)
    refXsec = options.refXsec
    refXsecFile = options.refXsecFile
    if refXsecFile is not None:
        print "INFO: Input ref xsec file!"
        gluinoFile = rt.TFile.Open(refXsecFile,"READ")
        gluinoHistName = refXsecFile.split("/")[-1].split(".")[0]
        gluinoHist = gluinoFile.Get(gluinoHistName)
        refXsec = 1.e3*gluinoHist.GetBinContent(gluinoHist.FindBin(mGluino))
        print "INFO: ref xsec taken to be: %s mass %d, xsec = %f fb"%(gluinoHistName, mGluino, refXsec)
    outdir = options.outdir
    sigma = options.sigma
    signalRegion = options.signalRegion
    
    other_parameters = cfg.getVariables(box, "other_parameters")
    temp = rt.RooWorkspace("temp")
    for parameters in other_parameters:
        temp.factory(parameters)
        
    lumi = temp.var("lumi_value").getVal()
    lumi_uncert = temp.var("lumi_uncert").getVal()
    trigger_uncert = temp.var("trigger_uncert").getVal()
    lepton_uncert = temp.var("lepton_uncert").getVal()


    x = array('d', cfg.getBinning(box)[0])
    y = array('d', cfg.getBinning(box)[1])
    z = array('d', cfg.getBinning(box)[2])
    
    nBins = (len(x)-1)*(len(y)-1)*(len(z)-1)
    
    w = rt.RooWorkspace("w%s"%box)
    
    th1x = rt.RooRealVar("th1x","th1x",0,0,nBins)
    th1xBins = array('d',range(0,nBins+1))
    th1xRooBins = rt.RooBinning(nBins, th1xBins, "uniform")
    th1x.setBinning(th1xRooBins)

    th1xList = rt.RooArgList()
    th1xList.add(th1x)
    th1xSet = rt.RooArgSet()
    th1xSet.add(th1x)

    #channel = rt.RooCategory("channel","channel")
    #channel.defineType(box)

    RootTools.Utils.importToWS(w,th1x)
    #RootTools.Utils.importToWS(w,channel)
    
    histos = {}
    histos1d = {}

    
    if box in ["MuEle", "EleEle", "MuMu"]:
        initialBkgs = ["TTj1b"]
    elif box == "Jet2b":
        initialBkgs = ["TTj2b", "TTj3b"]
    else:
        initialBkgs = ["TTj1b", "TTj2b", "TTj3b"]
        
    print"\nINFO: retreiving %s box workspace\n"%box
    workspace = infile.Get("%s/Box%s_workspace"%(box,box))
    data = workspace.data("RMRTree")
    fr = workspace.obj("independentFR")

    #get the background nuisance parmeter names 
    parList = fr.floatParsFinal()
    paramNames = []
    for p in RootTools.RootIterator.RootIterator(parList):
        paramNames.append(p.GetName())

    print "INFO: background nuisance parameters are", paramNames

    bkgs = []
    bkgs.extend(initialBkgs)

    
    histos[box,model] = rt.TH3D("%s_%s_3d"%(box,model),"%s_%s_3d"%(box,model),len(x)-1,x,len(y)-1,y,len(z)-1,z)
    histos[box,"data"] = rt.TH3D("%s_%s_3d"%(box,"data"),"%s_%s_3d"%(box,"data"),len(x)-1,x,len(y)-1,y,len(z)-1,z)

    emptyHist3D = {}
    emptyHist3D[box] = rt.TH3D("EmptyHist3D_%s"%(box),"EmptyHist3D_%s"%(box),len(x)-1,x,len(y)-1,y,len(z)-1,z)
    RootTools.Utils.importToWS(w,emptyHist3D[box])


    def rescaleNorm(paramName, workspace, x, y):
        bkg = paramName.split("_")[-1]
        B = workspace.var("b_%s"%bkg).getVal()
        N = workspace.var("n_%s"%bkg).getVal()
        X0 = workspace.var("MR0_%s"%bkg).getVal()
        Y0 = workspace.var("R0_%s"%bkg).getVal()
        NTOT = workspace.var("Ntot_%s"%bkg).getVal()
        total_integral = Gfun(x[0],y[0],X0,Y0,B,N)-Gfun(x[0],y[-1],X0,Y0,B,N)-Gfun(x[-1],y[0],X0,Y0,B,N)+Gfun(x[-1],y[-1],X0,Y0,B,N)
        excl_integral = -Gfun(x[0],y[-1],X0,Y0,B,N)-Gfun(x[-1],y[0],X0,Y0,B,N)+Gfun(x[-1],y[-1],X0,Y0,B,N)+Gfun(x[0],y[1],X0,Y0,B,N)+Gfun(x[1],y[0],X0,Y0,B,N)-Gfun(x[1],y[1],X0,Y0,B,N)
        return NTOT*(excl_integral/total_integral)
    
    paramList = rt.RooArgList()
    for paramName in paramNames:
        paramList.add(workspace.var(paramName))
        paramValue = workspace.var(paramName).getVal()
        if paramName.find("Ntot")!=-1: 
            paramValue = rescaleNorm(paramName, workspace, x, y)
            print "rescaled %s[%e]"%(paramName,paramValue)
        w.factory("%s_%s[%e]"%(paramName,box,paramValue))
        w.var("%s_%s"%(paramName,box)).setError(workspace.var(paramName).getError())


    w.factory("MRCut_%s[%i,%i,%i]"%(box,x[1],x[1],x[1]))
    w.factory("RCut_%s[%e,%e,%e]"%(box,y[1],y[1],y[1]))
    
    zCut = 1
    BtagCut = {}
    for bkg in initialBkgs:
        w.factory("BtagCut_%s[%i,%i,%i]"%(bkg,zCut,zCut,zCut))
        zCut+=1
        


        
    #pdfList = rt.RooArgList()
    #coefList = rt.RooArgList()
    if box not in ["Jet2b"]:
        razorPdf_TTj1b = rt.RooRazor3DBinPdf("%s_%s"%(box,"TTj1b"),"razorPdf_%s_%s"%(box,"TTj1b"),
                                             w.var("th1x"),
                                             w.var("MR0_%s_%s"%("TTj1b",box)),w.var("R0_%s_%s"%("TTj1b",box)),
                                             w.var("b_%s_%s"%("TTj1b",box)),w.var("n_%s_%s"%("TTj1b",box)),
                                             w.var("MRCut_%s"%(box)),w.var("RCut_%s"%(box)),w.var("BtagCut_%s"%("TTj1b")),
                                             w.obj("EmptyHist3D_%s"%(box)))
        
        RootTools.Utils.importToWS(w,razorPdf_TTj1b)
        #pdfList.add(razorPdf_TTj1b)
        #coefList.add(w.var("Ntot_%s_%s"%("TTj1b",box)))
    if box not in ["MuEle","EleEle","MuMu"]:
        razorPdf_TTj2b = rt.RooRazor3DBinPdf("%s_%s"%(box,"TTj2b"),"razorPdf_%s_%s"%(box,"TTj2b"),
                                             w.var("th1x"),
                                             w.var("MR0_%s_%s"%("TTj2b",box)),w.var("R0_%s_%s"%("TTj2b",box)),
                                             w.var("b_%s_%s"%("TTj2b",box)),w.var("n_%s_%s"%("TTj2b",box)),
                                             w.var("MRCut_%s"%(box)),w.var("RCut_%s"%(box)),w.var("BtagCut_%s"%("TTj2b")),
                                             w.obj("EmptyHist3D_%s"%(box)))
        
        RootTools.Utils.importToWS(w,razorPdf_TTj2b)
        razorPdf_TTj3b = rt.RooRazor3DBinPdf("%s_%s"%(box,"TTj3b"),"razorPdf_%s_%s"%(box,"TTj3b"),
                                             w.var("th1x"),
                                             w.var("MR0_%s_%s"%("TTj2b",box)),w.var("R0_%s_%s"%("TTj2b",box)),
                                             w.var("b_%s_%s"%("TTj2b",box)),w.var("n_%s_%s"%("TTj2b",box)),
                                             w.var("MRCut_%s"%(box)),w.var("RCut_%s"%(box)),w.var("BtagCut_%s"%("TTj3b")),
                                             w.obj("EmptyHist3D_%s"%(box)))       
        RootTools.Utils.importToWS(w,razorPdf_TTj3b)
        
        #razorPdf_TTj23b = rt.RooAddPdf("razorPdf_TTj23b_%s"%(box),"razorPdf_TTj23b_%s"%(box),razorPdf_TTj3b,razorPdf_TTj2b,w.var("f3_%s_%s"%("TTj2b",box)))
        #pdfList.add(razorPdf_TTj23b)
        #coefList.add(w.var("Ntot_%s_%s"%("TTj2b",box)))
        
    #razorPdf = rt.RooAddPdf("razorPdf_%s"%(box),"razorPdf_%s"%(box),pdfList,coefList)
    #RootTools.Utils.importToWS(w,razorPdf)
        
    print "\nINFO: %s box fit result!\n"%box
    fr.Print("v")
    
    cen = [workspace.var(paramName).getVal() for paramName in paramNames]
    err = [workspace.var(paramName).getError() for paramName in paramNames]
        
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
    data_obs = data_obs.reduce(getCutString(box,signalRegion))
    data_obs.SetName("data_obs")
    
    data_obs.fillHistogram(histos[box,"data"],rt.RooArgList(MR,Rsq,nBtag))


    # SIGNAL HISTOGRAMS 
    wHisto = sigFile.Get('wHisto_pdferr_nom')
    btagUp =  sigFile.Get('wHisto_btagerr_up')
    btagDown =  sigFile.Get('wHisto_btagerr_down')
    
    jesUp =  sigFile.Get('wHisto_JESerr_up')
    jesDown =  sigFile.Get('wHisto_JESerr_down')
    isrUp =  sigFile.Get('wHisto_ISRerr_up')
    isrDown =  sigFile.Get('wHisto_ISRerr_down')
    
    pdf =  sigFile.Get('wHisto_pdferr_pe')

    # adding signal shape systematics
    print "\nINFO: Now obtaining signal shape systematics\n"
    
    histos[(box,"%s_IsrUp"%(model))] = rebin3d(isrUp,x,y,z, box, signalRegion)
    histos[(box,"%s_IsrDown"%(model))] = rebin3d(isrDown,x,y,z, box, signalRegion)
    
    histos[(box,"%s_BtagUp"%(model))] = rebin3d(btagUp,x,y,z, box, signalRegion)
    histos[(box,"%s_BtagDown"%(model))] = rebin3d(btagDown,x,y,z, box, signalRegion)

    histos[(box,"%s_JesUp"%(model))] = rebin3d(jesUp,x,y,z, box, signalRegion)
    histos[(box,"%s_JesDown"%(model))] = rebin3d(jesDown,x,y,z, box, signalRegion)
    
    pdfUp = wHisto.Clone("%s_%s_PdfUp_3d"%(box,model))
    pdfUp.SetTitle("%s_%s_PdfUp_3d"%(box,model))
    pdfDown = wHisto.Clone("%s_%s_PdfDown_3d"%(box,model))
    pdfDown.SetTitle("%s_%s_PdfDown_3d"%(box,model))
    pdfAbs = pdf.Clone("PdfAbs_3d")
    pdfAbs.Multiply(wHisto)
    pdfUp.Add(pdfAbs,1.0)
    pdfDown.Add(pdfAbs,-1.0)
    histos[(box,"%s_PdfUp"%(model))] = rebin3d(pdfUp,x,y,z, box, signalRegion)
    histos[(box,"%s_PdfDown"%(model))] = rebin3d(pdfDown,x,y,z, box, signalRegion)
    
    #set the per box eff value
    sigNorm = wHisto.Integral()
    sigEvents = sigNorm*lumi*refXsec
    print "\nINFO: now multiplying:  efficiency x lumi x refXsec = %f x %f x %f = %f"%(sigNorm,lumi,refXsec,sigEvents)
    
    histos[box,model] = rebin3d(wHisto.Clone("%s_%s_3d"%(box,model)), x, y, z, box, signalRegion)
    histos[box,model].SetTitle("%s_%s_3d"%(box,model))
    histos[box,model].Scale(lumi*refXsec)
    
    for paramName in ["Jes","Isr","Btag","Pdf"]:
        print "\nINFO: Now renormalizing signal shape systematic histograms to nominal\n"
        print "signal shape variation %s"%paramName
        for syst in ['Up','Down']:
            if histos[box,"%s_%s%s"%(model,paramName,syst)].Integral() > 0:
                histos[box,"%s_%s%s"%(model,paramName,syst)].Scale( histos[box,model].Integral()/histos[box,"%s_%s%s"%(model,paramName,syst)].Integral())

    #unroll histograms 3D -> 1D
    print "\nINFO: Now Unrolling 3D histograms\n" 
    dataHist = {}
    for index, histo in histos.iteritems():
        box, bkg = index
        print box, bkg
        totalbins = (len(x)-1)*(len(y)-1)*(len(z)-1)
        if bkg=="data":
            histos1d[box,bkg] = rt.TH1D("data_obs","data_obs",totalbins, 0, totalbins)
        else:
            histos1d[box,bkg] = rt.TH1D("%s_%s"%(box,bkg),"%s_%s"%(box,bkg),totalbins, 0, totalbins)
            
        totalbins = histos1d[box,bkg].GetNbinsX()
        newbin = 0
        for i in xrange(1,histo.GetNbinsX()+1):
            for j in xrange(1,histo.GetNbinsY()+1):
                for k in xrange(1,histo.GetNbinsZ()+1):
                    newbin += 1
                    histos1d[box,bkg].SetBinContent(newbin,histo.GetBinContent(i,j,k))
                        
        if bkg=="data":
            #dataHist[box,bkg] = rt.RooDataHist("data_obs", "data_obs", th1xList, rt.RooFit.Index(channel),rt.RooFit.Import(box,histos1d[box,bkg]))
            dataHist[box,bkg] = rt.RooDataHist("data_obs", "data_obs", th1xList, rt.RooFit.Import(histos1d[box,bkg]))
        else:
            dataHist[box,bkg] = rt.RooDataHist("%s_%s"%(box,bkg), "%s_%s"%(box,bkg), th1xList, rt.RooFit.Import(histos1d[box,bkg]))

        RootTools.Utils.importToWS(w,dataHist[box,bkg])
    print "\nINFO: Now writing data card\n"

    w.Print("v")
    writeDataCard(box,model,massPoint,"%s/razor_combine_%s_%s_%s.txt"%(outdir,box,model,massPoint),initialBkgs,paramNames,w,lumi_uncert,trigger_uncert,lepton_uncert)
    os.system("cat %s/razor_combine_%s_%s_%s.txt \n"%(outdir,box,model,massPoint)) 
    
    outFile = rt.TFile.Open("%s/razor_combine_%s_%s_%s.root"%(outdir,box,model,massPoint),"RECREATE")
    outFile.cd()
    w.Write()
    outFile.Close()
