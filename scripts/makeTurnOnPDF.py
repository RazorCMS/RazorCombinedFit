#!/usr/bin/env python
import ROOT as rt
from ROOT import std
import os, sys, array

def getBinContent(histo, x, y):
    
    xaxis = histo.GetXaxis()
    yaxis = histo.GetYaxis()
    
    xbin = xaxis.FindBin(x)
    ybin = yaxis.FindBin(y)
    
    bin = histo.GetBin(xbin,ybin)
    
    return histo.GetBinContent(bin)
    
def setBinContent(histo, x, y, val):
    
    xaxis = histo.GetXaxis()
    yaxis = histo.GetYaxis()
    
    xbin = xaxis.FindBin(x)
    ybin = yaxis.FindBin(y)
    
    bin = histo.GetBin(xbin,ybin)
    
    histo.SetBinContent(bin, val)

if __name__ == '__main__':

    from optparse import OptionParser    
    parser = OptionParser()
    parser.add_option('--bnn',dest="bnn",type="string",default=None,
                  help="Name of the BNN output file to use")
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('-o','--output',dest="output",type="string",default='turnon.root',
                  help="Name of the output file")
      
    (options,args) = parser.parse_args()
    
    MR = rt.RooRealVar("MR", "MR", 450., 4000.)
    Rsq = rt.RooRealVar("Rsq", "Rsq", 0.03, 1.0)

    if options.config is not None:
        from RazorCombinedFit.Framework import Config
        cfg = Config.Config(options.config)
        
        workspace = rt.RooWorkspace(options.box)
        for value in cfg.getVariables(options.box):
            workspace.factory(value)
        cfg.getVariablesRange(options.box, 'variables', workspace)
        
        MR = workspace.var('MR')
        Rsq = workspace.var('Rsq')    
    
    if not os.path.exists(options.bnn):
        print 'BNN input file must exist'
        sys.exit(-1)
        
    rt.gROOT.ProcessLine(".L %s+" % options.bnn)
    name, _ = os.path.splitext(os.path.basename(options.bnn))
    
    _temp = __import__('ROOT', globals(), locals(), [name], -1)
    bnnClass = getattr(_temp,name)
    
    minMR = MR.getMin()
    maxMR = MR.getMax()
    nBinsMR = rt.TMath.Nint(abs(maxMR-minMR))
    #nBinsMR = 20
    stepMR = abs(maxMR-minMR)/(1.0*nBinsMR)
    
    minRsq = Rsq.getMin()
    maxRsq = Rsq.getMax()
    nBinsRsq = rt.TMath.Nint(100*abs(maxRsq-minRsq))
    #nBinsRsq = 20
    stepRsq = abs(maxRsq-minRsq)/(1.0*nBinsRsq)
    
    nominal = rt.TH2D('turnOn','NominalTurnOn',\
                 nBinsMR+1,minMR-(stepMR/2.0),maxMR+(stepMR/2.0),
                 nBinsRsq+1,minRsq-(stepRsq/2.0),maxRsq+(stepRsq/2.0)
                 )
    rms = nominal.Clone('turnOnError')
    
    sample = 100
    vars = std.vector('double')(2)
    rms_vars = array.array('d',[0.0 for i in xrange(sample)])
    for i in xrange(nBinsMR):
        mr_now = minMR + (i*stepMR)
        for j in xrange(nBinsRsq):
            rsq_now = minRsq + (j*stepRsq)
    
            vars[0] = mr_now
            vars[1] = rsq_now

            nom = bnnClass(vars)
            setBinContent(nominal,mr_now,rsq_now, nom)
            for k in xrange(sample):
                rms_vars[k] = bnnClass(vars,k,k)
            rms_value = rt.TMath.RMS(sample,rms_vars)
            #we use the percentage rather than the absolute
            setBinContent(rms,mr_now,rsq_now, rms_value/nom)
            print nom, rms_value
                
            
    out = rt.TFile.Open(options.output,'recreate')
    nominal.Write()
    rms.Write()
    out.Close()
    
    