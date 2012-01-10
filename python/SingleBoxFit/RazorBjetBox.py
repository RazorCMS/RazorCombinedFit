from RazorCombinedFit.Framework import Box
import RootTools
import RazorBox
import ROOT as rt

class RazorBjetBox(RazorBox.RazorBox):
    
    def __init__(self, name, variables):
        super(RazorBjetBox,self).__init__(name, variables)
        
        # now we switch off the redundant Znn component in the Had box
        self.zeros = {'TTj':[],'Wln':['Mu','MuMu','EleEle','MuEle'],'Zll':['Had','BJet','Ele','Mu','MuMu','EleEle','MuEle'],'Znn':['Had','BJet','Ele','MuMu','EleEle','MuEle']}

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
            # the "effective" first component in the Had box
            if z == "Wln" and self.name == "BJet": self.float1stComponent(z)
            elif z == "Wln" and self.name == "Had": self.float1stComponent(z)
            else : self.float1stComponentWithPenalty(z, True)
            # the b2nd parameter is floated in the 1Lep boxes (no penalty term)
            if z == "TTj" and self.name == "Mu": self.float2ndComponentWithPenalty(z, False)
            elif self.name != "Had" and self.name != "BJet": self.float2ndComponentWithPenalty(z, True)
            self.floatYield(z)
            if self.name != "Had" and self.name != "BJet": self.floatFraction(z)

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

        if self.name == "Had" or self.name == "BJet": self.workspace.var("b1st_TTj").setConstant(rt.kFALSE)

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

        if self.name != "MuEle" and self.name != "MuMu" and self.name != "EleEle":
            # no ttbar
            Ntt = self.workspace.var("Ntot_TTj").getVal()
            self.workspace.var("Ntot_TTj").setVal(0.)
            Nznn = 0            
            toyDataWln = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(50*(data.numEntries()-Ntt-Nznn)))
            toyDataWln = toyDataWln.reduce(self.getVarRangeCutNamed(ranges=ranges))                
            self.workspace.var("Ntot_TTj").setVal(Ntt)

        xmin = min([self.workspace.var(xvarname).getMin(r) for r in ranges])
        xmax = max([self.workspace.var(xvarname).getMax(r) for r in ranges])

        # define 1D histograms
        histoData = rt.TH1D("histoData", "histoData",nbins, xmin, xmax)
        histoToy = rt.TH1D("histoToy", "histoToy",nbins, xmin, xmax)
        histoToyTTj = rt.TH1D("histoToyTTj", "histoToyTTj",nbins, xmin, xmax)
        histoToyWln = rt.TH1D("histoToyWln", "histoToyWln",nbins, xmin, xmax)
        histoToyZnn = rt.TH1D("histoToyZnn", "histoToyZnn",nbins, xmin, xmax)

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
        if self.name != "MuEle" and self.name != "MuMu" and self.name != "EleEle":
            toyDataWln.fillHistogram(histoToyWln,rt.RooArgList(self.workspace.var(xvarname)))
            toyData.fillHistogram(histoToyTTj,rt.RooArgList(self.workspace.var(xvarname)))
            histoToyTTj.Add(histoToyWln, -1)
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

        if self.name != "MuEle" and self.name != "MuMu" and self.name != "EleEle":
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
        if self.name != "MuEle" and self.name != "MuMu" and self.name != "EleEle":
            histToReturn.append(histoToyTTj)
            histToReturn.append(histoToyWln)

        return histToReturn
