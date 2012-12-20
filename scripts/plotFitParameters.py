#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
from array import *


def readFitResult(label, fileName):
    box = label.split("_")[-1]
    rootFile = rt.TFile(fileName)
    #read the variables from the workspace
    myWS = rootFile.Get(box+"/Box"+box+"_workspace")
    fitResult = rootFile.Get(box+"/independentFR")
    fitResult.Print("v")
    #get the final values from the fit
    parList = fitResult.floatParsFinal()
    fitPars = {}
    for p in RootTools.RootIterator.RootIterator(parList):
        fitPars[p.GetName()] = [p.getVal(),p.getError()]
    return fitPars

def getHisto(parName,parFiles):
    print parName
    parHisto = rt.TH1D(parName,parName,len(parFiles),0,len(parFiles))
    binNum = 0
    setAxis = parHisto.GetXaxis()
    setAxis.SetTitle("")
    for label, parValErr in reversed(sorted(parFiles.iteritems())):
        binNum +=1
        try:
            parVal = parValErr[parName][0]
            parErr = parValErr[parName][1]
            parHisto.SetBinContent(binNum,parVal)
            parHisto.SetBinError(binNum,parErr)
        except KeyError:
            print "oh no"
        parHisto.SetMarkerStyle(8)
        parHisto.SetMarkerColor(rt.kViolet)
        parHisto.SetLineColor(rt.kAzure)
        parHisto.SetMarkerSize(1.2)
        setAxis.SetBinLabel(binNum,label.replace("_"," "))
    return parHisto

def setstyle():
    rt.gStyle.SetCanvasBorderMode(0)
    rt.gStyle.SetCanvasColor(rt.kWhite)
    rt.gStyle.SetCanvasDefH(400) 
    rt.gStyle.SetCanvasDefW(600) 
    rt.gStyle.SetCanvasDefX(0)  
    rt.gStyle.SetCanvasDefY(0)

    rt.gStyle.SetPadBorderMode(0)
    rt.gStyle.SetPadColor(rt.kWhite)
    rt.gStyle.SetPadGridX(False)
    rt.gStyle.SetPadGridY(False)
    rt.gStyle.SetGridColor(0)
    rt.gStyle.SetGridStyle(3)
    rt.gStyle.SetGridWidth(1)
    
    rt.gStyle.SetFrameBorderMode(0)
    rt.gStyle.SetFrameBorderSize(1)
    rt.gStyle.SetFrameFillColor(0)
    rt.gStyle.SetFrameFillStyle(0)
    rt.gStyle.SetFrameLineColor(1)
    rt.gStyle.SetFrameLineStyle(1)
    rt.gStyle.SetFrameLineWidth(1)
    
    rt.gStyle.SetPaperSize(20,26)
    rt.gStyle.SetPadTopMargin(0.075)
    rt.gStyle.SetPadRightMargin(0.17)
    rt.gStyle.SetPadBottomMargin(0.24)
    rt.gStyle.SetPadLeftMargin(0.07)
    
    rt.gStyle.SetTitleFont(132,"xyz") 
    rt.gStyle.SetTitleFont(132," ")   
    rt.gStyle.SetTitleSize(0.06,"xyz")
    rt.gStyle.SetTitleSize(0.06," ")  
    rt.gStyle.SetLabelFont(132,"xyz")
    rt.gStyle.SetLabelSize(0.05,"xyz")
    rt.gStyle.SetLabelColor(1,"xyz")
    rt.gStyle.SetTextFont(132)
    rt.gStyle.SetTextSize(0.08)
    rt.gStyle.SetStatFont(132)
    rt.gStyle.SetMarkerStyle(8)
    #rt.gStyle.SetHistLineWidth((rt.Width_t) 1.85)
    rt.gStyle.SetLineStyleString(2,"[12 12]")
    rt.gStyle.SetErrorX(0.001)
    rt.gStyle.SetOptTitle(1)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptFit(11111111)
    rt.gStyle.SetPadTickX(1)
    rt.gStyle.SetPadTickY(1)

    def set_palette(name="default", ncontours=255):
        """Set a color palette from a given RGB list
        stops, red, green and blue should all be lists of the same length
        see set_decent_colors for an example"""

        if name == "gray" or name == "grayscale":
            stops = [0.00, 0.34, 0.61, 0.84, 1.00]
            red   = [1.00, 0.95, 0.95, 0.65, 0.15]
            green = [1.00, 0.85, 0.7, 0.5, 0.3]
            blue  = [0.95, 0.6, 0.3, 0.45, 0.65]
            # elif name == "whatever":
            # (define more palettes)
        elif name == "chris":
            stops = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
            red =   [ 1.0,   0.95,  0.95,  0.65,   0.15 ]
            green = [ 1.0,  0.85, 0.7, 0.5,  0.3 ]
            blue =  [ 0.95, 0.6 , 0.3,  0.45, 0.65 ]
        else:
            # default palette, looks cool
            stops = [0.00, 0.34, 0.61, 0.84, 1.00]
            red   = [0.00, 0.00, 0.87, 1.00, 0.51]
            green = [0.00, 0.81, 1.00, 0.20, 0.00]
            blue  = [0.51, 1.00, 0.12, 0.00, 0.00]

        s = array('d', stops)
        r = array('d', red)
        g = array('d', green)
        b = array('d', blue)

        npoints = len(s)
        rt.TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
        rt.gStyle.SetNumberContours(ncontours)

    set_palette("chris")

    rt.gStyle.cd()

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('-d','--dir',dest="outdir",default="./",type="string",
                  help="Output directory to store datasets")
    parser.add_option('--max',dest="max",type="int",default=-1,
                  help="The last event to take from the input Dataset")
    parser.add_option('--min',dest="min",type="int",default=0,
                  help="The first event to take from the input Dataset")  
    (options,args) = parser.parse_args()

    if options.config is None:
        import inspect, os
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(writeCocktail)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    print 'Input files are %s' % ', '.join(args)

    setstyle()
    
    labels = {}
    for f in args:
        if f.lower().endswith('.root'):
            decorator = f[:-5]
            
            label = decorator.split('razor_output_')[-1]
            if not labels.has_key(label):
                labels[label] = f
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f

    parFiles = {}
    for label, files in labels.iteritems():
        print label
        parFiles[label] = readFitResult(label, files)
    
    parNameList = parFiles[label].keys()
    for parName in parNameList:
        parHisto = getHisto(parName,parFiles)

        c = rt.TCanvas("c%s"%parName,"c%s"%parName,600,400)
        c.SetLogy(0)
        #if parName.find("b_") !=-1 or parName.find("n_")!=-1 or parName.find("Ntot_") !=-1:
        #    c.SetLogy(1)
        parHisto.Draw('E1')
        c.Print("%s/%s.pdf"%(options.outdir,parName))
