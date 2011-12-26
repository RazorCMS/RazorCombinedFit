from RazorCombinedFit.Framework import Box
import RootTools
import RazorBox
import ROOT as rt

class RazorBjetBox(RazorBox.RazorBox):
    
    def __init__(self, name, variables):
        super(RazorBjetBox,self).__init__(name, variables)
        
        # now we switch off the redundant Znn component in the Had box
        self.zeros = {'TTj':[],'Wln':['Had','Mu','MuMu','EleEle','MuEle'],'Zll':['Had','Ele','Mu','MuMu','EleEle','MuEle'],'Znn':['Had','Ele','MuMu','EleEle','MuEle']}

        self.cut = 'MR >= 0.0'

    
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
            if z == "Wln" and self.name == "Had": self.float1stComponent(z)
            else : self.float1stComponentWithPenalty(z)
            if self.name != "Had": self.float2ndComponentWithPenalty(z, True)
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

        #if self.name == "Had": self.workspace.var("b1st_TTj").setConstant(rt.kFALSE)

        #remove redundant second components
        if self.name == "Ele":
            self.fix2ndComponent("Wln")
            self.workspace.var("f2_Wln").setVal(0.)
            self.workspace.var("f2_Wln").setConstant(rt.kTRUE)
        if self.name == "Mu":
            self.fix2ndComponent("Znn")
            self.workspace.var("f2_Znn").setVal(0.)
            self.workspace.var("f2_Znn").setConstant(rt.kTRUE)

