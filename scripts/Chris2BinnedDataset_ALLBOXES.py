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

def convertTree2Dataset(tree, nbin, outputFile, config, minH, maxH, nToys, write = True):
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
 
        histo = rt.TH2D("wHisto_%s" %box,"wHisto_%s" %box, nbin, mRmin, mRmax, nbin, rsqMin, rsqMax)
        tree.Project("wHisto_%s" %box, "RSQ:MR", 'LEP_W*W*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
        rooDataHist = rt.RooDataHist("RMRHistTree_%s" %box,"RMRHistTree_%s" %box,rt.RooArgList(rt.RooArgSet(MR,Rsq)),histo)
        data.append(rooDataHist)
        data.append(histo.Clone())
        wHisto.append(histo.Clone())

        # JES correctiobns UP
        histo_JESup = rt.TH2D("wHisto_JESup_%s" %box,"wHisto_JESup_%s" %box, nbin, mRmin, mRmax, nbin, rsqMin, rsqMax)
        tree.Project("wHisto_JESup_%s" %box, "RSQ_JES_UP:MR_JES_UP", 'LEP_W*W*(MR_JES_UP >= %f && MR_JES_UP <= %f && RSQ_JES_UP >= %f && RSQ_JES_UP <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
        data.append(histo_JESup.Clone())
        wHisto_JESup.append(histo_JESup.Clone())

        # JES correctiobns DOWN
        histo_JESdown = rt.TH2D("wHisto_JESdown_%s" %box,"wHisto_JESdown_%s" %box, nbin, mRmin, mRmax, nbin, rsqMin, rsqMax)
        tree.Project("wHisto_JESdown_%s" %box,  "RSQ_JES_DOWN:MR_JES_DOWN", 'LEP_W*W*(MR_JES_DOWN >= %f && MR_JES_DOWN <= %f && RSQ_JES_DOWN >= %f && RSQ_JES_DOWN <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
        data.append(histo_JESdown.Clone())
        wHisto_JESdown.append(histo_JESdown.Clone())

        # xsec UP
        histo_xsecup = rt.TH2D("wHisto_xsecup_%s" %box,"wHisto_xsecup_%s" %box, nbin, mRmin, mRmax, nbin, rsqMin, rsqMax)
        tree.Project("wHisto_xsecup_%s" %box, "RSQ:MR",  'LEP_W*W_UP*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
        data.append(histo_xsecup.Clone())
        wHisto_xsecup.append(histo_xsecup.Clone())
        
        # xsec correctiobns DOWN
        histo_xsecdown = rt.TH2D("wHisto_xsecdown_%s" %box,"wHisto_xsecdown_%s" %box, nbin, mRmin, mRmax, nbin, rsqMin, rsqMax)
        tree.Project("wHisto_xsecdown_%s" %box, "RSQ:MR",  'LEP_W*W_DOWN*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
        data.append(histo_xsecdown.Clone())
        wHisto_xsecdown.append(histo_xsecdown.Clone())
        
        # PDF central (new nominal) and error (for systematics)
        histo_pdfCEN, histo_pdfSYS = makePDFPlot(tree, histo, nbin, mRmin, mRmax, nbin, rsqMin, rsqMax, boxMap[box])
        histo_pdfCEN.SetName("wHisto_pdfCEN_%s" %box)
        histo_pdfSYS.SetName("wHisto_pdfSYS_%s" %box)
        data.append(histo_pdfCEN.Clone())
        data.append(histo_pdfSYS.Clone())
        wHisto_pdfCEN.append(histo_pdfCEN.Clone())
        wHisto_pdfSYS.append(histo_pdfSYS.Clone())

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
            wHisto_i = rt.TH2D("wHisto_%s_%i" %(box, i),"wHisto_%s_%i" %(box, i), nbin, mRmin, mRmax, nbin, rsqMin, rsqMax)
            for ix in range(1,101):
                for iy in range(1,101):
                    # uncorrelated systematics: lepton efficiency data/MC 1%
                    lepFactor = math.pow(1.01,gRnd.Gaus(0., 1.))
                    # uncorrelated systematics: JES corrections ADDITIVE (scaled bin by bin)
                    jesFactor  = gRnd.Gaus(0., 1.)
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
                        # add xsec systematics
                        #if xsecFactor > 0: newvalue = newvalue* + xsecFactor*(wHisto_xsecup[ibox].GetBinContent(ix,iy)-nominal)
                        #else: newvalue = newvalue*math.pow( + xsecFactor*(wHisto_xsecdown[ibox].GetBinContent(ix,iy)-nominal))
                        mXsec, sXsec = getMeanSigma(nominal, wHisto_xsecup[ibox].GetBinContent(ix,iy), wHisto_xsecdown[ibox].GetBinContent(ix,iy))
                        if mXsec > 0: newvalue = newvalue*mXsec/nominal*math.pow(1.+sXsec/mXsec, xsecFactor)
                        # add jes systematics
                        #if jesFactor > 0: newvalue = newvalue + jesFactor*(wHisto_JESup[ibox].GetBinContent(ix,iy)-nominal)
                        #else: newvalue = newvalue + jesFactor*(wHisto_JESdown[ibox].GetBinContent(ix,iy)-nominal)               
                        mJES, sJES = getMeanSigma(nominal, wHisto_JESup[ibox].GetBinContent(ix,iy), wHisto_JESdown[ibox].GetBinContent(ix,iy))
                        if mJES > 0: newvalue = newvalue*mJES/nominal*math.pow(1.+sJES/mJES, jesFactor)
                        # apply the systematic correction to the pdf value
                        # the pdf code return the efficiency in each bin, with an error
                        # that includes the systematic effect. We use this to get a
                        # new value for the content of the bin
                        mPDF = wHisto_pdfCEN[ibox].GetBinContent(ix,iy)
                        sPDF = wHisto_pdfSYS[ibox].GetBinContent(ix,iy)
                        if 1+mPDF > 0.: newvalue = newvalue*(1+mPDF)*math.pow(1+sPDF/(1+mPDF),gRnd.Gaus(0.,1.))
                        #newvalue = newvalue *(1+ gRnd.Gaus(wHisto_pdfCEN[ibox].GetBinContent(ix,iy), wHisto_pdfSYS[ibox].GetBinContent(ix,iy)))
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
        ds = convertTree2Dataset(tree, 100, outputFile, 'Dummy', config, box, 0, -1, -1, write = False)
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
    parser.add_option('-x','--box',dest="box",default=None,type="string",
                  help="Specify only one box")
    parser.add_option('-t','--toys',dest="toys",type="int",default=1000,
                  help="Number of toys")
    parser.add_option('-n','--nbin',dest="nbin",type="int",default=100,
                      help="Number of bins in R2 and mR")
    
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
            convertTree2Dataset(input.Get('EVENTS'), options.nbin, decorator, cfg,options.min,options.max,options.toys)

        else:
            "File '%s' of unknown type. Looking for .root files only" % f
