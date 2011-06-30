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

        data = RootTools.getDataSet(inputFile,'RMRTree')
        
        #the parameters of interest are the offsets and shape parameters
        # already created by the PDF 
        print 'Rcuts',rcuts
        print 'Reduced dataset'
        data.Print("V")
            
            
        
        

