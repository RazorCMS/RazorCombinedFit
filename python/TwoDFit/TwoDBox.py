from RazorCombinedFit.Framework import Box
import RootTools
import ROOT as rt

class TwoDBox(Box.Box):
    
    def __init__(self, name, variables):
        super(TwoDBox,self).__init__(name, variables)

    def define(self, inputFile, cuts):
        
        rcuts = cuts.get('rcuts',[])
        rcuts.sort()

        # define the two components
        self.workspace.factory("RooRazor2DTail::PDF1st(MR,R,MR01st[35,-100,200],R01st[-0.12,-1,0],b1st[0.001,0,10])")
        self.workspace.factory("RooRazor2DTail::PDF2nd(MR,R,MR02nd[-1.48,-100,200],R02nd[-0.22,-1,0],b2nd[0.001,0,10])")
        #define the two yields
        self.workspace.factory("N_ttbar_1st[2000, -10., 100000]")
        self.workspace.factory("N_ttbar_2nd[1000, -10., 100000]")
        # reasonable errors (do we need it?)
        #self.workspace.var("MR01st").setError(10.)
        #self.workspace.var("R01st").setError(0.1)
        #self.workspace.var("b1st").setError(0.1)
        #self.workspace.var("N_ttbar_1st").setError(100.)
        #self.workspace.var("MR02nd").setError(10.)
        #self.workspace.var("R02nd").setError(0.1)
        #self.workspace.var("b2nd").setError(0.1)
        #self.workspace.var("N_ttbar_2nd").setError(200.)

        #associate the yields to the pdfs through extended PDFs
        self.workspace.factory("RooExtendPdf::ePDF1st(PDF1st, N_ttbar_1st)")
        self.workspace.factory("RooExtendPdf::ePDF2nd(PDF2nd, N_ttbar_2nd)")
        # build the total PDF
        model = rt.RooAddPdf("fitmodel", "fitmodel", rt.RooArgList(self.workspace.pdf("ePDF1st"),self.workspace.pdf("ePDF2nd")))        
        # import the model in the workspace.
        self.importToWS(model)
        #print the workspace
        self.workspace.Print()

        #create the dataset
        data = RootTools.getDataSet(inputFile,'RMRTree')
        #import the dataset to the workspace
        self.importToWS(data)
        
        #the parameters of interest are the offsets and shape parameters
        # already created by the PDF 
        print 'Rcuts',rcuts
        print 'Reduced dataset'
        data.Print("V")
            
    def plotMR(self, inputFile):
        # project the data on R
        frameMR = self.workspace.var("MR").frame(self.workspace.var("MR").getMin(), 3000., 100)
        frameMR.SetName("MRplot")
        frameMR.SetTitle("MRplot")
        #        data = rt.RooDataSet(self.workspace.genobj("RMRTree"))
        #before I find a better way
        data = RootTools.getDataSet(inputFile,'RMRTree')
        data.plotOn(frameMR)
        # project the full PDF on the data
        self.workspace.pdf("fitmodel").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue))

        Ntt1 = self.workspace.var("N_ttbar_1st").getVal()
        Ntt2 = self.workspace.var("N_ttbar_1st").getVal()

        # project the first component
        self.workspace.pdf("PDF1st").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(Ntt1/(Ntt1+Ntt2)))
        #, rt.RooFit.Normalization(self.workspace.var("N_ttbar_1st").getVal()))
        # project the second component
        self.workspace.pdf("PDF2nd").plotOn(frameMR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(Ntt2/(Ntt1+Ntt2)))
        #, rt.RooFit.Normalization(self.workspace.var("N_ttbar_2nd").getVal()))
        return frameMR

    def plotR(self, inputFile):
        # project the data on R
        frameR = self.workspace.var("R").frame(self.workspace.var("R").getMin(), 1.5, 100)
        frameR.SetName("Rplot")
        frameR.SetTitle("Rplot")
        #before I find a better way
        data = RootTools.getDataSet(inputFile,'RMRTree')
        data.plotOn(frameR)

        Ntt1 = self.workspace.var("N_ttbar_1st").getVal()
        Ntt2 = self.workspace.var("N_ttbar_1st").getVal()
        
        # project the full PDF
        self.workspace.pdf("fitmodel").plotOn(frameR, rt.RooFit.LineColor(rt.kBlue)) 
        # project the first component
        self.workspace.pdf("PDF1st").plotOn(frameR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(8), rt.RooFit.Normalization(Ntt1/(Ntt1+Ntt2)))
        # project the second component
        self.workspace.pdf("PDF2nd").plotOn(frameR, rt.RooFit.LineColor(rt.kBlue), rt.RooFit.LineStyle(9), rt.RooFit.Normalization(Ntt2/(Ntt1+Ntt2)))

        return frameR
