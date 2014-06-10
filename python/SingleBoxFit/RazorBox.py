from RazorCombinedFit.Framework import Box
import math
import RootTools
import ROOT as rt
from array import *
import sys

#this is global, to be reused in the plot making
def getBinning(boxName, varName, btag):
    if boxName in ["BJet"]:
        if varName == "MR" : return [400, 450, 550, 700, 900, 1200, 1600, 2500, 4000]
        elif varName == "Rsq" :
            return [0.25,0.30,0.41,0.52,0.64,0.80,1.5]
    else:
        if varName == "MR" : return [350, 450, 550, 700, 900, 1200, 1600, 2500, 4000]
        elif varName == "Rsq" :
            return [0.08, 0.10, 0.15, 0.20,0.30,0.41,0.52,0.64,0.80,1.5]

        
    if varName == "nBtag" :
        if btag == "NoBtag":        return [0,1]
        elif btag == "Btag":        return [1,2,3,4]
    if varName == "nJet" :
        if btag == "NoJet":        return [0,1]
        elif btag == "Jet":        return [1,2,3,4]

            
def FindLastBin(h):
    for i in range(1,h.GetXaxis().GetNbins()):
        thisbin = h.GetXaxis().GetNbins()-i
        if h.GetBinContent(thisbin)>=0.1: return thisbin+1
    return h.GetXaxis().GetNbins()    
                     
class RazorBox(Box.Box):
    
    def __init__(self, name, variables, fitMode = '3D', btag = True, fitregion = ""):
        super(RazorBox,self).__init__(name, variables)
        #data
        if not btag:
            self.btag = "NoBtag"
            self.zeros = {'TTj1b':[],'TTj2b':[],'Vpj':[]}
        else:
            self.btag = "Btag"
            self.njet = "Jet"
            self.zeros = {'TTj1b':['Jet2b'],
                          'TTj2b':['MuEle','EleEle','MuMu','TauTauJet','Jet1b'],
                          'Vpj':['MuEle','EleEle','MuMu','Mu','MuJet','MuMultiJet','EleJet','EleMultiJet','MuTau','EleTau','TauTauJet','MultiJet','Jet','Jet2b','Ele','BJetHS','BJetLS', 'BJet']}
                        
        if fitregion=="Sideband": self.fitregion = "LowMR,LowRsq"#,LowMR"
        #if fitregion=="Sideband": self.fitregion = "fR1, fR2, fR3, fR4, fR5"
        # for CLs limit setting  remove the following line
        elif fitregion=="FULL": self.fitregion = "FULL"#"LowRsq,LowMR,HighMR"
        else: self.fitregion = fitregion
        self.fitMode = fitMode

        self.cut = 'Rsq > 0.0'
        
        
    def addTailPdf(self, flavour, doSYS):
        label = '_%s' % flavour
        # 2D FIT
        if self.fitMode == "2D":
            # define the R^2 vs MR
            if doSYS == True:
                self.workspace.factory("RooRazor2DTail_SYS::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                #tail-systematic parameter
                self.workspace.var("n%s" %label).setConstant(rt.kFALSE)
            else:
                self.workspace.factory("RooRazor2DTail::RazPDF%s(MR,Rsq,MR0%s,R0%s,b%s)" %(label,label,label,label))
                #self.workspace.factory("RooRazor2DTail_SYS::PDF%s(MR,Rsq,MR0%s,R0%s,b%s,n%s)" %(label,label,label,label,label))
                #tail-systematic parameter fixed to 1.0
                self.workspace.var("n%s" %label).setVal(1.0)
                self.workspace.var("n%s" %label).setConstant(rt.kTRUE)
            #associate the yields to the pdfs through extended PDFs
            self.workspace.factory("RooExtendPdf::ePDF%s(RazPDF%s, Ntot%s)" %(label, label, label))
            
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
    def floatComponentWithPenalty(self,flavour):
        self.fixParsPenalty("R0_%s" % flavour)
        self.fixPars("R0_%s_s" % flavour)
        self.fixParsPenalty("b_%s" % flavour)
        self.fixPars("b_%s_s" % flavour)
        self.fixParsPenalty("n_%s" % flavour)
        self.fixPars("n_%s_s" % flavour)
            
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
        self.workspace.factory("expr::MRnorm('@0*(1/4000.)',MR)")
        
        # charge +1 pdf
        if self.fitMode == "4D":
            self.workspace.factory("RooTwoBin::PlusPDF(CHARGE,plusOne[1.])")
            self.workspace.factory("RooTwoBin::MinusPDF(CHARGE,minusOne[-1.])")
        
        # add only relevant components (for generating toys)
        myPDFlist = rt.RooArgList()
        for z in self.zeros:
            print z
            if self.name not in self.zeros[z]:
                self.addTailPdf(z, not (z=="Vpj"))
                #self.addTailPdf(z, True)
                myPDFlist.add(self.workspace.pdf("ePDF_%s"%z))

        # add ALL the different components (for combining boxes in limit setting later):
        # - W+jets
        # - ttbar+jets 1b
        # - ttbar+jets j2b
        #self.addTailPdf("Vpj",False)
        #self.addTailPdf("TTj1b",True)
        #if self.fitMode=='3D' or self.name!="Jet1b": self.addTailPdf("TTj2b",True)
        
        # build the total PDF
        #if self.fitMode=='3D': myPDFlist = rt.RooArgList(self.workspace.pdf("ePDF_Vpj"), self.workspace.pdf("ePDF_TTj1b"), self.workspace.pdf("ePDF_TTj2b"))
        #elif self.fitMode=='2D' or self.name!="Jet1b": myPDFlist = rt.RooArgList(self.workspace.pdf("ePDF_Vpj"), self.workspace.pdf("ePDF_TTj1b"))
                        
        model = rt.RooAddPdf(self.fitmodel, self.fitmodel, myPDFlist)
        model.Print('V')
      
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
            #self.floatComponentWithPenalty(z)
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
        Ndata = data.reduce(self.getVarRangeCutNamed(ranges=self.fitregion.split(","))).sumEntries()

        # self.workspace.var("Ntot_TTj2b").setVal(Ndata*N_TTj2b/(N_TTj2b+N_TTj1b+N_Vpj))
        # self.workspace.var("Ntot_TTj1b").setVal(Ndata*N_TTj1b/(N_TTj2b+N_TTj1b+N_Vpj))
        # self.workspace.var("Ntot_Vpj").setVal(Ndata*N_Vpj/(N_TTj2b+N_TTj1b+N_Vpj))

        
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
        signalModel, nSig = self.makeRooRazor3DSignal(inputFile,modelName)
                 
        # compute the expected yield/(pb-1)
        self.workspace.var('sigma').setVal(signalXsec)
       
        #set the MC efficiency relative to the number of events generated
        # compute the signal yield multiplying by the efficiency
        self.workspace.factory("expr::Ntot_%s('@0*@1*@2*@3',sigma, lumi, eff, eff_value_%s)" %(modelName,self.name))
        self.workspace.Print("V")
        extended = self.workspace.factory("RooExtendPdf::eBinPDF_%s(%s, Ntot_%s)" % (modelName,signalModel,modelName))
        
        theRealFitModel = "fitmodel"
        
        SpBPdfList = rt.RooArgList(self.workspace.pdf("eBinPDF_Signal"))
        # prevent nan when there is no signal expected
        if self.workspace.var("Ntot_TTj1b").getVal() > 0: SpBPdfList.add(self.workspace.pdf("ePDF_TTj1b"))
        if self.workspace.var("Ntot_TTj2b").getVal() > 0: SpBPdfList.add(self.workspace.pdf("ePDF_TTj2b"))
        if self.workspace.var("Ntot_Vpj").getVal() > 0: SpBPdfList.add(self.workspace.pdf("ePDF_Vpj"))
                
        add = rt.RooAddPdf('%s_%sCombined' % (theRealFitModel,modelName),'Signal+BG PDF',
                           SpBPdfList)
        
        self.importToWS(add)
        self.signalmodel = add.GetName()
        return extended.GetName()
        
    def plot(self, inputFile, store, box, data=None, fitmodel="none", frName="none"):
              
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 64, ranges=[self.fitregion],data=data,fitmodel=fitmodel)]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 50, ranges=[self.fitregion],data=data,fitmodel=fitmodel)]
        if self.fitMode == "3D": [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "nBtag", 3, ranges=[self.fitregion],data=data,fitmodel=fitmodel)]
     
    def plot1D(self, inputFile, varname, nbin=200, ranges=None, data=None, fitmodel="none", frName="none"):

        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        print ''
        print 'rangeCut', rangeCut
        print ''
        # set the integral precision
        rt.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-30)
        rt.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-30)
        
        # get the max and min (if different than default)
        xmin = min([self.workspace.var(varname).getMin(myRange) for myRange in ranges])
        xmax = max([self.workspace.var(varname).getMax(myRange) for myRange in ranges])
        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree')
        if fitmodel=="none":
            fitmodel = self.fitmodel
        if frName=="none":
            frName = "independentFR"
        print data.GetName()
        print fitmodel
        print frName
        
        data_cut = data.reduce(self.cut)
        data_cut = data_cut.reduce(rangeCut)
        
        datamin = array('d',[0])
        datamax = array('d',[0])
        data_cut.getRange(self.workspace.var(varname), datamin, datamax, 0, False)
        
        # project the data on the variable
        if varname =="nBtag":
            frameMR = self.workspace.var(varname).frame(rt.RooFit.Range(xmin,xmax),rt.RooFit.Bins(int(xmax-xmin)))
        elif varname =="Rsq":
            rsqMin = xmin
            if datamax[0] < 0.5:
                rsqMax = 0.5
                nbin = 8*(rsqMax-rsqMin)/(0.05)
            elif datamax[0] < 0.75:
                rsqMax = 0.75
                nbin = 4*(rsqMax-rsqMin)/(0.05)
            elif datamax[0] < 1.0:
                rsqMax = 1.25
                nbin = 3*(rsqMax-rsqMin)/(0.05)
            elif datamax[0] < 1.25:
                rsqMax = 1.25
                nbin = 3*(rsqMax-rsqMin)/(0.05)
            else:
                rsqMax = 1.5
                nbin = 3*(rsqMax-rsqMin)/(0.05)
            frameMR = self.workspace.var(varname).frame(rt.RooFit.Range(rsqMin,rsqMax),rt.RooFit.Bins(int(nbin)))
        elif varname =="MR":
            mrMin = xmin
            if datamax[0] < 800:
                mrMax = 800
                nbin = 4*(mrMax-mrMin)/(50)
            elif datamax[0] < 1200:
                mrMax = 1200
                nbin = 2*(mrMax-mrMin)/(50)
            elif datamax[0] < 1600:
                mrMax = 2000
                nbin = 2*(mrMax-mrMin)/(50)
            elif datamax[0] < 2000:
                mrMax = 2000
                nbin = 2*(mrMax-mrMin)/(50)
            elif datamax[0] < 2500:
                mrMax = 2000
                nbin = 2*(mrMax-mrMin)/(50)
            elif datamax[0] < 3000:
                mrMax = 2000
                nbin = 2*(mrMax-mrMin)/(50)
            else:
                mrMax = 4000
                nbin = 1*(mrMax-mrMin)/(50)
            frameMR = self.workspace.var(varname).frame(rt.RooFit.Range(mrMin,mrMax),rt.RooFit.Bins(int(nbin)))
        
        #plot data
        data_cut.plotOn(frameMR)
        buff = 1e-12
        if ",".join(ranges).find("3b")!=-1 and ",".join(ranges).find("2b")!=-1:
            plotlabel = "23b"
            btagMin = 2+buff
            btagMax = 4-buff
        elif ",".join(ranges).find("3b")!=-1:
            plotlabel = "3b"
            btagMin = 3+buff
            btagMax = 4-buff
        elif ",".join(ranges).find("2b")!=-1:
            plotlabel = "2b"
            btagMin = 2+buff
            btagMax = 3-buff
        elif ",".join(ranges).find("1b")!=-1:
            plotlabel = "1b"
            btagMin = 1+buff
            btagMax = 2-buff
        else:
            plotlabel = ""
            btagMin = self.workspace.var("nBtag").getMin()
            btagMax = self.workspace.var("nBtag").getMax()


        if varname=="MR":
            mrBins = getBinning(self.name, "MR", self.btag)
            rsqBins = getBinning(self.name, "Rsq", self.btag)[:3]
        elif varname=="Rsq":
            mrBins = getBinning(self.name, "MR", self.btag)[:3]
            rsqBins = getBinning(self.name, "Rsq", self.btag)
        else:
            mrBins = getBinning(self.name, "MR", self.btag)
            rsqBins = getBinning(self.name, "Rsq", self.btag)
            
        
        self.workspace.var("MR").setRange("VeryLowMR%s"%plotlabel,mrBins[0],mrBins[1])
        self.workspace.var("Rsq").setRange("VeryLowMR%s"%plotlabel,rsqBins[1],rsqBins[-1])
        self.workspace.var("nBtag").setRange("VeryLowMR%s"%plotlabel,btagMin,btagMax)
        self.workspace.var("MR").setRange("NotVeryLowMR%s"%plotlabel,mrBins[1],mrBins[-1])
        self.workspace.var("Rsq").setRange("NotVeryLowMR%s"%plotlabel,rsqBins[0],rsqBins[-1])
        self.workspace.var("nBtag").setRange("NotVeryLowMR%s"%plotlabel,btagMin,btagMax)
        self.workspace.var("MR").setRange("VeryLowRsq%s"%plotlabel,mrBins[1],mrBins[-1])
        self.workspace.var("Rsq").setRange("VeryLowRsq%s"%plotlabel,rsqBins[0],rsqBins[1])
        self.workspace.var("nBtag").setRange("VeryLowRsq%s"%plotlabel,btagMin,btagMax)
        self.workspace.var("MR").setRange("NotVeryLowRsq%s"%plotlabel,mrBins[0],mrBins[-1])
        self.workspace.var("Rsq").setRange("NotVeryLowRsq%s"%plotlabel,rsqBins[1],rsqBins[-1])
        self.workspace.var("nBtag").setRange("NotVeryLowRsq%s"%plotlabel,btagMin,btagMax)
        
        if varname=="MR":
            self.workspace.var("MR").setRange("InterMR",mrBins[1],mrBins[2])
            self.workspace.var("Rsq").setRange("InterMR",rsqBins[1],rsqBins[-1])
            self.workspace.var("nBtag").setRange("InterMR",btagMin,btagMax)
            self.workspace.var("MR").setRange("FinalMR",mrBins[2],mrBins[-1])
            self.workspace.var("Rsq").setRange("FinalMR",rsqBins[0],rsqBins[1])
            self.workspace.var("nBtag").setRange("FinalMR",btagMin,btagMax)
            MRRanges = ["VeryLowMR%s"%plotlabel,"NotVeryLowMR%s"%plotlabel]
            if ranges==['LowRsq','LowMR']:
                MRRanges = ["VeryLowMR%s"%plotlabel,"InterMR","FinalMR"]
            if ranges==['HighMR']:
                MRRanges=ranges 
        elif varname=="Rsq":
            self.workspace.var("MR").setRange("FinalRsq",mrBins[0],mrBins[-1])
            self.workspace.var("Rsq").setRange("FinalRsq",rsqBins[1],rsqBins[2])
            self.workspace.var("nBtag").setRange("FinalRsq",btagMin,btagMax)
            MRRanges = ["VeryLowRsq%s"%plotlabel,"NotVeryLowRsq%s"%plotlabel]
            if ranges==['LowRsq','LowMR']:
                MRRanges = ["VeryLowRsq%s"%plotlabel,"LowMR"]
            if ranges==['HighMR']:
                MRRanges=ranges 
        elif varname=="nBtag":
            MRRanges = [",".join(ranges)]
            

        frameMR.SetName(varname+"_rooplot_"+fitmodel+"_"+data.GetName()+"_"+plotlabel)
        frameMR.SetTitle("")
        if varname=="MR":
            frameMR.SetXTitle("M_{R} [GeV]")
        if varname=="Rsq":
            frameMR.SetXTitle("R^{2}")
        if varname=="nBtag":
            frameMR.SetXTitle("n_{b-tag}")
            
        # get fit result to visualize error
        fr = self.workspace.obj(frName)
        
        # to get statistical error (error only from Ntot)
        
        errorArgSet = rt.RooArgSet()
        components = ["TTj1b","TTj2b","Vpj"]
        [errorArgSet.add(self.workspace.var("n_%s"%z)) for z in components if self.name not in self.zeros[z]]
        [errorArgSet.add(self.workspace.var("b_%s"%z)) for z in components if self.name not in self.zeros[z]]
        [errorArgSet.add(self.workspace.var("MR0_%s"%z)) for z in components if self.name not in self.zeros[z]]
        [errorArgSet.add(self.workspace.var("R0_%s"%z)) for z in components if self.name not in self.zeros[z]]
        #[errorArgSet.add(self.workspace.var("f3_%s"%z)) for z in components if self.name not in self.zeros[z]]
        #[errorArgSet.add(self.workspace.var("Ntot_%s"%z)) for z in components if self.name not in self.zeros[z]]
        errorArgSet.Print("v")
        
        # PLOT TOTAL ERROR
        [self.workspace.pdf(fitmodel).plotOn(frameMR,rt.RooFit.LineColor(rt.kBlue), rt.RooFit.FillColor(rt.kBlue-10),rt.RooFit.ProjectionRange(MRRange),rt.RooFit.Range(MRRange),rt.RooFit.NormRange(MRRange),rt.RooFit.VisualizeError(fr,errorArgSet,1,True)) for MRRange  in MRRanges]
         # PLOT THE TOTAL NOMINAL
        [self.workspace.pdf(fitmodel).plotOn(frameMR, rt.RooFit.Name("Total"), rt.RooFit.LineColor(rt.kBlue), rt.RooFit.FillColor(rt.kBlue-10),rt.RooFit.ProjectionRange(MRRange),rt.RooFit.Range(MRRange),rt.RooFit.NormRange(MRRange)) for MRRange in MRRanges]
            
        # plot each individual component: Vpj
        vars = rt.RooArgSet(self.workspace.set('variables'))
        norm_region = ','.join(MRRanges)
        N_Vpj = self.workspace.var("Ntot_Vpj").getVal()*(self.getFitPDF("ePDF_Vpj").createIntegral(vars,vars,0,norm_region).getVal()/self.getFitPDF("ePDF_Vpj").createIntegral(vars,vars).getVal())
        # plot each individual component: TTj2b
        N_TTj2b = 0.
        if self.fitMode!="2D":
            N_TTj2b = self.workspace.var("Ntot_TTj2b").getVal()*(self.getFitPDF("ePDF_TTj2b").createIntegral(vars,vars,0,norm_region).getVal()/self.getFitPDF("ePDF_TTj2b").createIntegral(vars,vars).getVal())
        # plot each individual component: TTj1b
        N_TTj1b = self.workspace.var("Ntot_TTj1b").getVal()*(self.getFitPDF("ePDF_TTj1b").createIntegral(vars,vars,0,norm_region).getVal()/self.getFitPDF("ePDF_TTj1b").createIntegral(vars,vars).getVal())

        Ntot = N_Vpj+N_TTj2b+N_TTj1b
        
        showVpj=(N_Vpj>0)
        showTTj2b =(N_TTj2b>0)
        showTTj1b = (N_TTj1b>0)

        if showTTj1b:
            # project the first component: TTj1b
            [self.workspace.pdf("ePDF_TTj1b").plotOn(frameMR,rt.RooFit.Name("TTj1b"), rt.RooFit.LineColor(rt.kViolet), rt.RooFit.LineStyle(8),rt.RooFit.Normalization(N_TTj1b/Ntot),rt.RooFit.ProjectionRange(MRRange),rt.RooFit.Range(MRRange),rt.RooFit.NormRange(MRRange)) for MRRange in MRRanges]
        if showTTj2b:
            # project the second component: TTj2b
            [self.workspace.pdf("ePDF_TTj2b").plotOn(frameMR,rt.RooFit.Name("TTj2b"), rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8),rt.RooFit.Normalization(N_TTj2b/Ntot),rt.RooFit.ProjectionRange(MRRange),rt.RooFit.Range(MRRange),rt.RooFit.NormRange(MRRange)) for MRRange in MRRanges]
        if showVpj:
            # project the last component: Vpj
            [self.workspace.pdf("ePDF_Vpj").plotOn(frameMR, rt.RooFit.Name("Vpj"), rt.RooFit.LineColor(rt.kGreen), rt.RooFit.LineStyle(8),rt.RooFit.Normalization(N_Vpj/Ntot),rt.RooFit.ProjectionRange(MRRange),rt.RooFit.Range(MRRange),rt.RooFit.NormRange(MRRange)) for MRRange in MRRanges]

        #plot data again
        data_cut.plotOn(frameMR,rt.RooFit.Name("Data"))
        self.workspace.Print("V")


        if (self.workspace.function("Ntot_Signal")!=None):
            MRRanges = ['HighMR']
            for MRRange in MRRanges:
                N_Signal = self.workspace.function("Ntot_Signal").getVal()*(self.getFitPDF("eBinPDF_Signal").createIntegral(vars,vars,0,MRRange).getVal()/self.getFitPDF("eBinPDF_Signal").createIntegral(vars,vars).getVal())
                print "N_Signal", N_Signal
                self.workspace.pdf('eBinPDF_Signal').plotOn(frameMR, rt.RooFit.Name("Signal"), rt.RooFit.DrawOption("L"),rt.RooFit.LineColor(rt.kBlack),rt.RooFit.FillColor(rt.kBlack),rt.RooFit.FillStyle(3001),rt.RooFit.ProjectionRange(MRRange),rt.RooFit.Range(MRRange),rt.RooFit.NormRange(MRRange),rt.RooFit.Normalization(N_Signal,rt.RooAbsReal.NumEvent))
        else:
            N_Signal = 0
        

        if varname=="Rsq":
            frameMR.SetMinimum(0.5)
            frameMR.SetMaximum(5000)
        elif varname=="nBtag":
            frameMR.SetMinimum(5)
            frameMR.SetMaximum(50000)
        elif varname=="MR":
            frameMR.SetMinimum(0.5)
            frameMR.SetMaximum(5000)
        d = rt.TCanvas("d","d",600,500)
        rt.gPad.SetLogy()
        frameMR.Draw()

        
        # legend
        if showTTj2b and showTTj1b and showVpj and (N_Signal>0):
            leg = rt.TLegend(0.7,0.5,0.93,0.93)
        elif showTTj2b and showTTj1b and showVpj:
            leg = rt.TLegend(0.7,0.55,0.93,0.93)
        elif showTTj2b and showTTj1b:
            leg = rt.TLegend(0.7,0.65,0.93,0.93)
        else:
            leg = rt.TLegend(0.7,0.72,0.93,0.93)
        leg.SetFillColor(0)
        leg.SetTextFont(42)
        leg.SetLineColor(0)

        leg.AddEntry("Data","Data","pe")
        leg.AddEntry("Total","Total Bkgd","lf")
        if showVpj:
            leg.AddEntry("TTj1b","1 b-tag, t#bar{t}+jets","l")
            leg.AddEntry("Vpj","1 b-tag, V+jets","l")
        else:
            if showTTj1b:
                leg.AddEntry("TTj1b","1 b-tag","l")
        if showTTj2b:
            leg.AddEntry("TTj2b","#geq 2 b-tag","l")
        if (N_Signal>0):
            leg.AddEntry("Signal","Signal","l")
        leg.Draw()

        
        pt = rt.TPaveText(0.25,0.75,0.6,0.87,"ndc")
        pt.SetBorderSize(0)
        pt.SetFillColor(0)
        pt.SetFillStyle(0)
        pt.SetLineColor(0)
        pt.SetTextAlign(21)
        pt.SetTextFont(42)
        pt.SetTextSize(0.045)
        Preliminary = "Preliminary"
        Lumi = 19.3
        Energy = 8
        text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
        text = pt.AddText("Razor %s Box #int L = %3.1f fb^{-1}" %(self.name,Lumi))
        pt.Draw()
    
        fitregionLabel = '_'.join(self.fitregion.split(","))
        if self.fitregion == "LowRsq,LowMR,HighMR": fitregionLabel = "FULL"
        elif self.fitregion == "LowRsq,LowMR": fitregionLabel = "Sideband"
        elif self.fitregion == "HighMR": fitregionLabel = "HighMR"
        elif self.fitregion == "LowRsq1b,LowMR1b,HighMR1b": fitregionLabel = "1b"
        elif self.fitregion == "LowRsq2b,LowMR2b,HighMR2b": fitregionLabel = "2b"
        elif self.fitregion == "LowRsq3b,LowMR3b,HighMR3b": fitregionLabel = "3b"
        
        d.Print("razor_rooplot_%s_%s_%s_%s_%s.pdf"%(varname,fitregionLabel,plotlabel,data.GetName(),self.name))
        
        return [frameMR]

    def plot1DHistoAllComponents(self, inputFile, varname, nbins = 25, ranges=None, data=None, fitmodel=None):
        Preliminary = "Preliminary"
        #Preliminary = "Simulation"
        Energy = 8.0
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
            
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        print ''
        print 'rangeCut', rangeCut
        print ''

        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
        data = data.reduce(self.cut)
        data = data.reduce(rangeCut)
            
        # save original event yields
        if self.workspace.var("Ntot_TTj2b") != None:
            N_TTj2b = self.workspace.var("Ntot_TTj2b").getVal()
        if self.workspace.var("Ntot_TTj1b") != None:
            N_TTj1b = self.workspace.var("Ntot_TTj1b").getVal()
        if self.workspace.var("Ntot_Vpj") != None:
            N_Vpj = self.workspace.var("Ntot_Vpj").getVal()
        if self.workspace.function("Ntot_Signal") != None:
            N_Signal = self.workspace.function("Ntot_Signal").getVal()
        else: N_Signal = 0.
        print 'N_signal', N_Signal

            
        # Generate a sample of signal
        effCutSignal = 1
        self.workspace.var("Ntot_Vpj").setVal(0.)
        self.workspace.var("Ntot_TTj1b").setVal(0.)
        self.workspace.var("Ntot_TTj2b").setVal(0.)
        if N_Signal>1:
            toyDataSignal = self.workspace.pdf(self.signalmodel).generate(self.workspace.set('variables'), int(50*(N_Signal)))
            beforeCutSignal = float(toyDataSignal.sumEntries())
            toyDataSignal = toyDataSignal.reduce(rangeCut)
            afterCutSignal = float(toyDataSignal.sumEntries())
            effCutSignal = afterCutSignal / beforeCutSignal
            print effCutSignal
            
        # Generate a sample of Vpj
        effCutVpj = 1
        self.workspace.var("Ntot_Vpj").setVal(N_Vpj)
        self.workspace.var("Ntot_TTj1b").setVal(0.)
        self.workspace.var("Ntot_TTj2b").setVal(0.)
        if N_Vpj>1:
            toyDataVpj = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(50*(N_Vpj)))
            beforeCutVpj = float(toyDataVpj.sumEntries())
            toyDataVpj = toyDataVpj.reduce(rangeCut)
            afterCutVpj = float(toyDataVpj.sumEntries())
            effCutVpj = afterCutVpj / beforeCutVpj

        # Generate a sample of TTj1b
        effCutTTj1b = 1
        self.workspace.var("Ntot_Vpj").setVal(0.)
        self.workspace.var("Ntot_TTj1b").setVal(N_TTj1b)
        self.workspace.var("Ntot_TTj2b").setVal(0.)
        if N_TTj1b>1 :
            toyDataTTj1b = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(50*(N_TTj1b)))
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
        if N_TTj2b>1 :
            toyDataTTj2b = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(50*(N_TTj2b)))
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

        xmin = min([self.workspace.var(varname).getMin(r) for r in ranges])
        xmax = max([self.workspace.var(varname).getMax(r) for r in ranges])

        # variable binning for plots
        bins = getBinning(self.name, varname, self.btag)
        
        nbins =len(bins)-1
        xedge = array("d",bins)
        print "Binning in variable %s is "%varname
        print bins
        
        # define 1D histograms
        histoData = self.setPoissonErrors(rt.TH1D("histoData", "histoData",len(bins)-1, xedge))
        histoToy = self.setPoissonErrors(rt.TH1D("histoToy", "histoToy",len(bins)-1, xedge))
        histoToySignal = self.setPoissonErrors(rt.TH1D("histoToySignal", "histoToySignal",len(bins)-1, xedge))
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

        def SetErrors(histo):
            for i in range(1, histo.GetNbinsX()+1):
                histo.SetBinError(i,max(rt.TMath.Sqrt(histo.GetBinContent(i)), 1))

        # project the data on the histograms
        data.fillHistogram(histoData,rt.RooArgList(self.workspace.var(varname)))
        data.Print('V')
        
        if N_Signal>1: toyDataSignal.fillHistogram(histoToySignal,rt.RooArgList(self.workspace.var(varname)))
        if N_Vpj>1: toyDataVpj.fillHistogram(histoToyVpj,rt.RooArgList(self.workspace.var(varname)))
        if N_TTj1b>1 :toyDataTTj1b.fillHistogram(histoToyTTj1b,rt.RooArgList(self.workspace.var(varname)))
        if N_TTj2b>1 : toyDataTTj2b.fillHistogram(histoToyTTj2b,rt.RooArgList(self.workspace.var(varname)))
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
        
        histoToySignal.Scale(0.02)
        histoToyTTj2b.Scale(0.02)
        histoToyVpj.Scale(0.02)
        histoToyTTj1b.Scale(0.02)
        SetErrors(histoToyTTj2b)
        SetErrors(histoToyVpj)
        SetErrors(histoToyTTj1b)
        setName(histoToyTTj2b,varname)
        setName(histoToyVpj,varname)
        setName(histoToyTTj1b,varname)
        histoToyTTj1b.SetLineColor(rt.kViolet)
        histoToyTTj1b.SetLineWidth(2)
        histoToyTTj2b.SetLineColor(rt.kRed)
        histoToyTTj2b.SetLineWidth(2)
        histoToyVpj.SetLineColor(rt.kGreen)
        histoToyVpj.SetLineWidth(2)

        histoToy.Scale(0.02)
        SetErrors(histoToy)
        setName(histoData,varname)
        setName(histoToy,varname)
        setName(histoToySignal,varname)
        histoData.SetMarkerStyle(20)
        histoData.SetLineWidth(2)
        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        rt.gStyle.SetOptStat(0000)
        rt.gStyle.SetOptTitle(0)

        showTTj2b = (N_TTj2b>0)
        showVpj = (N_Vpj>0)
        showTTj1b = (N_TTj1b>0)
        showSignal = (N_Signal>0)


        # legend
        if showTTj2b and showTTj1b and showVpj and showSignal:
            leg = rt.TLegend(0.7,0.45,0.93,0.93)
        elif showTTj2b and showTTj1b and showVpj:
            leg = rt.TLegend(0.7,0.55,0.93,0.93)
        elif showTTj2b and showTTj1b and showSignal:
            leg = rt.TLegend(0.7,0.55,0.93,0.93)
        elif showTTj2b and showTTj1b:
            leg = rt.TLegend(0.7,0.65,0.93,0.93)
        else:
            leg = rt.TLegend(0.7,0.72,0.93,0.93)
        leg.SetFillColor(0)
        leg.SetTextFont(42)
        leg.SetLineColor(0)


        leg.AddEntry(histoData,"Data","lep")
        leg.AddEntry(histoToy,"Total Bkgd","lf")
        if showVpj:
            leg.AddEntry(histoToyTTj1b,"1 b-tag, t#bar{t}+jets","f")
            leg.AddEntry(histoToyVpj,"1 b-tag, V+jets","f")
        else:
            if showTTj1b:
                leg.AddEntry(histoToyTTj1b,"1 b-tag","l")
        if showTTj2b:
            leg.AddEntry(histoToyTTj2b,"#geq 2 b-tag","l")
        if showSignal:
            leg.AddEntry(histoToySignal,"Signal","lf")
        
        leg.Draw()



        btagLabel = "#geq 1 b-tag"
        if ranges==["3b"]:
            btagLabel = "#geq 3 b-tag"
        if ranges==["2b","3b"]:
            btagLabel = "#geq 2 b-tag"
        if ranges==["2b"]:
            btagLabel = "2 b-tag"
        

        # plot labels
        #pt = rt.TPaveText(0.4,0.8,0.5,0.93,"ndc")
        pt = rt.TPaveText(0.25,0.67,0.7,0.93,"ndc")
        pt.SetBorderSize(0)
        pt.SetTextSize(0.05)
        pt.SetFillColor(0)
        pt.SetFillStyle(0)
        pt.SetLineColor(0)
        pt.SetTextAlign(21)
        pt.SetTextFont(42)
        pt.SetTextSize(0.062)
        text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
        Lumi = 19.3
        text = pt.AddText("Razor %s Box #int L = %3.1f fb^{-1}" %(self.name,Lumi))
    
        c = rt.TCanvas("c","c",500,400)
        pad1 = rt.TPad("pad1","pad1",0,0.25,1,1)
        pad2 = rt.TPad("pad2","pad2",0,0,1,0.25)
        
        pad1.Range(-213.4588,-0.3237935,4222.803,5.412602);
        pad2.Range(-213.4588,-2.206896,4222.803,3.241379);

        pad1.SetLeftMargin(0.15)
        pad2.SetLeftMargin(0.15)
        pad1.SetRightMargin(0.05)
        pad2.SetRightMargin(0.05)
        pad1.SetTopMargin(0.05)
        pad2.SetTopMargin(0.)
        pad1.SetBottomMargin(0.)
        pad2.SetBottomMargin(0.47)
    
        #pad1.SetBottomMargin(0)
        pad1.Draw()
        pad1.cd()
        rt.gPad.SetLogy()
        c.SetName('DataMC_%s_%s_ALLCOMPONENTS' % (varname,'_'.join(ranges)) )
        
        histoToy.SetMinimum(0.5)
        histoToy.GetYaxis().SetTitleSize(0.08)
        histoToy.GetYaxis().SetTitle("Events")
        histoToy.GetXaxis().SetTitle("")
        histoToy.GetXaxis().SetLabelOffset(0.16)
        histoToy.GetXaxis().SetLabelSize(0.06)
        histoToy.GetYaxis().SetLabelSize(0.06)
        histoToy.GetXaxis().SetTitleSize(0.06)
        histoToy.GetYaxis().SetTitleSize(0.08)
        histoToy.GetXaxis().SetTitleOffset(1)
        #if varname == "MR": histoToy.SetMaximum(histoToy.GetMaximum()*2.)
        #elif varname == "Rsq": histoToy.SetMaximum(histoToy.GetMaximum()*2.)
        #elif varname == "nBtag": histoToy.SetMaximum(histoToy.GetMaximum()*5.)
        if varname == "MR":
            histoToy.SetMaximum(5.e4)
            histoToy.SetMinimum(0.5)
        elif varname == "Rsq":
            histoToy.SetMaximum(5.e4)
            histoToy.SetMinimum(0.5)
        elif varname == "nBtag":
            histoToy.SetMaximum(5.e4)
            histoToy.SetMinimum(0.5)
        histoData.GetXaxis().SetRange(1,FindLastBin(histoData))
        histoToy.GetXaxis().SetRange(1,FindLastBin(histoData))
        #if histoToy.GetBinContent(histoToy.GetNbinsX())>=15.: histoToy.SetMinimum(15.)
        #if histoToy.GetBinContent(histoToy.GetNbinsX())>=50.: histoToy.SetMinimum(50.)
            
            
        
        histoToy.SetFillColor(rt.kBlue-10)
        histoToy.SetFillStyle(1001)
        histoData.SetLineColor(rt.kBlack)
        histoData.Draw("pe")
        histoToy.DrawCopy('e2')
        histoData.Draw("pesame")
        leg.Draw("same")
        pt.Draw("same")

        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        
        if self.workspace.var("Ntot_Vpj").getVal():
            histoToyVpjAdd = histoToyVpj.Clone("histoToyVpjAdd")
            histoToyVpjAdd.DrawCopy("histsame")
            c1 = rt.gROOT.GetColor(rt.kGreen-4)
            c1.SetAlpha(1.0)
            histoToyVpjAdd.SetFillStyle(0)
            if varname=="nBtag":
                histoToyVpjAdd.Add(histoToyTTj1b)
                histoToyVpjAdd.SetFillStyle(1001)
                c1.SetAlpha(1.0)
                histoToyVpj.SetFillColor(rt.kGreen-4)
                histoToyVpjAdd.SetFillColor(rt.kGreen-4)
            histoToyVpjAdd.DrawCopy('histsame')
        if self.workspace.var("Ntot_TTj1b").getVal():
            histoToyTTj1b.DrawCopy("histsame")
            c2 = rt.gROOT.GetColor(rt.kViolet-4)
            c2.SetAlpha(1.0)
            histoToyTTj1b.SetFillStyle(0)
            if varname=="nBtag":
                histoToyTTj1b.SetFillStyle(1001)
                c2.SetAlpha(1.0)
                histoToyTTj1b.SetFillColor(rt.kViolet-4)
            histoToyTTj1b.DrawCopy('histsame')
        if self.workspace.var("Ntot_TTj2b").getVal():
            histoToyTTj2b.DrawCopy('histsame')
            c3 = rt.gROOT.GetColor(rt.kRed-4)
            c3.SetAlpha(1.0)
            histoToyTTj2b.SetFillStyle(0)
            if varname=="nBtag":
                histoToyTTj2b.SetFillStyle(1001)
                c3.SetAlpha(1.0)
                histoToyTTj2b.SetFillColor(rt.kRed-4)
            histoToyTTj2b.DrawCopy('histsame')
        # total
        if varname=="nBtag":
            histoToy.SetFillColor(rt.kBlue-10)
            histoToy.SetFillStyle(1001)
            histoToy.DrawCopy('e2same')
        histoToyCOPY = histoToy.Clone("histoToyCOPY")
        histoToyCOPY.SetFillStyle(0)
        histoToyCOPY.Draw('histsame')
        histoData.Draw("pesame")

        if N_Signal>0:
            c4 = rt.gROOT.GetColor(rt.kGray+2)
            c4.SetAlpha(1.0)
            histoToySignal.SetLineColor(rt.kBlack)
            histoToySignal.SetFillColor(rt.kGray+2)
            histoToySignal.SetLineStyle(2)
            histoToySignal.SetFillStyle(3005)
            histoToySignal.SetLineWidth(2)
            histoToySignal.Draw("histfsame")
            

        c.Update()
    
        c.cd()
        
        pad2.Draw()
        pad2.cd()
        rt.gPad.SetLogy(0)
        histoData.Sumw2()
        histoToyCOPY.Sumw2()
        hMRDataDivide = histoData.Clone(histoData.GetName()+"Divide")
        hMRDataDivide.Sumw2()

        hMRTOTclone = histoToyCOPY.Clone(histoToyCOPY.GetName()+"Divide") 
        hMRTOTcopyclone = histoToy.Clone(histoToyCOPY.GetName()+"Divide") 
        hMRTOTcopyclone.GetYaxis().SetLabelSize(0.18)
        hMRTOTcopyclone.SetTitle("")
        hMRTOTcopyclone.SetMaximum(3.5)
        hMRTOTcopyclone.SetMinimum(0.)
        if varname=="BTAG": hMRTOTcopyclone.GetXaxis().SetLabelSize(0.32)
        else: hMRTOTcopyclone.GetXaxis().SetLabelSize(0.22)
        hMRTOTcopyclone.GetXaxis().SetTitleSize(0.22)
 
        for i in range(1, histoData.GetNbinsX()+1):
            tmpVal = hMRTOTcopyclone.GetBinContent(i)
            if tmpVal != -0.:
                hMRDataDivide.SetBinContent(i, hMRDataDivide.GetBinContent(i)/tmpVal)
                hMRDataDivide.SetBinError(i, hMRDataDivide.GetBinError(i)/tmpVal)
                hMRTOTcopyclone.SetBinContent(i, hMRTOTcopyclone.GetBinContent(i)/tmpVal)
                hMRTOTcopyclone.SetBinError(i, hMRTOTcopyclone.GetBinError(i)/tmpVal)
                hMRTOTclone.SetBinContent(i, hMRTOTclone.GetBinContent(i)/tmpVal)
                hMRTOTclone.SetBinError(i, hMRTOTclone.GetBinError(i)/tmpVal)

        hMRTOTcopyclone.GetXaxis().SetTitleOffset(0.97)
        hMRTOTcopyclone.GetXaxis().SetLabelOffset(0.02)
        if varname == "MR":
            hMRTOTcopyclone.GetXaxis().SetTitle("M_{R} [GeV]")
        if varname == "RSQ":
            hMRTOTcopyclone.GetXaxis().SetTitle("R^{2}")
        if varname == "BTAG":
            hMRTOTcopyclone.GetXaxis().SetTitle("n_{b-tag}")

        hMRTOTcopyclone.GetYaxis().SetNdivisions(504,rt.kTRUE)
        hMRTOTcopyclone.GetYaxis().SetTitleOffset(0.2)
        hMRTOTcopyclone.GetYaxis().SetTitleSize(0.22)
        hMRTOTcopyclone.GetYaxis().SetTitle("Data/Bkgd")
        hMRTOTcopyclone.GetXaxis().SetTicks("+")
        hMRTOTcopyclone.GetXaxis().SetTickLength(0.07)
        hMRTOTcopyclone.SetMarkerColor(rt.kBlue-10)
        hMRTOTcopyclone.Draw("e2")
        hMRDataDivide.Draw('pesame')
        hMRTOTcopyclone.Draw("axissame")

        pad2.Update()
        pad1.cd()
        pad1.Update()
        pad1.Draw()
        c.cd()
        
        histToReturn = [histoToy, histoData, c]
        histToReturn.append(histoToyVpj)
        histToReturn.append(histoToyTTj1b)
        histToReturn.append(histoToyTTj2b)
        histToReturn.append(histoToySignal)

        
        fitLabel = '_'.join(self.fitregion.split(","))
        if self.fitregion == "LowRsq,LowMR,HighMR": fitLabel = "FULL"
        elif self.fitregion == "LowRsq,LowMR": fitLabel = "Sideband"
        elif self.fitregion == "HighMR": fitLabel = "HighMR"
        elif self.fitregion == "LowRsq1b,LowMR1b,HighMR1b": fitLabel = "1b"
        elif self.fitregion == "LowRsq2b,LowMR2b,HighMR2b": fitLabel = "2b"
        elif self.fitregion == "LowRsq3b,LowMR3b,HighMR3b": fitLabel = "3b"
            
        c.Print("razor_canvas_%s_%s_%s_%s.pdf"%(self.name,fitLabel,'_'.join(ranges), varname))
        
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"c\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad1\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad2\");")
        return histToReturn

    def plot2DHisto(self, inputFile, ranges=None, data=None, fitmodel=None):
        #Preliminary = "Preliminary"
        Preliminary = "Simulation"
        Energy = 8.0
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
            
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        print ''
        print 'rangeCut', rangeCut
        print ''

        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
        data = data.reduce(self.cut)
        data = data.reduce(rangeCut)
            
        # save original event yields
        if self.workspace.var("Ntot_TTj2b") != None:
            N_TTj2b = self.workspace.var("Ntot_TTj2b").getVal()
        if self.workspace.var("Ntot_TTj1b") != None:
            N_TTj1b = self.workspace.var("Ntot_TTj1b").getVal()
        if self.workspace.var("Ntot_Vpj") != None:
            N_Vpj = self.workspace.var("Ntot_Vpj").getVal()
        if self.workspace.function("Ntot_Signal") != None:
            N_Signal = self.workspace.function("Ntot_Signal").getVal()
        else: N_Signal = 0.

            
        # Generate a sample of signal
        effCutSignal = 1
        self.workspace.var("Ntot_Vpj").setVal(0.)
        self.workspace.var("Ntot_TTj1b").setVal(0.)
        self.workspace.var("Ntot_TTj2b").setVal(0.)
        if N_Signal>1:
            toyDataSignal = self.workspace.pdf(self.signalmodel).generate(self.workspace.set('variables'), int(1000*(N_Signal)))
            beforeCutSignal = float(toyDataSignal.sumEntries())
            toyDataSignal = toyDataSignal.reduce(rangeCut)
            afterCutSignal = float(toyDataSignal.sumEntries())
            effCutSignal = afterCutSignal / beforeCutSignal

        # Generate a sample of Vpj
        effCutVpj = 1
        self.workspace.var("Ntot_Vpj").setVal(N_Vpj)
        self.workspace.var("Ntot_TTj1b").setVal(0.)
        self.workspace.var("Ntot_TTj2b").setVal(0.)
        if N_Vpj>1:
            toyDataVpj = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(1000*(N_Vpj)))
            beforeCutVpj = float(toyDataVpj.sumEntries())
            toyDataVpj = toyDataVpj.reduce(rangeCut)
            afterCutVpj = float(toyDataVpj.sumEntries())
            effCutVpj = afterCutVpj / beforeCutVpj

        # Generate a sample of TTj1b
        effCutTTj1b = 1
        self.workspace.var("Ntot_Vpj").setVal(0.)
        self.workspace.var("Ntot_TTj1b").setVal(N_TTj1b)
        self.workspace.var("Ntot_TTj2b").setVal(0.)
        if N_TTj1b>1 :
            toyDataTTj1b = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(1000*(N_TTj1b)))
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
        if N_TTj2b>1 :
            toyDataTTj2b = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(1000*(N_TTj2b)))
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

        # variable binning for plots
        MRbins = getBinning(self.name, "MR", self.btag)
        Rsqbins = getBinning(self.name, "Rsq", self.btag)
        x = array('d',MRbins)
        y = array('d',Rsqbins)
        
        
        # define 2D histograms
        histoData = self.setPoissonErrors(rt.TH2D("histo2DData","", len(MRbins)-1, x, len(Rsqbins)-1, y))
        histoDataFineBin = self.setPoissonErrors(rt.TH2D("histo2DDataFine","", 100, x[0],x[-1],100,y[0],y[-1]))
        histoToy = self.setPoissonErrors(rt.TH2D("histo2DToy","", len(MRbins)-1, x, len(Rsqbins)-1, y))
        histoToyFineBin = self.setPoissonErrors(rt.TH2D("histo2DToyFine","", 100, x[0],x[-1],100,y[0],y[-1]))
        histoToySignal = self.setPoissonErrors(rt.TH2D("histo2DToySignal","", len(MRbins)-1, x, len(Rsqbins)-1, y))
        histoToySignalFineBin = self.setPoissonErrors(rt.TH2D("histo2DToySignalFine","", 100, x[0],x[-1],100,y[0],y[-1]))
        histoToyVpj = self.setPoissonErrors(rt.TH2D("histo2DToyVpj","", len(MRbins)-1, x, len(Rsqbins)-1, y))
        histoToyVpjFineBin = self.setPoissonErrors(rt.TH2D("histo2DToyVpjFine","", 100, x[0],x[-1],100,y[0],y[-1]))
        histoToyTTj1b = self.setPoissonErrors(rt.TH2D("histo2DToyTTj1b","", len(MRbins)-1, x, len(Rsqbins)-1, y))
        histoToyTTj1bFineBin = self.setPoissonErrors(rt.TH2D("histo2DToyTTj1bFine","", 100, x[0],x[-1],100,y[0],y[-1]))
        histoToyTTj2b = self.setPoissonErrors(rt.TH2D("histo2DToyTTj2b","", len(MRbins)-1, x, len(Rsqbins)-1, y))
        histoToyTTj2bFineBin = self.setPoissonErrors(rt.TH2D("histo2DToyTTj2bFine","", 100, x[0],x[-1],100,y[0],y[-1]))

        def setName(h):
            h.SetName('%s_%s_%s_ALLCOMPONENTS' % (h.GetName(),'MRRsq','_'.join(ranges)) )
            # axis labels
            h.GetXaxis().SetTitleSize(0.065)
            h.GetYaxis().SetTitleSize(0.065)
            h.GetXaxis().SetLabelSize(0.065)
            h.GetYaxis().SetLabelSize(0.065)
            #h.GetXaxis().SetTitleOffset(0.90)
            #h.GetYaxis().SetTitleOffset(0.93)
            h.GetXaxis().SetMoreLogLabels()
            h.GetXaxis().SetNoExponent()
        
            # x axis
            h.GetYaxis().SetTitle("R^{2}")
            h.GetXaxis().SetTitle("M_{R}[GeV]")

                

        def SetErrors(histo):
            for i in range(1,histo.GetNbinsX()+1):
                for j in range(1,histo.GetNbinsY()+1):
                    histo.SetBinError(i,j, rt.TMath.Sqrt(histo.GetBinContent(i, j)))

        # project the data on the histograms
        MRRsqList = rt.RooArgList()
        MRRsqList.add(self.workspace.var('MR'))
        MRRsqList.add(self.workspace.var('Rsq'))

        data.reduce(rangeCut)
        data.fillHistogram(histoData,MRRsqList)
        data.fillHistogram(histoDataFineBin,MRRsqList)
        
        if N_Signal>1:
            toyDataSignal.fillHistogram(histoToySignal,MRRsqList)
            toyDataSignal.fillHistogram(histoToySignalFineBin,MRRsqList)
        if N_Vpj>1:
            toyDataVpj.fillHistogram(histoToyVpj,MRRsqList)
            toyDataVpj.fillHistogram(histoToyVpjFineBin,MRRsqList)
        if N_TTj1b>1 :
            toyDataTTj1b.fillHistogram(histoToyTTj1b,MRRsqList)
            toyDataTTj1b.fillHistogram(histoToyTTj1bFineBin,MRRsqList)
        if N_TTj2b>1 :
            toyDataTTj2b.fillHistogram(histoToyTTj2b,MRRsqList)
            toyDataTTj2b.fillHistogram(histoToyTTj2bFineBin,MRRsqList)
        # make the total
        if self.workspace.var("Ntot_Vpj") != None and N_Vpj>1:
            histoToy.Add(histoToyVpj, +1)
            histoToyFineBin.Add(histoToyVpjFineBin, +1)
        if self.workspace.var("Ntot_TTj1b") != None and N_TTj1b>1 :
            histoToy.Add(histoToyTTj1b, +1)
            histoToyFineBin.Add(histoToyTTj1bFineBin, +1)
        if self.workspace.var("Ntot_TTj2b") != None and N_TTj2b>1:
            histoToy.Add(histoToyTTj2b, +1)
            histoToyFineBin.Add(histoToyTTj2bFineBin, +1)
            
        # We shouldn't scale to the data, we should scale to our prediction
        print "DATA NORM %f"%histoData.Integral()
        print "FIT NORM  %f"%(N_TTj2b*effCutTTj2b+N_Vpj*effCutVpj+N_TTj1b*effCutTTj1b)
        scaleFactor = (N_TTj2b*effCutTTj2b+N_Vpj*effCutVpj+N_TTj1b*effCutTTj1b)/histoToy.Integral()
        print "scaleFactor = %f"%scaleFactor
        
        histoToySignal.Scale(0.001)
        histoToySignalFineBin.Scale(0.001)
        histoToyTTj2b.Scale(0.001)
        histoToyVpj.Scale(0.001)
        histoToyTTj1b.Scale(0.001)
        SetErrors(histoToyTTj2b)
        SetErrors(histoToyVpj)
        SetErrors(histoToyTTj1b)
        setName(histoToyTTj2b)
        setName(histoToyVpj)
        setName(histoToyTTj1b)

        histoToy.Scale(0.001)
        histoToyFineBin.Scale(0.001)
        SetErrors(histoToy)
        setName(histoData)
        setName(histoDataFineBin)
        setName(histoToy)
        setName(histoToyFineBin)
        setName(histoToySignal)
        setName(histoToySignalFineBin)

        rt.gStyle.SetOptStat(0000)
        rt.gStyle.SetOptTitle(0)

        showTTj2b = (N_TTj2b>0)
        showVpj = (N_Vpj>0)
        showTTj1b = (N_TTj1b>0)
        showSignal = (N_Signal>0)
    
        c = rt.TCanvas("c","c",600,400)
        c.SetLeftMargin(0.15)
        c.SetBottomMargin(0.15)
        c.SetLogy()
        c.SetLogx()
        c.Update()


        ncontours = 999
        stops = [ 0.00, 0.1, 0.25, 0.65, 1.00 ]
        #stops = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
        red =   [ 1.0,   0.95,  0.95,  0.65,   0.15 ]
        green = [ 1.0,  0.85, 0.7, 0.5,  0.3 ]
        blue =  [ 0.95, 0.6 , 0.3,  0.45, 0.65 ]
        s = array('d', stops)
        r = array('d', red)
        g = array('d', green)
        b = array('d', blue)
        npoints = len(s)
        #rt.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
        rt.gStyle.SetNumberContours(ncontours)

        rt.gStyle.cd()
    
        Red = array('d',  [0.00, 0.70, 0.90, 1.00, 1.00, 1.00, 1.00])
        Green = array('d',[0.00, 0.70, 0.90, 1.00, 0.90, 0.70, 0.00])
        Blue = array('d', [1.00, 1.00, 1.00, 1.00, 0.90, 0.70, 0.00])
        Length =array('d',[0.00, 0.10, 0.25, 0.333, 0.5, 0.85, 1.00]) # colors get darker faster at 4sigma
        #rt.TColor.CreateGradientColorTable(7,Length,Red,Green,Blue,999)
        rt.gStyle.SetNumberContours(999)
    
        histoDivide = histoData.Clone("histoDivide")
        histoDivide.SetMaximum(3.)
        histoDivide.Divide(histoToy)
        #histoDivide.Draw("colz")
        #histoToySignal.Draw("colz")
        #histoToySignalFineBin.Draw("colz")
        histoDataFineBin.Draw("colz")
        #histoToyFineBin.SetMaximum(50)
        #histoToyFineBin.Draw("colz")



        pt = rt.TPaveText(0.5,0.65,0.93,0.88,"ndc")
        pt.SetBorderSize(0)
        pt.SetTextSize(0.04)
        pt.SetFillColor(0)
        pt.SetFillStyle(0)
        pt.SetLineColor(0)
        pt.SetTextAlign(21)
        pt.SetTextFont(42)
        text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
        Lumi = 19.3
        text = pt.AddText("Razor %s Box #int L = %3.1f fb^{-1}" %(self.name,Lumi))
        text = pt.AddText("pp#rightarrowt#bar{t}+jets,  #sigma = 234 pb")
        #text = pt.AddText("Razor pdf")
        #text = pt.AddText("")
        text = pt.AddText("pp#rightarrow#tilde{g}#tilde{g}, #tilde{g}#rightarrow b#bar{b}#tilde{#chi}^{0}, #sigma = 0.01 pb")
        pt.Draw("same")
        
        tlatexList = []
        for iBinX in range(1,histoToy.GetNbinsX()+1):
            for iBinY in range(1,histoToy.GetNbinsY()+1):
                binCont = histoToy.GetBinContent(iBinX,iBinY)
                datCont = histoData.GetBinContent(iBinX,iBinY)
                if binCont>=1. or datCont>=1.:
                    xBin  = histoToy.GetXaxis().GetBinLowEdge(iBinX) + .25*histoToy.GetXaxis().GetBinWidth(iBinX)
                    yBin = histoToy.GetYaxis().GetBinLowEdge(iBinY) + .3*histoToy.GetYaxis().GetBinWidth(iBinY)
                    tlatex = rt.TLatex(xBin,yBin,"#frac{%.0f}{%.0f}"%(datCont,binCont))
                    tlatex.SetTextSize(0.05)
                    tlatex.SetTextFont(42)
                    tlatexList.append(tlatex)

        #for tlatex in tlatexList: tlatex.Draw()



        # the real log labels
        tlabels = []
        if self.name=="Jet1b":
            tlabels.append(rt.TLatex(330,0.485, "0.5"))
            tlabels.append(rt.TLatex(330,0.39, "0.4"))
            tlabels.append(rt.TLatex(330,0.295, "0.3"))
        elif self.name=="MultiJet" or self.name=="TauTauJet" or self.name=="Jet2b":
            tlabels.append(rt.TLatex(330,0.76, "0.8"))
            tlabels.append(rt.TLatex(330,0.47, "0.5"))
            tlabels.append(rt.TLatex(330,0.285, "0.3"))
        else:
            tlabels.append(rt.TLatex(240,0.75, "0.8"))
            tlabels.append(rt.TLatex(240,0.375, "0.4"))
            tlabels.append(rt.TLatex(240,0.19, "0.2"))
        
        for tlabel in tlabels:
            tlabel.SetTextSize(0.065)
            tlabel.SetTextFont(42)
            tlabel.Draw()
        
        # the gray lines
        xLines = []
        yLines = []

        lastX = len(x)-1
        lastY = len(y)-1

        for i in range(1,lastY):
            xLines.append(rt.TLine(x[0], y[i], x[lastX], y[i]))
            xLines[i-1].SetLineStyle(2);
            xLines[i-1].SetLineColor(rt.kGray);
        
        for i in range(1,lastX):
            yLines.append(rt.TLine(x[i], y[0], x[i], y[lastY]))
            yLines[i-1].SetLineStyle(2)
            yLines[i-1].SetLineColor(rt.kGray)


        fitLabel = '_'.join(self.fitregion.split(","))
        if self.fitregion == "LowRsq,LowMR,HighMR": fitLabel = "FULL"
        elif self.fitregion == "LowRsq,LowMR": fitLabel = "Sideband"
        elif self.fitregion == "HighMR": fitLabel = "HighMR"
        elif self.fitregion == "LowRsq1b,LowMR1b,HighMR1b": fitLabel = "1b"
        elif self.fitregion == "LowRsq2b,LowMR2b,HighMR2b": fitLabel = "2b"
        elif self.fitregion == "LowRsq3b,LowMR3b,HighMR3b": fitLabel = "3b"


        col1 = rt.gROOT.GetColor(rt.kGray+1)
        #col1.SetAlpha(0.3)

        
        fGreenGraphs = []
        if fitLabel=="Sideband":
            predColor = rt.kGreen
            yLines.append(rt.TLine(x[2], y[1], x[2], y[-1]))
            yLines[-1].SetLineStyle(2)
            yLines[-1].SetLineWidth(2)
            yLines[-1].SetLineColor(predColor)
            xLines.append(rt.TLine(x[2], y[1], x[-1], y[1]))
            xLines[-1].SetLineStyle(2)
            xLines[-1].SetLineWidth(2)
            xLines[-1].SetLineColor(predColor)
            col2 = rt.gROOT.GetColor(predColor-10)
            col2.SetAlpha(0.5)
        
            fGreen = rt.TGraph(5)
            fGreen.SetPoint(0,x[0],y[1])
            fGreen.SetPoint(1,x[2],y[1])
            fGreen.SetPoint(2,x[2],y[-1])
            fGreen.SetPoint(3,x[0],y[-1])
            fGreen.SetPoint(4,x[0],y[1])
            fGreen.SetFillColor(predColor-10)
            fGreenGraphs.append(fGreen)

            fGreen = rt.TGraph(5)
            fGreen.SetPoint(0,x[1],y[0])
            fGreen.SetPoint(1,x[-1],y[0])
            fGreen.SetPoint(2,x[-1],y[1])
            fGreen.SetPoint(3,x[1],y[1])
            fGreen.SetPoint(4,x[1],y[0])
            fGreen.SetFillColor(predColor-10)
            fGreenGraphs.append(fGreen)
            
        elif fitLabel=="LowRsq":
            predColor = rt.kMagenta
            xLines.append(rt.TLine(x[1], y[1], x[-1], y[1]))
            xLines[-1].SetLineStyle(2)
            xLines[-1].SetLineWidth(2)
            xLines[-1].SetLineColor(predColor)
            col2 = rt.gROOT.GetColor(predColor-10)
            col2.SetAlpha(0.5)
            
            fGreen = rt.TGraph(5)
            fGreen.SetPoint(0,x[1],y[0])
            fGreen.SetPoint(1,x[-1],y[0])
            fGreen.SetPoint(2,x[-1],y[1])
            fGreen.SetPoint(3,x[1],y[1])
            fGreen.SetPoint(4,x[1],y[0])
            fGreen.SetFillColor(predColor-10)
            fGreenGraphs.append(fGreen)
        elif fitLabel=="LowMR":
            predColor = rt.kCyan
            yLines.append(rt.TLine(x[2], y[1], x[2], y[-1]))
            yLines[-1].SetLineStyle(2)
            yLines[-1].SetLineWidth(2)
            yLines[-1].SetLineColor(predColor)
            col2 = rt.gROOT.GetColor(predColor-10)
            col2.SetAlpha(0.5)
            
            fGreen = rt.TGraph(5)
            fGreen.SetPoint(0,x[0],y[1])
            fGreen.SetPoint(1,x[2],y[1])
            fGreen.SetPoint(2,x[2],y[-1])
            fGreen.SetPoint(3,x[0],y[-1])
            fGreen.SetPoint(4,x[0],y[1])
            fGreen.SetFillColor(predColor-10)
            fGreenGraphs.append(fGreen)
        elif fitLabel=="FULL":
            predColor = rt.kBlue
            col2 = rt.gROOT.GetColor(predColor-10)
            col2.SetAlpha(0.5)
            
            fGreen = rt.TGraph(5)
            fGreen.SetPoint(0,x[0],y[1])
            fGreen.SetPoint(1,x[1],y[1])
            fGreen.SetPoint(2,x[1],y[-1])
            fGreen.SetPoint(3,x[0],y[-1])
            fGreen.SetPoint(4,x[0],y[1])
            fGreen.SetFillColor(predColor-10)
            fGreenGraphs.append(fGreen)
            
            fGreen = rt.TGraph(5)
            fGreen.SetPoint(0,x[1],y[0])
            fGreen.SetPoint(1,x[-1],y[0])
            fGreen.SetPoint(2,x[-1],y[-1])
            fGreen.SetPoint(3,x[1],y[-1])
            fGreen.SetPoint(4,x[1],y[0])
            fGreen.SetFillColor(predColor-10)
            fGreenGraphs.append(fGreen)

        fGrayGraphs = []
        fGray = rt.TGraph(5)

        if fitLabel=="LowMR":
            fGray.SetPoint(0,x[0],y[0])
            fGray.SetPoint(1,x[0],y[1])
            fGray.SetPoint(2,x[-1],y[1])
            fGray.SetPoint(3,x[-1],y[0])
            fGray.SetPoint(4,x[0],y[0])
        else:
            fGray.SetPoint(0,x[0],y[0])
            fGray.SetPoint(1,x[0],y[1])
            fGray.SetPoint(2,x[1],y[1])
            fGray.SetPoint(3,x[1],y[0])
            fGray.SetPoint(4,x[0],y[0])
        fGray.SetFillColor(rt.kGray+1)
        fGrayGraphs.append(fGray)
            
        for i in range(0,len(xLines)): xLines[i].Draw()
        for i in range(0,len(yLines)): yLines[i].Draw()

        for fGreen in fGreenGraphs: fGreen.Draw("F")
        for fGray in fGrayGraphs: fGray.Draw("F")
            
        c.Update()
    
        c.cd()
        
        histToReturn = [histoToy, histoData, c]
        #histToReturn.append(histoToyVpj)
        #histToReturn.append(histoToyTTj1b)
        #histToReturn.append(histoToyTTj2b)
        #histToReturn.append(histoToySignal)

            
        c.Print("razor_canvas_%s_%s_%s_%s.pdf"%(self.name,fitLabel,'_'.join(ranges), 'MR_Rsq'))
        
        return histToReturn

    def plot1DSlice(self, inputFile, varname, ranges=None, data=None, fitmodel=None):
        #Preliminary = "Preliminary"
        Preliminary = "Simulation"
        Energy = 8.0
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
            
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        print ''
        print 'rangeCut', rangeCut
        print ''

        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
        data = data.reduce(self.cut)
        data = data.reduce(rangeCut)

        N_TTj2b = 0
        N_TTj1b = 0
        N_Vpj = 0
        N_Signal = 0
        # save original event yields
        if self.workspace.var("Ntot_TTj2b") != None:
            N_TTj2b = self.workspace.var("Ntot_TTj2b").getVal()
        if self.workspace.var("Ntot_TTj1b") != None:
            N_TTj1b = self.workspace.var("Ntot_TTj1b").getVal()
        if self.workspace.var("Ntot_Vpj") != None:
            N_Vpj = self.workspace.var("Ntot_Vpj").getVal()
        if self.workspace.function("Ntot_Signal") != None:
            N_Signal = self.workspace.function("Ntot_Signal").getVal()

        toyData = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(100*(N_Signal+N_TTj1b+N_TTj2b+N_Vpj)))
        toyData = toyData.reduce(rangeCut)

        # variable binning for plots
        
        if varname=="MR":
            othervarname="Rsq"
            MRbins = getBinning(self.name, "MR", self.btag)
            Rsqbins = getBinning(self.name, "Rsq", self.btag)
            myRsqbins = [0.25,0.30,0.41,0.52,1.5]
            rsqLabels = ["0.25#leqR^{2}<0.3","0.3#leqR^{2}<0.41","0.41#leqR^{2}<0.52","R^{2}#geq0.52"]
        else:
            othervarname="MR"
            MRbins = getBinning(self.name, "Rsq", self.btag)
            Rsqbins = getBinning(self.name, "MR", self.btag)
            myRsqbins = [400,550,900,4000]
            rsqLabels = ["400#leqM_{R}<550","550#leqM_{R}<900","M_{R}#geq900"]

        x = array('d',MRbins)
        y = array('d',Rsqbins)



        histoData = [self.setPoissonErrors(rt.TH1D("histoData%i"%i, "histoData%i"%i,len(MRbins)-1, x)) for i in range(0,len(myRsqbins)-1)]
        histoToy =  [self.setPoissonErrors(rt.TH1D("histoToy%i"%i, "histoToy%i"%i,len(MRbins)-1, x)) for i in range(0,len(myRsqbins)-1)]


        # project the data on the histograms
        MRList = rt.RooArgList()
        MRList.add(self.workspace.var('%s'%varname))


        for i in range(0,len(myRsqbins)-1):
            data.fillHistogram(histoData[i],MRList,"%s>=%f&&%s<%f"%(othervarname,myRsqbins[i],othervarname,myRsqbins[i+1]))
            toyData.fillHistogram(histoToy[i],MRList,"%s>=%f&&%s<%f"%(othervarname,myRsqbins[i],othervarname,myRsqbins[i+1]))
        
        [h.Scale(0.01) for h in histoToy]

        
        def setName(h):
            h.SetName('%s_%s_%s1DSlice' % (h.GetName(),'_'.join(ranges),varname) )
            # axis labels
            h.GetXaxis().SetTitleSize(0.065)
            h.GetYaxis().SetTitleSize(0.065)
            h.GetXaxis().SetLabelSize(0.065)
            h.GetYaxis().SetLabelSize(0.065)
            #h.GetXaxis().SetTitleOffset(0.90)
            #h.GetYaxis().SetTitleOffset(0.93)
            h.GetXaxis().SetMoreLogLabels()
            h.GetXaxis().SetNoExponent()
        
            # x axis
            if varname=="MR":
                h.GetXaxis().SetTitle("M_{R} [GeV]")
            elif varname=="Rsq":
                h.GetXaxis().SetTitle("R_{2}")
            h.GetYaxis().SetTitle("Events")
            
        [setName(h) for h in histoToy]
        [setName(h) for h in histoData]
        
        def SetErrors(histo):
            for i in range(1, histo.GetNbinsX()+1):
                histo.SetBinError(i,max(rt.TMath.Sqrt(histo.GetBinContent(i)), 1))


        [SetErrors(h) for h in histoToy]
        [SetErrors(h) for h in histoData]
    
        fitLabel = '_'.join(self.fitregion.split(","))
        if self.fitregion == "LowRsq,LowMR,HighMR": fitLabel = "FULL"
        elif self.fitregion == "LowRsq,LowMR": fitLabel = "Sideband"


        for i in range(0, len(myRsqbins)-1):
            c = rt.TCanvas("c","c",500,400)
            pad1 = rt.TPad("pad1","pad1",0,0.25,1,1)
            pad2 = rt.TPad("pad2","pad2",0,0,1,0.25)

            pad1.Range(-213.4588,-0.3237935,4222.803,5.412602);
            pad2.Range(-213.4588,-2.206896,4222.803,3.241379);

            pad1.SetLeftMargin(0.15)
            pad2.SetLeftMargin(0.15)
            pad1.SetRightMargin(0.05)
            pad2.SetRightMargin(0.05)
            pad1.SetTopMargin(0.05)
            pad2.SetTopMargin(0.)
            pad1.SetBottomMargin(0.)
            pad2.SetBottomMargin(0.47)
            pad1.Draw()
            pad1.cd()
            rt.gPad.SetLogy()
            
            #histoData[i].GetXaxis().SetRange(1,FindLastBin(histoData[i]))
            if fitLabel=="Sideband" and ((varname=="MR" and i==0) or varname=="Rsq"):
                if varname=="MR":
                    histoData[i].GetXaxis().SetRange(2,histoData[i].GetNbinsX()-1)
                else:
                    histoData[i].GetXaxis().SetRange(2,histoData[i].GetNbinsX())
            elif fitLabel=="Sideband" and varname=="MR" and i>0:
                histoData[i].GetXaxis().SetRange(3,histoData[i].GetNbinsX()-1)
            elif fitLabel=="LowMR" and varname=="MR":
                 histoData[i].GetXaxis().SetRange(3,histoData[i].GetNbinsX()-1)
            elif fitLabel=="LowMR" and varname=="Rsq" and i==0:
                if varname=="MR":
                    histoData[i].GetXaxis().SetRange(2,histoData[i].GetNbinsX()-1)
                else:
                    histoData[i].GetXaxis().SetRange(2,histoData[i].GetNbinsX())
                    
            histoData[i].SetMarkerStyle(20)
            
            histoToy[i].SetFillStyle(1001)
            histoData[i].SetLineColor(rt.kBlack)
            
            predColor = rt.kBlue
            
            if fitLabel=="FULL":
                predColor = rt.kBlue
            elif fitLabel=="Sideband":
                predColor = rt.kGreen
            elif fitLabel=="LowRsq":
                predColor = rt.kMagenta
            elif fitLabel=="LowMR":
                predColor = rt.kCyan
                
            histoToy[i].SetFillColor(predColor-10)
            histoToy[i].SetLineColor(predColor)
            histoToy[i].SetLineWidth(2)
            histoData[i].SetLineWidth(2)
            
            histoData[i].Draw("pe")

            
            histoData[i].SetMaximum(1.e3)
            histoData[i].SetMinimum(.05)
            if varname=="Rsq":
                histoData[i].SetMinimum(.5)
            if varname=="MR":
                histoData[i].SetMaximum(1.e4)
            
            if varname=="MR":
                tline = rt.TLine(550, 0.05, 550, 1.e3)
            elif varname=="Rsq":
                tline = rt.TLine(0.3, 0.5, 0.3, 1.e3)

                    
            if varname=="MR":
                histoToy[i].GetXaxis().SetNdivisions(509)
                histoData[i].GetXaxis().SetNdivisions(509)
                
            histoToy[i].DrawCopy("e2same")
            histoData[i].Draw("pesame")

            # total
            histoToyCOPY = histoToy[i].Clone("histoToyCOPY")
            histoToyCOPY.SetFillStyle(0)
            histoToyCOPY.Draw('histsame')
            histoData[i].Draw("pesame")



            leg = rt.TLegend(0.7,0.72,0.93,0.93)
            leg.SetFillColor(0)
            leg.SetTextFont(42)
            leg.SetLineColor(0)

            leg.AddEntry(histoData[i],"Data","lep")
            leg.AddEntry(histoToy[i],"Total Bkgd","lf")
            
            rt.gStyle.SetOptStat(0000)
            rt.gStyle.SetOptTitle(0)
            
            pt = rt.TPaveText(0.25,0.5,0.7,0.93,"ndc")
            pt.SetBorderSize(0)
            pt.SetTextSize(0.05)
            pt.SetFillColor(0)
            pt.SetFillStyle(0)
            pt.SetLineColor(0)
            pt.SetTextAlign(21)
            pt.SetTextFont(42)
            pt.SetTextSize(0.062)
            text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
            Lumi = 19.3
            text = pt.AddText("Razor %s Box #int L = %3.1f fb^{-1}" %(self.name,Lumi))
            pt.AddText("")
            text = pt.AddText("                            %s " %(rsqLabels[i]))
            if varname=="MR" and i==0:
                text = pt.AddText("                                                        Very Low R^{2} Fit")
            elif varname=="Rsq" and i==0:
                text = pt.AddText("                                                        Low M_{R} Fit")
            elif varname=="MR" and i>0:
                text = pt.AddText("                                                        High M_{R} Extrapolation")
            elif varname=="Rsq" and i>0:
                text = pt.AddText("                                                        High M_{R} Extrapolation")
    

            leg.Draw()
            pt.Draw()
            
            tline.SetLineColor(predColor)
            tline.SetLineWidth(2)
            tline.SetLineStyle(2)
            if (((fitLabel=="Sideband" and i!=0) or fitLabel=="LowMR") and varname=="MR"):
                tline.Draw()
            elif (((fitLabel=="Sideband" and i!=0) or fitLabel=="LowRsq") and varname=="Rsq"):
                tline.Draw()
 
            
            c.Update()
    
            c.cd()
        
            pad2.Draw()
            pad2.cd()
            rt.gPad.SetLogy(0)
            histoData[i].Sumw2()
            histoToyCOPY.Sumw2()
            hMRDataDivide = histoData[i].Clone(histoData[i].GetName()+"Divide")
            hMRDataDivide.Sumw2()

            hMRTOTclone = histoToyCOPY.Clone(histoToyCOPY.GetName()+"Divide") 
            hMRTOTcopyclone = histoToy[i].Clone(histoToyCOPY.GetName()+"Divide") 
            hMRTOTcopyclone.GetYaxis().SetLabelSize(0.18)
            hMRTOTcopyclone.SetTitle("")
            hMRTOTcopyclone.SetMaximum(3.5)
            hMRTOTcopyclone.SetMinimum(0.)
            hMRTOTcopyclone.GetXaxis().SetLabelSize(0.22)
            hMRTOTcopyclone.GetXaxis().SetTitleSize(0.22)
 
            for j in range(1, histoData[i].GetNbinsX()+1):
                tmpVal = hMRTOTcopyclone.GetBinContent(j)
                if tmpVal != -0.:
                    hMRDataDivide.SetBinContent(j, hMRDataDivide.GetBinContent(j)/tmpVal)
                    hMRDataDivide.SetBinError(j, hMRDataDivide.GetBinError(j)/tmpVal)
                    hMRTOTcopyclone.SetBinContent(j, hMRTOTcopyclone.GetBinContent(j)/tmpVal)
                    hMRTOTcopyclone.SetBinError(j, hMRTOTcopyclone.GetBinError(j)/tmpVal)
                    hMRTOTclone.SetBinContent(j, hMRTOTclone.GetBinContent(j)/tmpVal)
                    hMRTOTclone.SetBinError(j, hMRTOTclone.GetBinError(j)/tmpVal)

                
            hMRTOTcopyclone.GetXaxis().SetTitleOffset(0.97)
            hMRTOTcopyclone.GetXaxis().SetLabelOffset(0.02)
            
            if varname=="MR":
                hMRTOTcopyclone.GetXaxis().SetTitle("M_{R} [GeV]")
            elif varname=="Rsq":
                hMRTOTcopyclone.GetXaxis().SetTitle("R^{2}")

            hMRTOTcopyclone.GetYaxis().SetNdivisions(504,rt.kTRUE)
            if varname=="MR":
                hMRTOTcopyclone.GetXaxis().SetNdivisions(509,rt.kTRUE)
            hMRTOTcopyclone.GetYaxis().SetTitleOffset(0.2)
            hMRTOTcopyclone.GetYaxis().SetTitleSize(0.22)
            hMRTOTcopyclone.GetYaxis().SetTitle("Data/Bkgd")
            hMRTOTcopyclone.GetXaxis().SetTicks("+")
            hMRTOTcopyclone.GetXaxis().SetTickLength(0.07)
            hMRTOTcopyclone.SetMarkerColor(predColor-10)
            #hMRTOTcopyclone.GetXaxis().SetRange(1,FindLastBin(histoData[i]))
            if fitLabel=="Sideband" and ((varname=="MR" and i==0) or varname=="Rsq"):
                if varname=="MR":
                    hMRTOTcopyclone.GetXaxis().SetRange(2,histoData[i].GetNbinsX()-1)
                else:
                    hMRTOTcopyclone.GetXaxis().SetRange(2,histoData[i].GetNbinsX())
            elif fitLabel=="Sideband" and varname=="MR" and i>0:
                hMRTOTcopyclone.GetXaxis().SetRange(3,histoData[i].GetNbinsX()-1)
            elif fitLabel=="LowMR" and varname=="MR":
                 hMRTOTcopyclone.GetXaxis().SetRange(3,histoData[i].GetNbinsX()-1)
            elif fitLabel=="LowMR" and varname=="Rsq" and i==0:
                if varname=="MR":
                    hMRTOTcopyclone.GetXaxis().SetRange(2,histoData[i].GetNbinsX()-1)
                else:
                    hMRTOTcopyclone.GetXaxis().SetRange(2,histoData[i].GetNbinsX())
            hMRTOTcopyclone.Draw("e2")
            hMRDataDivide.Draw('psame')
            hMRTOTcopyclone.Draw("axissame")

            pad2.Update()
            pad1.cd()
            pad1.Update()
            pad1.Draw()
            c.cd()
            
            
            c.Print("razor_canvas_%s_%s_%s_%sSlice_%i.pdf"%(self.name,fitLabel,'_'.join(ranges), varname,i))

        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"c\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad1\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad2\");")

        histoToy.extend(histoData)
        return [h for h in histoToy]


        


    def plot1DSideband(self, inputFile, varname, ranges=None, data=None, fitmodel=None):
        #Preliminary = "Preliminary"
        Preliminary = "Simulation"
        Energy = 8.0
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
            
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        print ''
        print 'rangeCut', rangeCut
        print ''

        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
        data = data.reduce(self.cut)
        data = data.reduce(rangeCut)

        N_TTj2b = 0
        N_TTj1b = 0
        N_Vpj = 0
        N_Signal = 0
        # save original event yields
        if self.workspace.var("Ntot_TTj2b") != None:
            N_TTj2b = self.workspace.var("Ntot_TTj2b").getVal()
        if self.workspace.var("Ntot_TTj1b") != None:
            N_TTj1b = self.workspace.var("Ntot_TTj1b").getVal()
        if self.workspace.var("Ntot_Vpj") != None:
            N_Vpj = self.workspace.var("Ntot_Vpj").getVal()
        if self.workspace.function("Ntot_Signal") != None:
            N_Signal = self.workspace.function("Ntot_Signal").getVal()

        toyData = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(100*(N_Signal+N_TTj1b+N_TTj2b+N_Vpj)))
        toyData = toyData.reduce(rangeCut)

        # variable binning for plots
        
        if varname=="MR":
            othervarname="Rsq"
            MRbins = [400,425,450,475,500,525,550]
            Rsqbins = getBinning(self.name, "Rsq", self.btag)
            myRsqbins = [0.3,1.5]
            rsqLabels = ["0.3#leqR^{2}<1.5"]
        
        if varname=="Rsq":
            othervarname="MR"
            MRbins = [0.25,0.26,0.27,0.28,0.29,0.3]
            Rsqbins = getBinning(self.name, "MR", self.btag)
            myRsqbins = [450,4000]
            rsqLabels = ["450#leqM_{R}<4000"]
            
        x = array('d',MRbins)
        y = array('d',Rsqbins)



        histoData = [self.setPoissonErrors(rt.TH1D("histoData%i"%i, "histoData%i"%i,len(MRbins)-1, x)) for i in range(0,len(myRsqbins)-1)]
        histoToy =  [self.setPoissonErrors(rt.TH1D("histoToy%i"%i, "histoToy%i"%i,len(MRbins)-1, x)) for i in range(0,len(myRsqbins)-1)]


        # project the data on the histograms
        MRList = rt.RooArgList()
        MRList.add(self.workspace.var('%s'%varname))


        for i in range(0,len(myRsqbins)-1):
            data.fillHistogram(histoData[i],MRList,"%s>=%f&&%s<%f"%(othervarname,myRsqbins[i],othervarname,myRsqbins[i+1]))
            toyData.fillHistogram(histoToy[i],MRList,"%s>=%f&&%s<%f"%(othervarname,myRsqbins[i],othervarname,myRsqbins[i+1]))
        
        [h.Scale(0.01) for h in histoToy]

        
        def setName(h):
            h.SetName('%s_%s_%s1DSlice' % (h.GetName(),'_'.join(ranges),varname) )
            # axis labels
            h.GetXaxis().SetTitleSize(0.065)
            h.GetYaxis().SetTitleSize(0.065)
            h.GetXaxis().SetLabelSize(0.065)
            h.GetYaxis().SetLabelSize(0.065)
            #h.GetXaxis().SetTitleOffset(0.90)
            #h.GetYaxis().SetTitleOffset(0.93)
            h.GetXaxis().SetMoreLogLabels()
            h.GetXaxis().SetNoExponent()
        
            # x axis
            if varname=="MR":
                h.GetXaxis().SetTitle("M_{R} [GeV]")
            elif varname=="Rsq":
                h.GetXaxis().SetTitle("R_{2}")
            h.GetYaxis().SetTitle("Events")
            
        [setName(h) for h in histoToy]
        [setName(h) for h in histoData]
        
        def SetErrors(histo):
            for i in range(1, histo.GetNbinsX()+1):
                histo.SetBinError(i,max(rt.TMath.Sqrt(histo.GetBinContent(i)), 1))


        [SetErrors(h) for h in histoToy]
        [SetErrors(h) for h in histoData]
    
        fitLabel = '_'.join(self.fitregion.split(","))
        if self.fitregion == "LowRsq,LowMR,HighMR": fitLabel = "FULL"
        elif self.fitregion == "LowRsq,LowMR": fitLabel = "Sideband"


        for i in range(0, len(myRsqbins)-1):
            c = rt.TCanvas("c","c",500,400)
            pad1 = rt.TPad("pad1","pad1",0,0.25,1,1)
            pad2 = rt.TPad("pad2","pad2",0,0,1,0.25)

            pad1.Range(-213.4588,-0.3237935,4222.803,5.412602);
            pad2.Range(-213.4588,-2.206896,4222.803,3.241379);

            pad1.SetLeftMargin(0.15)
            pad2.SetLeftMargin(0.15)
            pad1.SetRightMargin(0.05)
            pad2.SetRightMargin(0.05)
            pad1.SetTopMargin(0.05)
            pad2.SetTopMargin(0.)
            pad1.SetBottomMargin(0.)
            pad2.SetBottomMargin(0.47)
            pad1.Draw()
            pad1.cd()
            rt.gPad.SetLogy()
            
            histoData[i].SetMarkerStyle(20)
            
            histoToy[i].SetFillStyle(1001)
            histoData[i].SetLineColor(rt.kBlack)
            
            predColor = rt.kBlue
            
            if fitLabel=="FULL":
                predColor = rt.kBlue
            elif fitLabel=="Sideband":
                predColor = rt.kGreen
            elif fitLabel=="LowRsq":
                predColor = rt.kMagenta
            elif fitLabel=="LowMR":
                predColor = rt.kCyan
                
            histoToy[i].SetFillColor(predColor-10)
            histoToy[i].SetLineColor(predColor)
            histoToy[i].SetLineWidth(2)
            histoData[i].SetLineWidth(2)
            
            
            if varname=="MR":
                tline = rt.TLine(550, 50., 550, 1.e3)
                histoToy[i].GetXaxis().SetNdivisions(206,False)
                histoData[i].GetXaxis().SetNdivisions(206,False)
                histoData[i].SetMaximum(5.e2)
                histoData[i].SetMinimum(40)
            if varname=="Rsq":
                tline = rt.TLine(0.3, 50., 0.3, 1.e3)
                histoToy[i].GetXaxis().SetNdivisions(205,False)
                histoData[i].GetXaxis().SetNdivisions(205,False)
                histoData[i].SetMaximum(2.e2)
                histoData[i].SetMinimum(70)

            
            histoData[i].Draw("pe")
            histoToy[i].DrawCopy("e2same")
            histoData[i].Draw("pesame")

            # total
            histoToyCOPY = histoToy[i].Clone("histoToyCOPY")
            histoToyCOPY.SetFillStyle(0)
            histoToyCOPY.Draw('histsame')
            histoData[i].Draw("pesame")



            leg = rt.TLegend(0.7,0.72,0.93,0.93)
            leg.SetFillColor(0)
            leg.SetTextFont(42)
            leg.SetLineColor(0)

            leg.AddEntry(histoData[i],"Data","lep")
            leg.AddEntry(histoToy[i],"Total Bkgd","lf")
            
            rt.gStyle.SetOptStat(0000)
            rt.gStyle.SetOptTitle(0)
            
            pt = rt.TPaveText(0.25,0.5,0.7,0.93,"ndc")
            pt.SetBorderSize(0)
            pt.SetTextSize(0.05)
            pt.SetFillColor(0)
            pt.SetFillStyle(0)
            pt.SetLineColor(0)
            pt.SetTextAlign(21)
            pt.SetTextFont(42)
            pt.SetTextSize(0.062)
            text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
            Lumi = 19.3
            text = pt.AddText("Razor %s Box #int L = %3.1f fb^{-1}" %(self.name,Lumi))
            pt.AddText("")
            text = pt.AddText("                            %s " %(rsqLabels[i]))
            if fitLabel in ["LowMR","Sideband"] and varname=="MR" and i==0:
                text = pt.AddText("                                                        Low M_{R} Fit")
            if fitLabel in ["LowRsq","Sideband"] and varname=="Rsq" and i==0:
                text = pt.AddText("                                                        Very Low R^{2} Fit")
    

            leg.Draw()
            pt.Draw()
            
            tline.SetLineColor(predColor)
            tline.SetLineWidth(2)
            tline.SetLineStyle(2)
            
            c.Update()
    
            c.cd()
        
            pad2.Draw()
            pad2.cd()
            rt.gPad.SetLogy(0)
            histoData[i].Sumw2()
            histoToyCOPY.Sumw2()
            hMRDataDivide = histoData[i].Clone(histoData[i].GetName()+"Divide")
            hMRDataDivide.Sumw2()

            hMRTOTclone = histoToyCOPY.Clone(histoToyCOPY.GetName()+"Divide") 
            hMRTOTcopyclone = histoToy[i].Clone(histoToyCOPY.GetName()+"Divide") 
            hMRTOTcopyclone.GetYaxis().SetLabelSize(0.18)
            hMRTOTcopyclone.SetTitle("")
            hMRTOTcopyclone.SetMaximum(3.5)
            hMRTOTcopyclone.SetMinimum(0.)
            hMRTOTcopyclone.GetXaxis().SetLabelSize(0.22)
            hMRTOTcopyclone.GetXaxis().SetTitleSize(0.22)
 
            for j in range(1, histoData[i].GetNbinsX()+1):
                tmpVal = hMRTOTcopyclone.GetBinContent(j)
                if tmpVal != -0.:
                    hMRDataDivide.SetBinContent(j, hMRDataDivide.GetBinContent(j)/tmpVal)
                    hMRDataDivide.SetBinError(j, hMRDataDivide.GetBinError(j)/tmpVal)
                    hMRTOTcopyclone.SetBinContent(j, hMRTOTcopyclone.GetBinContent(j)/tmpVal)
                    hMRTOTcopyclone.SetBinError(j, hMRTOTcopyclone.GetBinError(j)/tmpVal)
                    hMRTOTclone.SetBinContent(j, hMRTOTclone.GetBinContent(j)/tmpVal)
                    hMRTOTclone.SetBinError(j, hMRTOTclone.GetBinError(j)/tmpVal)

                
            hMRTOTcopyclone.GetXaxis().SetTitleOffset(0.97)
            hMRTOTcopyclone.GetXaxis().SetLabelOffset(0.02)
            
            if varname=="MR":
                hMRTOTcopyclone.GetXaxis().SetTitle("M_{R} [GeV]")
            elif varname=="Rsq":
                hMRTOTcopyclone.GetXaxis().SetTitle("R^{2}")

            hMRTOTcopyclone.GetYaxis().SetNdivisions(504,rt.kTRUE)
            if varname=="MR":
                hMRTOTcopyclone.GetXaxis().SetNdivisions(206,False)
            elif varname=="Rsq":
                hMRTOTcopyclone.GetXaxis().SetNdivisions(205,False)
            hMRTOTcopyclone.GetYaxis().SetTitleOffset(0.2)
            hMRTOTcopyclone.GetYaxis().SetTitleSize(0.22)
            hMRTOTcopyclone.GetYaxis().SetTitle("Data/Bkgd")
            hMRTOTcopyclone.GetXaxis().SetTicks("+")
            hMRTOTcopyclone.GetXaxis().SetTickLength(0.07)
            hMRTOTcopyclone.SetMarkerColor(predColor-10)
            hMRTOTcopyclone.Draw("e2")
            hMRDataDivide.Draw('psame')
            hMRTOTcopyclone.Draw("axissame")

            pad2.Update()
            pad1.cd()
            pad1.Update()
            pad1.Draw()
            c.cd()
            
            
            c.Print("razor_canvas_%s_%s_%s_%sSideband_%i.pdf"%(self.name,fitLabel,'_'.join(ranges), varname,i))

        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"c\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad1\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad2\");")

        histoToy.extend(histoData)
        return [h for h in histoToy]


        
