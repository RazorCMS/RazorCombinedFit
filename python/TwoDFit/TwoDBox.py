from RazorCombinedFit.Framework import Box
import RootTools
import ROOT as rt

class TwoDBox(Box.Box):
    
    def __init__(self, name, variables):
        super(TwoDBox,self).__init__(name, variables)

    def define(self, inputFile):
        
        #create the dataset
        data = RootTools.getDataSet(inputFile,'RMRTree')
        #import the dataset to the workspace
        self.importToWS(data)
        print 'Reduced dataset'
        #data.Print("V")

        # define the two components
        self.workspace.factory("RooRazor2DTail::PDF1st(MR,Rsq,MR01st,R01st,b1st)")
        self.workspace.factory("RooRazor2DTail::PDF2nd(MR,Rsq,MR02nd,R02nd,b2nd)")
        #define the two yields
        self.workspace.factory("expr::N_1st('@0*(1-@1)',Ntot,f2)")
        self.workspace.factory("expr::N_2nd('@0*@1',Ntot,f2)")
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
        store.store(self.plot1D(inputFile, "MR", 50, 250., 1500.), dir=box)
        store.store(self.plot1D(inputFile, "Rsq",50, 0.04, .8), dir=box)
        store.store(self.plotRsqMR(inputFile), dir=box)
            
    def plot1D(self, inputFile, varname, nbin=200, xmin=-99, xmax=-99):
        # set the integral precision
        rt.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-10)
        rt.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-10)
        # get the max and min (if different thandefault)
        if xmax==xmin:
            xmin = self.workspace.var(varname).getMin()
            xmax = self.workspace.var(varname).getMax()
        # project the data on R
        frameMR = self.workspace.var(varname).frame(xmin, xmax, nbin)
        frameMR.SetName(varname+"plot")
        frameMR.SetTitle(varname+"plot")
        #        data = rt.RooDataSet(self.workspace.genobj("RMRTree"))
        #before I find a better way
        data = RootTools.getDataSet(inputFile,'RMRTree')
        data.plotOn(frameMR)
        # project the full PDF on the data
        self.workspace.pdf("fitmodel").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue))

        N1 = self.workspace.var("Ntot").getVal()*(1-self.workspace.var("f2").getVal())
        N2 = self.workspace.var("Ntot").getVal()*self.workspace.var("f2").getVal()

        # project the first component
        self.workspace.pdf("PDF1st").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(N1/(N1+N2)))
        # project the second component
        self.workspace.pdf("PDF2nd").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(N2/(N1+N2)))
        return frameMR

    def plotRsqMR(self, inputFile):
        #before I find a better way
        data = RootTools.getDataSet(inputFile,'RMRTree')
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
