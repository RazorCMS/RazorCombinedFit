from RazorCombinedFit.Framework import Box
import math
import RootTools
import RazorBox
import ROOT as rt
from array import *
import sys
from math import *

class RazorMultiBBox(RazorBox.RazorBox):

    def __init__(self, name, variables, fitMode = '1D', fitregion = 'FULL'):
        super(RazorMultiBBox,self).__init__(name, variables)
        
        # TTJets DEFAULT
        self.zeros = {'TTj':[]} 
        self.cut = 'MDR >= 0.0' 
        self.fitregion = fitregion
        self.fitMode = fitMode


    def getBinning(self, boxName, varName):
        if varName == "MDR" : return range(0,1.,0.01)
        if varName == "gammaR" : return range(1.,5.,0.04)
        if varName == "nBtag" : return range(2.,7.,1.)
         
    def define(self, inputFile):
            
        MDR  = self.workspace.var("MDR")
        label = 'TTj'
        #self.workspace.factory("RooTwoSideGaussianWithOneExponentialTailAndOneInverseN::PDF_%s(MDR, MDR0_%s, SigmaL_%s, SigmaR_%s, S1_%s, S2_%s, N_%s, F1_%s )" %(label,label,label, label,label,label,label,label))
        #self.workspace.factory("RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential::PDF_%s(MDR, MDR0_%s,SigmaL_%s, SigmaR_%s, S1_%s, S2_%s, A1_%s, F1_%s)"%(label,label,label,label,label,label,label,label))
        #self.workspace.factory("RooTwoSideGaussianWithOneXDependentExponential::PDF_%s(MDR, MDR0_%s,SigmaL_%s, SigmaR_%s, S1_%s, A1_%s)"%(label,label,label,label,label,label))
        #self.workspace.factory("RooTwoSideGaussianWithThreeExponentialTails::PDF_%s(MDR, MDR0_%s,SigmaL_%s, SigmaR_%s, S1_%s, S2_%s, S3_%s, F1_%s, F2_%s)"%(label,label,label,label,label,label,label,label,label))
        self.workspace.factory("RooTwoSideGaussianWithTwoExponentialTails::PDF_%s(MDR, MDR0_%s,SigmaL_%s, SigmaR_%s, S1_%s, S2_%s, F1_%s)"%(label,label,label,label,label,label,label))
        
        #self.workspace.factory("RooTwoSideGaussianWithOneExponentialTailAndOneInverseN::PDF_%s(MDR, MDR0_%s,SigmaL_%s, SigmaR_%s, S1_%s, S2_%s, N_%s, F1_%s)"%(label,label,label,label,label,label,label,label))
        self.workspace.factory("RooExtendPdf::ePDF_%s(PDF_%s, Ntot_%s)"%(label,label,label))


        # float all TTj parameters 
        self.fixPars(label,False)
        
        self.fitmodel = "ePDF_%s"%label
        
        #print the workspace
        self.workspace.Print("v")
                               
    def plot(self, inputFile, store, box, data=None, fitmodel="none", frName="none"):
        self.setstyle()
        [store.store(s, dir=box) for s in self.plot1D(inputFile, "MDR", nbins=70, ranges=['FULL'], data=data, fitmodel=fitmodel, frName=frName )]
        
    def plot1D(self, inputFile, varname, nbins=100, ranges=None, data=None, fitmodel="none", frName="none"):
        rangeCut = self.getVarRangeCutNamed(ranges=ranges)
        
        # set the integral precision
        #rt.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-30)
        #rt.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-30)

        
        # get the max and min (if different than default)
        xmin = min([self.workspace.var(varname).getMin(myRange) for myRange in ranges])
        xmax = max([self.workspace.var(varname).getMax(myRange) for myRange in ranges])
        if data is None:
            data = RootTools.getDataSet(inputFile,'MDRTree')
        if fitmodel=="none":
            fitmodel = self.fitmodel
        if frName=="none":
            frName = "independentFR"


        self.workspace.var(varname).setBins(int(nbins))
        frame = self.workspace.var(varname).frame(rt.RooFit.Range(xmin,xmax),rt.RooFit.Bins(int(nbins)))


        frame.SetName("multib_"+varname+"_rooplot_"+fitmodel+"_"+data.GetName())
        frame.SetTitle("")
        if varname=="MDR":
            frame.SetXTitle("M_{#Delta}^{R} [TeV]")
            
        # get fit result to visualize error
        fr = self.workspace.obj(frName)
        

        # to get error band
        errorArgSet = rt.RooArgSet()
        components = ["TTj"]
        for z in components:
            if self.name not in self.zeros[z]:
                errorArgSet.add(self.workspace.set("pdfpars_%s"%z))
                errorArgSet.add(self.workspace.set("otherpars_%s"%z))
            
        errorArgSet.Print("v")


        # plot the data
        data_cut = data.reduce(rangeCut)
        data_cut.plotOn(frame,rt.RooFit.Name("Data") )

        
        pdf =  self.workspace.pdf(fitmodel)
        
        # PLOT TOTAL ERROR +- 1sigma, +- 2 sigma
        [pdf.plotOn(frame,rt.RooFit.LineColor(rt.kBlue-10), rt.RooFit.FillColor(rt.kBlue-10),rt.RooFit.Range(myrange),rt.RooFit.VisualizeError(fr,errorArgSet,2,True),rt.RooFit.Name("twoSigma")) for myrange  in ranges]
        [pdf.plotOn(frame,rt.RooFit.LineColor(rt.kBlue-9), rt.RooFit.FillColor(rt.kBlue-9),rt.RooFit.Range(myrange),rt.RooFit.VisualizeError(fr,errorArgSet,1,True),rt.RooFit.Name("oneSigma")) for myrange  in ranges]
        
        # PLOT THE TOTAL NOMINAL
        [pdf.plotOn(frame, rt.RooFit.Name("Totalpm1sigma"), rt.RooFit.LineColor(rt.kBlue), rt.RooFit.FillColor(rt.kBlue-9),rt.RooFit.Range(myrange)) for myrange in ranges]
        [pdf.plotOn(frame, rt.RooFit.Name("Totalpm2sigma"), rt.RooFit.LineColor(rt.kBlue), rt.RooFit.FillColor(rt.kBlue-10),rt.RooFit.Range(myrange)) for myrange in ranges]

        # plot the data again
        data_cut.plotOn(frame,rt.RooFit.Name("Data") )

        d = rt.TCanvas("d","d",600,500)
        
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
        
        pad1.Draw()
        pad1.cd()
        d.SetName('DataMC_%s_%s' % (varname,'_'.join(ranges)) )
        
        rt.gPad.SetLogy()
        frame.SetMaximum(5e6)
        frame.SetMinimum(0.005)
        frame.Draw()



        # get curves from frame
        curve1 = frame.getCurve("oneSigma").Clone("newcurve1")
        curve2 = frame.getCurve("twoSigma").Clone("newcurve2")
        nomcurve = frame.getCurve("Totalpm1sigma").Clone("newnomcurve")
        datahist = frame.getHist("Data").Clone("newdatahist")

        # get chisq from curves and paramter set: errorArgList
        chisqdof = nomcurve.chiSquare(datahist,errorArgSet.getSize())
        print "chisq/dof = %f" %chisqdof
        nomfunction = pdf.asTF(rt.RooArgList(self.workspace.var(varname)))
        
        # legend
        leg = rt.TLegend(0.65,0.6,0.93,0.93)
        leg.SetFillColor(0)
        leg.SetTextFont(42)
        leg.SetLineColor(0)
        leg.AddEntry("Data","Data","pe")
        leg.AddEntry("Totalpm1sigma","Total Bkgd #pm 1#sigma","lf")
        leg.AddEntry("Totalpm2sigma","Total Bkgd #pm 2#sigma","lf")
        leg.AddEntry(rt.TObject(),"#chi^{2}/dof = %.2f"%chisqdof,"")
        leg.Draw()
        
        pt = rt.TPaveText(0.25,0.75,0.6,0.87,"ndc")
        pt.SetBorderSize(0)
        pt.SetFillColor(0)
        pt.SetFillStyle(0)
        pt.SetLineColor(0)
        pt.SetTextAlign(21)
        pt.SetTextFont(42)
        pt.SetTextSize(0.065)
        Preliminary = "Simulation"
        Lumi = 19.3
        Energy = 8
        text = pt.AddText("CMS %s #sqrt{s} = %i TeV" %(Preliminary,int(Energy)))
        #text = pt.AddText("Razor %s Box #int L = %3.1f fb^{-1}" %(self.name,Lumi))
        #text = pt.AddText("Razor MultiB %s Box" %(self.name))
        text = pt.AddText("Razor MultiB All Boxes")
        pt.Draw()


        # ratio plot
        d.Update()
        d.cd()
        pad2.Draw()
        pad2.cd()

        
        rt.gPad.SetLogy(0)

        # get histogram from RooDataSet
        histData = rt.TH1D("histData","histData",nbins,xmin,xmax)
        data.fillHistogram(histData,rt.RooArgList(self.workspace.var(varname)))
        
        
        for i in range(1,histData.GetNbinsX()):
            xup = histData.GetXaxis().GetBinUpEdge(i)
            xlow = histData.GetXaxis().GetBinLowEdge(i)
            nomintegral = nomfunction.Integral(xlow,xup)/nomfunction.Integral(xmin,xmax)
            nomevents = pdf.expectedEvents(rt.RooArgSet(self.workspace.var(varname))) * nomintegral
            if nomevents>0.:
                histData.SetBinContent(i, histData.GetBinContent(i)/nomevents)
                histData.SetBinError(i, histData.GetBinError(i)/nomevents)

                
        
        histData.SetMarkerStyle(20)
        histData.SetLineWidth(1)
        histData.SetLineColor(rt.kBlack)
        

        for curve in [curve1,curve2]:
            for i in range(0,curve.GetN()):
                x = array('d',[0])
                y = array('d',[0])
                curve.GetPoint(i, x, y)
                if nomcurve.Eval(x[0])>0.:
                    curve.SetPoint(i, x[0], y[0]/nomcurve.Eval(x[0]))

        for j in range(0,nomcurve.GetN()):
            nomx = array('d',[0])
            nomy = array('d',[0])
            nomcurve.GetPoint(j, nomx, nomy)
            nomcurve.SetPoint(j, nomx[0], 1.)

        
        for obj in [curve1, curve2, nomcurve, histData]:
            obj.SetMinimum(0.)
            obj.SetMaximum(3.5)
            obj.GetXaxis().SetTitleOffset(0.97)
            obj.GetXaxis().SetLabelOffset(0.02)
            obj.GetXaxis().SetTitleSize(0.2)
            obj.GetXaxis().SetLabelSize(0.17)
            if varname == "MDR":
                obj.GetXaxis().SetTitle("M_{#Delta}^{R} [TeV]")
            obj.GetYaxis().SetNdivisions(504,rt.kTRUE)
            obj.GetYaxis().SetTitleOffset(0.27)
            obj.GetYaxis().SetTitleSize(0.2)
            obj.GetYaxis().SetLabelSize(0.17)
            obj.GetYaxis().SetTitle("Data/Bkgd")
            obj.GetXaxis().SetTicks("+")
            obj.GetXaxis().SetTickLength(0.07)
            obj.GetXaxis().SetRangeUser(xmin,xmax)

        
        histData.Draw("pe1")
        curve2.Draw("f same")
        curve1.Draw("f same")
        nomcurve.Draw("c same")
        histData.Draw("pe1 same")


        pad2.Update()
        pad1.cd()
        pad1.Update()
        pad1.Draw()
        d.cd()


        fitregionLabel = '_'.join(self.fitregion.split(","))
        
        d.Print("razor_rooplot_%s_%s_%s_%s.pdf"%(varname,fitregionLabel,data.GetName(),self.name))
        

        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"d\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad1\");")
        rt.gROOT.ProcessLine("delete gDirectory->FindObject(\"pad2\");")
        return [frame]
    
    def setstyle(self):
        # For the canvas:
        rt.gStyle.SetCanvasBorderMode(0)
        rt.gStyle.SetCanvasColor(rt.kWhite)
        rt.gStyle.SetCanvasDefH(400) #Height of canvas
        rt.gStyle.SetCanvasDefW(600) #Width of canvas
        rt.gStyle.SetCanvasDefX(0)   #POsition on screen
        rt.gStyle.SetCanvasDefY(0)

        # For the Pad:
        rt.gStyle.SetPadBorderMode(0)
        # rt.gStyle.SetPadBorderSize(Width_t size = 1)
        rt.gStyle.SetPadColor(rt.kWhite)
        rt.gStyle.SetPadGridX(False)
        rt.gStyle.SetPadGridY(False)
        rt.gStyle.SetGridColor(0)
        rt.gStyle.SetGridStyle(3)
        rt.gStyle.SetGridWidth(1)

        # For the frame:
        rt.gStyle.SetFrameBorderMode(0)
        rt.gStyle.SetFrameBorderSize(1)
        rt.gStyle.SetFrameFillColor(0)
        rt.gStyle.SetFrameFillStyle(0)
        rt.gStyle.SetFrameLineColor(1)
        rt.gStyle.SetFrameLineStyle(1)
        rt.gStyle.SetFrameLineWidth(1)

        # set the paper & margin sizes
        rt.gStyle.SetPaperSize(20,26)
        rt.gStyle.SetPadTopMargin(0.09)
        #rt.gStyle.SetPadRightMargin(0.065)
        rt.gStyle.SetPadRightMargin(0.15)
        rt.gStyle.SetPadBottomMargin(0.15)
        rt.gStyle.SetPadLeftMargin(0.17)

        # use large Times-Roman fonts
        rt.gStyle.SetTitleFont(42,"xyz")  # set the all 3 axes title font
        rt.gStyle.SetTitleFont(42," ")    # set the pad title font
        rt.gStyle.SetTitleSize(0.06,"xyz") # set the 3 axes title size
        rt.gStyle.SetTitleSize(0.06," ")   # set the pad title size
        rt.gStyle.SetLabelFont(42,"xyz")
        rt.gStyle.SetLabelSize(0.057,"xyz")
        rt.gStyle.SetLabelColor(1,"xyz")
        rt.gStyle.SetTextFont(42)
        rt.gStyle.SetTextSize(0.08)
        rt.gStyle.SetStatFont(42)

        # use bold lines and markers
        rt.gStyle.SetMarkerStyle(20)
        rt.gStyle.SetLineStyleString(2,"[12 12]") # postscript dashes

        #..Get rid of X error bars
        #rt.gStyle.SetErrorX(0.001)

        # do not display any of the standard histogram decorations
        rt.gStyle.SetOptTitle(0)
        rt.gStyle.SetOptStat(0)
        rt.gStyle.SetOptFit(1111)
        rt.gStyle.SetStatY(0.85)        
        rt.gStyle.SetStatX(0.92)                
        rt.gStyle.SetStatW(0.15)                
        rt.gStyle.SetStatH(0.15)                

        # put tick marks on top and RHS of plots
        rt.gStyle.SetPadTickX(1)
        rt.gStyle.SetPadTickY(1)

        ncontours = 999

        stops = [ 0.00, 0.1, 0.25, 0.65, 1.00 ]
        #stops = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
        red =   [ 1.0,   0.95,  0.95,  0.65,   0.15 ]
        green = [ 1.0,  0.85, 0.7, 0.5,  0.3 ]
        blue =  [ 0.95, 0.6 , 0.3,  0.45, 0.65 ]
        s = array('d', stops)
        r = array('d', red)
        g = array('d', green)
        b = array('d', blue)

        npoints = len(s)
        rt.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
        rt.gStyle.SetNumberContours(ncontours)

        rt.gStyle.cd()


        

