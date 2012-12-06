from RazorCombinedFit.Framework import Box
import math
import RootTools
import ROOT as rt
from array import *

#this is global, to be reused in the plot making
def getBinning(boxName, varName, btag):
    if boxName == "Jet" or boxName == "TauTauJet" or boxName == "MultiJet":
        if varName == "MR" :        return [400, 450, 550, 700, 900, 1200, 1600, 2500]
        elif varName == "Rsq" : 
            if btag == "NoBtag":    return [0.25,0.30,0.40,0.50]
            if btag == "Btag":      return [0.25,0.30,0.41,0.52,0.64,0.80,1.5]
    else:
        if varName == "MR" :        return [300, 350, 400, 550, 700, 900, 1200, 1600, 2500]
        elif varName == "Rsq" :
            if btag == "NoBtag":    return [0.15,0.20,0.30,0.40,0.50]
            elif btag == "Btag":    return [0.15,0.20,0.30,0.41,0.52,0.64,0.80,1.5]
    if varName == "nBtag" :
        if btag == "NoBtag":        return [0,1]
        elif btag == "Btag":        return [1,2,3,4,5]
                     
class RazorBox(Box.Box):
    
    def __init__(self, name, variables, fitMode = '3D', btag = True, fitregion = 'FULL'):
        super(RazorBox,self).__init__(name, variables)
        #data
        if not btag:
            self.btag = "NoBtag"
            self.zeros = {'TTj1b':[],'TTj2b':[],'Vpj':[]}
        else:
            self.btag = "Btag"
            self.zeros = {'TTj1b':[],'TTj2b':['MuEle','EleEle','MuMu','MuTau','EleTau','TauTauJet'],'Vpj':['MuEle','EleEle','MuMu','Mu','Ele','MuTau','EleTau','TauTauJet']}
            
        if fitregion=="Sideband": self.fitregion = "LowRsq,LowMR"
        elif fitregion=="FULL": self.fitregion = "LowRsq,LowMR,HighMR"
        else: self.fitregion = fitregion
        self.fitMode = fitMode
        
        self.cut = 'MR>=0.'
        
        
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
                self.workspace.factory("RooRazor2DTail_SYS::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                #tail-systematic parameter fixed to 1.0
                #self.workspace.var("n%s" %label).setVal(1.0)
                self.workspace.var("n%s" %label).setConstant(rt.kTRUE)
                
            ## define the nB pdf            
            self.workspace.factory("RooBTagMult::BtagPDF%s(nBtag,f1%s,f2%s,f3%s,f4%s)"%(label,label,label,label,label))
            ## the total PDF is the product of the two
            self.workspace.factory("PROD::PDF%s(RazPDF%s,BtagPDF%s)"%(label,label,label))
            ##associate the yields to the pdfs through extended PDFs
            self.workspace.factory("RooExtendPdf::ePDF%s(PDF%s, Ntot%s)"%(label,label,label))

        # 4D fit
        elif self.fitMode == "4D":
            # define the R^2 vs MR
            if doSYS == True:
                self.workspace.factory("RooRazor2DTail_SYS::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s[1.,0.8,5.0])" %(label,label,label,label,label))
                # tail-systematic parameter
                self.workspace.var("n%s" %label).setConstant(rt.kFALSE)
            else:
                self.workspace.factory("RooRazor2DTail_SYS::PDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                #tail-systematic parameter fixed to 1.0
                self.workspace.var("n%s" %label).setVal(1.0)
                self.workspace.var("n%s" %label).setConstant(rt.kTRUE)
            ## define the nB pdf
            self.workspace.factory("RooBTagMult::BtagPDF%s(nBtag,f1%s,f2%s,f3%s,f4%s)"%(label,label,label,label,label))
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
    def floatBTag(self,flavour):
        self.fixParsExact("f3_%s" % flavour, False)
        self.fixParsExact("f4_%s" % flavour, False)

    def floatBTagWithPenalties(self,flavour):
        self.fixParsPenalty("f1_%s" % flavour)
        self.fixParsPenalty("f2_%s" % flavour)
        self.fixParsPenalty("f3_%s" % flavour)
        self.fixParsPenalty("f4_%s" % flavour)
        self.fixPars("f1_%s_s" % flavour)
        self.fixPars("f2_%s_s" % flavour)
        self.fixPars("f3_%s_s" % flavour)
        self.fixPars("f4_%s_s" % flavour)
            
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
        
        # add the different components:
        # - W+jets
        # - ttbar+jets
        # - TTj1b
        self.addTailPdf("Vpj", False)
        self.addTailPdf("TTj1b", True)
        self.addTailPdf("TTj2b", True)

        # build the total PDF
        myPDFlist = rt.RooArgList(self.workspace.pdf("ePDF_Vpj"), self.workspace.pdf("ePDF_TTj2b"), self.workspace.pdf("ePDF_TTj1b"))
        
        model = rt.RooAddPdf(self.fitmodel, self.fitmodel, myPDFlist)
        
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
        self.fixPars("f4")

        def floatSomething(z):
            """Switch on or off whatever you want here"""
            # float BTAG
            if(self.btag == "Btag") and z=="TTj2b": self.floatBTag(z)
            self.floatComponent(z)
            self.floatYield(z)

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
        
        Ndata = data.reduce(self.cut).sumEntries()
        self.workspace.var("Ntot_TTj2b").setVal(Ndata*N_TTj2b/(N_TTj2b+N_TTj1b+N_Vpj))
        self.workspace.var("Ntot_TTj1b").setVal(Ndata*N_TTj1b/(N_TTj2b+N_TTj1b+N_Vpj))
        self.workspace.var("Ntot_Vpj").setVal(Ndata*N_Vpj/(N_TTj2b+N_TTj1b+N_Vpj))
        # switch off btag fractions if no events
        if self.fitMode == "3D" or self.fitMode == "4D":
            data1b = data.reduce("nBtag>=1&&nBtag<2")
            data2b = data.reduce("nBtag>=2&&nBtag<3")
            data3b = data.reduce("nBtag>=3&&nBtag<4")
            data4b = data.reduce("nBtag>=4&&nBtag<5")
            if data4b.numEntries() == 0:
                self.workspace.var("f4_TTj2b").setVal(0.)
                self.workspace.var("f4_TTj2b").setConstant(rt.kTRUE)
                self.workspace.var("f4_Vpj").setVal(0.)
                self.workspace.var("f4_Vpj").setConstant(rt.kTRUE)
                self.workspace.var("f4_TTj1b").setVal(0.)
                self.workspace.var("f4_TTj1b").setConstant(rt.kTRUE)
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
            del data1b, data2b, data3b, data4b
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
        
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=self.fitregion.split(","))]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=self.fitregion.split(","))]
        if self.fitMode == "3D": [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "nBtag", 5, ranges=self.fitregion.split(","))]

        if self.fitregion!='LowRsq,LowMR,HighMR':
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['LowRsq','LowMR','HighMR'])]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['LowRsq','LowMR','HighMR'])]
            if self.fitMode == "3D": [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "nBtag", 5, ranges=['LowRsq','LowMR','HighMR'])]

        # the 1b, 2b, 3b, 4b ranges still use the entire MR, Rsq range, so turn it off for the newFR fits
        #if self.fitMode == "3D":
        #    [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['1b'])]
        #    [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['1b'])]
        #    [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['2b'])]
        #    [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['2b'])]
        #    [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['3b'])]
        #    [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['3b'])]
        #    [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['4b'])]
        #    [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['4b'])]


    def plot1D(self, inputFile, varname, nbin=200, ranges=None):

        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        # set the integral precision
        rt.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-10) ;
        rt.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-10) ;
        # get the max and min (if different than default)
        xmin = self.workspace.var(varname).getMin()
        xmax = self.workspace.var(varname).getMax()
        data = RootTools.getDataSet(inputFile,'RMRTree')
        data = data.reduce(rt.RooFit.CutRange(rangeCut))
        data_cut = data.reduce(self.cut)
        
        # project the data on the variable
        frameMR = self.workspace.var(varname).frame(rt.RooFit.AutoSymRange(data_cut),rt.RooFit.Bins(nbin))
        frameMR.SetName(varname+"plot")
        frameMR.SetTitle(varname+"plot")
        
        data.plotOn(frameMR, rt.RooFit.LineColor(rt.kRed),rt.RooFit.MarkerColor(rt.kRed)) 
        data_cut.plotOn(frameMR)
        
        # project the full PDF on the data
        self.workspace.pdf(self.fitmodel).plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.Range(rangeCut))

        # plot each individual component: Vpj
        N_Vpj = self.workspace.function("Ntot_Vpj").getVal()
        # plot each individual component: TTj2b
        N_TTj2b = self.workspace.function("Ntot_TTj2b").getVal()
        # plot each individual component: TTj1b
        N_TTj1b = self.workspace.function("Ntot_TTj1b").getVal()

        Ntot = N_Vpj+N_TTj2b+N_TTj1b

        if N_Vpj >0:
            # project the first component: Vpj
            self.workspace.pdf("PDF_Vpj").plotOn(frameMR, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_Vpj/Ntot), rt.RooFit.Range(rangeCut))
        if N_TTj2b >0:
            # project the first component: TTj2b
            self.workspace.pdf("PDF_TTj2b").plotOn(frameMR, rt.RooFit.LineColor(rt.kOrange), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_TTj2b/Ntot), rt.RooFit.Range(rangeCut))
        if N_TTj1b >0:
            # project the first component: TTj1b
            self.workspace.pdf("PDF_TTj1b").plotOn(frameMR, rt.RooFit.LineColor(rt.kMagenta), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_TTj1b/Ntot), rt.RooFit.Range(rangeCut))
            
        return frameMR

    def plot1DHistoAllComponents(self, inputFile, xvarname, nbins = 25, ranges=None, data = None):
        
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
            
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)

        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
            
        # Generate a sample of Vpj
        effCutVpj = 1
        if self.workspace.var("Ntot_TTj2b") != None:
            N_TTj2b = self.workspace.var("Ntot_TTj2b").getVal()
            self.workspace.var("Ntot_TTj2b").setVal(0.)
        if self.workspace.var("Ntot_TTj1b") != None:
            N_TTj1b = self.workspace.var("Ntot_TTj1b").getVal()
            self.workspace.var("Ntot_TTj1b").setVal(0.)
        if self.workspace.var("Ntot_Vpj") != None:
            N_Vpj = self.workspace.var("Ntot_Vpj").getVal()
            if N_Vpj>1:
                toyDataVpj = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(N_Vpj)))
                beforeCutVpj = float(toyDataVpj.sumEntries())
                toyDataVpj = toyDataVpj.reduce(rangeCut)
                afterCutVpj = float(toyDataVpj.sumEntries())
                effCutVpj = afterCutVpj / beforeCutVpj

        # Generate a sample of TTj1b
        effCutTTj1b = 1
        self.workspace.var("Ntot_Vpj").setVal(0.)
        self.workspace.var("Ntot_TTj1b").setVal(N_TTj1b)
        if self.workspace.var("Ntot_TTj1b") != None and N_TTj1b>1 :
            toyDataTTj1b = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(N_TTj1b)))
            beforeCutTTj1b = float(toyDataTTj1b.sumEntries())
            toyDataTTj1b = toyDataTTj1b.reduce(rangeCut)
            afterCutTTj1b = float(toyDataTTj1b.sumEntries())
            effCutTTj1b = afterCutTTj1b / beforeCutTTj1b
                        
        # Generate a sample of TTj2b
        effCutTTj2b = 1
        self.workspace.var("Ntot_TTj2b").setVal(N_TTj2b)
        self.workspace.var("Ntot_TTj1b").setVal(0.)
        if self.workspace.var("Ntot_TTj2b") != None and N_TTj2b>1 :
            toyDataTTj2b = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(N_TTj2b)))
            beforeCutTTj2b = float(toyDataTTj2b.sumEntries())
            #toyDataTTj4b = toyDataTTj2b.reduce(rangeCut)
            #print "before 4b cut %f"%toyDataTTj4b.sumEntries()
            #toyDataTTj4b = toyDataTTj4b.reduce("nBtag>=4 && nBtag <5")
            #print "after 4b cut %f"%toyDataTTj4b.sumEntries()
            toyDataTTj2b = toyDataTTj2b.reduce(rangeCut)
            afterCutTTj2b = float(toyDataTTj2b.sumEntries())
            effCutTTj2b = afterCutTTj2b / beforeCutTTj2b
        # set the event yields back to their original values
        # NOTE: these original values REFER TO THE FULL REGION of MR and Rsq and nBtag!
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
        histoToyTTj2b = self.setPoissonErrors(rt.TH1D("histoToyTTj2b", "histoToyTTj2b",len(bins)-1, xedge))
        histoToyTTj1b = self.setPoissonErrors(rt.TH1D("histoToyTTj1b", "histoToyTTj1b",len(bins)-1, xedge))
        histoToyVpj = self.setPoissonErrors(rt.TH1D("histoToyVpj", "histoToyVpj",len(bins)-1, xedge))

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
                h.GetXaxis().SetBinLabel(3,"3")
                h.GetXaxis().SetBinLabel(4,"#geq 4")
                
            # y axis
            if name == "MR": h.GetYaxis().SetTitle("Events/(%i GeV)" %h.GetXaxis().GetBinWidth(1))
            elif name == "Rsq": h.GetYaxis().SetTitle("Events/(%4.3f)" %h.GetXaxis().GetBinWidth(1))
            elif name == "nBtag": h.GetYaxis().SetTitle("Events")

        def SetErrors(histo, nbins):
            for i in range(1, nbins+1):
                histo.SetBinError(i,rt.TMath.Sqrt(histo.GetBinContent(i)))

        # project the data on the histograms
        data.fillHistogram(histoData,rt.RooArgList(self.workspace.var(xvarname)))
        #toyData.fillHistogram(histoToy,rt.RooArgList(self.workspace.var(xvarname)))
        if self.workspace.var("Ntot_Vpj") != None and N_Vpj>1: toyDataVpj.fillHistogram(histoToyVpj,rt.RooArgList(self.workspace.var(xvarname)))
        if self.workspace.var("Ntot_TTj1b") != None and N_TTj1b>1 :toyDataTTj1b.fillHistogram(histoToyTTj1b,rt.RooArgList(self.workspace.var(xvarname)))
        if self.workspace.var("Ntot_TTj2b") != None and N_TTj2b>1 : toyDataTTj2b.fillHistogram(histoToyTTj2b,rt.RooArgList(self.workspace.var(xvarname)))
        # make the total
        if self.workspace.var("Ntot_TTj2b") != None and N_TTj2b>1: histoToy.Add(histoToyTTj2b, +1)
        if self.workspace.var("Ntot_Vpj") != None and N_Vpj>1: histoToy.Add(histoToyVpj, +1)
        if self.workspace.var("Ntot_TTj1b") != None and N_TTj1b>1 :histoToy.Add(histoToyTTj1b, +1)
        # We shouldn't scale to the data, we should scale to our prediction
        #scaleFactor = histoData.Integral()/histoToy.Integral()
        print "DATA NORM %f"%histoData.Integral()
        print "FIT NORM  %f"%(N_TTj2b*effCutTTj2b+N_Vpj*effCutVpj+N_TTj1b*effCutTTj1b)
        if N_TTj2b: scaleFactorTTj2b = (N_TTj2b*effCutTTj2b)/histoToyTTj2b.Integral()
        else: scaleFactorTTj2b = 1.
        if N_TTj1b: scaleFactorTTj1b = (N_TTj1b*effCutTTj1b)/histoToyTTj1b.Integral()
        else: scaleFactorTTj1b = 1.
        if N_Vpj: scaleFactorVpj = (N_Vpj*effCutVpj)/histoToyVpj.Integral()
        else: scaleFactorVpj  = 1.
        scaleFactor = (N_TTj2b*effCutTTj2b+N_Vpj*effCutVpj+N_TTj1b*effCutTTj1b)/histoToy.Integral()
        print "scaleFacorTTj1b = %f"%scaleFactorTTj1b
        print "scaleFacorTTj2b = %f"%scaleFactorTTj2b
        print "scaleFacorVpj = %f"%scaleFactorVpj
        print "scaleFacor = %f"%scaleFactor
        
        histoToyTTj2b.Scale(scaleFactorTTj2b)
        histoToyVpj.Scale(scaleFactorVpj)
        histoToyTTj1b.Scale(scaleFactorTTj1b)
        SetErrors(histoToyTTj2b, nbins)
        SetErrors(histoToyVpj, nbins)
        SetErrors(histoToyTTj1b, nbins)
        setName(histoToyTTj2b,xvarname)
        setName(histoToyVpj,xvarname)
        setName(histoToyTTj1b,xvarname)
        histoToyTTj1b.SetLineColor(rt.kViolet)
        histoToyTTj1b.SetLineWidth(2)
        histoToyTTj2b.SetLineColor(rt.kOrange)
        histoToyTTj2b.SetLineWidth(2)
        histoToyVpj.SetLineColor(rt.kRed)
        histoToyVpj.SetLineWidth(2)

        histoToy.Scale(scaleFactor)
        SetErrors(histoToy, nbins)
        setName(histoData,xvarname)
        setName(histoToy,xvarname)
        histoData.SetMarkerStyle(20)
        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        c = rt.TCanvas()
        c.SetLogy()
        c.SetName('DataMC_%s_%s_ALLCOMPONENTS' % (xvarname,'_'.join(ranges)) )
        #histoData.SetMinimum(1.)
        histoData.Draw("pe")

        histoToy.SetFillColor(rt.kBlue-10)
        histoToy.SetFillStyle(1001)
        histoToy.DrawCopy('e2same')

        histoToyStack = rt.THStack("histoToyStack","histoToyStack")
        if self.workspace.var("Ntot_Vpj").getVal():
            histoToyVpj.DrawCopy("histsame")
            c1 = rt.gROOT.GetColor(rt.kRed-4)
            c1.SetAlpha(1.0)
            histoToyVpj.SetFillStyle(0)
            if xvarname=="nBtag":
                histoToyVpj.SetFillStyle(1001)
                c1.SetAlpha(0.4)
                histoToyVpj.SetFillColor(rt.kRed-4)
                histoToyStack.Add(histoToyVpj)
            histoToyVpj.DrawCopy('histsame')
        if self.workspace.var("Ntot_TTj1b").getVal():
            histoToyTTj1b.DrawCopy("histsame")
            c2 = rt.gROOT.GetColor(rt.kViolet-4)
            c2.SetAlpha(1.0)
            histoToyTTj1b.SetFillStyle(0)
            if xvarname=="nBtag":
                histoToyTTj1b.SetFillStyle(1001)
                c2.SetAlpha(0.4)
                histoToyTTj1b.SetFillColor(rt.kViolet-4)
                histoToyStack.Add(histoToyTTj1b)
            histoToyTTj1b.DrawCopy('histsame')
        if self.workspace.var("Ntot_TTj2b").getVal():
            histoToyTTj2b.DrawCopy('histsame')
            c3 = rt.gROOT.GetColor(rt.kOrange-4)
            c3.SetAlpha(1.0)
            histoToyTTj2b.SetFillStyle(0)
            if xvarname=="nBtag":
                histoToyTTj2b.SetFillStyle(1001)
                c3.SetAlpha(0.4)
                histoToyTTj2b.SetFillColor(rt.kOrange-4)
                histoToyStack.Add(histoToyTTj2b)
            histoToyTTj2b.DrawCopy('histsame')
        # total
        if xvarname=="nBtag":
            histoToy.SetFillColor(rt.kBlue-10)
            histoToy.SetFillStyle(1001)
            histoToy.DrawCopy('e2same')
        histoToy.SetFillColor(rt.kWhite)
        histoToy.SetFillStyle(0)
        histoToy.DrawCopy('histsame')
        histoData.Draw("pesame")

        histToReturn = [histoToy, histoData, c]
        histToReturn.append(histoToyTTj2b)
        histToReturn.append(histoToyVpj)
        histToReturn.append(histoToyTTj1b)

        c.Print("razor_canvas_%s_%s_%s.pdf"%(self.name,'_'.join(ranges), xvarname))
        return histToReturn
