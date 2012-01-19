from RazorCombinedFit.Framework import Box
import math
import RootTools
import RazorBox
import ROOT as rt

class RazorMultiJetBox(RazorBox.RazorBox):
    
    def __init__(self, name, variables):
        super(RazorMultiJetBox,self).__init__(name, variables)
        
        #self.zeros = {'TTj':[],'Wln':['Mu','MuMu','EleEle','MuEle'],'Zll':['MuEle','Mu','Ele','Had'],'Znn':['Ele','MuMu','EleEle','MuEle'],'QCD':['Ele', 'Mu', 'MuEle','MuMu','EleEle','Had']}
        # this is what we did in 2011
        # self.zeros = {'TTj':[],'Wln':['Mu','MuMu','EleEle','MuEle'],'Zll':['MuEle','Mu','Ele','Had'],'Znn':['Ele','MuMu','EleEle','MuEle']}
        # now we switch off the redundant Znn component in the Had box
        self.zeros = {'TTj':[], 'QCD':['BJET']}

        self.cut = 'MR >= 0.0'

    def define(self, inputFile):
        
        #define the ranges
        mR  = self.workspace.var("MR")
        Rsq = self.workspace.var("Rsq")
        
        # add the different components:
        self.addTailPdf("QCD")
        self.addTailPdf("TTj")

        # build the total PDF
        myPDFlist = rt.RooArgList(self.workspace.pdf("ePDF1st_TTj"),self.workspace.pdf("ePDF2nd_TTj"),
                                  self.workspace.pdf("ePDF1st_QCD"),self.workspace.pdf("ePDF2nd_QCD"))
        model = rt.RooAddPdf(self.fitmodel, self.fitmodel, myPDFlist)
        
        # import the model in the workspace.
        self.importToWS(model)
        #print the workspace
        self.workspace.Print()

        ##### THIS IS A SIMPLIFIED FIT
        # fix all pdf parameters to the initial value
        self.fixPars("QCD")
        self.fixPars("TTj")

        def floatSomething(z):
            """Switch on or off whatever you want here"""
            # the "effective" first component in the Had box
            if not (self.name == "BJET" and z == "QCD"): self.float1stComponentWithPenalty(z)
            if z != "QCD": self.float2ndComponentWithPenalty(z, False)
            self.floatYield(z)
            self.floatFraction(z)

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

        #remove redundant second components
        self.fix2ndComponent("QCD")
        self.workspace.var("f2_QCD").setVal(0.)
        self.workspace.var("f2_QCD").setConstant(rt.kTRUE)
                    
                    
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

        return histToReturn

    # to be removed eventually
    def plot(self, inputFile, store, box):
        store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=['FULL']), dir=box)
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['FULL'])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['FULL'])]
