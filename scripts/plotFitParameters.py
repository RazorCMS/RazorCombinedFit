#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path
from array import *
import sys


boxes = ["MuJet","MuMultiJet","EleJet","EleMultiJet"]

boxDict = {"MuEle":0,"MuMu":1,"EleEle":2,"MuJet":3,"MuMultiJet":4,
           "EleJet":5,"EleMultiJet":6,"Jet2b":7,"MultiJet":8}
def box_sort_key(parFile):
    label = parFile[0]
    box, fit = label
    boxNum = boxDict[box]
    boxNum*=2
    if fit == "Full": boxNum+=1
    return boxNum

def readFitResult(label, fileName):
    box, fit = label
    rootFile = rt.TFile(fileName)
    #read the variables from the workspace
    myWS = rootFile.Get(box+"/Box"+box+"_workspace")
    fitResult = rootFile.Get(box+"/independentFR")
    fitResult.Print("v")
    #get the final values from the fit
    parList = fitResult.floatParsFinal()
    fitPars = {}
    for p in RootTools.RootIterator.RootIterator(parList):
        fitPars[p.GetName()] = [p.getVal(),p.getError(),p.getMin(),p.getMax()]
    return fitPars

def getParHisto(parName,parFiles):
    print parName
    numBins = 0
    
    for label, parValErr in sorted(parFiles.iteritems(),key=box_sort_key):
        try:
            parVal = parValErr[parName][0]
        except KeyError:
            continue
        numBins+=1
    parHisto = rt.TH1D(parName,parName,numBins,0,numBins)
    binNum = 0
    setAxis = parHisto.GetXaxis()
    setAxis.SetTitle("")
    for label, parValErr in sorted(parFiles.iteritems(),key=box_sort_key):
        box, fit = label
        try:
            parVal = parValErr[parName][0]
            parErr = parValErr[parName][1]
            parMin = parValErr[parName][2]
            parMax = parValErr[parName][3]
            binNum +=1
            parHisto.SetBinContent(binNum,parVal)
            parHisto.SetBinError(binNum,parErr)
            if (parName.find("n_")!=-1 or parName.find("b_")!=-1) and parVal-parErr<0.:
                #parHisto.SetBinError(binNum,abs(parVal))
                parHisto.SetMinimum(0)
        except KeyError:
            continue
            
        parHisto.SetMarkerStyle(8)
        #parHisto.SetMarkerColor(rt.kViolet)
        #parHisto.SetLineColor(rt.kAzure)
        parHisto.SetMarkerColor(rt.kCyan+2)
        parHisto.SetLineColor(rt.kCyan+2)
        parHisto.SetMarkerSize(1.2)
        setAxis.SetBinLabel(binNum,"%s %s"%(box,fit))
    return parHisto

def getBoxHisto(box,parFiles):
    print box
    numPars = len(parFiles[box,'Full'].keys())
    boxHisto = rt.TH1D(box,box,2*numPars,0,2*numPars)
    setAxis = boxHisto.GetXaxis()
    print numPars
    
    binNum=0
    
    for label, parValErr in sorted(parFiles.iteritems(),key=box_sort_key):        
        if label[0]!=box: continue
        print label
        box, fit = label

        for parName in parValErr.keys():
            parVal = parValErr[parName][0]
            parErr = parValErr[parName][1]
            parMin = parValErr[parName][2]
            parMax = parValErr[parName][3]
            binNum +=1
            boxHisto.SetBinContent(binNum,parVal)
            boxHisto.SetBinError(binNum,parErr) 
            setAxis.SetBinLabel(binNum,"%s %s"%(parName, fit))
        boxHisto.SetMarkerStyle(8)
        boxHisto.SetMarkerColor(rt.kViolet)
        boxHisto.SetLineColor(rt.kAzure)
        boxHisto.SetMarkerSize(1.2)
            
    return boxHisto

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
    rt.gStyle.SetPadLeftMargin(0.1)
    
    rt.gStyle.SetTitleFont(132,"xyz") 
    rt.gStyle.SetTitleFont(132," ")   
    rt.gStyle.SetTitleSize(0.06,"xyz")
    rt.gStyle.SetTitleSize(0.06," ")  
    rt.gStyle.SetLabelFont(132,"xyz")
    rt.gStyle.SetLabelSize(0.065,"xyz")
    rt.gStyle.SetLabelColor(1,"xyz")
    rt.gStyle.SetTextFont(132)
    rt.gStyle.SetTextSize(0.08)
    rt.gStyle.SetStatFont(132)
    rt.gStyle.SetMarkerStyle(8)
    #rt.gStyle.SetHistLineWidth((rt.Width_t) 1.85)
    rt.gStyle.SetLineStyleString(2,"[12 12]")
    rt.gStyle.SetErrorX(0.2)
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
            
            fit = decorator.split("Fits")[0]
            for box in boxes:
                if not labels.has_key((box,fit)):
                    labels[box,fit] = f
            

            "File '%s' of unknown type. Looking for .root files only" % f

    parFiles = {}
    for label, files in labels.iteritems():
        print label
        parFiles[label] = readFitResult(label, files)

    parNameSet = set([])
    for label, files in labels.iteritems():
        parNameSet = parNameSet.union(set(parFiles[label].keys()))

        
    c = rt.TCanvas("c","c",600,400)
    c.SetLogy(0)
    
    # for box in boxes:
    #     boxHisto = getBoxHisto(box,parFiles)
    #     boxHisto.Draw('E1')
    #     c.Print("%s/%s.pdf"%(options.outdir,box))


    for parName in parNameSet:
        parHisto = getParHisto(parName,parFiles)
        tlines = []
        parHisto.Draw('E1')
        rt.gPad.Update()

        for i in xrange(2, parHisto.GetNbinsX()+1,2):
            tlines.append(rt.TLine(i, rt.gPad.GetFrame().GetY1(), i, rt.gPad.GetFrame().GetY2()))
        for tline in tlines:
            tline.Draw("same")
        c.Print("%s/%s.pdf"%(options.outdir,parName))
        
