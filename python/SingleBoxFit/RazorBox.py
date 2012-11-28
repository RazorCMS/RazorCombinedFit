from RazorCombinedFit.Framework import Box
import math
import RootTools
import ROOT as rt
from array import *

#this is global, to be reused in the plot making
#this binning is poss
def getBinning_fine(boxName, varName, btag):
    if boxName == "Jet" or boxName == "TauTauJet" or boxName == "MultiJet":
        if varName == "MR" : return [400, 480, 560, 650, 750, 860, 980, 1200, 1600, 2500]
        if varName == "Rsq" : 
            if btag == "NoBtag": return [0.18,0.22,0.26,0.30,0.35,0.40,0.45,0.50]
            else: return [0.18,0.22,0.26,0.30,0.35,0.40,0.45,0.50,0.56,0.62,0.70,0.80,1.5]
        if varName == "nBtag" : return [0,1,2,3,4,5]
    else:
        if varName == "MR" : return [350, 410, 480, 560, 650, 750, 860, 980, 1200, 1600, 2500]
        if varName == "Rsq" :
            if btag == "NoBtag": return [0.11,0.15,0.2,0.25,0.30,0.35,0.40,0.45,0.50]
            else: return [0.11,0.15,0.2,0.25,0.30,0.35,0.40,0.45,0.50,0.56,0.62,0.70,0.80,1.5]
        if varName == "nBtag" : return [0,1,2,3,4,5]

def getBinning(boxName, varName, btag):
    if boxName == "Jet" or boxName == "TauTauJet" or boxName == "MultiJet":
        if varName == "MR" : return [400, 550, 700, 900, 1200, 1600, 2500]
        if varName == "Rsq" : 
            if btag == "NoBtag": return [0.18,0.24,0.35,0.50]
            else: return [0.18,0.24,0.32,0.41,0.52,0.64,0.80,1.5]
        if varName == "nBtag" : return [0,1,2,3,4,5]
    else:
        if varName == "MR" : return [350, 420, 500, 600, 740, 900, 1200, 1600, 2500]
        if varName == "Rsq" :
            if btag == "NoBtag": return [0.11,0.17,0.23,0.35,0.50]
            else: return [0.11,0.15,0.21,0.30,0.41,0.52,0.64,0.80,1.5]
        if varName == "nBtag" : return [0,1,2,3,4,5]
            
class RazorBox(Box.Box):
    
    def __init__(self, name, variables, fitMode = '2D', btag = True, fitregion = 'FULL'):
        super(RazorBox,self).__init__(name, variables)
        #data
        if not btag:
            self.btag = "NoBtag"
            self.zeros = {'UEC':[],'TTj':['MuEle','EleEle','MuMu','Mu','Ele','MuTau','EleTau','Jet','TauTauJet','MultiJet'],'Vpj':['MuEle','EleEle','MuMu','Mu','Ele','MuTau','EleTau','Jet','TauTauJet','MultiJet']}
        else:
            self.btag = "Btag"
            self.zeros = {'UEC':[],'TTj':['MuEle','EleEle','MuMu','Mu','Ele','MuTau','EleTau','Jet','TauTauJet','MultiJet'],'Vpj':['MuEle','EleEle','MuMu','Mu','Ele','MuTau','EleTau','Jet','TauTauJet','MultiJet']}
        self.cut = 'MR>=0'
        if fitregion=="SidebandL": self.fitregion = "SidebandMR,SidebandRsq"
        else: self.fitregion = fitregion
        self.fitMode = fitMode
        
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
                self.workspace.factory("RooRazor2DTail::PDF%s(MR,Rsq,MR0%s,R0%s,b%s)" %(label,label,label,label))
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
                self.workspace.factory("RooRazor2DTail::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s)" %(label,label,label,label))
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
                self.workspace.factory("RooRazor2DTail::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s)" %(label,label,label,label))
            ## define the nB pdf
            self.workspace.Print()
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
        self.fixParsExact("f1_%s" % flavour, False)
        self.fixParsExact("f2_%s" % flavour, False)
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

        # charge +1 pdf
        if self.fitMode == "4D":
            self.workspace.factory("RooTwoBin::PlusPDF(CHARGE,plusOne[1.])")
            self.workspace.factory("RooTwoBin::MinusPDF(CHARGE,minusOne[-1.])")
        
        # add the different components:
        # - W+jets
        # - ttbar+jets
        # - UEC
        self.addTailPdf("Vpj", False)
        self.addTailPdf("TTj", False)
        self.addTailPdf("UEC", True)

        # build the total PDF
        myPDFlist = rt.RooArgList(self.workspace.pdf("ePDF_Vpj"), self.workspace.pdf("ePDF_TTj"), self.workspace.pdf("ePDF_UEC"))
        #myPDFlist.add(self.workspace.pdf("ePDF_Zll"))
        #myPDFlist.add(self.workspace.pdf("ePDF_Znn"))
        #myPDFlist.add(self.workspace.pdf("ePDF_QCD"))
        model = rt.RooAddPdf(self.fitmodel, self.fitmodel, myPDFlist)
        
        # import the model in the workspace.
        self.importToWS(model)
        #print the workspace
        self.workspace.Print()

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
            if(self.btag == "Btag"):
                if (z == "TTj" and self.name != "MuMu" and self.name != "EleMu" and self.name != "EleEle"): self.floatBTagWithPenalties(z)
                else: self.floatBTag(z)
            # the "effective" first component in the Had box
            #if z == "Vpj" and self.name == "Had": self.floatComponent(z)
            # the b parameter in UEC is floated w/o penalty term in the 1Lep and Had boxes 
            #elif self.name == "Mu" and z == "UEC": self.floatComponentWithPenalty(z, False)
            #elif self.name == "Ele" and z == "UEC": self.floatComponentWithPenalty(z, False)
            #elif self.name == "Had" and z == "UEC": self.floatComponentWithPenalty(z, False)
            # otherwise the full component gets penalty terms 
            #else : self.floatComponentWithPenalty(z, True)
            #else :
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
        Nttj = self.workspace.var("Ntot_TTj").getVal()
        Nuec = self.workspace.var("Ntot_UEC").getVal()
        Nvpj = self.workspace.var("Ntot_Vpj").getVal()
        data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
        
        #in the case that the input file is an MC input file
        if data is None or not data:
            return None
        
        Ndata = data.sumEntries()
        self.workspace.var("Ntot_TTj").setVal(Ndata*Nttj/(Nttj+Nuec+Nvpj))
        self.workspace.var("Ntot_UEC").setVal(Ndata*Nuec/(Nttj+Nuec+Nvpj))
        self.workspace.var("Ntot_Vpj").setVal(Ndata*Nvpj/(Nttj+Nuec+Nvpj))
        # switch off btag fractions if no events
        if self.fitMode == "3D" or self.fitMode == "4D":
            data1b = data.reduce("nBtag>=1&&nBtag<2")
            data2b = data.reduce("nBtag>=2&&nBtag<3")
            data3b = data.reduce("nBtag>=3&&nBtag<4")
            data4b = data.reduce("nBtag>=4&&nBtag<5")
            if data4b.numEntries() == 0:
                self.workspace.var("f4_TTj").setVal(0.)
                self.workspace.var("f4_TTj").setConstant(rt.kTRUE)
                self.workspace.var("f4_Vpj").setVal(0.)
                self.workspace.var("f4_Vpj").setConstant(rt.kTRUE)
                self.workspace.var("f4_UEC").setVal(0.)
                self.workspace.var("f4_UEC").setConstant(rt.kTRUE)
            if data3b.numEntries() == 0:
                self.workspace.var("f3_TTj").setVal(0.)
                self.workspace.var("f3_TTj").setConstant(rt.kTRUE)
                self.workspace.var("f3_Vpj").setVal(0.)
                self.workspace.var("f3_Vpj").setConstant(rt.kTRUE)
                self.workspace.var("f3_UEC").setVal(0.)
                self.workspace.var("f3_UEC").setConstant(rt.kTRUE)
            if data2b.numEntries() == 0:
                self.workspace.var("f2_TTj").setVal(0.)
                self.workspace.var("f2_TTj").setConstant(rt.kTRUE)
                self.workspace.var("f2_Vpj").setVal(0.)
                self.workspace.var("f2_Vpj").setConstant(rt.kTRUE)
                self.workspace.var("f2_UEC").setVal(0.)
                self.workspace.var("f2_UEC").setConstant(rt.kTRUE)
            if data1b.numEntries() == 0:
                self.workspace.var("f1_TTj").setVal(0.)
                self.workspace.var("f1_TTj").setConstant(rt.kTRUE)
                self.workspace.var("f1_Vpj").setVal(0.)
                self.workspace.var("f1_Vpj").setConstant(rt.kTRUE)
                self.workspace.var("f1_UEC").setVal(0.)
                self.workspace.var("f1_UEC").setConstant(rt.kTRUE)
            del data1b, data2b, data3b, data4b
        del data
            
        # switch off V+jets in the high-btag bins
        #self.workspace.var("f2_Vpj").setVal(0.)
        #self.workspace.var("f1_Vpj").setConstant(rt.kTRUE)
        #self.workspace.var("f2_Vpj").setVal(0.)
        #self.workspace.var("f2_Vpj").setConstant(rt.kTRUE)
        #self.workspace.var("f3_Vpj").setVal(0.)
        #self.workspace.var("f3_Vpj").setConstant(rt.kTRUE)
        #self.workspace.var("f4_Vpj").setVal(0.)
        #self.workspace.var("f4_Vpj").setConstant(rt.kTRUE)
        # I am having troubles with the fit...
        #self.workspace.var("f4_UEC").setVal(0.)
        #self.workspace.var("f4_UEC").setConstant(rt.kTRUE)
        #self.workspace.var("f4_TTj").setVal(0.)
        #self.workspace.var("f4_TTj").setConstant(rt.kTRUE)
        #self.workspace.var("f3_TTj").setConstant(rt.kTRUE)
        #self.workspace.var("f1_TTj").setConstant(rt.kTRUE)
        #self.workspace.var("f2_TTj").setConstant(rt.kTRUE)
        ##### 
        #self.workspace.var("MR0_TTj").setVal(0.)
        #self.workspace.var("MR0_TTj").setConstant(rt.kTRUE)
        #self.workspace.var("MR0_Vpj").setVal(0.)
        #self.workspace.var("MR0_Vpj").setConstant(rt.kTRUE)
        #self.workspace.var("MR0_UEC").setVal(0.)
        #self.workspace.var("MR0_UEC").setConstant(rt.kTRUE)

        #self.fixPars("MR0_TTj")
        #self.fixPars("R0_TTj")
        #self.fixPars("b_TTj")
        #self.fixPars("n_TTj")

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
        self.importToWS(add)
        self.workspace.Print()
        self.signalmodel = add.GetName()
        return extended.GetName()
        
    def plot(self, inputFile, store, box):
        #store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=['fR1', 'fR2','fR3','fR4']), dir=box)
        #store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=['FULL']), dir=box)

        #[store.store(s, dir=box) for s in self.plot1DHisto(inputFile, "MR", ranges=['fR1', 'fR2','fR3','fR4'])]
        #[store.store(s, dir=box) for s in self.plot1DHisto(inputFile, "Rsq", ranges=['fR1', 'fR2','fR3','fR4'])]
        #[store.store(s, dir=box) for s in self.plot1DHisto(inputFile, "MR", ranges=['FULL'])]
        #[store.store(s, dir=box) for s in self.plot1DHisto(inputFile, "Rsq", ranges=['FULL'])]

        #[store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 25, ranges=['fR1', 'fR2','fR3','fR4'])]
        #[store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['fR1', 'fR2','fR3','fR4'])]

        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=[self.fitregion])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=[self.fitregion])]

        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['FULL'])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['FULL'])]
        #[store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "nBtag", 5, ranges=['FULL'])]

        #store.store(self.plot1D(inputFile, "MR", 80, ranges=['FULL']), dir=box)
        #store.store(self.plot1D(inputFile, "Rsq", 25, ranges=['FULL']), dir=box)
        #store.store(self.plot1D(inputFile, "nBtag", 5, ranges=['FULL']), dir=box)

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
        # plot each individual component: TTj
        N_TTj = self.workspace.function("Ntot_TTj").getVal()
        # plot each individual component: UEC
        N_UEC = self.workspace.function("Ntot_UEC").getVal()
        # plot each individual component: Zll
        #N_Zll = self.workspace.function("Ntot_Zll").getVal()
        # plot each individual component: Znn
        #N_Znn = self.workspace.function("Ntot_Znn").getVal()
        # plot each individual component: QCD
        #N_QCD = 0 #self.workspace.function("Ntot_QCD").getVal() 

        Ntot = N_Vpj+N_TTj+N_UEC#+N_QCD+N_Zll+N_Znn

        if N_Vpj >0:
            # project the first component: Vpj
            self.workspace.pdf("PDF_Vpj").plotOn(frameMR, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_Vpj/Ntot), rt.RooFit.Range(rangeCut))
        if N_TTj >0:
            # project the first component: TTj
            self.workspace.pdf("PDF_TTj").plotOn(frameMR, rt.RooFit.LineColor(rt.kOrange), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_TTj/Ntot), rt.RooFit.Range(rangeCut))
        if N_UEC >0:
            # project the first component: UEC
            self.workspace.pdf("PDF_UEC").plotOn(frameMR, rt.RooFit.LineColor(rt.kMagenta), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N_UEC/Ntot), rt.RooFit.Range(rangeCut))
            
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
        #toyData = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), 50*data.numEntries())
        #toyData = toyData.reduce(self.getVarRangeCutNamed(ranges=ranges))

        # Generate a sample of Vpj
        if self.workspace.var("Ntot_TTj") != None:
            Ntt = self.workspace.var("Ntot_TTj").getVal()
            self.workspace.var("Ntot_TTj").setVal(0.)
        if self.workspace.var("Ntot_UEC") != None:
            Nuec = self.workspace.var("Ntot_UEC").getVal()
            self.workspace.var("Ntot_UEC").setVal(0.)
        if self.workspace.var("Ntot_Vpj") != None:
            Nvpj = self.workspace.var("Ntot_Vpj").getVal()
            if Nvpj>1:
                #toyDataVpj = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(data.numEntries()-Ntt-Nuec)))
                toyDataVpj = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(100*(Nvpj)))
                toyDataVpj = toyDataVpj.reduce(self.getVarRangeCutNamed(ranges=ranges))

        # Generate a sample of UEC
        self.workspace.var("Ntot_Vpj").setVal(0.)
        self.workspace.var("Ntot_UEC").setVal(Nuec)
        if self.workspace.var("Ntot_UEC") != None and Nuec>1 :
            #toyDataUEC = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(data.numEntries()-Ntt-Nvpj)))
            toyDataUEC = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(100*(Nuec)))
            toyDataUEC = toyDataUEC.reduce(self.getVarRangeCutNamed(ranges=ranges))
                        
        # Generate a sample of TTj
        self.workspace.var("Ntot_TTj").setVal(Ntt)
        self.workspace.var("Ntot_UEC").setVal(0.)
        if self.workspace.var("Ntot_TTj") != None and Ntt>1 :
            #toyDataUEC = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(data.numEntries()-Ntt-Nvpj)))
            toyDataTTj = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(100*(Ntt)))
            toyDataTTj = toyDataTTj.reduce(self.getVarRangeCutNamed(ranges=ranges))
             
        self.workspace.var("Ntot_UEC").setVal(Nuec)
        self.workspace.var("Ntot_Vpj").setVal(Nvpj)
        #self.workspace.var("Ntot_Znn").setVal(Nznn)

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
        histoToyTTj = self.setPoissonErrors(rt.TH1D("histoToyTTj", "histoToyTTj",len(bins)-1, xedge))
        histoToyUEC = self.setPoissonErrors(rt.TH1D("histoToyUEC", "histoToyUEC",len(bins)-1, xedge))
        histoToyVpj = self.setPoissonErrors(rt.TH1D("histoToyVpj", "histoToyVpj",len(bins)-1, xedge))
        #histoToyZnn = self.setPoissonErrors(rt.TH1D("histoToyZnn", "histoToyZnn",len(bins)-1, xedge))

        def setName(h, name):
            h.SetName('%s_%s_%s_ALLCOMPONENTS' % (h.GetName(),name,'_'.join(ranges)) )
            # x axis
            if name == "MR": h.GetXaxis().SetTitle("M_{R} [GeV]")
            elif name == "Rsq": h.GetXaxis().SetTitle("R^{2}")
            elif name == "nBtag": h.GetXaxis().SetTitle("n_{Bjet}")
            # y axis
            if name == "MR": h.GetYaxis().SetTitle("Events/(%i GeV)" %h.GetXaxis().GetBinWidth(1))
            elif name == "Rsq": h.GetYaxis().SetTitle("Events/(%4.3f)" %h.GetXaxis().GetBinWidth(1))
            elif name == "nBtag": h.GetYaxis().SetTitle("Events")
            # axis labels
            h.GetXaxis().SetTitleSize(0.05)
            h.GetYaxis().SetTitleSize(0.05)
            h.GetXaxis().SetLabelSize(0.05)
            h.GetYaxis().SetLabelSize(0.05)
            h.GetXaxis().SetTitleOffset(0.90)
            h.GetYaxis().SetTitleOffset(0.93)
        
        def SetErrors(histo, nbins):
            for i in range(1, nbins+1):
                histo.SetBinError(i,rt.TMath.Sqrt(histo.GetBinContent(i)))

        # project the data on the histograms
        #data.tree().Project("histoData",xvarname)
        data.fillHistogram(histoData,rt.RooArgList(self.workspace.var(xvarname)))
        #toyData.fillHistogram(histoToy,rt.RooArgList(self.workspace.var(xvarname)))
        if self.workspace.var("Ntot_Vpj") != None and Nvpj>1: toyDataVpj.fillHistogram(histoToyVpj,rt.RooArgList(self.workspace.var(xvarname)))
        if self.workspace.var("Ntot_UEC") != None and Nuec>1 :toyDataUEC.fillHistogram(histoToyUEC,rt.RooArgList(self.workspace.var(xvarname)))
        if self.workspace.var("Ntot_TTj") != None and Ntt>1 : toyDataTTj.fillHistogram(histoToyTTj,rt.RooArgList(self.workspace.var(xvarname)))
        # make the total
        if self.workspace.var("Ntot_TTj") != None and Ntt>1: histoToy.Add(histoToyTTj, +1)
        if self.workspace.var("Ntot_Vpj") != None and Nvpj>1: histoToy.Add(histoToyVpj, +1)
        if self.workspace.var("Ntot_UEC") != None and Nuec>1 :histoToy.Add(histoToyUEC, +1)
        scaleFactor = histoData.Integral()/histoToy.Integral()
        #if self.name == "Had":
        #    toyDataZnn.fillHistogram(histoToyZnn,rt.RooArgList(self.workspace.var(xvarname)))
        #    histoToyTTj.Add(histoToyZnn, -1)
        #    histoToyZnn.Scale(scaleFactor)
        #    SetErrors(histoToyZnn, nbins)
        #    setName(histoToyZnn,xvarname)
        #    histoToyZnn.SetLineColor(rt.kGreen)    
        histoToyTTj.Scale(scaleFactor)
        histoToyVpj.Scale(scaleFactor)
        histoToyUEC.Scale(scaleFactor)
        SetErrors(histoToyTTj, nbins)
        SetErrors(histoToyVpj, nbins)
        SetErrors(histoToyUEC, nbins)
        setName(histoToyTTj,xvarname)
        setName(histoToyVpj,xvarname)
        setName(histoToyUEC,xvarname)
        histoToyUEC.SetLineColor(rt.kViolet)
        histoToyUEC.SetLineWidth(2)
        histoToyTTj.SetLineColor(rt.kOrange)
        histoToyTTj.SetLineWidth(2)
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
        histoData.Draw("pe")

        if self.workspace.var("Ntot_Vpj").getVal():
            histoToyVpj.DrawCopy("histsame")
            histoToyVpj.SetFillColor(rt.kRed)
            histoToyVpj.SetFillStyle(3018)
            histoToyVpj.Draw('e2same')
        if self.workspace.var("Ntot_UEC").getVal() and self.name != "MuEle":
            histoToyUEC.DrawCopy("histsame")
            histoToyUEC.SetFillColor(rt.kViolet)
            histoToyUEC.SetFillStyle(3018)
            histoToyUEC.Draw('e2same')
        if self.workspace.var("Ntot_TTj").getVal():
            histoToyTTj.DrawCopy('histsame')
            histoToyTTj.SetFillColor(rt.kOrange)
            histoToyTTj.SetFillStyle(3018)
            histoToyTTj.Draw('e2same')        
        # total
        histoToy.DrawCopy('histsame')
        histoToy.DrawCopy('histsame')
        histoToy.SetFillColor(rt.kBlue)
        histoToy.SetFillStyle(3018)
        histoToy.Draw('e2same')

        # add standard text
        #pt = rt.TPaveText(0.6,0.6,0.9,0.9,"ndr")
        #pt.SetBorderSize(0)
        #pt.SetFillColor(0)
        #pt.SetFillStyle(0)
        #pt.SetLineColor(0)
        #pt.SetTextAlign(13)
        #pt.SetTextSize(0.04831933)
        #text = pt.AddText("CMS Preliminary  #sqrt{s} = 7 TeV")
        #text = pt.AddText("Razor %s box #int Ldt = %3.2f fb^{-1} " %(self.name,self.workspace.var('Lumi').getVal()/1000.))
        #pt.Draw()
        
        #histoData.Draw("pesame")

        #leg = rt.TLegend(0.6,0.6,0.9,0.9)
        #leg.SetFillColor(0)
        #leg.AddEntry(histoToyVpj,"W+jets","l")
        #leg.AddEntry(histoToyTTj,"t#bar{t}","l")
        #leg.AddEntry(histoToyUEC,"UEC","l")
        #if self.name == "Had": leg.AddEntry(histoToyZnn,"Z(#nu#nu)+jets","l")
        #leg.AddEntry(histoToy,"Total","l")
        #leg.Draw("same")

        histToReturn = [histoToy, histoData, c]
        histToReturn.append(histoToyTTj)
        if self.name != "MuEle": histToReturn.append(histoToyVpj)
        histToReturn.append(histoToyUEC)
        #if self.name == "Had": histToReturn.append(histoToyZnn)

        c.Print("razor_canvas_%s.pdf"%(xvarname))
        return histToReturn
