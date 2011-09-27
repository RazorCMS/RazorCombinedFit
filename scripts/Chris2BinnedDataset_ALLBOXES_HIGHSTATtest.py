from optparse import OptionParser
import os
from pdfShit import *

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'Mu':3,'Ele':4,'Had':5}
cross_sections = {'SingleTop_s':4.21,'SingleTop_t':64.6,'SingleTop_tw':10.6,\
                               'TTj':157.5,'Zll':3048,'Znn':2*3048,'Wln':31314,\
                               'WW':43,'WZ':18.2,'ZZ':5.9,'Vgamma':173
                               }
lumi = 1.0

def getMeanSigma(n0, nP, nM):
    maxVal = max(n0, nP, nM)
    minVal = min(n0, nP, nM)
    return (maxVal+minVal)/2., (maxVal-minVal)/2.

def writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin):
    
    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+outputBox,'UPDATE')
    for mydata in data:
        mydata.Write()
    output.Close()

def convertTree2Dataset(tree, nbinx, nbiny, outputFile, config, minH, maxH, nToys, scale, write = True):
    """This defines the format of the RooDataSet"""

    boxes = ["MuEle", "MuMu", "EleEle", "Mu", "Ele", "Had"]

    wHisto = []
    wHisto_JESup = []
    wHisto_JESdown = []
    wHisto_xsecup = []
    wHisto_xsecdown = []
    wHisto_pdfCEN = []
    wHisto_pdfSYS = []

    #this is the nominal histogram
    for box in boxes:               
        data = [] 
        workspace = rt.RooWorkspace(box)
        variables = config.getVariablesRange(box,"variables",workspace)
        args = workspace.allVars()

        #we cut away events outside our MR window
        mRmin = args['MR'].getMin()
        mRmax = args['MR'].getMax()

        #we cut away events outside our Rsq window
        rsqMin = args['Rsq'].getMin()
        rsqMax = args['Rsq'].getMax()
        rMin = rt.TMath.Sqrt(rsqMin)
        rMax = rt.TMath.Sqrt(rsqMax)
        
        # set the same binning for the RooRealVars
        MR =  workspace.var("MR")
        Rsq =  workspace.var("Rsq")
 
        histo = rt.TH2D("wHisto_%s" %box,"wHisto_%s" %box, nbinx, mRmin, mRmax, nbiny, rsqMin, rsqMax)
        tree.Project("wHisto_%s" %box, "RSQ:MR", 'W*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
        rooDataHist = rt.RooDataHist("RMRHistTree_%s" %box,"RMRHistTree_%s" %box,rt.RooArgList(rt.RooArgSet(MR,Rsq)),histo)
        data.append(rooDataHist)
        data.append(histo.Clone())
        wHisto.append(histo.Clone())

        #write objects for this box
        if write: writeTree2DataSet(data, outputFile, "%s.root" %box, rMin, mRmin)
        # cleanup
        del data
        del workspace
        del variables
        del args
        del mRmin
        del mRmax
        del MR
        del Rsq

    # random number generator
    pid = os.getpid()
    now = rt.TDatime()
    today = now.GetDate()
    clock = now.GetTime()
    seed = today+clock+pid+137
    gRnd = rt.TRandom3(seed)

    # rescale the statistics
    if scale != 1. and scale != 0.:
        for ix in range(1,nbinx+1):
            for iy in range(1,nbiny+1):
                for ibox in range(0,len(boxes)):
                    wHisto[ibox].SetBinContent(ix,iy,gRnd.Poisson(wHisto[ibox].GetBinContent(ix,iy)*scale)/scale)

    for i in xrange(nToys):
        # correlated systematics: LUMI 4.5% MULTIPLICATIVE sumInQuadrature  sumInQuadrature RvsMR trigger 2% = 4.9%
        lumiFactor = math.pow((1.049), gRnd.Gaus(0., 1.))
        # triggerLepton 3% per trigger set
        muTriggerFactor =  math.pow(1.03,gRnd.Gaus(0.,1.))
        eleTriggerFactor =  math.pow(1.03,gRnd.Gaus(0.,1.))      
        # correlated systematics: xsection ADDITIVE (scaled bin by bin)
        xsecFactor = gRnd.Gaus(0., 1.)
        for ibox in range(0,len(boxes)):
            box = boxes[ibox]
            workspace = rt.RooWorkspace(box)
            variables = config.getVariablesRange(box,"variables",workspace)
            args = workspace.allVars()

            #we cut away events outside our MR window
            mRmin = args['MR'].getMin()
            mRmax = args['MR'].getMax()

            #we cut away events outside our Rsq window
            rsqMin = args['Rsq'].getMin()
            rsqMax = args['Rsq'].getMax()
            rMin = rt.TMath.Sqrt(rsqMin)
            rMax = rt.TMath.Sqrt(rsqMax)

            # set the same binning for the RooRealVars
            MR =  workspace.var("MR")
            Rsq =  workspace.var("Rsq")

            box = boxes[ibox]
            # create a copy of the histogram
            wHisto_i = rt.TH2D("wHisto_%s_%i" %(box, i),"wHisto_%s_%i" %(box, i), nbinx, mRmin, mRmax, nbiny, rsqMin, rsqMax)
            for ix in range(1,nbinx+1):
                for iy in range(1,nbiny+1):
                    # uncorrelated systematics: lepton efficiency data/MC 1%
                    lepFactor = math.pow(1.01,gRnd.Gaus(0., 1.))                   
                    # compute the total
                    # starting value
                    nominal = wHisto[ibox].GetBinContent(ix,iy)
                    if nominal != 0:
                        # add lumi systematics
                        newvalue = nominal*lumiFactor
                        # add the lep trigger eff
                        if box == "MuMu" or box == "MuEle" or box == "Mu": newvalue = newvalue*muTriggerFactor
                        if box == "EleEle" or box == "Ele": newvalue = newvalue*eleTriggerFactor
                        if box != "Had": newvalue = newvalue*lepFactor
                        # add xsec systematics: NA
                        # add jes systematics: NA
                        # apply the systematic correction to the pdf value: NA
                        # fill histogram
                        wHisto_i.SetBinContent(ix,iy,max(0.,newvalue))
                    else:
                        wHisto_i.SetBinContent(ix,iy,max(0.,nominal))
            data = [wHisto_i,rt.RooDataHist("RMRHistTree_%s_%i" %(box,i),"RMRHistTree_%s_%i" %(box,i),rt.RooArgList(rt.RooArgSet(MR,Rsq)),wHisto_i)]            
            if write: writeTree2DataSet(data, outputFile, "%s.root" %box, rMin, mRmin)
            del wHisto_i
            del data
            del workspace
            del variables
            del args
            del mRmin
            del mRmax
            del MR
            del Rsq
   
    return []

def printEfficiencies(tree, outputFile, config, flavour):
    """Backout the MC efficiency from the weights"""
    print 'ERROR:: This functionality produces incorrect results as we\'re missing a factor somewhere...'
    
    cross_section = cross_sections[flavour]
    
    for box in boxMap:
        ds = convertTree2Dataset(tree, 100, 100, outputFile, 'Dummy', config, box, 0, -1, -1, write = False)
        row = ds[0].get(0)
        W = ds.mean(row['W'])
        n_i = (cross_section*lumi)/W
        n_f = ds.numEntries()
        print 'Efficienty: %s: %f (n_i=%f; n_f=%i)' % (box,n_f/n_i,n_i, n_f)
    

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('--max',dest="max",type="int",default=-1,
                  help="The last event to take from the input Dataset")
    parser.add_option('--min',dest="min",type="int",default=0,
                  help="The first event to take from the input Dataset")  
    parser.add_option('-e','--eff',dest="eff",default=False,action='store_true',
                  help="Calculate the MC efficiencies")
    parser.add_option('-f','--flavour',dest="flavour",default='TTj',
                  help="The flavour of MC used as input")
    parser.add_option('-r','--run',dest="run",default=-1,type=float,
                  help="The minimum run number")
    parser.add_option('-d','--dir',dest="outdir",default="./",type="string",
                  help="Output directory to store datasets")
    parser.add_option('-t','--toys',dest="toys",type="int",default=1000,
                  help="Number of toys")
    parser.add_option('-x','--nbinx',dest="nbinx",type="int",default=100,
                      help="Number of bins in mR")
    parser.add_option('-y','--nbiny',dest="nbiny",type="int",default=100,
                      help="Number of bins in R^2")
    parser.add_option('-s','--scale',dest="scale",type="float",default=1.,
                      help="Statistics scale factor")
    
    (options,args) = parser.parse_args()
    
    if options.config is None:
        import inspect, os
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(convertTree2Dataset)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    
    print 'Input files are %s' % ', '.join(args)
    for f in args:
        if f.lower().endswith('.root'):
            input = rt.TFile.Open(f)

            decorator = options.outdir+"/"+os.path.basename(f)[:-5]
            convertTree2Dataset(input.Get('EVENTS'), options.nbinx, options.nbiny, decorator, cfg,options.min,options.max,options.toys,options.scale)

        else:
            "File '%s' of unknown type. Looking for .root files only" % f
