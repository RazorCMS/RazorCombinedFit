from RazorCombinedFit.Framework import Box
import RootTools
import ROOT as rt

class TwoDBox(Box.Box):
    
    def __init__(self, name, variables):
        super(TwoDBox,self).__init__(name, variables)
        self.cut = 'MR >= 0.0'

    def define(self, inputFile):
        xmin = self.workspace.var("MR").getMin()
        xmax = self.workspace.var("MR").getMax()
        ymin = self.workspace.var("Rsq").getMin()
        ymax = self.workspace.var("Rsq").getMax()
        
        #create the dataset
        data = RootTools.getDataSet(inputFile,'RMRTree').reduce("MR >= %f && MR <= %f" %(xmin, xmax)).reduce("Rsq >= %f && Rsq < %f" %(ymin, ymax))
        #use weights
        data
        #import the dataset to the workspace
        self.importToWS(data)
        print 'Reduced dataset'
        #data.Print("V")

        #define the yield as eps*r*L*sigma
        self.yieldToCrossSection()

        #define the ranges
        mR  = self.workspace.var("MR")
        Rsq = self.workspace.var("Rsq")

        # TIGHT
        mR.setRange("B1", 300, 650.)
        Rsq.setRange("B1", 0.09, 0.2)
        mR.setRange("B2", 300, 450.)
        Rsq.setRange("B2", 0.2, 0.3)
        mR.setRange("B3", 300, 350.)
        Rsq.setRange("B3", 0.3, 0.5)
        mR.setRange("FULL", 300, 3500.)
        Rsq.setRange("FULL", 0.09, 0.5)

        #LOOSE
        #mR.setRange("B1", 200, 650.)
        #Rsq.setRange("B1", 0.04, 0.2)
        #mR.setRange("B2", 200, 450.)
        #Rsq.setRange("B2", 0.2, 0.3)
        #mR.setRange("B3", 200, 350.)
        #Rsq.setRange("B3", 0.3, 0.5)
        #mR.setRange("FULL", 200, 3500.)
        #Rsq.setRange("FULL", 0.04, 0.5)

        # define the two components
        self.workspace.factory("RooRazor2DTail::PDF1st(MR,Rsq,MR01st,R01st,b1st)")
        self.workspace.factory("RooRazor2DTail::PDF2nd(MR,Rsq,MR02nd,R02nd,b2nd)")
        #define the two yields
        self.workspace.factory("expr::N_1st('@0*(1-@1*@2)',Ntot,f2,rf)")
        self.workspace.factory("expr::N_2nd('@0*@1*@2',Ntot,f2,rf)")
        #associate the yields to the pdfs through extended PDFs
        self.workspace.factory("RooExtendPdf::ePDF1st(PDF1st, N_1st)")
        self.workspace.factory("RooExtendPdf::ePDF2nd(PDF2nd, N_2nd)")
        # build the total PDF
        model = rt.RooAddPdf("fitmodel", "fitmodel", rt.RooArgList(self.workspace.pdf("ePDF1st"),self.workspace.pdf("ePDF2nd")))        
        # import the model in the workspace.
        self.importToWS(model)
        
        if self.workspace.var('b1st_m') and self.workspace.var('b1st_s'): 
            self.fixVariable('b1st','b1st_m','b1st_s')
        
        #print the workspace
        self.workspace.Print()
        
    def plot(self, inputFile, store, box):
        super(TwoDBox,self).plot(inputFile, store, box)
        store.store(self.plot1D(inputFile, "MR", 50), dir=box)
        store.store(self.plot1D(inputFile, "Rsq",50), dir=box)
        store.store(self.plotRsqMR(inputFile), dir=box)
            
    def plot1D(self, inputFile, varname, nbin=200, xmin=-99, xmax=-99):
        # set the integral precision
        rt.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-10)
        rt.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-10)
        # get the max and min (if different thandefault)
        if xmax==xmin:
            xmin = self.workspace.var(varname).getMin("FULL")
            xmax = self.workspace.var(varname).getMax("FULL")
        # project the data on R
        frameMR = self.workspace.var(varname).frame(xmin, xmax, nbin)
        frameMR.SetName(varname+"plot")
        frameMR.SetTitle(varname+"plot")
        #        data = rt.RooDataSet(self.workspace.genobj("RMRTree"))
        data = self.workspace.data("RMRTree")
        data.plotOn(frameMR)
        # project the full PDF on the data
        self.workspace.pdf("fitmodel").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.Range("FULL"))

        N1 = self.workspace.function("N_1st").getVal()
        N2 = self.workspace.function("N_2nd").getVal()

        # project the first component
        self.workspace.pdf("PDF1st").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1/(N1+N2)),rt.RooFit.Range("FULL"))
        # project the second component
        self.workspace.pdf("PDF2nd").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2/(N1+N2)), rt.RooFit.Range("FULL"))
        return frameMR

    def plotRsqMR(self, inputFile):
        data = self.workspace.data("RMRTree")
        toyData = self.workspace.pdf("fitmodel").generate(rt.RooArgSet(self.workspace.argSet("MR,Rsq")), 10*data.numEntries())

        # define 2D histograms
        histoData = rt.TH2D("histoData", "histoData",
                            100, self.workspace.var("MR").getMin(), 3500.,
                            100, self.workspace.var("Rsq").getMin(), 1.)
        histoToy = rt.TH2D("histoToy", "histoToy",
                            100, self.workspace.var("MR").getMin(), 3500.,
                            100, self.workspace.var("Rsq").getMin(), 1.)
        # project the data on the histograms
        data.tree().Project("histoData","Rsq:MR")
        toyData.tree().Project("histoToy","Rsq:MR")
        histoToy.Scale(histoData.Integral()/histoToy.Integral())
        histoData.Add(histoToy, -1)
        return histoData
