from RazorCombinedFit.Framework import Box
import math
import RootTools
import ROOT as rt
from array import *
import sys

#this is global, to be reused in the plot making
def getBinning(boxName, varName, btag):
    if boxName == "Jet" or boxName == "TauTauJet" or boxName == "MultiJet":
        if varName == "MR" :        return [400, 450, 550, 700, 900, 1200, 1600, 2500, 4000]
        elif varName == "Rsq" : 
            if btag == "NoBtag":    return [0.25,0.30,0.40,0.50]
            if btag == "Btag":      return [0.25,0.30,0.41,0.52,0.64,0.80,1.5]
    else:
        if varName == "MR" :        return [300, 350, 450, 550, 700, 900, 1200, 1600, 2500, 4000]
        elif varName == "Rsq" :
            if btag == "NoBtag":    return [0.15,0.20,0.30,0.40,0.50]
            elif btag == "Btag":    return [0.15,0.20,0.30,0.41,0.52,0.64,0.80,1.5]
    if varName == "nBtag" :
        if btag == "NoBtag":        return [0,1]
        elif btag == "Btag":        return [1,2,3,4]

            
def FindLastBin(h):
    for i in range(1,h.GetXaxis().GetNbins()):
        thisbin = h.GetXaxis().GetNbins()-i
        if h.GetBinContent(thisbin)>=0.1: return thisbin+1
    return h.GetXaxis().GetNbins()    
                     
class RazorBox(Box.Box):
    
    def __init__(self, name, variables, fitMode = '3D', btag = True, fitregion = 'FULL'):
        super(RazorBox,self).__init__(name, variables)
        #data
        if not btag:
            self.btag = "NoBtag"
            self.zeros = {'TTj1b':[],'TTj2b':[],'Vpj':[]}
        else:
            self.btag = "Btag"
            self.zeros = {'TTj1b':[],'TTj2b':['MuEle','EleEle','MuMu','TauTauJet'],'Vpj':['MuEle','EleEle','MuMu','Mu','Ele','MuTau','EleTau','TauTauJet','MultiJet']}
                        
        if fitregion=="Sideband": self.fitregion = "LowRsq,LowMR"
        elif fitregion=="FULL": self.fitregion = "LowRsq,LowMR,HighMR"
        else: self.fitregion = fitregion
        self.fitMode = fitMode

        self.cut = 'MR>0.'
        
        
    def addTailPdf(self, flavour, doSYS):
        label = '_%s' % flavour
        # 2D FIT
        if self.fitMode == "2D":
            # define the R^2 vs MR
            if doSYS == True:
                self.workspace.factory("RooRazor2DTail_SYS::PDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                #tail-systematic parameter
                self.workspace.var("n%s" %label).setConstant(rt.kFALSE)
            else:
                #self.workspace.factory("RooRazor2DTail::PDF%s(MR,Rsq,MR0%s,R0%s,b%s)" %(label,label,label,label))
                self.workspace.factory("RooRazor2DTail_SYS::PDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                #tail-systematic parameter fixed to 1.0
                self.workspace.var("n%s" %label).setVal(1.0)
                self.workspace.var("n%s" %label).setConstant(rt.kTRUE)
            #associate the yields to the pdfs through extended PDFs
            self.workspace.factory("RooExtendPdf::ePDF%s(PDF%s, Ntot%s)" %(label, label, label))
            
        # 3D fit
        elif self.fitMode == "3D":
            # define the R^2 vs MR
            if doSYS == True:
                self.workspace.factory("RooRazor2DTail_SYS::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                # tail-systematic parameter
                self.workspace.var("n%s" %label).setConstant(rt.kFALSE)
            else:
                #self.workspace.factory("RooRazor2DTail::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s)" %(label,label,label,label))
                self.workspace.factory("RooRazor2DTail_SYS::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                #tail-systematic parameter fixed to 1.0
                self.workspace.var("n%s" %label).setVal(1.0)
                self.workspace.var("n%s" %label).setConstant(rt.kTRUE)
                
            ## define the nB pdf            
            self.workspace.factory("RooBTagMult::BtagPDF%s(nBtag,f1%s,f2%s,f3%s)"%(label,label,label,label))
            ## the total PDF is the product of the two
            self.workspace.factory("PROD::PDF%s(RazPDF%s,BtagPDF%s)"%(label,label,label))
            ##associate the yields to the pdfs through extended PDFs
            self.workspace.factory("RooExtendPdf::ePDF%s(PDF%s, Ntot%s)"%(label,label,label))
            # to force numerical integration and use default precision 1e-7
            #self.workspace.pdf("RazPDF%s"%label).forceNumInt(rt.kTRUE)
            #rt.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
            #rt.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)


        # 4D fit
        elif self.fitMode == "4D":
            # define the R^2 vs MR
            if doSYS == True:
                self.workspace.factory("RooRazor2DTail_SYS::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                # tail-systematic parameter
                self.workspace.var("n%s" %label).setConstant(rt.kFALSE)
            else:
                self.workspace.factory("RooRazor2DTail_SYS::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                #tail-systematic parameter fixed to 1.0
                self.workspace.var("n%s" %label).setVal(1.0)
                self.workspace.var("n%s" %label).setConstant(rt.kTRUE)
            ## define the nB pdf
            self.workspace.factory("RooBTagMult::BtagPDF%s(nBtag,f1%s,f2%s,f3%s)"%(label,label,label,label))
            ## for each charge, the 4D PDF is the product of the two * the charge 
            self.workspace.factory("PROD::PDF%sPlus(RazPDF%s,BtagPDF%s,PlusPDF)"%(label,label,label))
            self.workspace.factory("PROD::PDF%sMinus(RazPDF%s,BtagPDF%s,MinusPDF)"%(label,label,label))
            #define the plus and minus yields
            self.workspace.factory("expr::N_minus%s('@0*(1-@1)',Ntot%s,fplus%s)" %(label,label,label))
            self.workspace.factory("expr::N_plus%s('@0*@1',Ntot%s,fplus%s)" %(label,label,label))
            ##associate the yields to the pdfs through extended PDFs
            self.workspace.factory("RooExtendPdf::ePDFPlus%s(PDF%sPlus, N_plus%s)"%(label,label,label))
            self.workspace.factory("RooExtendPdf::ePDFMinus%s(PDF%sMinus, N_minus%s)"%(label,label,label))
            thisPDFlist = rt.RooArgList(self.workspace.pdf("ePDFPlus%s" %label), self.workspace.pdf("ePDFMinus%s" %label))
            model = rt.RooAddPdf("ePDF%s" %label, "ePDF%s" %label, thisPDFlist)

    def switchOff(self, species) :
        self.workspace.var("Ntot_"+species).setVal(0.)
        self.workspace.var("Ntot_"+species).setConstant(rt.kTRUE)

    #add penalty terms and float
    def floatComponentWithPenalty(self,flavour, alsoB):
        self.fixParsPenalty("MR0_%s" % flavour)
        self.fixParsPenalty("R0_%s" % flavour)
        self.fixPars("MR0_%s_s" % flavour)
        self.fixPars("R0_%s_s" % flavour)
        if alsoB == True:
            self.fixParsPenalty("b_%s" % flavour)
            self.fixPars("b_%s_s" % flavour)
        else:
            self.fixParsExact("b_%s" % flavour, False)
            
    def floatBTagf3(self,flavour):
        self.fixParsExact("f3_%s" % flavour, False)
        
    def floatBTagf2(self,flavour):
        self.fixParsExact("f2_%s" % flavour, False)

    def floatBTagWithPenalties(self,flavour):
        self.fixParsPenalty("f1_%s" % flavour)
        self.fixParsPenalty("f2_%s" % flavour)
        self.fixParsPenalty("f3_%s" % flavour)
        self.fixPars("f1_%s_s" % flavour)
        self.fixPars("f2_%s_s" % flavour)
        self.fixPars("f3_%s_s" % flavour)
            
    def floatComponent(self,flavour):
        self.fixParsExact("MR0_%s" % flavour, False)
        self.fixParsExact("R0_%s" % flavour, False)
        self.fixParsExact("b_%s" % flavour, False)
    def floatYield(self,flavour):
        self.fixParsExact("Ntot_%s" % flavour, False)
    def fixComponent(self,flavour):
        self.fixParsExact("MR0_%s" % flavour, True)
        self.fixParsExact("R0_%s" % flavour, True)
        self.fixParsExact("b_%s" % flavour, True)        
    
    def addDataSet(self, inputFile):
        #create the dataset
        data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
        #import the dataset to the workspace
        self.importToWS(data)

    def define(self, inputFile):
        
        #define the ranges
        mR  = self.workspace.var("MR")
        Rsq = self.workspace.var("Rsq")
        nBtag  = self.workspace.var("nBtag")

        # charge +1 pdf
        if self.fitMode == "4D":
            self.workspace.factory("RooTwoBin::PlusPDF(CHARGE,plusOne[1.])")
            self.workspace.factory("RooTwoBin::MinusPDF(CHARGE,minusOne[-1.])")
        
        # add only relevant components (for generating toys)
        #myPDFlist = rt.RooArgList()
        #for z in self.zeros:
        #    if self.name not in self.zeros[z]:
        #        #self.addTailPdf(z, not (z=="Vpj"))
        #        self.addTailPdf(z, True)
        #        myPDFlist.add(self.workspace.pdf("ePDF_%s"%z))

        # add ALL the different components (for combining boxes in limit setting later):
        # - W+jets
        # - ttbar+jets 1b
        # - ttbar+jets j2b
        self.addTailPdf("Vpj",True)
        self.addTailPdf("TTj1b",True)
        self.addTailPdf("TTj2b",True)
        # build the total PDF
        myPDFlist = rt.RooArgList(self.workspace.pdf("ePDF_Vpj"), self.workspace.pdf("ePDF_TTj1b"), self.workspace.pdf("ePDF_TTj2b"))
                
        model = rt.RooAddPdf(self.fitmodel, self.fitmodel, myPDFlist)
        
        model.Print("v")
        # import the model in the workspace.
        self.importToWS(model)
        #print the workspace
        self.workspace.Print("v")

        ##### THIS IS A SIMPLIFIED FIT
        # fix all pdf parameters (except the n) to the initial value
        self.fixPars("MR0_")
        self.fixPars("R0_")
        self.fixPars("b_")
        self.fixPars("f1")
        self.fixPars("f2")
        self.fixPars("f3")
        #self.fixPars("f4")

        def floatSomething(z):
            """Switch on or off whatever you want here"""
            # float BTAG
            if(self.btag == "Btag") and z=="TTj2b": self.floatBTagf3(z)
            self.floatComponent(z)
            self.floatYield(z)
            #self.fixPars("R0_")
            #self.fixPars("MR0_",False)
            #self.fixPars("n_")

        # switch off not-needed components (box by box)
        fixed = []
        for z in self.zeros:
            if self.name in self.zeros[z]:
                self.fixPars(z)
                self.switchOff(z)
            else:
                if not z in fixed:
                    floatSomething(z)
                    fixed.append(z)
                        
        # set normalizations
        N_TTj2b = self.workspace.var("Ntot_TTj2b").getVal()
        N_TTj1b = self.workspace.var("Ntot_TTj1b").getVal()
        N_Vpj = self.workspace.var("Ntot_Vpj").getVal()
        data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
        
        #in the case that the input file is an MC input file
        if data is None or not data:
            return None
        Ndata = data.reduce(self.getVarRangeCutNamed(ranges=self.fitregion.split(","))).sumEntries()
        self.workspace.var("Ntot_TTj2b").setVal(Ndata*N_TTj2b/(N_TTj2b+N_TTj1b+N_Vpj))
        self.workspace.var("Ntot_TTj1b").setVal(Ndata*N_TTj1b/(N_TTj2b+N_TTj1b+N_Vpj))
        self.workspace.var("Ntot_Vpj").setVal(Ndata*N_Vpj/(N_TTj2b+N_TTj1b+N_Vpj))
        # switch off btag fractions if no events
        if self.fitMode == "3D" or self.fitMode == "4D":
            data1b = data.reduce("nBtag>=1&&nBtag<2")
            data2b = data.reduce("nBtag>=2&&nBtag<3")
            data3b = data.reduce("nBtag>=3&&nBtag<4")
            if data3b.numEntries() == 0:
                self.workspace.var("f3_TTj2b").setVal(0.)
                self.workspace.var("f3_TTj2b").setConstant(rt.kTRUE)
                self.workspace.var("f3_Vpj").setVal(0.)
                self.workspace.var("f3_Vpj").setConstant(rt.kTRUE)
                self.workspace.var("f3_TTj1b").setVal(0.)
                self.workspace.var("f3_TTj1b").setConstant(rt.kTRUE)
            if data2b.numEntries() == 0:
                #this is now a function
                #self.workspace.var("f2_TTj2b").setVal(0.)
                #self.workspace.var("f2_TTj2b").setConstant(rt.kTRUE)
                self.workspace.var("f2_Vpj").setVal(0.)
                self.workspace.var("f2_Vpj").setConstant(rt.kTRUE)
                self.workspace.var("f2_TTj1b").setVal(0.)
                self.workspace.var("f2_TTj1b").setConstant(rt.kTRUE)
            del data1b, data2b, data3b
        del data
        

    def addSignalModel(self, inputFile, signalXsec, modelName = None):
        
        if modelName is None:
            modelName = 'Signal'
        
        # signalModel is the 2D pdf [normalized to one]
        # nSig is the integral of the histogram given as input
        signalModel, nSig = self.makeRooHistPdf(inputFile,modelName)
        # compute the expected yield/(pb-1)
        if signalXsec > 0.:
            # for SMS: the integral is the efficiency.
            # We multiply it by the specified xsection
            nSig = nSig*signalXsec
        else:
            # here nSig is the expected yields for 1000 pb-1
            # and we turn it into the expcted yield in a pb-1
            nSig = nSig/1000.

        #set the MC efficiency relative to the number of events generated
        #epsilon = self.workspace.factory("expr::Epsilon_%s('%i/@0',nGen_%s)" % (modelName,nSig,modelName) )
        #self.yieldToCrossSection(modelName) #define Ntot
        self.workspace.factory("rSig[1.]")
        self.workspace.var("rSig").setConstant(rt.kTRUE)
        # compute the signal yield multiplying by the efficiency
        self.workspace.factory("expr::Ntot_%s('%f*@0*@1', Lumi, rSig)" %(modelName,nSig))
        extended = self.workspace.factory("RooExtendPdf::eBinPDF_%s(%s, Ntot_%s)" % (modelName,signalModel,modelName))
        #add = rt.RooAddPdf('%s_%sCombined' % (self.fitmodel,modelName),'Signal+BG PDF',
        #                   rt.RooArgList(self.workspace.pdf(self.fitmodel),extended)
        #                   )
        theRealFitModel = "fitmodel"
        add = rt.RooAddPdf('%s_%sCombined' % (theRealFitModel,modelName),'Signal+BG PDF',
                           rt.RooArgList(self.workspace.pdf(theRealFitModel),extended)
                           )
        self.importsToWS(add)
        self.workspace.Print()
        self.signalmodel = add.GetName()
        return extended.GetName()
        
    def plot(self, inputFile, store, box):
        print "not plotting"
        #[store.store(s, dir=box) for s in self.plot1D(inputFile, "MR", 80, ranges=self.fitregion.split(","))]
        #[store.store(s, dir=box) for s in self.plot1D(inputFile, "Rsq", 25, ranges=self.fitregion.split(","))]
        #if self.fitMode == "3D": [store.store(s, dir=box) for s in self.plot1D(inputFile, "nBtag", 5, ranges=self.fitregion.split(","))]

        # # the real plot 1d Histos:
        
        # # just the fitregion:
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=self.fitregion.split(","))]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=self.fitregion.split(","))]
        if self.fitMode == "3D": [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "nBtag", 3, ranges=self.fitregion.split(","))]
            
        # # the full region
        if self.fitregion!='LowRsq,LowMR,HighMR':
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['LowRsq','LowMR','HighMR'])]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['LowRsq','LowMR','HighMR'])]
            if self.fitMode == "3D": [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "nBtag", 3, ranges=['LowRsq','LowMR','HighMR'])]

        if not (self.name=='MuEle' or self.name=='MuMu' or self.name=='EleEle' or self.name=='TauTauJet'):
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['LowRsq1b','LowMR1b','HighMR1b'])]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['LowRsq1b','LowMR1b','HighMR1b'])]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['LowRsq2b','LowMR2b','HighMR2b','LowRsq3b','LowMR3b','HighMR3b'])]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['LowRsq2b','LowMR2b','HighMR2b','LowRsq3b','LowMR3b','HighMR3b'])]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['LowRsq2b','LowMR2b','HighMR2b'])]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['LowRsq2b','LowMR2b','HighMR2b'])]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['LowRsq3b','LowMR3b','HighMR3b'])]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['LowRsq3b','LowMR3b','HighMR3b'])]
            


    def plot1D(self, inputFile, varname, nbin=200, ranges=None, data = None):

        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        # set the integral precision
        rt.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-10) ;
        rt.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-10) ;
        # get the max and min (if different than default)
        xmin = self.workspace.var(varname).getMin()
        xmax = self.workspace.var(varname).getMax()
        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree')
        data_cut = data.reduce(rangeCut)
        data_cut = data_cut.reduce(self.cut)
        
        # project the data on the variable
        if varname =="nBtag":
            RooBtagbins = rt.RooBinning(1,4)
            RooBtagbins.addBoundary(2)
            RooBtagbins.addBoundary(3)
            frameMR = self.workspace.var(varname).frame(rt.RooFit.Range(1,4),rt.RooFit.Binning(RooBtagbins))
        else:
            frameMR = self.workspace.var(varname).frame(rt.RooFit.AutoSymRange(data_cut),rt.RooFit.Bins(nbin))
        frameMR.SetName(varname+"plot")
        frameMR.SetTitle(varname+"plot")
        
        if varname=="nBtag":
            #data.plotOn(frameMR, rt.RooFit.LineColor(rt.kRed),rt.RooFit.MarkerColor(rt.kRed),rt.RooFit.Binning(RooBtagbins))
            data_cut.plotOn(frameMR, rt.RooFit.Binning(RooBtagbins))
        else:
            #data.plotOn(frameMR, rt.RooFit.LineColor(rt.kRed),rt.RooFit.MarkerColor(rt.kRed))
            data_cut.plotOn(frameMR)
        
        # project the full PDF on the data
        if varname=="MR":
            self.workspace.pdf(self.fitmodel).plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.ProjectionRange("LowMR"),rt.RooFit.Range("LowMR"),rt.RooFit.NormRange("NormRange"))
        elif varname=="Rsq":
            self.workspace.pdf(self.fitmodel).plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.ProjectionRange("LowRsq"),rt.RooFit.Range("LowRsq"),rt.RooFit.NormRange("NormRange"))
        self.workspace.pdf(self.fitmodel).plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.ProjectionRange("HighMR"), rt.RooFit.Range("HighMR"),rt.RooFit.NormRange("NormRange"))
            
        # plot each individual component: Vpj
        N_Vpj = self.workspace.function("Ntot_Vpj").getVal()
        # plot each individual component: TTj2b
        N_TTj2b = self.workspace.function("Ntot_TTj2b").getVal()
        # plot each individual component: TTj1b
        N_TTj1b = self.workspace.function("Ntot_TTj1b").getVal()

        Ntot = N_Vpj+N_TTj2b+N_TTj1b

        if N_Vpj >0:
            # project the first component: Vpj
            if varname=="MR":
                self.workspace.pdf("PDF_Vpj").plotOn(frameMR, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_Vpj/Ntot),rt.RooFit.ProjectionRange("LowMR"),rt.RooFit.Range("LowMR"),rt.RooFit.NormRange("NormRange"))
            elif varname=="Rsq":
                self.workspace.pdf("PDF_Vpj").plotOn(frameMR, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_Vpj/Ntot),rt.RooFit.ProjectionRange("LowRsq"),rt.RooFit.Range("LowRsq"),rt.RooFit.NormRange("NormRange"))
            self.workspace.pdf("PDF_Vpj").plotOn(frameMR, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_Vpj/Ntot),rt.RooFit.ProjectionRange("HighMR"),rt.RooFit.Range("HighMR"),rt.RooFit.NormRange("NormRange"))
        if N_TTj2b >0:
            # project the first component: TTj2b
            if varname=="MR":
                self.workspace.pdf("PDF_TTj2b").plotOn(frameMR, rt.RooFit.LineColor(rt.kOrange), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_TTj2b/Ntot),rt.RooFit.ProjectionRange("LowMR"),rt.RooFit.Range("LowMR"),rt.RooFit.NormRange("NormRange"))
            elif varname=="Rsq":
                self.workspace.pdf("PDF_TTj2b").plotOn(frameMR, rt.RooFit.LineColor(rt.kOrange), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_TTj2b/Ntot),rt.RooFit.ProjectionRange("LowRsq"),rt.RooFit.Range("LowRsq"),rt.RooFit.NormRange("NormRange"))
            self.workspace.pdf("PDF_TTj2b").plotOn(frameMR, rt.RooFit.LineColor(rt.kOrange), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_TTj2b/Ntot),rt.RooFit.ProjectionRange("HighMR"),rt.RooFit.Range("HighMR"),rt.RooFit.NormRange("NormRange"))
        if N_TTj1b >0:
            # project the first component: TTj1b
            if varname=="MR":
                self.workspace.pdf("PDF_TTj1b").plotOn(frameMR, rt.RooFit.LineColor(rt.kMagenta), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_TTj1b/Ntot),rt.RooFit.ProjectionRange("LowMR"),rt.RooFit.Range("LowMR"),rt.RooFit.NormRange("NormRange"))
            elif varname=="Rsq":
                self.workspace.pdf("PDF_TTj1b").plotOn(frameMR, rt.RooFit.LineColor(rt.kMagenta), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_TTj1b/Ntot),rt.RooFit.ProjectionRange("LowRsq"),rt.RooFit.Range("LowRsq"),rt.RooFit.NormRange("NormRange"))
            self.workspace.pdf("PDF_TTj1b").plotOn(frameMR, rt.RooFit.LineColor(rt.kMagenta), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_TTj1b/Ntot),rt.RooFit.ProjectionRange("HighMR"),rt.RooFit.Range("HighMR"),rt.RooFit.NormRange("NormRange"))
        d = rt.TCanvas()
        rt.gPad.SetLogy()
        frameMR.Draw()
        d.Print("%s.pdf"%varname)
        return [frameMR]

    def plot1DHistoAllComponents(self, inputFile, xvarname, nbins = 25, ranges=None, data = None):
        Preliminary = "Preliminary"
        #Preliminary = "Simulation"
        Energy = 8.0
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
            
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)

        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
            
        # save original event yields
        if self.workspace.var("Ntot_TTj2b") != None:
            N_TTj2b = self.workspace.var("Ntot_TTj2b").getVal()
        if self.workspace.var("Ntot_TTj1b") != None:
            N_TTj1b = self.workspace.var("Ntot_TTj1b").getVal()
        if self.workspace.var("Ntot_Vpj") != None:
            N_Vpj = self.workspace.var("Ntot_Vpj").getVal()

            
        # Generate a sample of Vpj
        effCutVpj = 1
        self.workspace.var("Ntot_Vpj").setVal(N_Vpj)
        self.workspace.var("Ntot_TTj1b").setVal(0.)
        self.workspace.var("Ntot_TTj2b").setVal(0.)
        if self.workspace.var("Ntot_Vpj") != None and N_Vpj>1:
            toyDataVpj = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(N_Vpj)))
            beforeCutVpj = float(toyDataVpj.sumEntries())
            toyDataVpj = toyDataVpj.reduce(rangeCut)
            afterCutVpj = float(toyDataVpj.sumEntries())
            effCutVpj = afterCutVpj / beforeCutVpj

        # Generate a sample of TTj1b
        effCutTTj1b = 1
        self.workspace.var("Ntot_Vpj").setVal(0.)
        self.workspace.var("Ntot_TTj1b").setVal(N_TTj1b)
        self.workspace.var("Ntot_TTj2b").setVal(0.)
        if self.workspace.var("Ntot_TTj1b") != None and N_TTj1b>1 :
            toyDataTTj1b = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(N_TTj1b)))
            beforeCutTTj1b = float(toyDataTTj1b.sumEntries())
            toyDataTTj1b = toyDataTTj1b.reduce(rangeCut)
            afterCutTTj1b = float(toyDataTTj1b.sumEntries())
            effCutTTj1b = afterCutTTj1b / beforeCutTTj1b
                        
        # Generate a sample of TTj2b
        print "f1_TTj2b = %f"%self.workspace.var("f1_TTj2b").getVal()
        print "f3_TTj2b = %f"%self.workspace.var("f3_TTj2b").getVal()
        effCutTTj2b = 1
        self.workspace.var("Ntot_Vpj").setVal(0.)
        self.workspace.var("Ntot_TTj1b").setVal(0.)
        self.workspace.var("Ntot_TTj2b").setVal(N_TTj2b)
        if self.workspace.var("Ntot_TTj2b") != None and N_TTj2b>1 :
            toyDataTTj2b = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(N_TTj2b)))
            beforeCutTTj2b = float(toyDataTTj2b.sumEntries())
            toyDataTTj2b = toyDataTTj2b.reduce(rangeCut)
            afterCutTTj2b = float(toyDataTTj2b.sumEntries())
            effCutTTj2b = afterCutTTj2b / beforeCutTTj2b
            
        # set the event yields back to their original values
        # NOTE: these original values REFER TO THE FULL RANGE OF VARIABLES MR and Rsq and nBtag!
        print "EFFICIENCIES for this rangeCut"
        print "TTj1b %f"%effCutTTj1b
        print "TTj2b %f"%effCutTTj2b
        print "Vpj %f"%effCutVpj
        self.workspace.var("Ntot_TTj2b").setVal(N_TTj2b)
        self.workspace.var("Ntot_TTj1b").setVal(N_TTj1b)
        self.workspace.var("Ntot_Vpj").setVal(N_Vpj)

        xmin = min([self.workspace.var(xvarname).getMin(r) for r in ranges])
        xmax = max([self.workspace.var(xvarname).getMax(r) for r in ranges])

        # variable binning for plots
        bins = getBinning(self.name, xvarname, self.btag)
        
        nbins =len(bins)-1
        xedge = array("d",bins)
        print "Binning in variable %s is "%xvarname
        print bins
        
        # define 1D histograms
        histoData = self.setPoissonErrors(rt.TH1D("histoData", "histoData",len(bins)-1, xedge))
        histoToy = self.setPoissonErrors(rt.TH1D("histoToy", "histoToy",len(bins)-1, xedge))
        histoToyVpj = self.setPoissonErrors(rt.TH1D("histoToyVpj", "histoToyVpj",len(bins)-1, xedge))
        histoToyTTj1b = self.setPoissonErrors(rt.TH1D("histoToyTTj1b", "histoToyTTj1b",len(bins)-1, xedge))
        histoToyTTj2b = self.setPoissonErrors(rt.TH1D("histoToyTTj2b", "histoToyTTj2b",len(bins)-1, xedge))

        def setName(h, name):
            h.SetName('%s_%s_%s_ALLCOMPONENTS' % (h.GetName(),name,'_'.join(ranges)) )
            # axis labels
            h.GetXaxis().SetTitleSize(0.05)
            h.GetYaxis().SetTitleSize(0.05)
            h.GetXaxis().SetLabelSize(0.05)
            h.GetYaxis().SetLabelSize(0.05)
            h.GetXaxis().SetTitleOffset(0.90)
            h.GetYaxis().SetTitleOffset(0.93)
        
            # x axis
            if name == "MR": h.GetXaxis().SetTitle("M_{R} [GeV]")
            elif name == "Rsq": h.GetXaxis().SetTitle("R^{2}")
            elif name == "nBtag":
                h.GetXaxis().SetTitle("n_{b-tag}")
                h.GetXaxis().SetLabelSize(0.08)
                h.GetXaxis().SetBinLabel(1,"1")
                h.GetXaxis().SetBinLabel(2,"2")
                h.GetXaxis().SetBinLabel(3,"#geq 3")
                
            # y axis
            if name == "MR": h.GetYaxis().SetTitle("Events/(%i GeV)" %h.GetXaxis().GetBinWidth(1))
            elif name == "Rsq": h.GetYaxis().SetTitle("Events/(%4.3f)" %h.GetXaxis().GetBinWidth(1))
            elif name == "nBtag": h.GetYaxis().SetTitle("Events")

        def SetErrors(histo, nbins):
            for i in range(1, nbins+1):
                histo.SetBinError(i,rt.TMath.Sqrt(histo.GetBinContent(i)))

        # project the data on the histograms
        data.fillHistogram(histoData,rt.RooArgList(self.workspace.var(xvarname)))
        print xvarname
        self.workspace.var(xvarname).Print()
        
        if self.workspace.var("Ntot_Vpj") != None and N_Vpj>1: toyDataVpj.fillHistogram(histoToyVpj,rt.RooArgList(self.workspace.var(xvarname)))
        if self.workspace.var("Ntot_TTj1b") != None and N_TTj1b>1 :toyDataTTj1b.fillHistogram(histoToyTTj1b,rt.RooArgList(self.workspace.var(xvarname)))
        if self.workspace.var("Ntot_TTj2b") != None and N_TTj2b>1 : toyDataTTj2b.fillHistogram(histoToyTTj2b,rt.RooArgList(self.workspace.var(xvarname)))
        # make the total
        if self.workspace.var("Ntot_Vpj") != None and N_Vpj>1: histoToy.Add(histoToyVpj, +1)
        if self.workspace.var("Ntot_TTj1b") != None and N_TTj1b>1 :histoToy.Add(histoToyTTj1b, +1)
        if self.workspace.var("Ntot_TTj2b") != None and N_TTj2b>1: histoToy.Add(histoToyTTj2b, +1)
            
        # We shouldn't scale to the data, we should scale to our prediction
        #scaleFactor = histoData.Integral()/histoToy.Integral()
        print "DATA NORM %f"%histoData.Integral()
        print "FIT NORM  %f"%(N_TTj2b*effCutTTj2b+N_Vpj*effCutVpj+N_TTj1b*effCutTTj1b)
        scaleFactor = (N_TTj2b*effCutTTj2b+N_Vpj*effCutVpj+N_TTj1b*effCutTTj1b)/histoToy.Integral()
        #scaleFactor = (N_TTj2b+N_Vpj+N_TTj1b)/histoToy.Integral()
        print "scaleFactor = %f"%scaleFactor
        
        histoToyTTj2b.Scale(scaleFactor)
        histoToyVpj.Scale(scaleFactor)
        histoToyTTj1b.Scale(scaleFactor)
        SetErrors(histoToyTTj2b, nbins)
        SetErrors(histoToyVpj, nbins)
        SetErrors(histoToyTTj1b, nbins)
        setName(histoToyTTj2b,xvarname)
        setName(histoToyVpj,xvarname)
        setName(histoToyTTj1b,xvarname)
        histoToyTTj1b.SetLineColor(rt.kViolet)
        histoToyTTj1b.SetLineWidth(2)
        histoToyTTj2b.SetLineColor(rt.kRed)
        histoToyTTj2b.SetLineWidth(2)
        histoToyVpj.SetLineColor(rt.kGreen)
        histoToyVpj.SetLineWidth(2)

        histoToy.Scale(scaleFactor)
        SetErrors(histoToy, nbins)
        setName(histoData,xvarname)
        setName(histoToy,xvarname)
        histoData.SetMarkerStyle(20)
        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        rt.gStyle.SetOptStat(0000)
        rt.gStyle.SetOptTitle(0)



        if N_TTj2b>0 and N_TTj1b>0:
            leg = rt.TLegend(0.65,0.65,0.93,0.93)
        else:
            leg = rt.TLegend(0.65,0.72,0.93,0.93)
        leg.SetFillColor(0)
        leg.SetTextFont(42)
        leg.SetLineColor(0)


        btagLabel = "#geq 1 b-tag"
        if ranges==["3b"]:
            btagLabel = "#geq 3 b-tag"
        if ranges==["2b","3b"]:
            btagLabel = "#geq 2 b-tag"
        if ranges==["2b"]:
            btagLabel = "2 b-tag"
        
        leg.AddEntry(histoData,"Data","lep")
        if xvarname=="nBtag":
            if N_TTj1b>0 and N_TTj2b>0:
                leg.AddEntry(histoToyTTj1b,"1 b-tag","f")
                leg.AddEntry(histoToyTTj2b,"#geq 2 b-tag","f")
        else:
            if N_TTj1b>0 and N_TTj2b>0:
                leg.AddEntry(histoToyTTj1b,"1 b-tag","l")
                leg.AddEntry(histoToyTTj2b,"#geq 2 b-tag","l")

        # plot labels
        pt = rt.TPaveText(0.4,0.8,0.5,0.93,"ndc")
        pt.SetBorderSize(0)
        pt.SetTextSize(0.05)
        pt.SetFillColor(0)
        pt.SetFillStyle(0)
        pt.SetLineColor(0)
        pt.SetTextAlign(21)
        pt.SetTextFont(42)
        pt.SetTextSize(0.042)
        text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
        pt.AddText("t#bar{t}+jets Razor %s Box, %s"%(self.name,btagLabel))
    
        c = rt.TCanvas("c","c",900,700)
        pad1 = rt.TPad("pad1","pad1",0,0.25,1,1)
        pad2 = rt.TPad("pad2","pad2",0,0,1,0.25)
        
        pad1.SetLeftMargin(0.15)
        pad2.SetLeftMargin(0.15)
        pad1.SetRightMargin(0.05)
        pad2.SetRightMargin(0.05)
        pad1.SetTopMargin(0.05)
        pad2.SetTopMargin(0.02)
        pad1.SetBottomMargin(0.02)
        pad2.SetBottomMargin(0.35)
    
        #pad1.SetBottomMargin(0)
        pad1.Draw()
        pad1.cd()
        rt.gPad.SetLogy()
        c.SetName('DataMC_%s_%s_ALLCOMPONENTS' % (xvarname,'_'.join(ranges)) )
        
        histoToy.SetMinimum(0.5)
        histoToy.GetYaxis().SetTitle("Events")
        histoToy.GetXaxis().SetTitle("")
        histoToy.GetXaxis().SetLabelOffset(0.16)
        histoToy.GetXaxis().SetLabelSize(0.06)
        histoToy.GetYaxis().SetLabelSize(0.06)
        histoToy.GetXaxis().SetTitleSize(0.06)
        histoToy.GetYaxis().SetTitleSize(0.06)
        histoToy.GetXaxis().SetTitleOffset(1)
        if xvarname == "MR": histoToy.SetMaximum(histoToy.GetMaximum()*2.)
        elif xvarname == "Rsq": histoToy.SetMaximum(histoToy.GetMaximum()*2.)
        elif xvarname == "nBtag": histoToy.SetMaximum(histoToy.GetMaximum()*5.)
        histoToy.GetXaxis().SetRange(0,FindLastBin(histoToy))
        #if histoToy.GetBinContent(histoToy.GetNbinsX())>=10.: histoToy.SetMinimum(5.)
        #if histoToy.GetBinContent(histoToy.GetNbinsX())>=100.: histoToy.SetMinimum(50.)
            
            
        
        histoToy.SetFillColor(rt.kBlue-10)
        histoToy.SetFillStyle(1001)
        histoData.Draw("pe")
        histoToy.DrawCopy('e2')
        histoData.Draw("pesame")
        leg.Draw("same")
        pt.Draw("same")
        
        leg.AddEntry(histoToy,"Total Background")

        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)
        
        if self.workspace.var("Ntot_Vpj").getVal():
            histoToyVpjAdd = histoToyVpj.Clone("histoToyVpjAdd")
            histoToyVpjAdd.DrawCopy("histsame")
            c1 = rt.gROOT.GetColor(rt.kGreen-4)
            c1.SetAlpha(1.0)
            histoToyVpjAdd.SetFillStyle(0)
            if xvarname=="nBtag":
                histoToyVpjAdd.Add(histoToyTTj1b)
                histoToyVpjAdd.SetFillStyle(1001)
                c1.SetAlpha(1.0)
                histoToyVpjAdd.SetFillColor(rt.kGreen-4)
            histoToyVpjAdd.DrawCopy('histsame')
        if self.workspace.var("Ntot_TTj1b").getVal():
            histoToyTTj1b.DrawCopy("histsame")
            c2 = rt.gROOT.GetColor(rt.kViolet-4)
            c2.SetAlpha(1.0)
            histoToyTTj1b.SetFillStyle(0)
            if xvarname=="nBtag":
                histoToyTTj1b.SetFillStyle(1001)
                c2.SetAlpha(1.0)
                histoToyTTj1b.SetFillColor(rt.kViolet-4)
            histoToyTTj1b.DrawCopy('histsame')
        if self.workspace.var("Ntot_TTj2b").getVal():
            histoToyTTj2b.DrawCopy('histsame')
            c3 = rt.gROOT.GetColor(rt.kRed-4)
            c3.SetAlpha(1.0)
            histoToyTTj2b.SetFillStyle(0)
            if xvarname=="nBtag":
                histoToyTTj2b.SetFillStyle(1001)
                c3.SetAlpha(1.0)
                histoToyTTj2b.SetFillColor(rt.kRed-4)
            histoToyTTj2b.DrawCopy('histsame')
        # total
        if xvarname=="nBtag":
            histoToy.SetFillColor(rt.kBlue-10)
            histoToy.SetFillStyle(1001)
            histoToy.DrawCopy('e2same')
        histoToyCOPY = histoToy.Clone("histoToyCOPY")
        histoToyCOPY.SetFillStyle(0)
        histoToyCOPY.Draw('histsame')
        histoData.Draw("pesame")

        histToReturn = [histoToy, histoData, c]
        histToReturn.append(histoToyVpj)
        histToReturn.append(histoToyTTj1b)
        histToReturn.append(histoToyTTj2b)

        c.cd()
        #pad2.SetTopMargin(0)
        pad2.SetGrid(1,1)
        pad2.Draw()
        pad2.cd()
        rt.gPad.SetLogy(0)
        histoData.Sumw2()
        histoToy.Sumw2()
        histoDataCOPY = histoData.Clone(histoData.GetName()+"COPY")
        histoDataCOPY.Sumw2()
        histoDataCOPY.GetYaxis().SetTitle("")
        histoDataCOPY.GetYaxis().SetLabelSize(0.12)
        histoDataCOPY.SetTitle("")
        if xvarname=="nBtag": histoDataCOPY.GetXaxis().SetLabelSize(0.28)
        else: histoDataCOPY.GetXaxis().SetLabelSize(0.18)
        histoDataCOPY.GetXaxis().SetTitleSize(0.18)
        histoDataCOPY.GetXaxis().SetTitleOffset(0.85)
        histoDataCOPY.Divide(histoToy)
        histoDataCOPY.SetLineWidth(2)
        histoDataCOPY.SetLineColor(rt.kBlue+1)
        histoDataCOPY.SetFillColor(rt.kBlue+1)
        histoDataCOPY.SetMarkerColor(rt.kBlue+1)
        histoDataCOPY.SetMarkerStyle(21)
        histoDataCOPY.SetMarkerSize(1)
        histoDataCOPY.SetFillStyle(1001)
        histoDataCOPY.GetYaxis().SetNdivisions(504,rt.kTRUE)
        histoDataCOPY.Draw('pe')

        leg.AddEntry(histoDataCOPY,"Ratio Data/Prediction","lep")
        
        fitLabel = '_'.join(self.fitregion.split(","))
        if self.fitregion == "LowRsq,LowMR,HighMR": fitLabel = "FULL"
        elif self.fitregion == "LowRsq,LowMR": fitLabel = "Sideband"
        elif self.fitregion == "HighMR": fitLabel = "HighMR"
        elif self.fitregion == "LowRsq1b,LowMR1b,HighMR1b": fitLabel = "1b"
        elif self.fitregion == "LowRsq2b,LowMR2b,HighMR2b": fitLabel = "2b"
        elif self.fitregion == "LowRsq3b,LowMR3b,HighMR3b": fitLabel = "3b"
            
        c.Print("razor_canvas_%s_%s_%s_%s.pdf"%(self.name,fitLabel,'_'.join(ranges), xvarname))
        
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"c\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad1\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad2\");")
        return histToReturn
