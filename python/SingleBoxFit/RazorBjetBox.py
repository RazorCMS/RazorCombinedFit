from RazorCombinedFit.Framework import Box
import RootTools
import RazorBox
import ROOT as rt

class RazorBjetBox(RazorBox.RazorBox):
    
    def __init__(self, name, variables):
        super(RazorBjetBox,self).__init__(name, variables)
        
        # now we switch off the redundant Znn component in the Had box
        self.zeros = {'TTj':[],'Wln':['Mu','MuMu','EleEle','MuEle'],'Zll':['Had','Ele','Mu','MuMu','EleEle','MuEle'],'Znn':['Had','Ele','MuMu','EleEle','MuEle']}

        self.cut = 'MR >= 0.0'

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
