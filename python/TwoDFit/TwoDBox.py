from RazorCombinedFit.Framework import Box
import RootTools
import ROOT as rt

class TwoDBox(Box.Box):
    
    def __init__(self, name, variables):
        super(TwoDBox,self).__init__(name, variables)

    def define(self, inputFile, cuts):
        
        rcuts = cuts.get('rcuts',[])
        rcuts.sort()
        
        #create the dataset
        data = RootTools.getDataSet(inputFile,'RMRTree')
        #import the dataset to the workspace
        self.importToWS(data)
        print 'Reduced dataset'
        data.Print("V")

        # define the two components
        self.workspace.factory("RooRazor2DTail::PDF1st(MR,Rsq,MR01st[35,-200,200],R01st[-0.22,-1,0.09],b1st[0.09,0,10])")
        self.workspace.factory("RooRazor2DTail::PDF2nd(MR,Rsq,MR02nd[0.,-400,200],R02nd[-0.22,-1,0.05],b2nd[0.03,0,10])")
        #define the two yields
        self.workspace.factory("expr::N_ttbar_1st('@0*(1-@1)',N_tt[1500, 0., %d],f2[0.03,0., 0.5])" % data.numEntries())
        self.workspace.factory("expr::N_ttbar_2nd('@0*@1',N_tt,f2)")
        #associate the yields to the pdfs through extended PDFs
        self.workspace.factory("RooExtendPdf::ePDF1st(PDF1st, N_ttbar_1st)")
        self.workspace.factory("RooExtendPdf::ePDF2nd(PDF2nd, N_ttbar_2nd)")
        # build the total PDF
        model = rt.RooAddPdf("fitmodel", "fitmodel", rt.RooArgList(self.workspace.pdf("ePDF1st"),self.workspace.pdf("ePDF2nd")))        
        # import the model in the workspace.
        self.importToWS(model)
        #print the workspace
        self.workspace.Print()
        
        #the parameters of interest are the offsets and shape parameters
        # already created by the PDF 
        print 'Rcuts',rcuts
        
    def plot(self, inputFile, store, box):
        super(TwoDBox,self).plot(inputFile, store, box)
        store.store(self.plotMR(inputFile), dir=box)
        store.store(self.plotRsq(inputFile), dir=box)
        store.store(self.plotRsqMR(inputFile), dir=box)
            
    def plotMR(self, inputFile):
        # project the data on R
        frameMR = self.workspace.var("MR").frame(self.workspace.var("MR").getMin(), 3000., 200)
        frameMR.SetName("MRplot")
        frameMR.SetTitle("MRplot")
        #        data = rt.RooDataSet(self.workspace.genobj("RMRTree"))
        #before I find a better way
        data = RootTools.getDataSet(inputFile,'RMRTree')
        data.plotOn(frameMR)
        # project the full PDF on the data
        self.workspace.pdf("fitmodel").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue))

        Ntt1 = self.workspace.var("N_tt").getVal()*(1-self.workspace.var("f2").getVal())
        Ntt2 = self.workspace.var("N_tt").getVal()*self.workspace.var("f2").getVal()

        # project the first component
        self.workspace.pdf("PDF1st").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(Ntt1/(Ntt1+Ntt2)))
        #, rt.RooFit.Normalization(self.workspace.var("N_ttbar_1st").getVal()))
        # project the second component
        self.workspace.pdf("PDF2nd").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(Ntt2/(Ntt1+Ntt2)))
        #, rt.RooFit.Normalization(self.workspace.var("N_ttbar_2nd").getVal()))
        return frameMR

    def plotRsq(self, inputFile):
        # project the data on Rsq
        frameRsq = self.workspace.var("Rsq").frame(self.workspace.var("Rsq").getMin(), 1.5, 200)
        frameRsq.SetName("Rsqplot")
        frameRsq.SetTitle("Rsqplot")
        #before I find a better way
        data = RootTools.getDataSet(inputFile,'RMRTree')
        data.plotOn(frameRsq)

        Ntt1 = self.workspace.var("N_tt").getVal()*(1-self.workspace.var("f2").getVal())
        Ntt2 = self.workspace.var("N_tt").getVal()*self.workspace.var("f2").getVal()
        
        # project the full PDF
        self.workspace.pdf("fitmodel").plotOn(frameRsq, rt.RooFit.LineColor(rt.kBlue)) 
        # project the first component
        self.workspace.pdf("PDF1st").plotOn(frameRsq, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(Ntt1/(Ntt1+Ntt2)))
        # project the second component
        self.workspace.pdf("PDF2nd").plotOn(frameRsq, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(Ntt2/(Ntt1+Ntt2)))

        return frameRsq

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
