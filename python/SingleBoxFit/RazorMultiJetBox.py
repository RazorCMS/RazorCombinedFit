from RazorCombinedFit.Framework import Box
import math
import RootTools
import RazorBox
import ROOT as rt

class RazorMultiJetBox(RazorBox.RazorBox):
    
    def __init__(self, name, variables):
        super(RazorMultiJetBox,self).__init__(name, variables)
        
        # DATA DEFAULT
        self.zeros = {'TTj':[], 'QCD':[]}
        # MC FIT: QCD
        #self.zeros = {'TTj':['Had','QCD'], 'QCD':[]}
        # MC FIT: TTj
        #self.zeros = {'TTj':[], 'QCD':['Had','BJET']}

        self.cut = 'MR >= 0.0'

    def define(self, inputFile):
        
        #define the ranges
        mR  = self.workspace.var("MR")
        Rsq = self.workspace.var("Rsq")
        
        # add the different components:
        self.addTailPdf("QCD",False)
        self.addTailPdf("TTj",True)

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
            self.float1stComponentWithPenalty(z, True)
            self.float2ndComponentWithPenalty(z, True)
            self.floatYield(z)
            self.floatFraction(z)
            self.fixParsPenalty("n2nd_%s" % z)
            #self.fixPars("n2nd_%s" % z)

        fixed = []
        for z in self.zeros:
            if self.name in self.zeros[z]:
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

        #self.fix2ndComponent("TTj")
                    
    def plot1DHistoAllComponents(self, inputFile, xvarname, nbins = 25, ranges=None, data = None):
        
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
        
        factor = 50    
        #before I find a better way
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
        toyData = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), factor*data.numEntries())
        toyData = toyData.reduce(self.getVarRangeCutNamed(ranges=ranges))
        
        #also show the data with loose leptons
        dataLep = data.reduce('nLepton > 0')

        xmin = min([self.workspace.var(xvarname).getMin(r) for r in ranges])
        xmax = max([self.workspace.var(xvarname).getMax(r) for r in ranges])

        # define 1D histograms
        histoData = self.setPoissonErrors(rt.TH1D("histoData", "histoData",nbins, xmin, xmax))
        histoDataLep = self.setPoissonErrors(rt.TH1D("histoDataLep", "histoDataLep",nbins, xmin, xmax))
        histoToy = self.setPoissonErrors(rt.TH1D("histoToy", "histoToy",nbins, xmin, xmax))
        histoToyTTj = self.setPoissonErrors(rt.TH1D("histoToyTTj", "histoToyTTj",nbins, xmin, xmax))
        histoToyQCD = self.setPoissonErrors(rt.TH1D("histoToyQCD", "histoToyQCD",nbins, xmin, xmax))

        def setName(h, name):
            h.SetName('%s_%s_%s_ALLCOMPONENTS' % (h.GetName(),name,'_'.join(ranges)) )
            h.GetXaxis().SetTitle(name)
        
        def SetErrors(histo, nbins):
            for i in range(1, nbins+1):
                histo.SetBinError(i,rt.TMath.Sqrt(histo.GetBinContent(i)))

        # project the data on the histograms
        #data.tree().Project("histoData",xvarname)
        data.fillHistogram(histoData,rt.RooArgList(self.workspace.var(xvarname)))
        dataLep.fillHistogram(histoDataLep,rt.RooArgList(self.workspace.var(xvarname)))
        toyData.fillHistogram(histoToy,rt.RooArgList(self.workspace.var(xvarname)))
        
        #Cache the numbers
        Ntt = self.workspace.var("Ntot_TTj").getVal()
        Nqcd = self.workspace.var("Ntot_QCD").getVal()
        
        #Generate the TTj component    
        self.workspace.var("Ntot_QCD").setVal(0.)
        toyDataTTj = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(factor*(data.numEntries()-Nqcd)))
        toyDataTTj.fillHistogram(histoToyTTj,rt.RooArgList(self.workspace.var(xvarname)))
        histoToyTTj.SetLineColor(rt.kRed)
        histoToyTTj.SetLineWidth(2)
        self.workspace.var("Ntot_QCD").setVal(Nqcd)
        
        #Generate the QCD component
        self.workspace.var("Ntot_TTj").setVal(0.)
        toyDataQCD = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(factor*(data.numEntries()-Ntt)))
        toyDataQCD.fillHistogram(histoToyQCD,rt.RooArgList(self.workspace.var(xvarname)))
        histoToyQCD.SetLineColor(rt.kGreen)
        histoToyQCD.SetLineWidth(2)
        self.workspace.var("Ntot_TTj").setVal(Ntt)        
        
        #put some protection in for divide by zero
        scaleFactor = 1.0
        if abs(histoToy.Integral()-0.0) > 1e-8:
            scaleFactor = histoData.Integral()/histoToy.Integral()

        histoToy.Scale(scaleFactor)
        histoToyTTj.Scale(scaleFactor)
        histoToyQCD.Scale(scaleFactor)
        SetErrors(histoToy, nbins)
        SetErrors(histoToyTTj, nbins)
        SetErrors(histoToyQCD, nbins)
        setName(histoData,xvarname)
        setName(histoDataLep,xvarname)
        setName(histoToy,xvarname)
        setName(histoToyTTj,xvarname)
        setName(histoToyQCD,xvarname)
        histoData.SetMarkerStyle(20)
        histoDataLep.SetLineWidth(2)
        histoDataLep.SetLineStyle(rt.kDashed)
        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        c = rt.TCanvas()
        c.SetName('DataMC_%s_%s_ALLCOMPONENTS' % (xvarname,'_'.join(ranges)) )
        histoData.Draw("pe")
        
        histoDataLep.Draw("histsame")

        histoToyTTj.DrawCopy('histsame')
        histoToyTTj.SetFillColor(rt.kRed)
        histoToyTTj.SetFillStyle(3018)
        histoToyTTj.Draw('e2same')  

        histoToyQCD.DrawCopy('histsame')
        histoToyQCD.SetFillColor(rt.kGreen)
        histoToyQCD.SetFillStyle(3018)
        histoToyQCD.Draw('e2same')  

        histoToy.DrawCopy('histsame')
        histoToy.SetFillColor(rt.kBlue)
        histoToy.SetFillStyle(3018)
        histoToy.Draw('e2same')

        histToReturn = [histoToy, histoToyQCD, histoToyTTj, histoData, histoDataLep, c]

        return histToReturn

#    # to be removed eventually
#    def plot(self, inputFile, store, box):
#        store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=['fR1,fR2,fR3,fR4,fR5']), dir=box)
#        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['fR1,fR2,fR3,fR4,fR5'])]
#        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 80, ranges=['fR1,fR2,fR3,fR4,fR5'])]
#        for r in ['FULL','fR1','fR2','fR3','fR4','fR5']:
#            store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=[r]), dir=box)
#            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=[r])]
#            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 80, ranges=[r])]

    # to be removed eventually
    def plot(self, inputFile, store, box):
        store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=['FULL']), dir=box)
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['FULL'])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 80, ranges=['FULL'])]
#        for r in ['FULL']:
#            store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=[r]), dir=box)
#            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=[r])]
#            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 80, ranges=[r])]
