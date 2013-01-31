from RazorCombinedFit.Framework import Box
import math
import RootTools
import RazorBox
import ROOT as rt
from array import *

# This is global, to be used also in the scripts for plots
def Binning(boxName, varName):
    if varName == "MR" : return [500.0, 550.0, 650.0, 790.0, 1000, 1500, 2200, 3000, 4000.0]
    if varName == "Rsq": return [0.05, 0.07, 0.12, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
   ##  if varName == "MR" : return [450.0, 550.0, 650.0, 790.0, 1000, 1500, 2200, 3000, 4000.0]
##     if varName == "Rsq": return [0.03, 0.07, 0.12, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
    if varName == "Btag": return [1.,5.]

class RazorMultiJetBox(RazorBox.RazorBox):
    
    def __init__(self, name, variables, twoComponents = False):
        super(RazorMultiJetBox,self).__init__(name, variables)
        
        self.zeros = {'TTj':[] , 'QCD':['Mu','Ele','CRMuBVeto','CREleBVeto']}
        self.cut = 'MR >= 0.0'
        
    def define(self, inputFile, twoComponentOnly = False):
        
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

        #fix all pdf parameters to the initial value
        self.fixPars("QCD")
        self.fixPars("TTj")

        def floatSomething(z):
            """Switch on or off whatever you want here"""
            # the "effective" first component in the Had box
            self.float1stComponentWithPenalty(z, True)
            self.float2ndComponentWithPenalty(z, True)
            self.floatYield(z)
            self.floatFraction(z)
            
            #we put the n parameter but fix it
            self.fixParsExact("n2nd_%s" % z, True)


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
        dataLep = data.reduce('MR > 1e6')

        xmin = min([self.workspace.var(xvarname).getMin(r) for r in ranges])
        xmax = max([self.workspace.var(xvarname).getMax(r) for r in ranges])

        # define 1D histograms
        histoData2011 = self.setPoissonErrors(rt.TH1D("histoData2011", "histoData2011",nbins, xmin, xmax))
        histoDataLep2011 = self.setPoissonErrors(rt.TH1D("histoDataLep2011", "histoDataLep2011",nbins, xmin, xmax))
        histoToy2011 = self.setPoissonErrors(rt.TH1D("histoToy2011", "histoToy2011",nbins, xmin, xmax))
        histoToyTTj2011 = self.setPoissonErrors(rt.TH1D("histoToyTTj2011", "histoToyTTj2011",nbins, xmin, xmax))
        histoToyQCD2011 = self.setPoissonErrors(rt.TH1D("histoToyQCD2011", "histoToyQCD2011",nbins, xmin, xmax))

        # variable binning for plots
        newbins = Binning(self.name, xvarname)
        newNbins =len(newbins)-1
        xedge = array("d",newbins)
        print "Binning in variable %s is "%xvarname
        print newbins
        histoData = self.setPoissonErrors(rt.TH1D("histoData", "histoData",newNbins, xedge))
        histoDataLep = self.setPoissonErrors(rt.TH1D("histoDataLep", "histoDataLep",newNbins, xedge))
        histoToy = self.setPoissonErrors(rt.TH1D("histoToy", "histoToy",newNbins, xedge))
        histoToyTTj = self.setPoissonErrors(rt.TH1D("histoToyTTj", "histoToyTTj",newNbins, xedge))
        histoToyQCD = self.setPoissonErrors(rt.TH1D("histoToyQCD", "histoToyQCD",newNbins, xedge))

        def setName(h, name):
            h.SetName('%s_%s_%s_ALLCOMPONENTS' % (h.GetName(),name,'_'.join(ranges)) )
            h.GetXaxis().SetTitle(name)
        
        def SetErrors(histo, nbins):
            for i in range(1, nbins+1):
                histo.SetBinError(i,rt.TMath.Sqrt(histo.GetBinContent(i)))

        # project the data on the histograms
        data.fillHistogram(histoData,rt.RooArgList(self.workspace.var(xvarname)))
        dataLep.fillHistogram(histoDataLep,rt.RooArgList(self.workspace.var(xvarname)))
        toyData.fillHistogram(histoToy,rt.RooArgList(self.workspace.var(xvarname)))
        data.fillHistogram(histoData2011,rt.RooArgList(self.workspace.var(xvarname)))
        dataLep.fillHistogram(histoDataLep2011,rt.RooArgList(self.workspace.var(xvarname)))
        toyData.fillHistogram(histoToy2011,rt.RooArgList(self.workspace.var(xvarname)))
        
        #Cache the numbers
        Ntt = self.workspace.var("Ntot_TTj").getVal()
        Nqcd = 0
        try : 
            Nqcd = self.workspace.var("Ntot_QCD").getVal()
        except TypeError :
            print 'no 2nd component requested, setting Nqcd to 0'
            Nqcd = 0
        
        #Generate the TTj component
        if Nqcd > 0 :
            self.workspace.var("Ntot_QCD").setVal(0.)
        toyDataTTj = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(factor*(data.numEntries()-Nqcd)))
        toyDataTTj.fillHistogram(histoToyTTj,rt.RooArgList(self.workspace.var(xvarname)))
        toyDataTTj.fillHistogram(histoToyTTj2011,rt.RooArgList(self.workspace.var(xvarname)))
        histoToyTTj.SetLineColor(rt.kRed)
        histoToyTTj.SetLineWidth(2)
        histoToyTTj2011.SetLineColor(rt.kRed)
        histoToyTTj2011.SetLineWidth(2)
        if Nqcd > 0 :
            self.workspace.var("Ntot_QCD").setVal(Nqcd)

        #Generate the QCD component
        if Nqcd > 1. :
            self.workspace.var("Ntot_TTj").setVal(0.)
            toyDataQCD = self.workspace.pdf(self.fitmodel).generate(self.workspace.set('variables'), int(factor*(data.numEntries()-Ntt)))
            toyDataQCD.fillHistogram(histoToyQCD,rt.RooArgList(self.workspace.var(xvarname)))
            toyDataQCD.fillHistogram(histoToyQCD2011,rt.RooArgList(self.workspace.var(xvarname)))
            histoToyQCD.SetLineColor(rt.kGreen)
            histoToyQCD.SetLineWidth(2)
            histoToyQCD2011.SetLineColor(rt.kGreen)
            histoToyQCD2011.SetLineWidth(2)
            self.workspace.var("Ntot_TTj").setVal(Ntt)     
        

        #put some protection in for divide by zero
        scaleFactor = 1.0
        if abs(histoToy.Integral()-0.0) > 1e-8:
            scaleFactor = histoData.Integral()/histoToy.Integral()

        histoToy.Scale(scaleFactor)
        histoToyTTj.Scale(scaleFactor)
        SetErrors(histoToy, newNbins)
        SetErrors(histoToyTTj, newNbins)
        setName(histoData,xvarname)
        setName(histoDataLep,xvarname)
        setName(histoToy,xvarname)
        setName(histoToyTTj,xvarname)
        if Nqcd > 0 :
            histoToyQCD.Scale(scaleFactor)
            SetErrors(histoToyQCD, newNbins)
            setName(histoToyQCD,xvarname)
        histoData.SetMarkerStyle(20)
        histoDataLep.SetLineWidth(2)
        histoDataLep.SetLineStyle(rt.kDashed)
        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        histoToy2011.Scale(scaleFactor)
        histoToyTTj2011.Scale(scaleFactor)
        SetErrors(histoToy2011, nbins)
        SetErrors(histoToyTTj2011, nbins)
        setName(histoData2011,xvarname)
        setName(histoDataLep2011,xvarname)
        setName(histoToy2011,xvarname)
        setName(histoToyTTj2011,xvarname)
        if Nqcd > 0 :
            histoToyQCD2011.Scale(scaleFactor)
            SetErrors(histoToyQCD2011, newNbins)
            setName(histoToyQCD2011,xvarname)
        histoData2011.SetMarkerStyle(20)
        histoDataLep2011.SetLineWidth(2)
        histoDataLep2011.SetLineStyle(rt.kDashed)
        histoToy2011.SetLineColor(rt.kBlue)
        histoToy2011.SetLineWidth(2)

        c = rt.TCanvas()
        c.SetName('DataMC_%s_%s_ALLCOMPONENTS' % (xvarname,'_'.join(ranges)) )
        histoData.Draw("pe")
        histoDataLep.Draw("histsame")
        histoToyTTj.DrawCopy('histsame')
        histoToyTTj.SetFillColor(rt.kRed)
        histoToyTTj.SetFillStyle(3018)
        histoToyTTj.Draw('e2same')
        if Nqcd > 0:
            histoToyQCD.DrawCopy('histsame')
            histoToyQCD.SetFillColor(rt.kGreen)
            histoToyQCD.SetFillStyle(3018)
            histoToyQCD.Draw('e2same')  
        histoToy.DrawCopy('histsame')
        histoToy.SetFillColor(rt.kBlue)
        histoToy.SetFillStyle(3018)
        histoToy.Draw('e2same')


        c2011 = rt.TCanvas()
        c2011.SetName('DataMC_%s_%s_ALLCOMPONENTS2011' % (xvarname,'_'.join(ranges)) )
        histoData2011.Draw("pe")        
        histoDataLep2011.Draw("histsame")
        histoToyTTj2011.DrawCopy('histsame')
        histoToyTTj2011.SetFillColor(rt.kRed)
        histoToyTTj2011.SetFillStyle(3018)
        histoToyTTj2011.Draw('e2same')
        if Nqcd > 0 :
            histoToyQCD2011.DrawCopy('histsame')
            histoToyQCD2011.SetFillColor(rt.kGreen)
            histoToyQCD2011.SetFillStyle(3018)
            histoToyQCD2011.Draw('e2same')  
        histoToy2011.DrawCopy('histsame')
        histoToy2011.SetFillColor(rt.kBlue)
        histoToy2011.SetFillStyle(3018)
        histoToy2011.Draw('e2same')

        histToReturn = [histoToy, histoToyTTj, histoData, histoDataLep, c, histoToy2011, histoToyTTj2011, histoData2011, histoDataLep2011, c2011]
        if Nqcd > 0:
            histToReturn.extend([histoToyQCD, histoToyQCD2011])
        return histToReturn

    # to be removed eventually
    def plot(self, inputFile, store, box):
        store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=['FULL']), dir=box)
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=['FULL'])]
        [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 80, ranges=['FULL'])]
#        for r in ['FULL']:
#            store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=[r]), dir=box)
#            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=[r])]
#            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 80, ranges=[r])]
