from RazorCombinedFit.Framework import Box
import math
import RootTools
import ROOT as rt

class RazorBox(Box.Box):
    
    def __init__(self, name, variables):
        super(RazorBox,self).__init__(name, variables)
        
        #self.zeros = {'TTj':[],'Wln':['Mu','MuMu','EleEle','MuEle'],'Zll':['MuEle','Mu','Ele','Had'],'Znn':['Ele','MuMu','EleEle','MuEle'],'QCD':['Ele', 'Mu', 'MuEle','MuMu','EleEle','Had']}
        # this is what we did in 2011
        # self.zeros = {'TTj':[],'Wln':['Mu','MuMu','EleEle','MuEle'],'Zll':['MuEle','Mu','Ele','Had'],'Znn':['Ele','MuMu','EleEle','MuEle']}
        # now we switch off the redundant Znn component in the Had box
        self.zeros = {'TTj':[],'Wln':['Mu','MuMu','EleEle','MuEle'],'Zll':['MuEle','Mu','Ele','Had'],'Znn':['Ele','MuMu','EleEle','MuEle']}

        self.cut = 'MR >= 0.0'

    def addTailPdf(self, flavour):
        
        label = '_%s' % flavour

        #define a flavour specific yield
        #self.yieldToCrossSection(flavour)
        # define the two components
        self.workspace.factory("RooRazor2DTail::PDF1st"+label+"(MR,Rsq,MR01st"+label+",R01st"+label+",b1st"+label+")")
        self.workspace.factory("RooRazor2DTail::PDF2nd"+label+"(MR,Rsq,MR02nd"+label+",R02nd"+label+",b2nd"+label+")")
        #define the two yields
        self.workspace.factory("expr::N_1st"+label+"('@0*(1-@1)',Ntot"+label+",f2"+label+")")
        self.workspace.factory("expr::N_2nd"+label+"('@0*@1',Ntot"+label+",f2"+label+")")

        #associate the yields to the pdfs through extended PDFs
        self.workspace.factory("RooExtendPdf::ePDF1st"+label+"(PDF1st"+label+", N_1st"+label+")")
        self.workspace.factory("RooExtendPdf::ePDF2nd"+label+"(PDF2nd"+label+", N_2nd"+label+")")
        #float the efficiency with a penalty term if a sigma is provided

    def addTailPdfVjets(self, flavour, flavourW):
        
        label = '_%s' % flavour
        labelW = '_%s' % flavourW

        #define a flavour specific yield
        #self.yieldToCrossSection(flavour)
        # define the two components
        self.workspace.factory("RooRazor2DTail::PDF1st"+label+"(MR,Rsq,MR01st"+label+",R01st"+label+",b1st"+label+")")
        self.workspace.factory("RooRazor2DTail::PDF2nd"+label+"(MR,Rsq,MR02nd"+labelW+",R02nd"+labelW+",b2nd"+labelW+")")
        #define the two yields
        self.workspace.factory("expr::N_1st"+label+"('@0*(1-@1)*@2',Ntot"+label+",f2"+label+")")
        self.workspace.factory("expr::N_2nd"+label+"('@0*@1*@2',Ntot"+label+",f2"+label+")")
        #associate the yields to the pdfs through extended PDFs
        self.workspace.factory("RooExtendPdf::ePDF1st"+label+"(PDF1st"+label+", N_1st"+label+")")
        self.workspace.factory("RooExtendPdf::ePDF2nd"+label+"(PDF2nd"+label+", N_2nd"+label+")")
        #float the efficiency with a penalty term if a sigma is provided

    def switchOff(self, species) :
        self.workspace.var("Ntot_"+species).setVal(0.)
        self.workspace.var("Ntot_"+species).setConstant(rt.kTRUE)
        self.workspace.var("f2_"+species).setConstant(rt.kTRUE)

    #add penalty terms and float
    def float1stComponentWithPenalty(self,flavour, alsoB):
        self.fixParsPenalty("MR01st_%s" % flavour)
        self.fixParsPenalty("R01st_%s" % flavour)
        self.fixPars("MR01st_%s_s" % flavour)
        self.fixPars("R01st_%s_s" % flavour)
        if alsoB == True:
            self.fixParsPenalty("b1st_%s" % flavour)
            self.fixPars("b1st_%s_s" % flavour)
        else:
            self.fixParsExact("b1st_%s" % flavour, False)

    def float2ndComponentWithPenalty(self,flavour, alsoB):
        self.fixParsPenalty("R02nd_%s" % flavour)
        self.fixPars("R02nd_%s_s" % flavour)
        self.fixParsPenalty("MR02nd_%s" % flavour)
        self.fixPars("MR02nd_%s_s" % flavour)
        if alsoB == True:
            self.fixParsPenalty("b2nd_%s" % flavour)
            self.fixPars("b2nd_%s_s" % flavour)
        else:
            self.fixParsExact("b2nd_%s" % flavour, False)
            
    def float1stComponent(self,flavour):
        self.fixParsExact("MR01st_%s" % flavour, False)
        self.fixParsExact("R01st_%s" % flavour, False)
        self.fixParsExact("b1st_%s" % flavour, False)
    def float2ndComponent(self,flavour):
        self.fixParsExact("MR02nd_%s" % flavour, False)
        self.fixParsExact("R02nd_%s" % flavour, False)
        self.fixParsExact("b2nd_%s" % flavour, False)        
    def floatFractionWithPenalty(self,flavour):
        self.fixParsPenalty("f2_%s" % flavour)
        self.fixPars("f2_%s_s" % flavour)
    def floatFraction(self,flavour):
        self.fixParsExact("f2_%s" % flavour, False)
    def floatYield(self,flavour):
        self.fixParsExact("Ntot_%s" % flavour, False)
    def fix2ndComponent(self,flavour):
        self.fixParsExact("MR02nd_%s" % flavour, True)
        self.fixParsExact("R02nd_%s" % flavour, True)
        self.fixParsExact("b2nd_%s" % flavour, True)        
    def fix1stComponent(self,flavour):
        self.fixParsExact("MR01st_%s" % flavour, True)
        self.fixParsExact("R01st_%s" % flavour, True)
        self.fixParsExact("b1st_%s" % flavour, True)        
    
    def addDataSet(self, inputFile):
        #create the dataset
        data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
        #import the dataset to the workspace
        self.importToWS(data)

    def define(self, inputFile):
        
        #define the ranges
        mR  = self.workspace.var("MR")
        Rsq = self.workspace.var("Rsq")
        
        # add the different components:
        # - W+jets
        # - Zll+jets
        # - Znn+jets
        # - ttbar+jets
        self.addTailPdf("Wln")    
        self.addTailPdf("Zll")
        self.addTailPdf("Znn")
        #self.addTailPdfVjets("Zll", "Wln")
        #self.addTailPdfVjets("Znn", "Wln")
        self.addTailPdf("TTj")
        #self.addTailPdf("QCD")

        # build the total PDF
        myPDFlist = rt.RooArgList(self.workspace.pdf("ePDF1st_Wln"),self.workspace.pdf("ePDF2nd_Wln"),
                                  self.workspace.pdf("ePDF1st_Zll"),self.workspace.pdf("ePDF2nd_Zll"),
                                                                    self.workspace.pdf("ePDF1st_Znn"),self.workspace.pdf("ePDF2nd_Znn"),
                                                                    self.workspace.pdf("ePDF1st_TTj"),self.workspace.pdf("ePDF2nd_TTj"))
        #myPDFlist.add(self.workspace.pdf("ePDF1st_QCD"))
        #myPDFlist.add(self.workspace.pdf("ePDF2nd_QCD"))    
        model = rt.RooAddPdf(self.fitmodel, self.fitmodel, myPDFlist)        
        
        # import the model in the workspace.
        self.importToWS(model)
        #print the workspace
        self.workspace.Print()

        ##### THIS IS A SIMPLIFIED FIT
        # fix all pdf parameters to the initial value
        self.fixPars("Zll")
        self.fixPars("Znn")
        self.fixPars("Wln")
        self.fixPars("TTj")
        #self.fixPars("QCD")

        def floatSomething(z):
            """Switch on or off whatever you want here"""
            # the "effective" first component in the Had box
            if z == "Wln" and self.name == "Had": self.float1stComponent(z)
            else : self.float1stComponentWithPenalty(z, True)
            # the b2nd parameter is floated in the 1Lep boxes (no penalty term)
            if self.name == "Mu" or self.name == "Ele" and z == "TTj": self.float2ndComponentWithPenalty(z, False)
            #if self.name == "Mu" and z == "TTj": self.float2ndComponentWithPenalty(z, False)
            elif self.name != "Had": self.float2ndComponentWithPenalty(z, True)
            self.floatYield(z)
            if self.name != "Had": self.floatFraction(z)

        # switch off not-needed components (box by box)
        fixed = []
        for z in self.zeros:
            if self.name in self.zeros[z]:
                #floatSomething(z)
                self.fixPars(z)
                self.switchOff(z)
            else:
                if not z in fixed:
                    floatSomething(z)
                    fixed.append(z)

        if self.name == "Had": self.workspace.var("b1st_TTj").setConstant(rt.kFALSE)

        #remove redundant second components
        if self.name == "Ele":
            self.fix2ndComponent("Wln")
            self.workspace.var("f2_Wln").setVal(0.)
            self.workspace.var("f2_Wln").setConstant(rt.kTRUE)
        if self.name == "Mu":
            self.fix2ndComponent("Znn")
            self.workspace.var("f2_Znn").setVal(0.)
            self.workspace.var("f2_Znn").setConstant(rt.kTRUE)
        #if self.name == "EleEle":
        if self.name == "MuMu" or self.name == "EleEle":
            self.fix2ndComponent("Zll")
            self.workspace.var("f2_Zll").setVal(0.)
            self.workspace.var("f2_Zll").setConstant(rt.kTRUE)

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
        store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=['fR1', 'fR2','fR3','fR4']), dir=box)
        store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=['FULL']), dir=box)
        #[store.store(s, dir=box) for s in self.plot1DHisto(inputFile, "MR", ranges=['fR1', 'fR2','fR3','fR4'])]
        #[store.store(s, dir=box) for s in self.plot1DHisto(inputFile, "Rsq", ranges=['fR1', 'fR2','fR3','fR4'])]
        #[store.store(s, dir=box) for s in self.plot1DHisto(inputFile, "MR", ranges=['FULL'])]
        #[store.store(s, dir=box) for s in self.plot1DHisto(inputFile, "Rsq", ranges=['FULL'])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 25, ranges=['fR1', 'fR2','fR3','fR4'])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['fR1', 'fR2','fR3','fR4'])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['FULL'])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['FULL'])]
                                        
    def plot1D(self, inputFile, varname, nbin=200, xmin=-99, xmax=-99, range = ''):
        
        # set the integral precision
        rt.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-10) ;
        rt.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-10) ;
        # get the max and min (if different than default)
        if xmax==xmin:
            xmin = self.workspace.var(varname).getMin()
            xmax = self.workspace.var(varname).getMax()
        data = RootTools.getDataSet(inputFile,'RMRTree')
        data = data.reduce(rt.RooFit.CutRange(range))
        data_cut = data.reduce(self.cut)
        
        # project the data on the variable
        frameMR = self.workspace.var(varname).frame(rt.RooFit.AutoSymRange(data_cut),rt.RooFit.Bins(nbin))
        frameMR.SetName(varname+"plot")
        frameMR.SetTitle(varname+"plot")
        
        data.plotOn(frameMR, rt.RooFit.LineColor(rt.kRed),rt.RooFit.MarkerColor(rt.kRed)) 
        data_cut.plotOn(frameMR)
        
        # project the full PDF on the data
        self.workspace.pdf(self.fitmodel).plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.Range(range))

        # plot each individual component: Wln
        N1_Wln = self.workspace.function("Ntot_Wln").getVal()*(1-self.workspace.var("f2_Wln").getVal())
        N2_Wln = self.workspace.function("Ntot_Wln").getVal()*self.workspace.var("f2_Wln").getVal()
        # plot each individual component: Zll
        N1_Zll = self.workspace.function("Ntot_Zll").getVal()*(1-self.workspace.var("f2_Zll").getVal())
        N2_Zll = self.workspace.function("Ntot_Zll").getVal()*self.workspace.var("f2_Zll").getVal()
        # plot each individual component: Znn
        N1_Znn = self.workspace.function("Ntot_Znn").getVal()*(1-self.workspace.var("f2_Znn").getVal())
        N2_Znn = self.workspace.function("Ntot_Znn").getVal()*self.workspace.var("f2_Znn").getVal()
        # plot each individual component: TTj
        N1_TTj = self.workspace.function("Ntot_TTj").getVal()*(1-self.workspace.var("f2_TTj").getVal())
        N2_TTj = self.workspace.function("Ntot_TTj").getVal()*self.workspace.var("f2_TTj").getVal()
        # plot each individual component: QCD
        N1_QCD = 0 #self.workspace.function("Ntot_QCD").getVal()*(1-self.workspace.var("f2_QCD").getVal())
        N2_QCD = 0 #self.workspace.function("Ntot_QCD").getVal()*self.workspace.var("f2_QCD").getVal()        

        Ntot = N1_Wln+N2_Wln+N1_Zll+N2_Zll+N1_Znn+N2_Znn+N1_TTj+N2_TTj+N1_QCD+N2_QCD

        if N1_Wln+N2_Wln >0:
            # project the first component: Wln
            self.workspace.pdf("PDF1st_Wln").plotOn(frameMR, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1_Wln/Ntot), rt.RooFit.Range(range))
            # project the second component: Wln
            self.workspace.pdf("PDF2nd_Wln").plotOn(frameMR, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2_Wln/Ntot), rt.RooFit.Range(range))
        if N1_Zll+N2_Zll >0:
            # project the first component: Zll
            self.workspace.pdf("PDF1st_Zll").plotOn(frameMR, rt.RooFit.LineColor(rt.kMagenta), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1_Zll/Ntot), rt.RooFit.Range(range))
            # project the second component: Zll
            self.workspace.pdf("PDF2nd_Zll").plotOn(frameMR, rt.RooFit.LineColor(rt.kMagenta), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2_Zll/Ntot), rt.RooFit.Range(range))
        if N1_Znn+N2_Znn >0:
            # project the first component: Znn
            self.workspace.pdf("PDF1st_Znn").plotOn(frameMR, rt.RooFit.LineColor(rt.kGreen), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1_Znn/Ntot), rt.RooFit.Range(range))
            # project the second component: Znn
            self.workspace.pdf("PDF2nd_Znn").plotOn(frameMR, rt.RooFit.LineColor(rt.kGreen), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2_Znn/Ntot), rt.RooFit.Range(range))
        if N1_TTj+N2_TTj >0:
            # project the first component: TTj
            self.workspace.pdf("PDF1st_TTj").plotOn(frameMR, rt.RooFit.LineColor(rt.kOrange), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1_TTj/Ntot), rt.RooFit.Range(range))
            # project the second component: TTj
            self.workspace.pdf("PDF2nd_TTj").plotOn(frameMR, rt.RooFit.LineColor(rt.kOrange), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2_TTj/Ntot), rt.RooFit.Range(range))
        if N1_QCD+N2_QCD >0:
            # project the first component: TTj
            self.workspace.pdf("PDF1st_QCD").plotOn(frameMR, rt.RooFit.LineColor(rt.kViolet), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1_QCD/Ntot), rt.RooFit.Range(range))
            # project the second component: TTj
            self.workspace.pdf("PDF2nd_QCD").plotOn(frameMR, rt.RooFit.LineColor(rt.kViolet), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2_QCD/Ntot), rt.RooFit.Range(range))            

        #leg = rt.TLegend("leg", "leg", 0.6, 0.6, 0.9, 0.9)
        #leg.AddEntry("PDF1st_Wln", "W+jets 1st")
        #leg.AddEntry("PDF2nd_Wln", "W+jets 2nd")
        #leg.AddEntry("PDF1st_Zll", "Z(ll)+jets 1st")
        #leg.AddEntry("PDF2nd_Zll", "Z(ll)+jets 2nd")
        #leg.AddEntry("PDF1st_Znn", "Z(#nu#nu)+jets 1st")
        #leg.AddEntry("PDF2nd_Znn", "Z(#nu#nu)+jets 2nd")
        #leg.AddEntry("PDF1st_TTj", "t#bar{t}+jets 1st")
        #leg.AddEntry("PDF2nd_TTj", "t#bar{t}+jets 2nd")
        
        return frameMR

    def plot1DHistoAllComponents(self, inputFile, xvarname, nbins = 25, ranges=None, data = None):
        
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
            
        #before I find a better way
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
        toyData = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), 50*data.numEntries())
        toyData = toyData.reduce(self.getVarRangeCutNamed(ranges=ranges))

        if self.name != "MuEle":
            # no ttbar
            Ntt = self.workspace.var("Ntot_TTj").getVal()
            self.workspace.var("Ntot_TTj").setVal(0.)
            # no znn+jets [this is ONLY for the Had box]
            Nznn = 0
            if self.name == "Had":
                Nznn = self.workspace.var("Ntot_Znn").getVal()
                self.workspace.var("Ntot_Znn").setVal(0.)
            
            toyDataWln = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(data.numEntries()-Ntt-Nznn)))
            toyDataWln = toyDataWln.reduce(self.getVarRangeCutNamed(ranges=ranges))
            if self.name == "Had":
                Nwj = self.workspace.var("Ntot_Wln").getVal()
                self.workspace.var("Ntot_Wln").setVal(0.)
                self.workspace.var("Ntot_Znn").setVal(Nznn)
                toyDataZnn = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(data.numEntries()-Ntt-Nwj)))
                toyDataZnn = toyDataZnn.reduce(self.getVarRangeCutNamed(ranges=ranges))
                self.workspace.var("Ntot_Wln").setVal(Nwj)
                
            self.workspace.var("Ntot_TTj").setVal(Ntt)

        xmin = min([self.workspace.var(xvarname).getMin(r) for r in ranges])
        xmax = max([self.workspace.var(xvarname).getMax(r) for r in ranges])

        # define 1D histograms
        histoData = self.setPoissonErrors(rt.TH1D("histoData", "histoData",nbins, xmin, xmax))
        histoToy = self.setPoissonErrors(rt.TH1D("histoToy", "histoToy",nbins, xmin, xmax))
        histoToyTTj = self.setPoissonErrors(rt.TH1D("histoToyTTj", "histoToyTTj",nbins, xmin, xmax))
        histoToyWln = self.setPoissonErrors(rt.TH1D("histoToyWln", "histoToyWln",nbins, xmin, xmax))
        histoToyZnn = self.setPoissonErrors(rt.TH1D("histoToyZnn", "histoToyZnn",nbins, xmin, xmax))

        def setName(h, name):
            h.SetName('%s_%s_%s_ALLCOMPONENTS' % (h.GetName(),name,'_'.join(ranges)) )
            h.GetXaxis().SetTitle(name)
        
        def SetErrors(histo, nbins):
            for i in range(1, nbins+1):
                histo.SetBinError(i,rt.TMath.Sqrt(histo.GetBinContent(i)))

        # project the data on the histograms
        #data.tree().Project("histoData",xvarname)
        data.fillHistogram(histoData,rt.RooArgList(self.workspace.var(xvarname)))
        toyData.fillHistogram(histoToy,rt.RooArgList(self.workspace.var(xvarname)))
        scaleFactor = histoData.Integral()/histoToy.Integral()
        if self.name != "MuEle":
            toyDataWln.fillHistogram(histoToyWln,rt.RooArgList(self.workspace.var(xvarname)))
            toyData.fillHistogram(histoToyTTj,rt.RooArgList(self.workspace.var(xvarname)))
            histoToyTTj.Add(histoToyWln, -1)
            if self.name == "Had":
                toyDataZnn.fillHistogram(histoToyZnn,rt.RooArgList(self.workspace.var(xvarname)))
                histoToyTTj.Add(histoToyZnn, -1)
                histoToyZnn.Scale(scaleFactor)
                SetErrors(histoToyZnn, nbins)
                setName(histoToyZnn,xvarname)
                histoToyZnn.SetLineColor(rt.kGreen)    
            histoToyTTj.Scale(scaleFactor)
            histoToyWln.Scale(scaleFactor)
            SetErrors(histoToyTTj, nbins)
            SetErrors(histoToyWln, nbins)
            setName(histoToyTTj,xvarname)
            setName(histoToyWln,xvarname)
            histoToyTTj.SetLineColor(rt.kOrange)
            histoToyTTj.SetLineWidth(2)
            if self.name == "EleEle" or self.name == "MuMu": histoToyWln.SetLineColor(rt.kMagenta)
            else: histoToyWln.SetLineColor(rt.kRed)
            histoToyWln.SetLineWidth(2)

        histoToy.Scale(scaleFactor)
        SetErrors(histoToy, nbins)
        setName(histoData,xvarname)
        setName(histoToy,xvarname)
        histoData.SetMarkerStyle(20)
        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        c = rt.TCanvas()
        c.SetName('DataMC_%s_%s_ALLCOMPONENTS' % (xvarname,'_'.join(ranges)) )
        histoData.Draw("pe")

        if self.name != "MuEle":
            if self.name == "Had":
                histoToyZnn.DrawCopy("histsame")
                histoToyZnn.SetFillColor(rt.kGreen)
                histoToyZnn.SetFillStyle(3018)
                histoToyZnn.Draw('e2same')            
            histoToyWln.DrawCopy("histsame")
            if self.name == "EleEle" or self.name == "MuMu": histoToyWln.SetFillColor(rt.kMagenta)
            else: histoToyWln.SetFillColor(rt.kRed)
            histoToyWln.SetFillStyle(3018)
            histoToyWln.Draw('e2same')
            histoToyTTj.DrawCopy('histsame')
            histoToyTTj.SetFillColor(rt.kOrange)
            histoToyTTj.SetFillStyle(3018)
            histoToyTTj.Draw('e2same')        
            histoToy.DrawCopy('histsame')

        histoToy.DrawCopy('histsame')
        histoToy.SetFillColor(rt.kBlue)
        histoToy.SetFillStyle(3018)
        histoToy.Draw('e2same')

        #histoData.Draw("pesame")

        #leg = rt.TLegend(0.6,0.6,0.9,0.9)
        #leg.SetFillColor(0)
        #leg.AddEntry(histoToyWln.GetName(),"W+jets","l")
        #leg.AddEntry(histoToyTTj.GetName(),"t#bar{t}","l")
        #leg.AddEntry(histoToy.GetName(),"Total","l")
        #leg.Draw()

        histToReturn = [histoToy, histoData, c]
        if self.name != "MuEle":
            histToReturn.append(histoToyTTj)
            histToReturn.append(histoToyWln)
            if self.name == "Had": histToReturn.append(histoToyZnn)

        return histToReturn
