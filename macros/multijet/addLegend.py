import ROOT as rt
import sys, os

def getContourIndex(size, percent):

    sigma = rt.TMath.Nint(size * percent) - 1
    if(sigma > size-1):
        sigma = size-1;
    return sigma;


def findToyUncertainties(pattern, central, var):
    
    import glob
    toys = glob.glob(pattern)
    
    toy_histos = []

    vars = {'Rsq':rt.RooRealVar('Rsq','R^{2}',0.9,0.03,1.0),'MR':rt.RooRealVar('MR','M_{R}',3499.0,500.0,4000.0)}
    
    count = 0
    for t in toys:
        input = rt.TFile.Open(t)
        ds = input.Get('RMRTree')
        
        h = central.Clone('%s_%d' % (central.GetName(), count) )
        h.Reset()
        h.SetDirectory(0)
        ds.fillHistogram(h,rt.RooArgList(vars[var]))
        toy_histos.append(h)
        
        input.Close()
        
        count += 1
    
    result = central.Clone('%s_toyerrors' % central.GetName())
    #result.Reset()
    result.SetDirectory(0)
    
    for i in xrange(1,central.GetXaxis().GetNbins()+1):
        values = []
        cent = central.GetBinContent(i)
        for h in toy_histos:
            values.append(h.GetBinContent(i))
        values.sort()
        
        size = len(values)
        med = getContourIndex(size, 0.5)#50%
        oneSigmaLow = getContourIndex(size, 0.1575)#17%
        oneSigmaHigh = getContourIndex(size, 0.8425)#100% - 17%
        
        median = values[med]
        uncert = 0.5*( abs(median - values[oneSigmaHigh])+ abs(median - values[oneSigmaLow]) )
        
        #don't use the median, otherwise the histograms won't normalise
        #result.SetBinContent(i, median)
        result.SetBinError(i, uncert)
        
    
    return result
    

if __name__ == '__main__':

    inputFile = sys.argv[1]
    if not os.path.exists(inputFile):
        raise Exception("The file '%s' does not exist" % inputFile)

    boxLabel = sys.argv[2]
    region = sys.argv[3]

    rootFile = rt.TFile.Open(inputFile)
    rootFile.cd(boxLabel)
    rootFile.ls()
    
    def plot(var, box, label, region):
        data = rt.gDirectory.Get('histoData_%s_FULL_ALLCOMPONENTS' % var)
        dataLep = rt.gDirectory.Get('histoDataLep_%s_FULL_ALLCOMPONENTS' % var)

        toy = findToyUncertainties('/Users/wreece/Downloads/gof_toys_BJet_FitRegion_10b/gof_toys_BJet_FitRegion_10b/frtoydata_BJet_*.root',\
                                   rt.gDirectory.Get('histoToy_%s_FULL_ALLCOMPONENTS' % var).Clone(), var)
        #toy = rt.gDirectory.Get('histoToy_%s_FULL_ALLCOMPONENTS' % var)
    
        #get back to the right place
        rootFile.cd(boxLabel)
        
        toy.SetFillStyle(3004)
        toy.SetMarkerColor(toy.GetLineColor())
        toyQCD = rt.gDirectory.Get('histoToyQCD_%s_FULL_ALLCOMPONENTS' % var)
        toyQCD.SetFillStyle(3004)
        toyQCD.SetMarkerColor(toyQCD.GetLineColor())
        toyTTj = rt.gDirectory.Get('histoToyTTj_%s_FULL_ALLCOMPONENTS' % var)
        toyTTj.SetFillStyle(3004)
        toyTTj.SetMarkerColor(toyTTj.GetLineColor())
        
        canvas = rt.TCanvas('%s_%s' % (var,box),'%s_%s' % (var,box),640,800)
        rt.gStyle.SetOptTitle(0)
        rt.gStyle.SetOptStat(0)
        canvas.Draw()
        
        pad1 = rt.TPad("pad1","pad1",0.0,0.0,1.,0.8)
        pad1.Draw();        
        pad1.SetLogy()
        pad1.cd()

        data.GetXaxis().SetTitle(label)
        data.GetYaxis().SetTitle('Entries')
        data.SetLineColor(rt.kBlack)
        data.GetXaxis().SetLabelSize(0.04)
        data.GetYaxis().SetLabelSize(0.04)
        data.GetXaxis().SetTitleSize(0.04)
        data.GetYaxis().SetTitleSize(0.04)
        data.GetYaxis().SetTitleOffset(1.1)
        
        data.Draw("errors")

        toy.Draw("e4same")
        toyLine = toy.Clone('toyLine')
        toyLine.SetFillColor(rt.kWhite)
        toyLine.Draw("hist same")

        #toyQCD.Draw('e4same')
        toyQCDLine = toyQCD.Clone('toyQCDLine')
        toyQCDLine.SetFillColor(rt.kWhite)
        toyQCDLine.Draw("hist same")
        
        #toyTTj.Draw('e4same')
        toyTTjLine = toyTTj.Clone('toyLine')
        toyTTjLine.SetFillColor(rt.kWhite)
        toyTTjLine.Draw("hist same")

        dataLep.Draw('hist same')
        data.Draw('esame')

        leg = rt.TLegend(0.5, 0.5, 0.85, 0.85,'%s Box' % box)
        leg.SetTextSize(0.03)
        leg.SetLineColor(rt.kWhite)
        leg.SetFillColor(rt.kWhite)
        leg.SetShadowColor(rt.kWhite)

        leg.AddEntry(data,'Data')
        leg.AddEntry(dataLep,'Loose leptons')
        leg.AddEntry(toy,'SM Total')
        leg.AddEntry(toyQCDLine, 'QCD')
        leg.AddEntry(toyTTjLine,'W+jets')
        leg.Draw()

        pad2 = rt.TPad("pad2","pad2",0.0,0.9,1.0,1.0)
        pad2.Draw()        
        pad2.cd()
        ratio = toy.Clone('ratio_%s_%s' % (var, box) )
        ratio.Sumw2()
        ratio.SetLineColor(rt.kBlack)
        ratio.Divide(data)
        #ratio.Scale(1./ratio.Integral())

        ratio.GetXaxis().SetLabelSize(0.0)
        ratio.GetXaxis().SetTitleSize(0.0)
        ratio.GetYaxis().SetLabelSize(0.1)
        ratio.GetYaxis().SetTitle("SM/Data")

        ratio.Draw("errors")

        canvas.SaveAs('%s_%s_%s.pdf' % (box, region, var) )
        canvas.SaveAs('%s_%s_%s.C' % (box, region, var) )


    plot('Rsq', boxLabel,'R^{2}', region)
    plot('MR', boxLabel,'M_{R} [GeV]', region)
    
