from RazorCombinedFit.Framework import Box
import math
import RootTools
import RazorBox
import ROOT as rt
from array import *

class RazorMultiJetBox(RazorBox.RazorBox):
    
    def __init__(self, name, variables, fitMode = '2D', fitregion = 'FULL'):
        super(RazorMultiJetBox,self).__init__(name, variables)
        
        # TTJets DEFAULT
        self.zeros = {'UEC':[], 'TTj':[], 'QCD':['BJet']}
        # MC FIT: QCD
        #self.zeros = {'UEC':['BJet','QCD'], 'QCD':[]}

        self.cut = 'MR >= 0.0' # && BDT>-0.115'
        if fitregion=="SidebandL": self.fitregion = "SidebandMR,SidebandRsq"
        else: self.fitregion = fitregion
        self.fitMode = fitMode


    def getBinning(self, boxName, varName):
        if boxName == "BJet":
            if varName == "MR" : return [450, 500, 560, 630, 710, 800, 900, 1100, 1500, 2000, 2600, 4000]
            if varName == "Rsq": return [0.03,0.06, 0.1, 0.14, 0.19, 0.25,0.32,0.41,0.52,0.64,0.80,1.]
        else:
            if varName == "MR" : return [350, 420, 500, 600, 740, 900, 1200, 1600, 2500, 4000]
            if varName == "Rsq": return [0.08,0.15,0.21,0.30,0.41,0.52,0.64,0.80,1.]

    def define(self, inputFile):
        
        #define the ranges
        mR  = self.workspace.var("MR")
        Rsq = self.workspace.var("Rsq")

        # add the different components:
        self.addTailPdf("QCD", False)
        self.addTailPdf("UEC", True)
        self.addTailPdf("TTj", True)

         # build the total PDF
        myPDFlist = rt.RooArgList(self.workspace.pdf("ePDF_UEC"),self.workspace.pdf("ePDF_TTj"),self.workspace.pdf("ePDF_QCD"))
        #probably this needs to be hacked to accommodate a non-extended pdf
        model = rt.RooAddPdf(self.fitmodel, self.fitmodel, myPDFlist)
        
        # import the model in the workspace.
        self.importToWS(model)
        #print the workspace
        self.workspace.Print()

        ##### THIS IS A SIMPLIFIED FIT
        # fix all pdf parameters to the initial value
        #self.fixPars("QCD")
        #self.fixPars("UEC")
        #self.fixPars("TTj")
        #self.fixPars("MR0_")
        #self.fixPars("R0_")
        #self.fixPars("b_")
        #self.fixPars("MR0_TTj")
        #self.fixPars("R0_TTj")
        #self.fixPars("b_TTj")
        self.fixPars("n_TTj")

        def floatSomething(z):
            """Switch on or off whatever you want here"""
            # the "effective" first component in the Had box
            self.floatYield(z)
            self.floatComponent(z)

        fixed = []
        for z in self.zeros:
            if self.name in self.zeros[z]:
                self.fixPars(z)
                self.switchOff(z)
            else:
                if not z in fixed:
                    floatSomething(z)
                    fixed.append(z)
        
        # set normalizations
        Nuec = self.workspace.var("Ntot_UEC").getVal()
        Nttj = self.workspace.var("Ntot_TTj").getVal()
        Nqcd = self.workspace.var("Ntot_QCD").getVal()
        data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
 
        #in the case that the input file is an MC input file
        if data is None or not data:
            return None
 
        Ndata = data.sumEntries()
        self.workspace.var("Ntot_UEC").setVal(Ndata*Nuec/(Nuec+Nttj+Nqcd))
        self.workspace.var("Ntot_TTj").setVal(Ndata*Nttj/(Nuec+Nttj+Nqcd))
        self.workspace.var("Ntot_QCD").setVal(Ndata*Nqcd/(Nuec+Nttj+Nqcd))

        del data
    
    def plot1DHistoAllComponents(self, inputFile, xvarname, nbins = 25, ranges=None, data = None):
        
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
        
        factor = 50    
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
        
        # variable binning for plots
        bins = self.getBinning(self.name, xvarname)
        nbins =len(bins)-1
        xedge = array("d",bins)
        print "Binning in variable %s is "%xvarname
        print bins
        
        # define 1D histograms
        histoData = self.setPoissonErrors(rt.TH1D("histoData", "histoData",nbins, xedge))
        histoToy = self.setPoissonErrors(rt.TH1D("histoToy", "histoToy",nbins, xedge))
        histoToyUEC = self.setPoissonErrors(rt.TH1D("histoToyUEC", "histoToyUEC",nbins, xedge))
        histoToyTTj = self.setPoissonErrors(rt.TH1D("histoToyTTj", "histoToyTTj",nbins, xedge))
        histoToyQCD = self.setPoissonErrors(rt.TH1D("histoToyQCD", "histoToyQCD",nbins, xedge))

        def setName(h, name):
            h.SetName('%s_%s_%s_ALLCOMPONENTS' % (h.GetName(),name,'_'.join(ranges)) )
            h.GetXaxis().SetTitle(name)
        
        def SetErrors(histo, nbins):
            for i in range(1, nbins+1):
                histo.SetBinError(i,rt.TMath.Sqrt(histo.GetBinContent(i)))

        # project the data on the histograms
        #data.tree().Project("histoData",xvarname)
        data.fillHistogram(histoData,rt.RooArgList(self.workspace.var(xvarname)))
        
        #Cache the numbers
        Nuec = self.workspace.var("Ntot_UEC").getVal()
        Nttj = self.workspace.var("Ntot_TTj").getVal()
        Nqcd = self.workspace.var("Ntot_QCD").getVal()

        #Generate the TTj first component component
        if self.workspace.var("Ntot_TTj") != None and Nttj > 0:
            self.workspace.var("Ntot_UEC").setVal(0.)
            self.workspace.var("Ntot_QCD").setVal(0.)
            toyDataTTj = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(factor*(Nttj)))
            toyDataTTj.fillHistogram(histoToyTTj,rt.RooArgList(self.workspace.var(xvarname)))
            histoToyTTj.SetLineColor(rt.kRed)
            histoToyTTj.SetLineWidth(2)
            self.workspace.var("Ntot_UEC").setVal(Nuec)
            self.workspace.var("Ntot_QCD").setVal(Nqcd)
            
        #Generate the UEC component    
        if self.workspace.var("Ntot_UEC") != None and Nuec > 0:
            self.workspace.var("Ntot_TTj").setVal(0.)
            self.workspace.var("Ntot_QCD").setVal(0.)
            #toyDataUEC = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(factor*(data.numEntries()-Nqcd)))
            toyDataUEC = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(factor*(Nuec)))
            toyDataUEC.fillHistogram(histoToyUEC,rt.RooArgList(self.workspace.var(xvarname)))
            histoToyUEC.SetLineColor(rt.kRed)
            histoToyUEC.SetLineWidth(2)
            self.workspace.var("Ntot_TTj").setVal(Nttj)
            self.workspace.var("Ntot_QCD").setVal(Nqcd)
        
        #Generate the QCD component
        if self.workspace.var("Ntot_QCD") != None and Nqcd > 0:
            self.workspace.var("Ntot_UEC").setVal(0.)
            self.workspace.var("Ntot_TTj").setVal(0.)
            #toyDataQCD = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(factor*(data.numEntries()-Nuec)))
            toyDataQCD = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(factor*(Nqcd)))
            toyDataQCD.fillHistogram(histoToyQCD,rt.RooArgList(self.workspace.var(xvarname)))
            histoToyQCD.SetLineColor(rt.kGreen)
            histoToyQCD.SetLineWidth(2)
            self.workspace.var("Ntot_UEC").setVal(Nuec)
            self.workspace.var("Ntot_TTj").setVal(Nttj)
        
        if self.workspace.var("Ntot_UEC") != None and Nuec>1 :histoToy.Add(histoToyUEC, +1)
        if self.workspace.var("Ntot_TTj") != None and Nttj>1 :histoToy.Add(histoToyTTj, +1)
        if self.workspace.var("Ntot_QCD") != None and Nqcd>1: histoToy.Add(histoToyQCD, +1)

        #put some protection in for divide by zero
        scaleFactor = 1.0
        if abs(histoToy.Integral()-0.0) > 1e-8:
            scaleFactor = histoData.Integral()/histoToy.Integral()

        histoToy.Scale(scaleFactor)
        histoToyUEC.Scale(scaleFactor)
        histoToyTTj.Scale(scaleFactor)
        histoToyQCD.Scale(scaleFactor)
        SetErrors(histoToy, nbins)
        SetErrors(histoToyUEC, nbins)
        SetErrors(histoToyTTj, nbins)
        SetErrors(histoToyQCD, nbins)
        setName(histoData,xvarname)
        setName(histoToy,xvarname)
        setName(histoToyUEC,xvarname)
        setName(histoToyTTj,xvarname)
        setName(histoToyQCD,xvarname)
        histoData.SetMarkerStyle(20)
        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        c = rt.TCanvas()
        c.SetName('DataMC_%s_%s_ALLCOMPONENTS' % (xvarname,'_'.join(ranges)) )
        histoData.Draw("pe")
        
        histoToyUEC.DrawCopy('histsame')
        histoToyUEC.SetLineColor(rt.kMagenta+2)
        histoToyUEC.SetFillColor(rt.kMagenta+2)
        histoToyUEC.SetFillStyle(3018)
        histoToyUEC.Draw('e2same')  

        if self.workspace.var("Ntot_TTj") != None and Nttj > 0:
            histoToyTTj.DrawCopy('histsame')
            histoToyTTj.SetLineColor(rt.kCyan)
            histoToyTTj.SetFillColor(rt.kCyan)
            histoToyTTj.SetFillStyle(3018)
            histoToyTTj.Draw('e2same')  

        if self.workspace.var("Ntot_QCD") != None and Nqcd > 0:
            histoToyQCD.DrawCopy('histsame')
            histoToyQCD.SetLineColor(rt.kGreen)
            histoToyQCD.SetFillColor(rt.kGreen)
            histoToyQCD.SetFillStyle(3018)
            histoToyQCD.Draw('e2same')  

        histoToy.DrawCopy('histsame')
        histoToy.SetFillColor(rt.kBlue)
        histoToy.SetFillStyle(3018)
        histoToy.Draw('e2same')

        if self.workspace.var("Ntot_QCD") != None and Nqcd > 0:
            histToReturn = [histoToy, histoToyQCD, histoToyTTj, histoToyUEC, histoData, c]
        else:
            histToReturn = [histoToy, histoToyTTj, histoToyUEC, histoData, c]

        return histToReturn

    # to be removed eventually
    def plot(self, inputFile, store, box):
        store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=['FULL']), dir=box)
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['FULL'])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 25, ranges=['FULL'])]
