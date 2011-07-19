from RazorCombinedFit.Framework import Box
import RootTools
import ROOT as rt

class RazorBox(Box.Box):
    
    def __init__(self, name, variables):
        super(RazorBox,self).__init__(name, variables)
        
        self.zeros = {'TTj':[],'Wln':['MuMu','EleEle','MuEle'],'Zll':['MuEle','Ele'],'Znn':['Mu','Ele','MuMu','EleEle','MuEle']}
        self.cut = 'MR <= 750'

    def addTailPdf(self, label):
        # define the two components
        self.workspace.factory("RooRazor2DTail::PDF1st"+label+"(MR,Rsq,MR01st"+label+",R01st"+label+",b1st"+label+")")
        self.workspace.factory("RooRazor2DTail::PDF2nd"+label+"(MR,Rsq,MR02nd"+label+",R02nd"+label+",b2nd"+label+")")
        #define the two yields
        self.workspace.factory("expr::N_1st"+label+"('@0*(1-@1)',Ntot"+label+",f2"+label+")")
        self.workspace.factory("expr::N_2nd"+label+"('@0*@1',Ntot"+label+",f2"+label+")")
        #associate the yields to the pdfs through extended PDFs
        self.workspace.factory("RooExtendPdf::ePDF1st"+label+"(PDF1st"+label+", N_1st"+label+")")
        self.workspace.factory("RooExtendPdf::ePDF2nd"+label+"(PDF2nd"+label+", N_2nd"+label+")")

    def switchOff(self, species) :
        self.workspace.var("Ntot_"+species).setVal(0.)
        self.workspace.var("Ntot_"+species).setConstant(rt.kTRUE)
        self.workspace.var("f2_"+species).setConstant(rt.kTRUE)

    def define(self, inputFile):
        
        #create the dataset
        data = RootTools.getDataSet(inputFile,'RMRTree')
        #import the dataset to the workspace
        self.importToWS(data)
        print 'Reduced dataset'
        #data.Print("V")

        # add the different components:
        # - W+jets
        # - Zll+jets
        # - Znn+jets
        # - ttbar+jets
        self.addTailPdf("_Wln")
        self.addTailPdf("_Zll")
        self.addTailPdf("_Znn")
        self.addTailPdf("_TTj")

        # build the total PDF
        model = rt.RooAddPdf("fitmodel", "fitmodel", rt.RooArgList(self.workspace.pdf("ePDF1st_Wln"),self.workspace.pdf("ePDF2nd_Wln"),
                                                                   self.workspace.pdf("ePDF1st_Zll"),self.workspace.pdf("ePDF2nd_Zll"),
                                                                   self.workspace.pdf("ePDF1st_Znn"),self.workspace.pdf("ePDF2nd_Znn"),
                                                                   self.workspace.pdf("ePDF1st_TTj"),self.workspace.pdf("ePDF2nd_TTj")))        
        
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
        
        #add penalty terms and float
        def float1stComponentWithPenalty(flavour):
            #self.fixParsPenalty("MR01st_%s" % flavour)
            #self.fixParsPenalty("R01st_%s" % flavour)
            self.fixParsPenalty("b1st_%s" % flavour)
        def floatFractionWithPenalty(flavour):
            self.fixParsPenalty("f2_%s" % flavour)

        # float all the yields and 2nd-component fractions
        self.fixPars("Ntot_", rt.kFALSE)
        #self.fixPars("f2_", rt.kFALSE)
        
        
        fixed = []
        for z in self.zeros:
            if self.name in self.zeros[z]:
                self.switchOff(z)
            else:
                if not z in fixed:
                    floatFractionWithPenalty(z)
                    if self.name != 'Had': float1stComponentWithPenalty(z)
                    fixed.append(z)
        
        # switch off not-needed components (box by box)
#        if self.name != "Had": self.switchOff("Znn")
#        if self.name == "MuEle":
#            self.switchOff("Wln")
#            self.switchOff("Zll")
#        if self.name == "MuMu" or self.name == "EleEle":
#            self.switchOff("Wln")

        
    def plot(self, inputFile, store, box):
        super(RazorBox,self).plot(inputFile, store, box)
        store.store(self.plot1D(inputFile, "MR", 50, 250., 1500.), dir=box)
        store.store(self.plot1D(inputFile, "Rsq",50, 0.04, .8), dir=box)
        store.store(self.plot2D(inputFile, "MR", "Rsq"), dir=box)
            
    def plot1D(self, inputFile, varname, nbin=200, xmin=-99, xmax=-99):
        # set the integral precision
        rt.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-10) ;
        rt.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-10) ;
        # get the max and min (if different thandefault)
        if xmax==xmin:
            xmin = self.workspace.var(varname).getMin()
            xmax = self.workspace.var(varname).getMax()
        # project the data on the variable
        frameMR = self.workspace.var(varname).frame(xmin, xmax, nbin)
        frameMR.SetName(varname+"plot")
        frameMR.SetTitle(varname+"plot")
        data = RootTools.getDataSet(inputFile,'RMRTree')
        data.plotOn(frameMR)
        # project the full PDF on the data
        self.workspace.pdf("fitmodel").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue))

        # plot each individual component: Wln
        N1_Wln = self.workspace.var("Ntot_Wln").getVal()*(1-self.workspace.var("f2_Wln").getVal())
        N2_Wln = self.workspace.var("Ntot_Wln").getVal()*self.workspace.var("f2_Wln").getVal()
        # plot each individual component: Zll
        N1_Zll = self.workspace.var("Ntot_Zll").getVal()*(1-self.workspace.var("f2_Zll").getVal())
        N2_Zll = self.workspace.var("Ntot_Zll").getVal()*self.workspace.var("f2_Zll").getVal()
        # plot each individual component: Znn
        N1_Znn = self.workspace.var("Ntot_Znn").getVal()*(1-self.workspace.var("f2_Znn").getVal())
        N2_Znn = self.workspace.var("Ntot_Znn").getVal()*self.workspace.var("f2_Znn").getVal()
        # plot each individual component: TTj
        N1_TTj = self.workspace.var("Ntot_TTj").getVal()*(1-self.workspace.var("f2_TTj").getVal())
        N2_TTj = self.workspace.var("Ntot_TTj").getVal()*self.workspace.var("f2_TTj").getVal()

        Ntot = N1_Wln+N2_Wln+N1_Zll+N2_Zll+N1_Znn+N2_Znn+N1_TTj+N2_TTj

        if N1_Wln+N2_Wln >0:
            # project the first component: Wln
            self.workspace.pdf("PDF1st_Wln").plotOn(frameMR, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1_Wln/Ntot))
            # project the second component: Wln
            self.workspace.pdf("PDF2nd_Wln").plotOn(frameMR, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2_Wln/Ntot))
        if N1_Zll+N2_Zll >0:
            # project the first component: Zll
            self.workspace.pdf("PDF1st_Zll").plotOn(frameMR, rt.RooFit.LineColor(rt.kMagenta), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1_Zll/Ntot))
            # project the second component: Zll
            self.workspace.pdf("PDF2nd_Zll").plotOn(frameMR, rt.RooFit.LineColor(rt.kMagenta), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2_Zll/Ntot))
        if N1_Znn+N2_Znn >0:
            # project the first component: Znn
            self.workspace.pdf("PDF1st_Znn").plotOn(frameMR, rt.RooFit.LineColor(rt.kGreen), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1_Znn/Ntot))
            # project the second component: Znn
            self.workspace.pdf("PDF2nd_Znn").plotOn(frameMR, rt.RooFit.LineColor(rt.kGreen), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2_Znn/Ntot))
        if N1_TTj+N2_TTj >0:
            # project the first component: TTj
            self.workspace.pdf("PDF1st_TTj").plotOn(frameMR, rt.RooFit.LineColor(rt.kOrange), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1_TTj/Ntot))
            # project the second component: TTj
            self.workspace.pdf("PDF2nd_TTj").plotOn(frameMR, rt.RooFit.LineColor(rt.kOrange), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2_TTj/Ntot))

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

    def plot2D(self, inputFile, xvarname, yvarname):
        #before I find a better way
        data = RootTools.getDataSet(inputFile,'RMRTree')
        toyData = self.workspace.pdf("fitmodel").generate(rt.RooArgSet(self.workspace.argSet(xvarname+","+yvarname)), 10*data.numEntries())

        # define 2D histograms
        histoData = rt.TH2D("histoData", "histoData",
                            100, self.workspace.var(xvarname).getMin(), self.workspace.var(xvarname).getMax(), 
                            100, self.workspace.var(yvarname).getMin(), self.workspace.var(yvarname).getMax())
        histoToy = rt.TH2D("histoToy", "histoToy",
                            100, self.workspace.var(xvarname).getMin(), self.workspace.var(xvarname).getMax(), 
                            100, self.workspace.var(yvarname).getMin(), self.workspace.var(yvarname).getMax())
        # project the data on the histograms
        data.tree().Project("histoData",yvarname+":"+xvarname)
        toyData.tree().Project("histoToy",yvarname+":"+xvarname)
        histoToy.Scale(histoData.Integral()/histoToy.Integral())
        histoData.Add(histoToy, -1)
        return histoData
