from RazorCombinedFit.Framework import Box
import RootTools
import ROOT as rt

class OneDBox(Box.Box):
    
    def __init__(self, name, variables):
        super(OneDBox,self).__init__(name, variables)

    def fit1D(self, inputFile, reduce = None, dataset = "RMRTree", *options):
        data = self.workspace.data(dataset)
        return self.fitData(self.getFitPDF(), data, *options)

    def defineRsqData(self, inputFile):
        # get the full data
        Rmin = self.workspace.var("Rsq").getMin()
        Rmax = self.workspace.var("Rsq").getMax()
        dataBIS = RootTools.getDataSet(inputFile,'RMRTree').reduce("Rsq>=%f && Rsq<%f" % (Rmin, Rmax))
        # create the binned dataset
        mRmin = self.workspace.var("MR").getMin()
        data1 = dataBIS.reduce("MR>=%f && MR<%f" % (mRmin, mRmin+25.))
        data2 = dataBIS.reduce("MR>=%f && MR<%f" % (mRmin+25, mRmin+50.))
        data3 = dataBIS.reduce("MR>=%f && MR<%f" % (mRmin+50, mRmin+75.))
        data4 = dataBIS.reduce("MR>=%f && MR<%f" % (mRmin+75, mRmin+100.))
        data5 = dataBIS.reduce("MR>=%f && MR<%f" % (mRmin+100, mRmin+125.))
        data6 = dataBIS.reduce("MR>=%f" % (mRmin+125.))
        # create the index Category
        c = rt.RooCategory("c","c") ;
        c.defineType("Bin1") ;
        c.defineType("Bin2") ;
        c.defineType("Bin3") ;
        c.defineType("Bin4") ;
        c.defineType("Bin5") ;
        c.defineType("Bin6") ;
        self.importToWS(c)

        #initialize the inclusive yields to right values and fix them
        self.workspace.var("N6").setVal(data6.numEntries())
        self.workspace.var("N5").setVal(data5.numEntries()+self.workspace.var("N6").getVal())
        self.workspace.var("N4").setVal(data4.numEntries()+self.workspace.var("N5").getVal())
        self.workspace.var("N3").setVal(data3.numEntries()+self.workspace.var("N4").getVal())
        self.workspace.var("N2").setVal(data2.numEntries()+self.workspace.var("N3").getVal())
        self.workspace.var("N1").setVal(data1.numEntries()+self.workspace.var("N2").getVal())
        self.workspace.var("N1").setConstant(rt.kTRUE)
        self.workspace.var("N2").setConstant(rt.kTRUE)
        self.workspace.var("N3").setConstant(rt.kTRUE)
        self.workspace.var("N4").setConstant(rt.kTRUE)
        self.workspace.var("N5").setConstant(rt.kTRUE)
        self.workspace.var("N6").setConstant(rt.kTRUE)
        # Create a dataset that imports contents of all the above datasets mapped by index category 
        data = rt.RooDataSet("RMRTree2","RMRTree2", rt.RooArgSet(self.workspace.var("Rsq")),rt.RooFit.Index(c),
                             rt.RooFit.Import("Bin1",data1),
                             rt.RooFit.Import("Bin2",data2),
                             rt.RooFit.Import("Bin3",data3),
                             rt.RooFit.Import("Bin4",data4),
                             rt.RooFit.Import("Bin5",data5),
                             rt.RooFit.Import("Bin6",data6))
        #import the dataset to the workspace
        self.importToWS(data)
        print 'Reduced dataset'
        #data.Print("V")
            

    def defineMRData(self, inputFile):
        # get the full data
        mRmin = self.workspace.var("MR").getMin()
        mRmax = self.workspace.var("MR").getMax()
        dataBIS = RootTools.getDataSet(inputFile,'RMRTree').reduce("MR>=%f && MR<%f" % (mRmin, mRmax))
        # create the binned dataset
        rsqmin = self.workspace.var("Rsq").getMin()
        data1 = dataBIS.reduce("Rsq>=%f && Rsq<%f" % (rsqmin, rsqmin+0.02))
        data2 = dataBIS.reduce("Rsq>=%f && Rsq<%f" % (rsqmin+0.02, rsqmin+0.04))
        data3 = dataBIS.reduce("Rsq>=%f && Rsq<%f" % (rsqmin+0.04, rsqmin+0.06))
        data4 = dataBIS.reduce("Rsq>=%f && Rsq<%f" % (rsqmin+0.06, rsqmin+0.08))
        data5 = dataBIS.reduce("Rsq>=%f && Rsq<%f" % (rsqmin+0.08, rsqmin+0.10))
        data6 = dataBIS.reduce("Rsq>=%f" % (rsqmin+0.10))
        # create the index Category
        c = rt.RooCategory("c","c") ;
        c.defineType("Bin1") ;
        c.defineType("Bin2") ;
        c.defineType("Bin3") ;
        c.defineType("Bin4") ;
        c.defineType("Bin5") ;
        c.defineType("Bin6") ;
        self.importToWS(c)

        #initialize the inclusive yields to right values and fix them
        self.workspace.var("N6").setVal(data6.numEntries())
        self.workspace.var("N5").setVal(data5.numEntries()+self.workspace.var("N6").getVal())
        self.workspace.var("N4").setVal(data4.numEntries()+self.workspace.var("N5").getVal())
        self.workspace.var("N3").setVal(data3.numEntries()+self.workspace.var("N4").getVal())
        self.workspace.var("N2").setVal(data2.numEntries()+self.workspace.var("N3").getVal())
        self.workspace.var("N1").setVal(data1.numEntries()+self.workspace.var("N2").getVal())
        self.workspace.var("N1").setConstant(rt.kTRUE)
        self.workspace.var("N2").setConstant(rt.kTRUE)
        self.workspace.var("N3").setConstant(rt.kTRUE)
        self.workspace.var("N4").setConstant(rt.kTRUE)
        self.workspace.var("N5").setConstant(rt.kTRUE)
        self.workspace.var("N6").setConstant(rt.kTRUE)
        # Create a dataset that imports contents of all the above datasets mapped by index category 
        data = rt.RooDataSet("RMRTree2","RMRTree2", rt.RooArgSet(self.workspace.var("MR")),rt.RooFit.Index(c),
                             rt.RooFit.Import("Bin1",data1),
                             rt.RooFit.Import("Bin2",data2),
                             rt.RooFit.Import("Bin3",data3),
                             rt.RooFit.Import("Bin4",data4),
                             rt.RooFit.Import("Bin5",data5),
                             rt.RooFit.Import("Bin6",data6))
        #import the dataset to the workspace
        self.importToWS(data)
        print 'Reduced dataset'
        #data.Print("V")

    def define(self, inputFile, useMR = rt.kTRUE):
        if useMR == rt.kTRUE: self.defineMRData(inputFile)
        else : self.defineRsqData(inputFile)
        var = "MR"
        if useMR != rt.kTRUE: var = "Rsq"

        # build the exponent parameters
        self.workspace.factory("expr::k1_1('-@0-@1*0.04',a1,b1)")
        self.workspace.factory("expr::k1_2('-@0-@1*0.06',a1,b1)")
        self.workspace.factory("expr::k1_3('-@0-@1*0.08',a1,b1)")
        self.workspace.factory("expr::k1_4('-@0-@1*0.10',a1,b1)")
        self.workspace.factory("expr::k1_5('-@0-@1*0.12',a1,b1)")
        self.workspace.factory("expr::k1_6('-@0-@1*0.14',a1,b1)")

        self.workspace.factory("expr::k2_1('-@0-@1*0.04',a2,b2)")
        self.workspace.factory("expr::k2_2('-@0-@1*0.06',a2,b2)")
        self.workspace.factory("expr::k2_3('-@0-@1*0.08',a2,b2)")
        self.workspace.factory("expr::k2_4('-@0-@1*0.10',a2,b2)")
        self.workspace.factory("expr::k2_5('-@0-@1*0.12',a2,b2)")
        self.workspace.factory("expr::k2_6('-@0-@1*0.14',a2,b2)")

        # buld the two components
        self.workspace.factory("Exponential::Expo1_1(%s,k1_1)" % var)
        self.workspace.factory("Exponential::Expo1_2(%s,k1_2)" % var)
        self.workspace.factory("Exponential::Expo1_3(%s,k1_3)" % var)
        self.workspace.factory("Exponential::Expo1_4(%s,k1_4)" % var)
        self.workspace.factory("Exponential::Expo1_5(%s,k1_5)" % var)
        self.workspace.factory("Exponential::Expo1_6(%s,k1_6)" % var)
        
        self.workspace.factory("Exponential::Expo2_1(%s,k2_1)" % var)
        self.workspace.factory("Exponential::Expo2_2(%s,k2_2)" % var)
        self.workspace.factory("Exponential::Expo2_3(%s,k2_3)" % var)
        self.workspace.factory("Exponential::Expo2_4(%s,k2_4)" % var)
        self.workspace.factory("Exponential::Expo2_5(%s,k2_5)" % var)
        self.workspace.factory("Exponential::Expo2_6(%s,k2_6)" % var)

        #self.workspace.factory("RooRazor1D::Expo1_1(MR,m1,s1,k1_1)")
        #self.workspace.factory("RooRazor1D::Expo1_2(MR,m2,s2,k1_2)")
        #self.workspace.factory("RooRazor1D::Expo1_3(MR,m3,s3,k1_3)")
        #self.workspace.factory("RooRazor1D::Expo1_4(MR,m4,s4,k1_4)")
        #self.workspace.factory("RooRazor1D::Expo1_5(MR,m5,s5,k1_5)")
        #self.workspace.factory("RooRazor1D::Expo1_6(MR,m6,s6,k1_6)")
        
        #self.workspace.factory("RooRazor1D::Expo2_1(MR,m1,s1,k2_1)")
        #self.workspace.factory("RooRazor1D::Expo2_2(MR,m2,s2,k2_2)")
        #self.workspace.factory("RooRazor1D::Expo2_3(MR,m3,s3,k2_3)")
        #self.workspace.factory("RooRazor1D::Expo2_4(MR,m4,s4,k2_4)")
        #self.workspace.factory("RooRazor1D::Expo2_5(MR,m5,s5,k2_5)")
        #self.workspace.factory("RooRazor1D::Expo2_6(MR,m6,s6,k2_6)")        

        # define the yields as a fucntion of total and 2nd component fraction
        self.workspace.factory("expr::N6_1st('@0*(1-@1)',N6,f6)")
        self.workspace.factory("expr::N6_2nd('@0*@1',N6,f6)")
        self.workspace.factory("expr::N5_1st('@0*(1-@1)',N5,f5)")
        self.workspace.factory("expr::N5_2nd('@0*@1',N5,f5)")
        self.workspace.factory("expr::N4_1st('@0*(1-@1)',N4,f4)")
        self.workspace.factory("expr::N4_2nd('@0*@1',N4,f4)")
        self.workspace.factory("expr::N3_1st('@0*(1-@1)',N3,f3)")
        self.workspace.factory("expr::N3_2nd('@0*@1',N3,f3)")
        self.workspace.factory("expr::N2_1st('@0*(1-@1)',N2,f2)")
        self.workspace.factory("expr::N2_2nd('@0*@1',N2,f2)")
        self.workspace.factory("expr::N1_1st('@0*(1-@1)',N1,f1)")
        self.workspace.factory("expr::N1_2nd('@0*@1',N1,f1)")

        # define the last bin pdf (the last bin is special)
        self.workspace.factory("RooExtendPdf::ePDF1_6(Expo1_6, N6_1st)")
        self.workspace.factory("RooExtendPdf::ePDF2_6(Expo2_6, N6_2nd)")

        # define the bin-by bin yield as the difference of the inclusive yields: 1st COMPONENT
        self.workspace.factory("expr::Nrel1st_1('@0-@1',N1_1st,N2_1st)")
        self.workspace.factory("expr::Nrel1st_2('@0-@1',N2_1st,N3_1st)")
        self.workspace.factory("expr::Nrel1st_3('@0-@1',N3_1st,N4_1st)")
        self.workspace.factory("expr::Nrel1st_4('@0-@1',N4_1st,N5_1st)")
        self.workspace.factory("expr::Nrel1st_5('@0-@1',N5_1st,N6_1st)")

        # define the bin-by bin yield as the difference of the inclusive yields: 2nd COMPONENT
        self.workspace.factory("expr::Nrel2nd_1('@0-@1',N1_2nd,N2_2nd)")
        self.workspace.factory("expr::Nrel2nd_2('@0-@1',N2_2nd,N3_2nd)")
        self.workspace.factory("expr::Nrel2nd_3('@0-@1',N3_2nd,N4_2nd)")
        self.workspace.factory("expr::Nrel2nd_4('@0-@1',N4_2nd,N5_2nd)")
        self.workspace.factory("expr::Nrel2nd_5('@0-@1',N5_2nd,N6_2nd)")

        # define the bin-by-bin PDFs as the differences of the inclusive PDFs: 1st COMPONENT
        self.workspace.factory("expr::f5_1st_1('1/(1-@0/@1)',N6_1st,N5_1st)")
        self.workspace.factory("expr::f5_1st_2('-@0/@1/(1-@0/@1)',N6_1st,N5_1st)")
        self.workspace.factory("SUM::PDF1_5(f5_1st_1*Expo1_5, f5_1st_2*Expo1_6)")
        self.workspace.factory("RooExtendPdf::ePDF1_5(PDF1_5, Nrel1st_5)")

        self.workspace.factory("expr::f4_1st_1('1/(1-@0/@1)',N5_1st,N4_1st)")
        self.workspace.factory("expr::f4_1st_2('-@0/@1/(1-@0/@1)',N5_1st,N4_1st)")
        self.workspace.factory("SUM::PDF1_4(f4_1st_1*Expo1_4, f4_1st_2*Expo1_5)")
        self.workspace.factory("RooExtendPdf::ePDF1_4(PDF1_4, Nrel1st_4)")

        self.workspace.factory("expr::f3_1st_1('1/(1-@0/@1)',N4_1st,N3_1st)")
        self.workspace.factory("expr::f3_1st_2('-@0/@1/(1-@0/@1)',N4_1st,N3_1st)")
        self.workspace.factory("SUM::PDF1_3(f3_1st_1*Expo1_3, f3_1st_2*Expo1_4)")
        self.workspace.factory("RooExtendPdf::ePDF1_3(PDF1_3, Nrel1st_3)")

        self.workspace.factory("expr::f2_1st_1('1/(1-@0/@1)',N3_1st,N2_1st)")
        self.workspace.factory("expr::f2_1st_2('-@0/@1/(1-@0/@1)',N3_1st,N2_1st)")
        self.workspace.factory("SUM::PDF1_2(f2_1st_1*Expo1_2, f2_1st_2*Expo1_3)")
        self.workspace.factory("RooExtendPdf::ePDF1_2(PDF1_2, Nrel1st_2)")

        self.workspace.factory("expr::f1_1st_1('1/(1-@0/@1)',N2_1st,N1_1st)")
        self.workspace.factory("expr::f1_1st_2('-@0/@1/(1-@0/@1)',N2_1st,N1_1st)")
        self.workspace.factory("SUM::PDF1_1(f1_1st_1*Expo1_1, f1_1st_2*Expo1_2)")                
        self.workspace.factory("RooExtendPdf::ePDF1_1(PDF1_1, Nrel1st_1)")

        # define the bin-by-bin PDFs as the differences of the inclusive PDFs: 2nd COMPONENT
        self.workspace.factory("expr::f5_2nd_1('1/(1-@0/@1)',N6_2nd,N5_2nd)")
        self.workspace.factory("expr::f5_2nd_2('-@0/@1/(1-@0/@1)',N6_2nd,N5_2nd)")
        self.workspace.factory("SUM::PDF2_5(f5_2nd_1*Expo2_5, f5_2nd_2*Expo2_6)")
        self.workspace.factory("RooExtendPdf::ePDF2_5(PDF2_5, Nrel2nd_5)")

        self.workspace.factory("expr::f4_2nd_1('1/(1-@0/@1)',N5_2nd,N4_2nd)")
        self.workspace.factory("expr::f4_2nd_2('-@0/@1/(1-@0/@1)',N5_2nd,N4_2nd)")
        self.workspace.factory("SUM::PDF2_4(f4_2nd_1*Expo2_4, f4_2nd_2*Expo2_5)")
        self.workspace.factory("RooExtendPdf::ePDF2_4(PDF2_4, Nrel2nd_4)")

        self.workspace.factory("expr::f3_2nd_1('1/(1-@0/@1)',N4_2nd,N3_2nd)")
        self.workspace.factory("expr::f3_2nd_2('-@0/@1/(1-@0/@1)',N4_2nd,N3_2nd)")
        self.workspace.factory("SUM::PDF2_3(f3_2nd_1*Expo2_3, f3_2nd_2*Expo2_4)")
        self.workspace.factory("RooExtendPdf::ePDF2_3(PDF2_3, Nrel2nd_3)")

        self.workspace.factory("expr::f2_2nd_1('1/(1-@0/@1)',N3_2nd,N2_2nd)")
        self.workspace.factory("expr::f2_2nd_2('-@0/@1/(1-@0/@1)',N3_2nd,N2_2nd)")
        self.workspace.factory("SUM::PDF2_2(f2_2nd_1*Expo2_2, f2_2nd_2*Expo2_3)")
        self.workspace.factory("RooExtendPdf::ePDF2_2(PDF2_2, Nrel2nd_2)")

        self.workspace.factory("expr::f1_2nd_1('1/(1-@0/@1)',N2_2nd,N1_2nd)")
        self.workspace.factory("expr::f1_2nd_2('-@0/@1/(1-@0/@1)',N2_2nd,N1_2nd)")
        self.workspace.factory("SUM::PDF2_1(f1_2nd_1*Expo2_1, f1_2nd_2*Expo2_2)")
        self.workspace.factory("RooExtendPdf::ePDF2_1(PDF2_1, Nrel2nd_1)")

        # define the TOTAL bin-by-bin pdf as the sume of the first and second component

        ePDF_1 = rt.RooAddPdf("ePDF_1", "ePDF_1", rt.RooArgList(self.workspace.pdf("ePDF1_1"),self.workspace.pdf("ePDF2_1")))
        ePDF_2 = rt.RooAddPdf("ePDF_2", "ePDF_2", rt.RooArgList(self.workspace.pdf("ePDF1_2"),self.workspace.pdf("ePDF2_2")))
        ePDF_3 = rt.RooAddPdf("ePDF_3", "ePDF_3", rt.RooArgList(self.workspace.pdf("ePDF1_3"),self.workspace.pdf("ePDF2_3")))
        ePDF_4 = rt.RooAddPdf("ePDF_4", "ePDF_4", rt.RooArgList(self.workspace.pdf("ePDF1_4"),self.workspace.pdf("ePDF2_4")))
        ePDF_5 = rt.RooAddPdf("ePDF_5", "ePDF_5", rt.RooArgList(self.workspace.pdf("ePDF1_5"),self.workspace.pdf("ePDF2_5")))
        ePDF_6 = rt.RooAddPdf("ePDF_6", "ePDF_6", rt.RooArgList(self.workspace.pdf("ePDF1_6"),self.workspace.pdf("ePDF2_6")))

        self.importToWS(ePDF_1)
        self.importToWS(ePDF_2)
        self.importToWS(ePDF_3)
        self.importToWS(ePDF_4)
        self.importToWS(ePDF_5)
        self.importToWS(ePDF_6)

        # build the total PDF
        model = rt.RooSimultaneous("fitmodel", "fitmodel", self.workspace.cat("c"))
        model.addPdf(self.workspace.pdf("ePDF_1"),"Bin1")
        model.addPdf(self.workspace.pdf("ePDF_2"),"Bin2")
        model.addPdf(self.workspace.pdf("ePDF_3"),"Bin3")
        model.addPdf(self.workspace.pdf("ePDF_4"),"Bin4")
        model.addPdf(self.workspace.pdf("ePDF_5"),"Bin5")
        model.addPdf(self.workspace.pdf("ePDF_6"),"Bin6")

        # import the model in the workspace.
        self.importToWS(model)
        
        #print the workspace
        self.workspace.Print()
        
