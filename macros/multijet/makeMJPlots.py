import ROOT as rt
import RootTools

class PlotMR(object):
    def __init__(self):
        self.var = 'MR'
        self.xaxis = 'M_{R} [GeV]'
    def setBinning(self, name, title):       
        h = rt.TH1D(name,title,25,500,3000)
        h.GetXaxis().SetTitle(self.xaxis)
        return h

class PlotRsq(object):
    def __init__(self):
        self.var = 'Rsq'
        self.xaxis = 'R^{2}'
    def setBinning(self, name, title):       
        h = rt.TH1D(name,title,9,0.05,0.5)
        h.GetXaxis().SetTitle(self.xaxis)
        return h  

class PlotBDT(object):
    def __init__(self):
        self.var = 'BDT'
        self.xaxis = 'BDT'
    def setBinning(self, name, title):       
        h = rt.TH1D(name,title,20,-1.,+1.)
        h.GetXaxis().SetTitle(self.xaxis)
        return h 
    
class PlotCHMultN(object):
    def __init__(self, N):
        self.var = 'CHMult%d' % N
        self.xaxis = 'CHMult%d' % N
    def setBinning(self, name, title):       
        h = rt.TH1D(name,title,20,0,200)
        h.GetXaxis().SetTitle(self.xaxis)
        return h     

class PlotGirthN(object):
    def __init__(self, N):
        self.var = 'Girth%d' % N
        self.xaxis = 'Girth%d' % N
    def setBinning(self, name, title):       
        h = rt.TH1D(name,title,10,0,0.5)
        h.GetXaxis().SetTitle(self.xaxis)
        return h 
    
class PlotTopMassN(object):
    def __init__(self, N):
        self.var = 'TopMass%d' % N
        self.xaxis = 'TopMass%d' % N
    def setBinning(self, name, title):       
        h = rt.TH1D(name,title,60,0,600)
        h.GetXaxis().SetTitle(self.xaxis)
        return h 

class PlotWMassN(object):
    def __init__(self, N):
        self.var = 'WMass%d' % N
        self.xaxis = 'WMass%d' % N
    def setBinning(self, name, title):       
        h = rt.TH1D(name,title,20,0,200)
        h.GetXaxis().SetTitle(self.xaxis)
        return h     

class PlotThetaHN(object):
    def __init__(self, N):
        self.var = 'ThetaH%d' % N
        self.xaxis = 'ThetaH%d' % N
    def setBinning(self, name, title):       
        h = rt.TH1D(name,title,20,-1,1)
        h.GetXaxis().SetTitle(self.xaxis)
        return h 
    
class PlotCount(object):
    
    def setBinning(self, name, title):
        pass
    
    def __init__(self, store, var, count_var, ranges):
        self.store = store
        self.var = var
        self.count_var = count_var
        
        self.ranges = ranges
        
        colors = RootTools.RazorStyle.getColorList()
        color_index = 0
        self.max_count = 0
        
        self.histograms = {}
        for r in self.ranges:
            name = '%s_%i_%i_%s' % (self.count_var,r[0],r[1],self.var)
            h = self.setBinning(name,name)
            h.SetLineColor(colors[color_index])
            h.SetMarkerColor(colors[color_index])
            self.histograms[r] = h
            color_index += 1
            
    def fill(self,row):
        
        val = row[self.var].getVal()
        count = row[self.count_var].getVal()
        
        if count > self.max_count:
            self.max_count = count
        
        for range, histogram in self.histograms.iteritems():
            if count < range[0] or count > range[1]: continue
            histogram.Fill(val)
    
    def rangeLabel(self, range):
        return '[%i-%i]' % range
            
    def final(self):
        
        dir='%s_%s' % (self.count_var,self.var)
        inc = self.histograms[self.ranges[0]]
        
        canvas = rt.TCanvas('%s_%s' % (self.count_var,self.var),'%s_%s' % (self.count_var,self.var),640,800)
        rt.gStyle.SetOptTitle(0)
        canvas.Draw()
        
        pad1 = rt.TPad("pad1","pad1",0.0,0.15,1.,1.)
        pad1.Draw();        
        pad1.SetLogy()
        pad1.cd()
        pad1.SetGridx()
        pad1.SetGridy()

        leg = rt.TLegend(0.50, 0.5, 0.9, 0.9)
        leg.SetTextSize(0.03)
        leg.SetLineColor(rt.kWhite)
        leg.SetFillColor(rt.kWhite)
        leg.SetShadowColor(rt.kWhite)
        
        option = ''
        for range in self.ranges:
            histo = self.histograms[range]
            self.store.add(histo,dir=dir)
            histo.Draw(option)
            
            histo.GetXaxis().SetTitle(self.xaxis)
            histo.GetYaxis().SetTitle('Entries')
            histo.GetXaxis().SetTitleFont(132)
            histo.GetYaxis().SetTitleFont(132)
            histo.GetXaxis().SetTitleSize(0.06)
            histo.GetYaxis().SetTitleSize(0.06)
            histo.GetXaxis().SetLabelFont(132)
            histo.GetYaxis().SetLabelFont(132)
            histo.GetXaxis().SetLabelSize(0.05)
            histo.GetYaxis().SetLabelSize(0.05)
            histo.GetXaxis().CenterTitle()
            histo.GetYaxis().CenterTitle()
            histo.GetYaxis().SetTitleOffset(1.3)
            histo.GetXaxis().SetTitleOffset(1.)
            histo.Draw(option)
            
            if histo is not inc:
                leg.AddEntry(histo,self.rangeLabel(range))
            else:
                leg.AddEntry(histo,'[Incl.]')
            
            if not option:
                option = 'same'
                
        leg.Draw()
        
        pad2 = rt.TPad("pad2","pad2",0.0,0.01,1.0,0.15)
        pad2.Draw()        
        pad2.cd()
        pad2.SetGridx()
        pad2.SetGridy()
        
        option = ''
        for range in self.ranges:
            histo = self.histograms[range]        
            if histo is inc: continue
            ratio = histo.Clone('ratio%s' % histo.GetName())
            ratio.GetYaxis().SetRangeUser(-0.5,0.5)
            ratio.Sumw2()
            ratio.Divide(inc)
            div = ratio.Integral()
            if div == 0.:
                div = 1.0
            ratio.Scale(1./div)
            ratio.GetYaxis().SetRangeUser(-0.5,0.5)
            ratio.Draw(option)
            
            ratio.GetXaxis().SetTitleFont(132)
            ratio.GetYaxis().SetTitleFont(132)
            ratio.GetXaxis().SetTitleSize(0.14)
            ratio.GetYaxis().SetTitleSize(0.14)
            ratio.GetXaxis().SetLabelFont(132)
            ratio.GetYaxis().SetLabelFont(132)
            ratio.GetXaxis().SetLabelSize(0.15)
            ratio.GetYaxis().SetLabelSize(0.15)
            ratio.GetXaxis().SetTitle(self.xaxis)
            ratio.GetYaxis().SetTitle(self.yaxis)            
            ratio.GetXaxis().CenterTitle()
            ratio.GetYaxis().CenterTitle();
            ratio.GetYaxis().SetTitleOffset(0.25)
            ratio.GetXaxis().SetTitleOffset(0.3)
            ratio.GetYaxis().SetRangeUser(-0.5,+0.5)
            
            ratio.SetFillColor(rt.kWhite);
            ratio.SetLineWidth(2);
            ratio.SetMarkerSize(1.0);
            ratio.GetYaxis().SetRangeUser(-0.5,0.5)            
            
            self.store.add(ratio, dir = dir)
            
            if not option:
                option = 'same'
        
        self.store.add(leg,dir=dir)
        self.store.add(canvas,dir=dir)
        canvas.SaveAs('%s.pdf' % canvas.GetName())
        canvas.SaveAs('%s.C' % canvas.GetName())
        print 'max %s = %i' % (self.count_var,self.max_count)


class PlotNPV(PlotCount):
    def __init__(self, store, var):
        PlotCount.__init__(self, store, var, 'nVertex', [(1,46),(1,5),(6,10),(11,15),(16,20),(21,46)])
        self.yaxis = "R(N_{PV}^{i} / N_{PV}^{INCL})"
            
class PlotNPVMR(PlotMR,PlotNPV):
    def __init__(self, store):
        PlotMR.__init__(self)
        PlotNPV.__init__(self, store, 'MR')

class PlotNPVRsq(PlotRsq,PlotNPV):
    def __init__(self, store):
        PlotRsq.__init__(self)   
        PlotNPV.__init__(self, store, 'Rsq')
        
class PlotNPVBDT(PlotBDT,PlotNPV):
    def __init__(self, store):
        PlotBDT.__init__(self)   
        PlotNPV.__init__(self, store, 'BDT')
        
class PlotNPVCHMultN(PlotCHMultN,PlotNPV):
    def __init__(self, store, N):
        PlotCHMultN.__init__(self, N)   
        PlotNPV.__init__(self, store, 'jet%dmult' % N)

class PlotNPVGirthN(PlotGirthN,PlotNPV):
    def __init__(self, store, N):
        PlotGirthN.__init__(self, N)   
        PlotNPV.__init__(self, store, 'jet%dgirth' % N)

class PlotNPVTopMassN(PlotTopMassN,PlotNPV):
    def __init__(self, store, N):
        PlotTopMassN.__init__(self, N)   
        PlotNPV.__init__(self, store, 'topMass%d' % N)

class PlotNPVWMassN(PlotWMassN,PlotNPV):
    def __init__(self, store, N):
        PlotWMassN.__init__(self, N)   
        PlotNPV.__init__(self, store, 'wMass%d' % N)

class PlotNPVThetaHN(PlotThetaHN,PlotNPV):
    def __init__(self, store, N):
        PlotThetaHN.__init__(self, N)   
        PlotNPV.__init__(self, store, 'thetaH%d' % N)

class PlotBTag(PlotCount):
    def __init__(self, store, var):
        PlotCount.__init__(self, store, var, 'nBtag', [(1,2),(0,0),(1,1),(2,2)])
        self.yaxis = "R(N_{CSV}^{i} / N_{CSV}^{INCL})"
    def rangeLabel(self, range):
        return '[%i CSV]' % range[0]
    
class PlotBTagMR(PlotMR,PlotBTag):
    def __init__(self, store):
        PlotMR.__init__(self)        
        PlotBTag.__init__(self, store, 'MR')
        
class PlotBTagRsq(PlotRsq,PlotBTag):
    def __init__(self, store):
        PlotRsq.__init__(self)        
        PlotBTag.__init__(self, store, 'Rsq')        
        
class PlotJetCount(PlotCount):
    def __init__(self, store, var):
        PlotCount.__init__(self, store, var, 'nJet', [(6,12),(6,6),(7,7),(8,8),(9,12)])
        self.yaxis = "R(N_{Jet}^{i} / N_{Jet}^{INCL})"
    def rangeLabel(self, range):
        if range[0] == range[1]:
            return '[%i Jets]' % range[0]
        else:
            return '[%d-%d Jets]' % (range[0],range[1])
        
class PlotJetMR(PlotMR,PlotJetCount):
    def __init__(self, store):
        PlotMR.__init__(self)        
        PlotJetCount.__init__(self, store, 'MR')
        
class PlotJetRsq(PlotRsq,PlotJetCount):
    def __init__(self, store):
        PlotRsq.__init__(self)        
        PlotJetCount.__init__(self, store, 'Rsq')         


if __name__ ==  '__main__':
    
    import sys

    RootTools.RazorStyle.setStyle()
    rt.gStyle.SetOptTitle(0)

    store = RootTools.RootFile.RootFile('razorMJControlPlots-8TeV.root')
#   plotters = [PlotNPVMR(store),PlotNPVRsq(store),PlotBTagMR(store),PlotBTagRsq(store),\
#        PlotJetMR(store),PlotJetRsq(store),PlotNPVBDT(store)]
#    plotters = [PlotNPVMR(store),PlotNPVRsq(store),PlotJetMR(store),PlotJetRsq(store),PlotNPVBDT(store)]
    plotters = []
#    for i in xrange(1,7):
#        plotters.append(PlotNPVCHMultN(store,i))
#        plotters.append(PlotNPVGirthN(store,i))
    for i in xrange(1,3):
        plotters.append(PlotNPVTopMassN(store,i))
        plotters.append(PlotNPVWMassN(store,i))
        plotters.append(PlotNPVThetaHN(store,i))
#    plotters = [PlotJetMR(store),PlotJetRsq(store)]

    def loop(fileName):
        input = rt.TFile.Open(fileName)
        dataSet = input.Get('RMRTree')
    
        for i in xrange(dataSet.numEntries()):
            row = dataSet.get(i)
            [p.fill(row) for p in plotters]
            del row

        input.Close()
    
    for arg in sys.argv[1:]:
        loop(arg)
        
        
    [p.final() for p in plotters]    
    store.write()
        
