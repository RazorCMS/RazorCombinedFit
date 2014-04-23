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



def getBinEvents(i, j, k, x, y, z, workspace):
    errorFlag = False
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

    fr = workspace.obj("independentFR")
    parList = fr.floatParsFinal()
    
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

    if (z[k-1]==1) :
        bin_events =  NTOT*integral/total_integral
    elif (z[k-1]==2) : 
        bin_events = (1.-F3)*NTOT*integral/total_integral
    elif (z[k-1]==3) : 
        bin_events =  F3*NTOT*integral/total_integral

    if bin_events <= 0:
        errorFlag = True
        print "\nERROR: bin razor pdf integral =", integral
        print "\nERROR: total razor pdf integral =", total_integral
        return 0., errorFlag
    return bin_events, errorFlag

def getBinningData(box):
    if box in ["Jet2b", "MultiJet"]:
        MRbins =  [400, 450, 500, 550, 600, 700, 800, 900, 1200, 1600, 2000, 3000, 4000]
        Rsqbins = [0.25,0.30,0.35,0.41,0.52,0.64,0.80,1.1,1.5]
    else:        
        MRbins =  [300, 350, 400, 450, 500, 550, 600, 700, 800, 900, 1200, 1600, 2000, 3000, 4000]
        Rsqbins = [0.15,0.20,0.25,0.35,0.41,0.52,0.64,0.80,1.1,1.5]
    if box in ["Jet2b"]: 
        nBtagbins = [2.,3.,4.]
    elif box in ["MuEle","EleEle","MuMu"]: 
        nBtagbins = [1.,4.]
    else: 
        nBtagbins = [1.,2.,3.,4.]
    return MRbins, Rsqbins, nBtagbins

def getCutString(box, signalRegion):
    if box in ["Jet2b","MultiJet"]:
        if signalRegion=="FULL":
            return "(MR>=400.&&Rsq>=0.25&&(MR>=450.||Rsq>=0.3))&&Rsq<1.5&&MR<4000."
        elif signalRegion=="HighMR":
            return "(MR>=550.&&Rsq>=0.3)&&Rsq<1.5&&MR<4000."
    else:
        if signalRegion=="FULL":
            return "(MR>=300.&&Rsq>=0.15&&(MR>=350.||Rsq>=0.2))&&Rsq<1.5&&MR<4000."
        elif signalRegion=="HighMR":
            return "(MR>=450.&&Rsq>=0.2)&&Rsq<1.5&&MR<4000."
                
def passCut(MRVal, RsqVal, box, signalRegion):
    passBool = False
    if box in ["Jet2b","MultiJet"]:
        if signalRegion=="FULL":
            if MRVal >= 400. and RsqVal >= 0.25 and (MRVal >= 450. or RsqVal >= 0.3) and MRVal < 4000. and RsqVal < 1.5: passBool = True
        elif signalRegion=="HighMR":
            if MRVal >= 550. and RsqVal >= 0.3 and MRVal < 4000. and RsqVal < 1.5: passBool = True
    else:
        if signalRegion=="FULL":
            if MRVal >= 300. and RsqVal >= 0.15 and (MRVal >= 350. or RsqVal >= 0.2) and MRVal < 4000. and RsqVal < 1.5: passBool = True
        elif signalRegion=="HighMR":
            if MRVal >= 450. and RsqVal >= 0.2 and MRVal < 4000. and RsqVal < 1.5: passBool = True

    return passBool

def average3d(oldhisto, x, y):
    newhisto = rt.TH3D(oldhisto.GetName()+"_average",oldhisto.GetTitle()+"_average",len(x)-1,x,len(y)-1,y,len(z)-1,z)
    for i in range(1,oldhisto.GetNbinsX()+1):
        for j in range(1,oldhisto.GetNbinsY()+1):
            for k in range(1,oldhisto.GetNbinsZ()+1):
                xold = oldhisto.GetXaxis().GetBinCenter(i)
                yold = oldhisto.GetYaxis().GetBinCenter(j)
                zold = oldhisto.GetZaxis().GetBinCenter(k)
                oldbincontent = oldhisto.GetBinContent(i,j,k)

                numCells = 9.
                totalweight = 0.
                mindistance = 10000.
                
                for deltaI in [-3, -2, -1, 0, 1, 2, 3]:
                    for deltaJ in [-3, -2, -1, 0, 1, 2, 3]:
                        xnew = oldhisto.GetXaxis().GetBinCenter(i+deltaI)
                        ynew = oldhisto.GetYaxis().GetBinCenter(j+deltaJ)
                        if i+deltaI<=0 or j+deltaJ<=0 or i+deltaI>=oldhisto.GetNbinsX()+1 or j+deltaJ>=oldhisto.GetNbinsY()+1: 
                            numCells -= 1. 
                            continue
                        if (deltaI, deltaJ) == (0, 0): 
                            totalweight += 100.
                            #totalweight += 100. # adding in this weight later.
                        elif rt.TMath.Abs(deltaI)<=1 and rt.TMath.Abs(deltaJ)<=1:
                            distance = rt.TMath.Power((xold-xnew)/(400.),2) + rt.TMath.Power((yold-ynew)/(0.3),2)
                            if distance < mindistance: mindistance = distance
                            #totalweight += rt.TMath.Exp(-distance)
                            totalweight += 1. 
                        elif rt.TMath.Abs(deltaI)<=2 and rt.TMath.Abs(deltaJ)<=2:
                            totalweight += 0.1
                        else:
                            totalweight += 0.01
                #totalweight += 30./mindistance # for (0,0) weight
                            
                for deltaI in [-3, -2, -1, 0, 1, 2, 3]:
                    for deltaJ in [-3, -2, -1, 0, 1, 2, 3]:
                        if i+deltaI<=0 or j+deltaJ<=0 or i+deltaI>=oldhisto.GetNbinsX()+1 or j+deltaJ>=oldhisto.GetNbinsY()+1: continue
                        xnew = oldhisto.GetXaxis().GetBinCenter(i+deltaI)
                        ynew = oldhisto.GetYaxis().GetBinCenter(j+deltaJ)
                        if (deltaI, deltaJ) == (0, 0): 
                            weight = 100.
                            #weight = 30./mindistance
                        elif rt.TMath.Abs(deltaI)<=1 and rt.TMath.Abs(deltaJ)<=1:
                            weight = 1.
                        elif rt.TMath.Abs(deltaI)<=2 and rt.TMath.Abs(deltaJ)<=2:
                            weight = 0.1
                        else: 
                             distance = rt.TMath.Power((xold-xnew)/(400.),2) + rt.TMath.Power((yold-ynew)/(0.3),2)
                             weight = 0.01
                             #weight = 1./distance
                             #weight = rt.TMath.Exp(-distance)
                        if passCut(xnew, ynew, box, signalRegion): 
                            newhisto.Fill(xnew, ynew, zold, (weight/totalweight)*oldbincontent)
    return newhisto

def rebin3d(oldhisto, x, y, z, box, signalRegion, average=False):
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
    if average: 
        print "AVERAGING!"
        newhistoaverage = average3d(newhisto,x,y)
        return newhistoaverage
    else:
        return newhisto

def rebin3dCoarse(oldhisto, xCoarse, yCoarse, zCoarse, xFine, yFine, zFine, box, signalRegion):
    print xCoarse
    print xFine
    print yCoarse
    print yFine
    newhistoCoarse = rt.TH3D(oldhisto.GetName()+"_coarse",oldhisto.GetTitle()+"_coarse",len(xCoarse)-1,xCoarse,len(yCoarse)-1,yCoarse,len(zCoarse)-1,zCoarse)
    newhistoCounts = rt.TH3D(oldhisto.GetName()+"_counts",oldhisto.GetTitle()+"_counts",len(xCoarse)-1,xCoarse,len(yCoarse)-1,yCoarse,len(zCoarse)-1,zCoarse)
    newhisto = rt.TH3D(oldhisto.GetName()+"_fine",oldhisto.GetTitle()+"_fine",len(xFine)-1,xFine,len(yFine)-1,yFine,len(zFine)-1,zFine)
    
    for i in range(1,oldhisto.GetNbinsX()+1):
        for j in range(1,oldhisto.GetNbinsY()+1):
            for k in range(1,oldhisto.GetNbinsZ()+1):
                xold = oldhisto.GetXaxis().GetBinCenter(i)
                yold = oldhisto.GetYaxis().GetBinCenter(j)
                zold = oldhisto.GetZaxis().GetBinCenter(k)
                if not passCut(xold, yold, box, signalRegion): continue
                oldbincontent = oldhisto.GetBinContent(i,j,k)
                newhistoCoarse.Fill(xold, yold, zold, max(0.,oldbincontent))
                newhistoCounts.Fill(xold, yold, zold)

    for i in range(1,newhisto.GetNbinsX()+1):
        for j in range(1,newhisto.GetNbinsY()+1):
            for k in range(1,newhisto.GetNbinsZ()+1):
                newhisto.SetBinContent(i,j,k,0.)
                xnew = newhisto.GetXaxis().GetBinCenter(i)
                ynew = newhisto.GetYaxis().GetBinCenter(j)
                znew = newhisto.GetZaxis().GetBinCenter(k)
                if not passCut(xnew, ynew, box, signalRegion): continue
                newYield = newhistoCoarse.GetBinContent(newhistoCoarse.FindBin(xnew,ynew,znew))
                numBins = newhistoCounts.GetBinContent(newhistoCounts.FindBin(xnew,ynew,znew))
                newhisto.SetBinContent(i,j,k,newYield/numBins)
                
    return newhisto
    
def writeDataCard(box,model,massPoint,txtfileName,bkgs,paramNames,w,lumi_uncert,trigger_uncert,lepton_uncert,penalty):
        txtfile = open(txtfileName,"w")
        txtfile.write("imax 1 number of channels\n")
        if box in ["MuEle","MuMu","EleEle"]:
            nBkgd = 1
            #nNuis = 12
            nNuis = 7
            txtfile.write("jmax %i number of backgrounds\n"%nBkgd)
            #txtfile.write("kmax %i number of nuisance parameters\n"%nNuis)
        elif box in ["Jet2b"]:
            nBkgd = 2
            #nNuis = 13
            nNuis = 7
            txtfile.write("jmax %i number of backgrounds\n"%nBkgd)
            #txtfile.write("kmax %i number of nuisance parameters\n"%nNuis)
        else:
            nBkgd = 3
            #nNuis = 18
            nNuis = 7
            txtfile.write("jmax %i number of backgrounds\n"%nBkgd)
            #txtfile.write("kmax %i number of nuisance parameters\n"%nNuis)
        txtfile.write("kmax * number of nuisance parameters\n")
        txtfile.write("------------------------------------------------------------\n")
        txtfile.write("observation	%.3f\n"%
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
                          (w.data("%s_%s"%(box,model)).sumEntries(),w.var("%s_%s_norm"%(box,"TTj1b")).getVal()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			lnN	%.3f       1.00\n"%lumi_uncert)
            txtfile.write("lepton			lnN	%.3f       1.00\n"%lepton_uncert)
            txtfile.write("trigger			lnN	%.3f       1.00\n"%trigger_uncert)
            txtfile.write("Pdf			shape	%.2f       -\n"%(1./1.))
            txtfile.write("Jes			shape	%.2f       -\n"%(1./1.))
            txtfile.write("Btag			shape	%.2f       -\n"%(1./1.))
            txtfile.write("Isr			shape	%.2f       -\n"%(1./1.))
            if penalty:
                normErr = 1.0+w.var("%s_%s_norm"%(box,bkgs[0])).getError()/w.var("%s_%s_norm"%(box,bkgs[0])).getVal()
                txtfile.write("%s_%s_norm  	lnN   	1.00       %.3f\n"%
                              (box,bkgs[0],normErr))
            else:
                txtfile.write("%s_%s_norm  	flatParam\n"%
                              (box,bkgs[0]))
        elif box in ["Jet2b"]:
            txtfile.write("bin		%s			%s			%s\n"%(box,box,box))
            txtfile.write("process		%s_%s 	%s_%s	%s_%s\n"%
                          (box,model,box,bkgs[0],box,bkgs[1]))
            txtfile.write("process        	0          		1			2\n")
            txtfile.write("rate            %.3f		%.3f		%.3f\n"%
                          (w.data("%s_%s"%(box,model)).sumEntries(),w.var("%s_%s_norm"%(box,"TTj2b")).getVal(),
                           w.var("%s_%s_norm"%(box,"TTj3b")).getVal()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			lnN	%.3f       1.00 1.00\n"%lumi_uncert)
            txtfile.write("lepton			lnN	%.3f       1.00 1.00\n"%lepton_uncert)
            txtfile.write("trigger			lnN	%.3f       1.00 1.00\n"%trigger_uncert)
            txtfile.write("Pdf			shape	%.2f       -	-\n"%(1./1.))
            txtfile.write("Jes			shape	%.2f       -	-\n"%(1./1.))
            txtfile.write("Btag			shape	%.2f       -	-\n"%(1./1.))
            txtfile.write("Isr			shape	%.2f       -	-\n"%(1./1.))
            if penalty:
                normErr = 1.0+w.var("%s_%s_norm"%(box,bkgs[0])).getError()/w.var("%s_%s_norm"%(box,bkgs[0])).getVal()
                txtfile.write("%s_%s_norm  	lnN   	1.00       %.3f	1.00\n"%
                              (box,bkgs[0],normErr))
                normErr = 1.0+w.var("%s_%s_norm"%(box,bkgs[1])).getError()/w.var("%s_%s_norm"%(box,bkgs[1])).getVal()
                txtfile.write("%s_%s_norm  	lnN   	1.00       1.00	%.3f\n"%
                              (box,bkgs[1],normErr))
            else:
                txtfile.write("%s_%s_norm  	flatParam\n"%
                              (box,bkgs[0]))
                txtfile.write("%s_%s_norm  	flatParam\n"%
                              (box,bkgs[1]))
        else:
            txtfile.write("bin		%s			%s			%s			%s\n"%(box,box,box,box))
            txtfile.write("process		%s_%s 	%s_%s	%s_%s	%s_%s\n"%
                          (box,model,box,bkgs[0],box,bkgs[1],box,bkgs[2]))
            txtfile.write("process        	0          		1			2			3\n")
            txtfile.write("rate            %.3f		%.3f		%.3f		%.3f\n"%
                          (w.data("%s_%s"%(box,model)).sumEntries(),w.var("%s_%s_norm"%(box,"TTj1b")).getVal(),
                           w.var("%s_%s_norm"%(box,"TTj2b")).getVal(),w.var("%s_%s_norm"%(box,"TTj3b")).getVal()))
            txtfile.write("------------------------------------------------------------\n")
            txtfile.write("lumi			lnN	%.3f       1.00	1.00 1.00\n"%lumi_uncert)
            txtfile.write("lepton			lnN	%.3f       1.00	1.00 1.00\n"%lepton_uncert)
            txtfile.write("trigger			lnN	%.3f       1.00	1.00 1.00\n"%trigger_uncert)
            txtfile.write("Pdf			shape	%.2f       -	-	-\n"%(1./1.))
            txtfile.write("Jes			shape	%.2f       -	-	-\n"%(1./1.))
            txtfile.write("Btag			shape	%.2f       -	-	-\n"%(1./1.))
            txtfile.write("Isr			shape	%.2f       -	-	-\n"%(1./1.))
            if penalty:
                normErr = 1.0+w.var("%s_%s_norm"%(box,bkgs[0])).getError()/w.var("%s_%s_norm"%(box,bkgs[0])).getVal()
                txtfile.write("%s_%s_norm  	lnN   	1.00       %.3f	1.00	1.00\n"%
                              (box,bkgs[0],normErr))
                normErr = 1.0+w.var("%s_%s_norm"%(box,bkgs[1])).getError()/w.var("%s_%s_norm"%(box,bkgs[1])).getVal()
                txtfile.write("%s_%s_norm  	lnN   	1.00       1.00	%.3f	1.00\n"%
                              (box,bkgs[1],normErr))
                normErr = 1.0+w.var("%s_%s_norm"%(box,bkgs[2])).getError()/w.var("%s_%s_norm"%(box,bkgs[2])).getVal()
                txtfile.write("%s_%s_norm  	lnN   	1.00       1.00	1.00	%.3f\n"%
                              (box,bkgs[2],normErr))
            else:
                txtfile.write("%s_%s_norm  	flatParam\n"%
                              (box,bkgs[0]))
                txtfile.write("%s_%s_norm  	flatParam\n"%
                              (box,bkgs[1]))
                txtfile.write("%s_%s_norm  	flatParam\n"%
                              (box,bkgs[2]))
        errorMult = 1.
        for paramName in paramNames:
            if paramName.find("Ntot")!=-1 or paramName.find("f3")!=-1: continue
            if penalty: 
                txtfile.write("%s_%s	param	%e    %e\n"%(paramName,box,w.var("%s_%s"%(paramName,box)).getVal(), errorMult*w.var("%s_%s"%(paramName,box)).getError()))
            else:
                txtfile.write("%s_%s  	flatParam\n"%
                              (paramName,box))
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
    parser.add_option('-e','--expected-a-priori',dest="expected_a_priori", default=False,action='store_true',
                  help="expected a priori")
    parser.add_option('-p','--penalty',dest="penalty", default=False,action='store_true',
                  help="multiply by penalty terms")

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

    try: 
        os.environ['CMSSW_BASE']
        loadVal = rt.gSystem.Load("${CMSSW_BASE}/lib/slc5_amd64_gcc472/libHiggsAnalysisCombinedLimit.so")
        if loadVal == -1:
            print "WARNING: NO HIGGS LIBRARY"
        loadVal = rt.gSystem.Load("${CMSSW_BASE}/src/RazorCombinedFit/lib/libRazor.so")
        if loadVal == -1:
            print "WARNING: NO RAZOR LIBRARY"         
    except: 
        print "no CMSSW"
        loadVal = rt.gSystem.Load("lib/libRazor.so")
        if loadVal == -1:
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
    expected_a_priori = options.expected_a_priori
    penalty = options.penalty
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
    expected_a_priori = options.expected_a_priori
    
    other_parameters = cfg.getVariables(box, "other_parameters")
    temp = rt.RooWorkspace("temp")
    for parameters in other_parameters:
        temp.factory(parameters)
        
    lumi = temp.var("lumi_value").getVal()
    lumi_uncert = temp.var("lumi_uncert").getVal()
    trigger_uncert = temp.var("trigger_uncert").getVal()
    lepton_uncert = temp.var("lepton_uncert").getVal()


    xSignal = array('d', cfg.getBinning(box)[0])
    ySignal = array('d', cfg.getBinning(box)[1])
    zSignal = array('d', cfg.getBinning(box)[2])

    x = array('d', getBinningData(box)[0])
    y = array('d', getBinningData(box)[1])
    z = array('d', getBinningData(box)[2])
    
    w = rt.RooWorkspace("w%s"%box)

    nMaxBins = 378
    #for testBox in ["MuEle", "EleEle", "MuMu", "MuMultiJet", "MuJet", "EleMultiJet", "EleJet", "MultiJet", "Jet2b"]:
    #    xTest = array('d', cfg.getBinning(testBox)[0])
    #    yTest = array('d', cfg.getBinning(testBox)[1])
    #    zTest = array('d', cfg.getBinning(testBox)[2])
    #    nTestBins = (len(xTest)-1)*(len(yTest)-1)*(len(zTest)-1)
    #    if nTestBins  > nMaxBins: nMaxBins = nTestBins
            
    nBins = nMaxBins    
    
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

    for bkg in bkgs:
        histos[box,bkg] = rt.TH3D("%s_%s_3d"%(box,bkg),"%s_%s_3d"%(box,bkg),len(x)-1,x,len(y)-1,y,len(z)-1,z)
    
    for bkg in initialBkgs:
        if bkg=="TTj3b": continue
        for i in xrange(1,len(x)):
            for j in xrange(1,len(y)):
                for k in xrange(1, len(z)):
                    if not passCut(x[i-1],y[j-1], box, signalRegion): continue
                    bin_events, errorFlag = getBinEvents(i,j,k,x,y,z,workspace)
                    if (bkg.find("1b")!=-1 and z[k-1]==1) :
                        histos[box,bkg].SetBinContent(i,j,k,bin_events)
                    elif (bkg.find("2b")!=-1 and z[k-1]==2) : 
                        histos[box,bkg].SetBinContent(i,j,k,bin_events)
                    elif (bkg.find("2b")!=-1 and z[k-1]==3) : 
                        histos[box,"TTj3b"].SetBinContent(i,j,k,bin_events)

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
        w.var("%s_%s"%(paramName,box)).setConstant(False)
        if paramName.find("n_")!=-1:
            w.var("%s_%s"%(paramName,box)).setMin(0.1)
        if paramName.find("b_")!=-1:
            w.var("%s_%s"%(paramName,box)).setMin(0.0001)
        elif paramName.find("MR0_")!=-1:
            w.var("%s_%s"%(paramName,box)).setMax(x[0])
        elif paramName.find("R0_")!=-1:
            w.var("%s_%s"%(paramName,box)).setMax(y[0])
            

    w.factory("MRCut_%s[%i]"%(box,x[0]+50.))
    w.factory("RCut_%s[%e]"%(box,y[0]+0.05))
    w.var("MRCut_%s"%box).setConstant(True)
    w.var("RCut_%s"%box).setConstant(True)
  
    if box not in ["Jet2b"]:
        w.factory("BtagCut_TTj1b[1]")
        w.var("BtagCut_TTj1b").setConstant(True)
    if box not in ["MuEle","EleEle","MuMu"]:
        w.factory("BtagCut_TTj2b[2]")
        w.var("BtagCut_TTj2b").setConstant(True)
        w.factory("BtagCut_TTj3b[3]")
        w.var("BtagCut_TTj3b").setConstant(True)
        

    pdfList = rt.RooArgList()
    #coefList = rt.RooArgList()
    if box not in ["Jet2b"]:
        razorPdf_TTj1b = rt.RooRazor3DBinPdf("%s_%s"%(box,"TTj1b"),"razorPdf_%s_%s"%(box,"TTj1b"),
                                             w.var("th1x"),
                                             w.var("MR0_%s_%s"%("TTj1b",box)),w.var("R0_%s_%s"%("TTj1b",box)),
                                             w.var("b_%s_%s"%("TTj1b",box)),w.var("n_%s_%s"%("TTj1b",box)),
                                             w.var("MRCut_%s"%(box)),w.var("RCut_%s"%(box)),w.var("BtagCut_%s"%("TTj1b")),
                                             w.obj("EmptyHist3D_%s"%(box)))
        w.factory("%s_%s_norm[%f,0,1e6]"%(box,"TTj1b",w.var("Ntot_TTj1b_%s"%box).getVal()))
        w.var("%s_%s_norm"%(box,"TTj1b")).setError(w.var("Ntot_TTj1b_%s"%box).getError())
        extRazorPdf_TTj1b = rt.RooExtendPdf("ext%s_%s"%(box,"TTj1b"),"extRazorPdf_%s_%s"%(box,"TTj1b"),razorPdf_TTj1b,w.var("%s_TTj1b_norm"%box))
        RootTools.Utils.importToWS(w,extRazorPdf_TTj1b)
        pdfList.add(extRazorPdf_TTj1b)
        #coefList.add(w.var("Ntot_%s_%s"%("TTj1b",box)))
    if box not in ["MuEle","EleEle","MuMu"]:
        razorPdf_TTj2b = rt.RooRazor3DBinPdf("%s_%s"%(box,"TTj2b"),"razorPdf_%s_%s"%(box,"TTj2b"),
                                             w.var("th1x"),
                                             w.var("MR0_%s_%s"%("TTj2b",box)),w.var("R0_%s_%s"%("TTj2b",box)),
                                             w.var("b_%s_%s"%("TTj2b",box)),w.var("n_%s_%s"%("TTj2b",box)),
                                             w.var("MRCut_%s"%(box)),w.var("RCut_%s"%(box)),w.var("BtagCut_%s"%("TTj2b")),
                                             w.obj("EmptyHist3D_%s"%(box)))        
        val = w.var("Ntot_TTj2b_%s"%box).getVal() * (1.0 - w.var("f3_TTj2b_%s"%box).getVal())
        w.factory("%s_%s_norm[%f,0,1e6]"%(box,"TTj2b", val ))
        w.var("%s_%s_norm"%(box,"TTj2b")).setError(w.var("Ntot_TTj2b_%s"%box).getError() *(1.0- w.var("f3_TTj2b_%s"%box).getVal()))
        extRazorPdf_TTj2b = rt.RooExtendPdf("ext%s_%s"%(box,"TTj2b"),"extRazorPdf_%s_%s"%(box,"TTj2b"),razorPdf_TTj2b,w.var("%s_TTj2b_norm"%box))
        RootTools.Utils.importToWS(w,extRazorPdf_TTj2b)
        pdfList.add(extRazorPdf_TTj2b)
        
        razorPdf_TTj3b = rt.RooRazor3DBinPdf("%s_%s"%(box,"TTj3b"),"razorPdf_%s_%s"%(box,"TTj3b"),
                                             w.var("th1x"),
                                             w.var("MR0_%s_%s"%("TTj2b",box)),w.var("R0_%s_%s"%("TTj2b",box)),
                                             w.var("b_%s_%s"%("TTj2b",box)),w.var("n_%s_%s"%("TTj2b",box)),
                                             w.var("MRCut_%s"%(box)),w.var("RCut_%s"%(box)),w.var("BtagCut_%s"%("TTj3b")),
                                             w.obj("EmptyHist3D_%s"%(box)))
        val = w.var("Ntot_TTj2b_%s"%box).getVal() * w.var("f3_TTj2b_%s"%box).getVal()
        w.factory("%s_%s_norm[%f,0,1e6]"%(box,"TTj3b",val))
        w.var("%s_%s_norm"%(box,"TTj3b")).setError(w.var("Ntot_TTj2b_%s"%box).getError() * w.var("f3_TTj2b_%s"%box).getVal())
        extRazorPdf_TTj3b = rt.RooExtendPdf("ext%s_%s"%(box,"TTj3b"),"extRazorPdf_%s_%s"%(box,"TTj3b"),razorPdf_TTj3b,w.var("%s_TTj3b_norm"%box))
        RootTools.Utils.importToWS(w,extRazorPdf_TTj3b)
        
        #razorPdf_TTj23b = rt.RooAddPdf("razorPdf_TTj23b_%s"%(box),"razorPdf_TTj23b_%s"%(box),razorPdf_TTj3b,razorPdf_TTj2b,w.var("f3_%s_%s"%("TTj2b",box)))
        pdfList.add(extRazorPdf_TTj3b)
        #coefList.add(w.var("Ntot_%s_%s"%("TTj2b",box)))
        
    razorPdf = rt.RooAddPdf("razorPdf_%s"%(box),"razorPdf_%s"%(box),pdfList)
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
    wHisto = sigFile.Get('wHisto')
    btagUp =  sigFile.Get('wHisto_btagerr_up')
    btagDown =  sigFile.Get('wHisto_btagerr_down')
    
    jesUp =  sigFile.Get('wHisto_JESerr_up')
    jesDown =  sigFile.Get('wHisto_JESerr_down')
    isrUp =  sigFile.Get('wHisto_ISRerr_up')
    isrDown =  sigFile.Get('wHisto_ISRerr_down')
    
    pdf =  sigFile.Get('wHisto_pdferr_pe')

    # adding signal shape systematics
    print "\nINFO: Now obtaining signal shape systematics\n"
    
    histos[(box,"%s_IsrUp"%(model))] = rebin3dCoarse(isrUp,xSignal,ySignal,zSignal, x, y, z, box, signalRegion)
    histos[(box,"%s_IsrDown"%(model))] = rebin3dCoarse(isrDown,xSignal,ySignal,zSignal, x, y, z, box, signalRegion)
    
    histos[(box,"%s_BtagUp"%(model))] = rebin3dCoarse(btagUp,xSignal,ySignal,zSignal, x, y, z, box, signalRegion)
    histos[(box,"%s_BtagDown"%(model))] = rebin3dCoarse(btagDown,xSignal,ySignal,zSignal, x, y, z, box, signalRegion)

    histos[(box,"%s_JesUp"%(model))] = rebin3dCoarse(jesUp,xSignal,ySignal,zSignal, x, y, z, box, signalRegion)
    histos[(box,"%s_JesDown"%(model))] = rebin3dCoarse(jesDown,xSignal,ySignal,zSignal, x, y, z, box, signalRegion)

    
    pdfUp = wHisto.Clone("%s_%s_PdfUp_3d"%(box,model))
    pdfUp.SetTitle("%s_%s_PdfUp_3d"%(box,model))
    pdfDown = wHisto.Clone("%s_%s_PdfDown_3d"%(box,model))
    pdfDown.SetTitle("%s_%s_PdfDown_3d"%(box,model))
    pdfAbs = pdf.Clone("PdfAbs_3d")
    pdfAbs.Multiply(wHisto)
    pdfUp.Add(pdfAbs,1.0)
    pdfDown.Add(pdfAbs,-1.0)
    histos[(box,"%s_PdfUp"%(model))] = rebin3dCoarse(pdfUp,xSignal,ySignal,zSignal, x, y, z, box, signalRegion)
    histos[(box,"%s_PdfDown"%(model))] = rebin3dCoarse(pdfDown,xSignal,ySignal,zSignal, x, y, z, box, signalRegion)
    
    #set the per box eff value
    pdfNom = rebin3d(sigFile.Get('wHisto_pdferr_nom'),xSignal,ySignal,zSignal,box,signalRegion)
    sigNorm = pdfNom.Integral()
    sigEvents = sigNorm*lumi*refXsec
    print "\nINFO: now multiplying:  efficiency x lumi x refXsec = %f x %f x %f = %f"%(sigNorm,lumi,refXsec,sigEvents)
    
    histos[box,model] = rebin3dCoarse(wHisto.Clone("%s_%s_3d"%(box,model)), xSignal, ySignal, zSignal, x, y, z, box, signalRegion)
    histos[box,model].SetTitle("%s_%s_3d"%(box,model))
    histos[box,model].Scale(sigEvents/histos[box,model].Integral())
    
    for paramName in ["Jes","Isr","Btag","Pdf"]:
        print "\nINFO: Now renormalizing signal shape systematic histograms to nominal\n"
        print "signal shape variation %s"%paramName
        for syst in ['Up','Down']:
            
            print "norm is %f"%histos[box,"%s_%s%s"%(model,paramName,syst)].Integral()
            if histos[box,"%s_%s%s"%(model,paramName,syst)].Integral() > 0:
                histos[box,"%s_%s%s"%(model,paramName,syst)].Scale( histos[box,model].Integral()/histos[box,"%s_%s%s"%(model,paramName,syst)].Integral())

    #unroll histograms 3D -> 1D
    print "\nINFO: Now Unrolling 3D histograms\n" 
    dataHist = {}
    for index, histo in histos.iteritems():
        box, bkg = index
        print box, bkg
        if bkg=="data":
            histos1d[box,bkg] = rt.TH1D("data_obs","data_obs",nBins, 0, nBins)
        else:
            histos1d[box,bkg] = rt.TH1D("%s_%s"%(box,bkg),"%s_%s"%(box,bkg),nBins, 0, nBins)
            
        newbin = 0
        for i in xrange(1,histo.GetNbinsX()+1):
            for j in xrange(1,histo.GetNbinsY()+1):
                for k in xrange(1,histo.GetNbinsZ()+1):
                    newbin += 1
                    histos1d[box,bkg].SetBinContent(newbin,histo.GetBinContent(i,j,k))
                        
        if bkg=="data":
            # replace data with expected asimov a priori
            #asimovData = razorPdf.generateBinned(th1xSet,rt.RooFit.Asimov())
            #asimovData.SetName("data_obs")
            #asimovData.SetTitle("data_obs")
            #dataHist[box,bkg] = asimovData

            #dataHist[box,bkg] = rt.RooDataHist("data_obs", "data_obs", th1xList, rt.RooFit.Index(channel),rt.RooFit.Import(box,histos1d[box,bkg]))
            dataHist[box,bkg] = rt.RooDataHist("data_obs", "data_obs", th1xList, rt.RooFit.Import(histos1d[box,bkg]))

            # turn off prefit   
            #if not expected_a_priori:
            plots = False
            if plots:                
                c = rt.TCanvas("c","c",500,500)
                frame = th1x.frame()
                dataHist[box,bkg].plotOn(frame)
                razorPdf.plotOn(frame)
                frame.Draw()
                c.SaveAs("razor1DFit_%s_preFit.pdf"%box)
                fr_new = razorPdf.fitTo(dataHist[box,bkg],rt.RooFit.Extended(),rt.RooFit.Save())
                fr_new.Print("v")
                frame2 = th1x.frame()
                dataHist[box,bkg].plotOn(frame2)
                razorPdf.plotOn(frame2)
                c = rt.TCanvas("c","c",500,500)
                frame2.Draw()
                c.SaveAs("razor1DFit_%s_postFit.pdf"%box)
                
                
            RootTools.Utils.importToWS(w,dataHist[box,bkg])
        elif bkg.find("TTj")==-1:
            dataHist[box,bkg] = rt.RooDataHist("%s_%s"%(box,bkg), "%s_%s"%(box,bkg), th1xList, rt.RooFit.Import(histos1d[box,bkg]))

            RootTools.Utils.importToWS(w,dataHist[box,bkg])
    print "\nINFO: Now writing data card\n"

    w.Print("v")
    writeDataCard(box,model,massPoint,"%s/razor_combine_%s_%s_%s.txt"%(outdir,box,model,massPoint),initialBkgs,paramNames,w,lumi_uncert,trigger_uncert,lepton_uncert,penalty)

            
    os.system("cat %s/razor_combine_%s_%s_%s.txt \n"%(outdir,box,model,massPoint)) 
    
    for bkg in initialBkgs:
        w.var("%s_%s_norm"%(box,bkg)).setVal(1.0)
        w.var("%s_%s_norm"%(box,bkg)).setMax(10.0)
    outFile = rt.TFile.Open("%s/razor_combine_%s_%s_%s.root"%(outdir,box,model,massPoint),"RECREATE")
    outFile.cd()
    
    for index, histo in histos.iteritems():
        histo.Write()
    w.Write()
    outFile.Close()
