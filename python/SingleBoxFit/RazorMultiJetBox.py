from RazorCombinedFit.Framework import Box
import math
import RootTools
import RazorBox
import ROOT as rt
from array import *
import sys

# This is global, to be used also in the scripts for plots
def Binning(boxName, varName):
    if varName == "MR" :
        if boxName.find("BJet")!=-1:
            return [500.0, 550.0, 650.0, 790.0, 1000, 1500, 2200, 3000, 4000.0]
        else:
            return [350.0, 400.0, 450.0, 500.0, 550.0, 650.0, 790.0, 1000, 1500, 2200, 3000, 4000.0]
            
    if varName == "Rsq": 
        if boxName.find("BJet")!=-1:
            return [0.05, 0.07, 0.12, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
        else:
            return [0.05, 0.07, 0.12, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
    if varName == "Btag": return [1.,5.]

def FindLastBin(h):
    for i in range(1,h.GetXaxis().GetNbins()):
        thisbin = h.GetXaxis().GetNbins()-i
        if h.GetBinContent(thisbin)>=0.1: return thisbin+1
    return h.GetXaxis().GetNbins()   

class RazorMultiJetBox(RazorBox.RazorBox):
    
    def __init__(self, name, variables, twoComponents = False, fitregion = ""):
        super(RazorMultiJetBox,self).__init__(name, variables)
        
        self.zeros = {'TTj':[] , 'QCD':['Mu','Ele','CRMuBVeto','CREleBVeto']}
        self.cut = 'MR >= 0.0'
        if fitregion =="FULL":
            self.fitregion = "FULL"
        else:
            self.fitregion = "fR1,fR2,fR3,fR4,fR5"
            print 'Using the fit range: %s' % self.fitregion

    def floatSomething(self, z, fitmodel = None, modeltype = "fitmodel"):
        """Switch on or off whatever you want here"""
        # the "effective" first component in the Had box
        self.float1stComponentWithPenalty(z, True, fitmodel, modeltype)
        self.float2ndComponentWithPenalty(z, True, fitmodel, modeltype)
        self.floatYield(z)
        if z!= "QCD": self.floatFraction(z)
        
        # we put the n parameter but fix it
        self.fixParsExact("n2nd_%s" % z, True)


    def define(self, inputFile, twoComponentOnly = False):
        
        #define the ranges
        mR  = self.workspace.var("MR")
        Rsq = self.workspace.var("Rsq")

        # add the different components:
        self.addTailPdf("QCD",False)
        self.addTailPdf("TTj",True)

        # build the total PDF
        myPDFlist = rt.RooArgList()
        for z in self.zeros:
            if self.name not in self.zeros[z]:
                myPDFlist.add(self.workspace.pdf("ePDF1st_%s"%z))
                if z!="QCD":
                    myPDFlist.add(self.workspace.pdf("ePDF2nd_%s"%z))
                    
            
        model = rt.RooAddPdf(self.fitmodel, self.fitmodel, myPDFlist)
        
        # import the model in the workspace.
        self.importToWS(model)
        #print the workspace
        self.workspace.Print()

        #fix all pdf parameters to the initial value
        self.fixPars("QCD")
        self.fixPars("TTj")

        fixed = []
        for z in self.zeros:
            if self.name in self.zeros[z]:
                self.fixPars(z)
                self.switchOff(z)
            else:
                if not z in fixed:
                    self.floatSomething(z)
                    fixed.append(z)

        
        newProdList = rt.RooArgList()
        newProdList.add(self.workspace.pdf('%s' % ("fitmodel")))
        for z in self.zeros:
            if self.name not in self.zeros[z]:
                newProdList.add(self.workspace.pdf("R01st_%s_penalty"%z))
                newProdList.add(self.workspace.pdf("MR01st_%s_penalty"%z))
                newProdList.add(self.workspace.pdf("b1st_%s_penalty"%z))
                if z!="QCD":
                    newProdList.add(self.workspace.pdf("R02nd_%s_penalty"%z))
                    newProdList.add(self.workspace.pdf("MR02nd_%s_penalty"%z))
                    newProdList.add(self.workspace.pdf("b2nd_%s_penalty"%z))

        
        #remove redundant second components
        self.fix2ndComponent("QCD")
        self.workspace.var("f2_QCD").setVal(0.)
        self.workspace.var("f2_QCD").setConstant(rt.kTRUE)


        newProd = rt.RooProdPdf("%s_newProd"%"fitmodel",'BG PDF with new product of penalties', newProdList)
        self.importToWS(newProd)
        self.fitmodel = newProd.GetName()

    
    def addSignalModel(self, inputFile, signalXsec, modelName = None):
        
        if modelName is None:
            modelName = 'Signal'
        
        # signalModel is the 2D pdf [normalized to one]
        # nSig is the integral of the histogram given as input
        signalModel, nSig = self.makeRooRazor2DSignal(inputFile,modelName)
        
        # compute the expected yield/(pb-1)
        self.workspace.var('sigma').setVal(signalXsec)
 
        #set the MC efficiency relative to the number of events generated
        # compute the signal yield multiplying by the efficiency
        self.workspace.factory("expr::Ntot_%s('@0*@1*@2*@3',sigma, lumi, eff, eff_value_%s)" %(modelName,self.name))
        extended = self.workspace.factory("RooExtendPdf::eBinPDF_%s(%s, Ntot_%s)" % (modelName,signalModel,modelName))
 
        theRealFitModel = "fitmodel"
        
        SpBPdfList = rt.RooArgList(self.workspace.pdf("ePDF1st_TTj"))
        # prevent nan when there is no signal expected
        if self.workspace.function("Ntot_%s"%modelName).getVal() > 0: SpBPdfList.add(self.workspace.pdf("eBinPDF_Signal"))
        if self.workspace.function("N_2nd_TTj").getVal() > 0: SpBPdfList.add(self.workspace.pdf("ePDF2nd_TTj"))
        if self.workspace.function("N_1st_QCD").getVal() > 0: SpBPdfList.add(self.workspace.pdf("ePDF1st_QCD"))
        if self.workspace.function("N_2nd_QCD").getVal() > 0: SpBPdfList.add(self.workspace.pdf("ePDF2nd_QCD"))
                

        add = rt.RooAddPdf('%s_%sCombined' % (theRealFitModel,modelName),'Signal+BG PDF',
                           SpBPdfList)
        self.importToWS(add)
        self.signalmodel = add.GetName()

        fixed = []
        for z in self.zeros:
            if self.name in self.zeros[z]:
                self.fixPars(z)
                self.switchOff(z)
            else:
                if not z in fixed:
                    self.floatSomething(z,None,"signalmodel")
                    fixed.append(z)

        newProdList = rt.RooArgList()
        newProdList.add(self.workspace.pdf('%s_%sCombined' % (theRealFitModel,modelName)))
        for z in self.zeros:
            if self.name not in self.zeros[z]:
                newProdList.add(self.workspace.pdf("R01st_%s_penalty"%z))
                newProdList.add(self.workspace.pdf("MR01st_%s_penalty"%z))
                newProdList.add(self.workspace.pdf("b1st_%s_penalty"%z))
                if z != "QCD":
                    newProdList.add(self.workspace.pdf("R02nd_%s_penalty"%z))
                    newProdList.add(self.workspace.pdf("MR02nd_%s_penalty"%z))
                    newProdList.add(self.workspace.pdf("b2nd_%s_penalty"%z))

        newProd = rt.RooProdPdf("%s_%sCombined_newProd" % (theRealFitModel,modelName),'Signal+BG PDF with new product of penalties', newProdList)
        self.importToWS(newProd)
        self.signalmodel = newProd.GetName()
        return newProd.GetName()
        #return extended.GetName()

    
    def plot1DHistoAllComponents(self, inputFile, xvarname, nbins = 25, ranges=None, data = None, fitmodel=None):
        
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
    def plot(self, inputFile, store, box, data=None, fitmodel=None):
        store.store(self.plot2D(inputFile, "MR", "Rsq", ranges=[self.fitregion]), dir=box)
        if data == None :
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "MR", 80, ranges=[self.fitregion], data=data, fitmodel=fitmodel)]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponents(inputFile, "Rsq", 80, ranges=[self.fitregion], data=data, fitmodel=fitmodel)]
        else :
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponentsWithSignal(inputFile, "MR", 80, ranges=[self.fitregion], data=data, fitmodel=fitmodel)]
            [store.store(s, dir=box) for s in self.plot1DHistoAllComponentsWithSignal(inputFile, "Rsq", 80, ranges=[self.fitregion], data=data, fitmodel=fitmodel)]

    def plot1DHistoAllComponentsWithSignal(self, inputFile, varname, nbins = 25, ranges=None, data=None, fitmodel=None):
        Preliminary = "Preliminary"
        #Preliminary = "Simulation"
        Energy = 8.0
        rangeNone = False
        if ranges is None:
            rangeNone = True
            ranges = ['']
            
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        print ''
        print 'rangeCut', rangeCut
        print ''

        if data is None:
            data = RootTools.getDataSet(inputFile,'RMRTree', self.cut)
            data = data.reduce(rangeCut)
        data = data.reduce(self.cut)
        data = data.reduce(rangeCut)
            
        # save original event yields
        if self.workspace.var("Ntot_TTj") != None:
            N_TTj = self.workspace.var("Ntot_TTj").getVal()
        if self.workspace.var("Ntot_QCD") != None:
            N_QCD = self.workspace.var("Ntot_QCD").getVal()
        if self.workspace.function("Ntot_Signal") != None:
            N_Signal = self.workspace.function("Ntot_Signal").getVal()
        else: N_Signal = 0.

        self.workspace.pdf(self.signalmodel).Print("V")
        bins = Binning(self.name, varname)
        
        nbins =len(bins)-1
        xedge = array("d",bins)
        print "Binning in variable %s is "%varname
        print bins
        
        # Generate a sample of signal
        effCutSignal = 1
        self.workspace.var("Ntot_TTj").setVal(0.)
        self.workspace.var("Ntot_QCD").setVal(0.)
        if N_Signal>1:
            toyDataSignal = self.workspace.pdf(self.signalmodel).generate(self.workspace.set('variables'), int(50*(N_Signal)))
            histoToySignal = rt.TH1D("histoToySignal", "histoToySignal",len(bins)-1, xedge)
            toyDataSignal.fillHistogram(histoToySignal,rt.RooArgList(self.workspace.var(varname)))
            beforeCutSignal = float(toyDataSignal.sumEntries())
            toyDataSignal = toyDataSignal.reduce(rangeCut)
            afterCutSignal = float(toyDataSignal.sumEntries())
            effCutSignal = afterCutSignal / beforeCutSignal
            print effCutSignal
            
        # Generate a sample of TTj
        effCutTTj1b = 1
        self.workspace.var("Ntot_QCD").setVal(0.)
        self.workspace.var("Ntot_TTj").setVal(N_TTj)
        if N_TTj>1 :
            toyDataTTj = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(50*(N_TTj)))
            beforeCutTTj = float(toyDataTTj.sumEntries())
            toyDataTTj = toyDataTTj.reduce(rangeCut)
            afterCutTTj = float(toyDataTTj.sumEntries())
            effCutTTj = afterCutTTj / beforeCutTTj
                        
        # Generate a sample of QCD
        print "f2_QCD = %f"%self.workspace.var("f2_QCD").getVal()
        effCutQCD = 1
        self.workspace.var("Ntot_TTj").setVal(0.)
        self.workspace.var("Ntot_QCD").setVal(N_QCD)
        if N_QCD>1 :
            toyDataQCD = self.workspace.pdf(fitmodel).generate(self.workspace.set('variables'), int(50*(N_QCD)))
            beforeCutQCD = float(toyDataQCD.sumEntries())
            toyDataQCD = toyDataQCD.reduce(rangeCut)
            afterCutQCD = float(toyDataQCD.sumEntries())
            effCutQCD = afterCutQCD / beforeCutQCD
            
        # set the event yields back to their original values
        # NOTE: these original values REFER TO THE FULL RANGE OF VARIABLES MR and Rsq and nBtag!
        print "EFFICIENCIES for this rangeCut"
        print "TTj %f"%effCutTTj
        print "QCD %f"%effCutQCD
        self.workspace.var("Ntot_QCD").setVal(N_QCD)
        self.workspace.var("Ntot_TTj").setVal(N_TTj)
      

        xmin = min([self.workspace.var(varname).getMin(r) for r in ranges])
        xmax = max([self.workspace.var(varname).getMax(r) for r in ranges])

        # variable binning for plots
        bins = Binning(self.name, varname)
        
        nbins =len(bins)-1
        xedge = array("d",bins)
        print "Binning in variable %s is "%varname
        print bins
        
        # define 1D histograms
        histoData = self.setPoissonErrors(rt.TH1D("histoData", "histoData",len(bins)-1, xedge))
        histoToy = self.setPoissonErrors(rt.TH1D("histoToy", "histoToy",len(bins)-1, xedge))
        histoToySignal = self.setPoissonErrors(rt.TH1D("histoToySignal", "histoToySignal",len(bins)-1, xedge))
        histoToyTTj = self.setPoissonErrors(rt.TH1D("histoToyTTj", "histoToyTTj",len(bins)-1, xedge))
        histoToyQCD = self.setPoissonErrors(rt.TH1D("histoToyQCD", "histoToyQCD",len(bins)-1, xedge))

        def setName(h, name):
            h.SetName('%s_%s_%s_ALLCOMPONENTS' % (h.GetName(),name,'_'.join(ranges)) )
            # axis labels
            h.GetXaxis().SetTitleSize(0.05)
            h.GetYaxis().SetTitleSize(0.05)
            h.GetXaxis().SetLabelSize(0.05)
            h.GetYaxis().SetLabelSize(0.05)
            h.GetXaxis().SetTitleOffset(0.90)
            h.GetYaxis().SetTitleOffset(0.93)
        
            # x axis
            if name == "MR": h.GetXaxis().SetTitle("M_{R} [GeV]")
            elif name == "Rsq": h.GetXaxis().SetTitle("R^{2}")
                 
            # y axis
            if name == "MR": h.GetYaxis().SetTitle("Events/(%i GeV)" %h.GetXaxis().GetBinWidth(1))
            elif name == "Rsq": h.GetYaxis().SetTitle("Events/(%4.3f)" %h.GetXaxis().GetBinWidth(1))
         
        def SetErrors(histo):
            for i in range(1, histo.GetNbinsX()+1):
                histo.SetBinError(i,max(rt.TMath.Sqrt(histo.GetBinContent(i)), 1))

        # project the data on the histograms
        data.fillHistogram(histoData,rt.RooArgList(self.workspace.var(varname)))
        print varname
        self.workspace.var(varname).Print()
        
        if N_Signal>1: toyDataSignal.fillHistogram(histoToySignal,rt.RooArgList(self.workspace.var(varname)))
        if N_TTj>1 :toyDataTTj.fillHistogram(histoToyTTj,rt.RooArgList(self.workspace.var(varname)))
        if N_QCD>1 : toyDataQCD.fillHistogram(histoToyQCD,rt.RooArgList(self.workspace.var(varname)))
        # make the total
        if self.workspace.var("Ntot_TTj") != None and N_TTj>1 :histoToy.Add(histoToyTTj, +1)
        if self.workspace.var("Ntot_QCD") != None and N_QCD>1: histoToy.Add(histoToyQCD, +1)
            
        # We shouldn't scale to the data, we should scale to our prediction
        #scaleFactor = histoData.Integral()/histoToy.Integral()
        print "DATA NORM %f"%histoData.Integral()
        print "FIT NORM  %f"%(N_QCD*effCutQCD+N_TTj*effCutTTj)
        scaleFactor = (N_QCD*effCutQCD+N_TTj*effCutTTj)/histoToy.Integral()
        print "scaleFactor = %f"%scaleFactor
        
        histoToySignal.Scale(0.02)
        histoToyQCD.Scale(0.02)
        histoToyTTj.Scale(0.02)
        SetErrors(histoToyQCD)
        SetErrors(histoToyTTj)
        setName(histoToyQCD,varname)
        setName(histoToyTTj,varname)
        histoToyTTj.SetLineColor(rt.kViolet)
        histoToyTTj.SetLineWidth(2)
        histoToyQCD.SetLineColor(rt.kRed)
        histoToyQCD.SetLineWidth(2)
     
        histoToy.Scale(0.02)
        SetErrors(histoToy)
        setName(histoData,varname)
        setName(histoToy,varname)
        setName(histoToySignal,varname)
        histoData.SetMarkerStyle(20)
        histoData.SetLineWidth(2)
        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        rt.gStyle.SetOptStat(0000)
        rt.gStyle.SetOptTitle(0)

        showQCD = (N_QCD>0)
        showTTj = (N_TTj>0)
        showSignal = (N_Signal>0)


        # legend
        if showQCD and showTTj  and showSignal:
            leg = rt.TLegend(0.7,0.45,0.93,0.93)
        elif showQCD and showTTj :
            leg = rt.TLegend(0.7,0.55,0.93,0.93)
        elif showQCD and showTTj and showSignal:
            leg = rt.TLegend(0.7,0.55,0.93,0.93)
        else:
            leg = rt.TLegend(0.7,0.72,0.93,0.93)
        leg.SetFillColor(0)
        leg.SetTextFont(42)
        leg.SetLineColor(0)


        leg.AddEntry(histoData,"Data","lep")
        leg.AddEntry(histoToy,"Total Bkgd","lf")
        if showTTj:
            leg.AddEntry(histoToyTTj,"TTj","l")
        if showQCD:
            leg.AddEntry(histoToyQCD,"QCD","l")
        if showSignal:
            leg.AddEntry(histoToySignal,"Signal","lf")
        
        leg.Draw()

        # plot labels
        #pt = rt.TPaveText(0.4,0.8,0.5,0.93,"ndc")
        pt = rt.TPaveText(0.25,0.67,0.7,0.93,"ndc")
        pt.SetBorderSize(0)
        pt.SetTextSize(0.05)
        pt.SetFillColor(0)
        pt.SetFillStyle(0)
        pt.SetLineColor(0)
        pt.SetTextAlign(21)
        pt.SetTextFont(42)
        pt.SetTextSize(0.062)
        text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
        Lumi = 19.3
        text = pt.AddText("Razor %s Box #int L = %3.1f fb^{-1}" %(self.name,Lumi))
    
        c = rt.TCanvas("c","c",500,400)
        pad1 = rt.TPad("pad1","pad1",0,0.25,1,1)
        pad2 = rt.TPad("pad2","pad2",0,0,1,0.25)
        
        pad1.Range(-213.4588,-0.3237935,4222.803,5.412602);
        pad2.Range(-213.4588,-2.206896,4222.803,3.241379);

        pad1.SetLeftMargin(0.15)
        pad2.SetLeftMargin(0.15)
        pad1.SetRightMargin(0.05)
        pad2.SetRightMargin(0.05)
        pad1.SetTopMargin(0.05)
        pad2.SetTopMargin(0.)
        pad1.SetBottomMargin(0.)
        pad2.SetBottomMargin(0.47)
    
        #pad1.SetBottomMargin(0)
        pad1.Draw()
        pad1.cd()
        rt.gPad.SetLogy()
        c.SetName('DataMC_%s_%s_ALLCOMPONENTS' % (varname,'_'.join(ranges)) )
        
        histoToy.SetMinimum(0.5)
        histoToy.GetYaxis().SetTitleSize(0.08)
        histoToy.GetYaxis().SetTitle("Events")
        histoToy.GetXaxis().SetTitle("")
        histoToy.GetXaxis().SetLabelOffset(0.16)
        histoToy.GetXaxis().SetLabelSize(0.06)
        histoToy.GetYaxis().SetLabelSize(0.06)
        histoToy.GetXaxis().SetTitleSize(0.06)
        histoToy.GetYaxis().SetTitleSize(0.08)
        histoToy.GetXaxis().SetTitleOffset(1)
        #if varname == "MR": histoToy.SetMaximum(histoToy.GetMaximum()*2.)
        #elif varname == "Rsq": histoToy.SetMaximum(histoToy.GetMaximum()*2.)
        #elif varname == "nBtag": histoToy.SetMaximum(histoToy.GetMaximum()*5.)
        if varname == "MR":
            histoToy.SetMaximum(5.e4)
            histoToy.SetMinimum(0.5)
        elif varname == "Rsq":
            histoToy.SetMaximum(5.e4)
            histoToy.SetMinimum(0.5)
        histoData.GetXaxis().SetRange(1,FindLastBin(histoData))
        histoToy.GetXaxis().SetRange(1,FindLastBin(histoData))
        #if histoToy.GetBinContent(histoToy.GetNbinsX())>=15.: histoToy.SetMinimum(15.)
        #if histoToy.GetBinContent(histoToy.GetNbinsX())>=50.: histoToy.SetMinimum(50.)
            
            
        
        histoToy.SetFillColor(rt.kBlue-10)
        histoToy.SetFillStyle(1001)
        histoData.SetLineColor(rt.kBlack)
        histoData.Draw("pe")
        histoToy.DrawCopy('e2')
        histoData.Draw("pesame")
        leg.Draw("same")
        pt.Draw("same")

        histoToy.SetLineColor(rt.kBlue)
        histoToy.SetLineWidth(2)

        
        if self.workspace.var("Ntot_TTj").getVal():
            histoToyTTj.DrawCopy("histsame")
            c2 = rt.gROOT.GetColor(rt.kViolet-4)
            c2.SetAlpha(1.0)
            histoToyTTj.SetFillStyle(0)
            histoToyTTj.DrawCopy('histsame')
        if self.workspace.var("Ntot_QCD").getVal():
            histoToyQCD.DrawCopy('histsame')
            c3 = rt.gROOT.GetColor(rt.kRed-4)
            c3.SetAlpha(1.0)
            histoToyQCD.SetFillStyle(0)
            histoToyQCD.DrawCopy('histsame')
        # total
        histoToyCOPY = histoToy.Clone("histoToyCOPY")
        histoToyCOPY.SetFillStyle(0)
        histoToyCOPY.Draw('histsame')
        histoData.Draw("pesame")

        if N_Signal>0:
            c4 = rt.gROOT.GetColor(rt.kGray+2)
            c4.SetAlpha(1.0)
            histoToySignal.SetLineColor(rt.kBlack)
            histoToySignal.SetFillColor(rt.kGray+2)
            histoToySignal.SetLineStyle(2)
            histoToySignal.SetFillStyle(3005)
            histoToySignal.SetLineWidth(2)
            histoToySignal.Draw("histfsame")
            

        c.Update()
    
        c.cd()
        
        pad2.Draw()
        pad2.cd()
        rt.gPad.SetLogy(0)
        histoData.Sumw2()
        histoToyCOPY.Sumw2()
        hMRDataDivide = histoData.Clone(histoData.GetName()+"Divide")
        hMRDataDivide.Sumw2()

        hMRTOTclone = histoToyCOPY.Clone(histoToyCOPY.GetName()+"Divide") 
        hMRTOTcopyclone = histoToy.Clone(histoToyCOPY.GetName()+"Divide") 
        hMRTOTcopyclone.GetYaxis().SetLabelSize(0.18)
        hMRTOTcopyclone.SetTitle("")
        hMRTOTcopyclone.SetMaximum(3.5)
        hMRTOTcopyclone.SetMinimum(0.)
        hMRTOTcopyclone.GetXaxis().SetLabelSize(0.22)
        hMRTOTcopyclone.GetXaxis().SetTitleSize(0.22)
 
        for i in range(1, histoData.GetNbinsX()+1):
            tmpVal = hMRTOTcopyclone.GetBinContent(i)
            if tmpVal != -0.:
                hMRDataDivide.SetBinContent(i, hMRDataDivide.GetBinContent(i)/tmpVal)
                hMRDataDivide.SetBinError(i, hMRDataDivide.GetBinError(i)/tmpVal)
                hMRTOTcopyclone.SetBinContent(i, hMRTOTcopyclone.GetBinContent(i)/tmpVal)
                hMRTOTcopyclone.SetBinError(i, hMRTOTcopyclone.GetBinError(i)/tmpVal)
                hMRTOTclone.SetBinContent(i, hMRTOTclone.GetBinContent(i)/tmpVal)
                hMRTOTclone.SetBinError(i, hMRTOTclone.GetBinError(i)/tmpVal)

        hMRTOTcopyclone.GetXaxis().SetTitleOffset(0.97)
        hMRTOTcopyclone.GetXaxis().SetLabelOffset(0.02)
        if varname == "MR":
            hMRTOTcopyclone.GetXaxis().SetTitle("M_{R} [GeV]")
        if varname == "RSQ":
            hMRTOTcopyclone.GetXaxis().SetTitle("R^{2}")
     
        hMRTOTcopyclone.GetYaxis().SetNdivisions(504,rt.kTRUE)
        hMRTOTcopyclone.GetYaxis().SetTitleOffset(0.2)
        hMRTOTcopyclone.GetYaxis().SetTitleSize(0.22)
        hMRTOTcopyclone.GetYaxis().SetTitle("Data/Bkgd")
        hMRTOTcopyclone.GetXaxis().SetTicks("+")
        hMRTOTcopyclone.GetXaxis().SetTickLength(0.07)
        hMRTOTcopyclone.SetMarkerColor(rt.kBlue-10)
        hMRTOTcopyclone.Draw("e2")
        hMRDataDivide.Draw('pesame')
        hMRTOTcopyclone.Draw("axissame")

        pad2.Update()
        pad1.cd()
        pad1.Update()
        pad1.Draw()
        c.cd()
        
        histToReturn = [histoToy, histoData, c]
        histToReturn.append(histoToyTTj)
        histToReturn.append(histoToyQCD)
        histToReturn.append(histoToySignal)

        
       ##  fitLabel = '_'.join(self.fitregion.split(","))
        if self.fitregion == "FULL":
            fitLabel = "FULL"
        else :
            fitLabel = 'Sideband'
        c.Print("razor_canvas_%s_%s_%s_0p0.pdf"%(self.name,fitLabel, varname))
        
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"c\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad1\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad2\");")
        return histToReturn

   
    
