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

def writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin):
    
    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+outputBox,'RECREATE')
    print output.GetName()
    for mydata in data: mydata.Write()
    output.Close()

def convertTree2Dataset(tree, outputFile, outputBox, config, box, min, max, nToys, write = True):
    """This defines the format of the RooDataSet"""
    
    workspace = rt.RooWorkspace(box)
    variables = config.getVariablesRange(box,"variables",workspace)

    args = workspace.allVars()
    data = rt.RooDataSet('RMRTree','Selected R and MR',args)
    
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

    #this is the nominal histogram
    wHisto = rt.TH2D("wHisto","wHisto", 100, mRmin, mRmax, 100, rsqMin, rsqMax)
    tree.Project("wHisto", "RSQ:MR", 'LEP_W*W*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
    data = [rt.RooDataHist("RMRHistTree","RMRHistTree",rt.RooArgList(rt.RooArgSet(MR,Rsq)),wHisto),wHisto]

    # JES correctiobns UP
    wHisto_JESup = rt.TH2D("wHisto_JESup","wHisto_JESup", 100, mRmin, mRmax, 100, rsqMin, rsqMax)
    tree.Project("wHisto_JESup", "RSQ_JES_UP:MR_JES_UP", 'LEP_W*W*(MR_JES_UP >= %f && MR_JES_UP <= %f && RSQ_JES_UP >= %f && RSQ_JES_UP <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
    data.append(wHisto_JESup)

    # JES correctiobns DOWN
    wHisto_JESdown = rt.TH2D("wHisto_JESdown","wHisto_JESdown", 100, mRmin, mRmax, 100, rsqMin, rsqMax)
    tree.Project("wHisto_JESdown",  "RSQ_JES_DOWN:MR_JES_DOWN", 'LEP_W*W*(MR_JES_DOWN >= %f && MR_JES_DOWN <= %f && RSQ_JES_DOWN >= %f && RSQ_JES_DOWN <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
    data.append(wHisto_JESdown)

    # xsec UP
    wHisto_xsecup = rt.TH2D("wHisto_xsecup","wHisto_xsecup", 100, mRmin, mRmax, 100, rsqMin, rsqMax)
    tree.Project("wHisto_xsecup", "RSQ:MR",  'LEP_W*W_UP*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
    data.append(wHisto_xsecup)
    
    # xsec correctiobns DOWN
    wHisto_xsecdown = rt.TH2D("wHisto_xsecdown","wHisto_xsecdown", 100, mRmin, mRmax, 100, rsqMin, rsqMax)
    tree.Project("wHisto_xsecdown", "RSQ:MR",  'LEP_W*W_DOWN*(MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (BOX_NUM == %i))' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]))
    data.append(wHisto_xsecdown)
    
    # PDF central (new nominal) and error (for systematics)
    wHisto_pdfCEN, wHisto_pdfSYS = makePDFPlot(tree, wHisto, 100, mRmin, mRmax, 100, rsqMin, rsqMax, boxMap[box])
    wHisto_pdfCEN.SetName("wHisto_pdfCEN")
    wHisto_pdfSYS.SetName("wHisto_pdfSYS")
    data.append(wHisto_pdfCEN)
    data.append(wHisto_pdfSYS)

    # random number generator
    pid = os.getpid()
    now = rt.TDatime()
    today = now.GetDate()
    clock = now.GetTime()
    seed = today+clock+pid+137
    gRnd = rt.TRandom3(seed)

    for i in xrange(nToys):
        # create a copy of the histogram
        wHisto_i = rt.TH2D("wHisto_%i" %i,"wHisto_%i" %i, 100, mRmin, mRmax, 100, rsqMin, rsqMax)
        # correlated systematics: LUMI 4.5% MULTIPLICATIVE
        lumiFactor = gRnd.Gaus(1., 0.045)
        # correlated systematics: xsection ADDITIVE (scaled bin by bin)
        xsecFactor = gRnd.Gaus(0., 1.)
        # correlated systematics: JES corrections ADDITIVE (scaled bin by bin)
        jesFactor  = gRnd.Gaus(0., 1.)
        for ix in range(1,101):
            for iy in range(1,101):
                # starting value
                nominal = wHisto.GetBinContent(ix,iy)
                if nominal != 0:
                    # uncorrelated systematics: lepton efficiency data/MC 1% [to check with Emanuele]
                    lepFactor = gRnd.Gaus(1., 0.01)
                    # compute the total
                    # add lumi systematics
                    newvalue = nominal*lumiFactor
                    if box != "Had": newvalue = newvalue*lepFactor
                    # add xsec systematics
                    if xsecFactor > 0: newvalue = newvalue + xsecFactor*(wHisto_xsecup.GetBinContent(ix,iy)-nominal)
                    else: newvalue = newvalue + xsecFactor*(wHisto_xsecdown.GetBinContent(ix,iy)-nominal)
                    # add jes systematics
                    if jesFactor > 0: newvalue = newvalue + jesFactor*(wHisto_JESup.GetBinContent(ix,iy)-nominal)
                    else: newvalue = newvalue + jesFactor*(wHisto_JESdown.GetBinContent(ix,iy)-nominal)               
                    # apply the systematic correction to the pdf value
                    # the pdf code return the efficiency in each bin, with an error
                    # that includes the systematic effect. We use this to get a
                    # new value for the content of the bin
                    newvalue = newvalue *(1+ gRnd.Gaus(wHisto_pdfCEN.GetBinContent(ix,iy), wHisto_pdfSYS.GetBinContent(ix,iy)))
                    # fill histogram
                    wHisto_i.SetBinContent(ix,iy,newvalue)
                else:
                    wHisto_i.SetBinContent(ix,iy,nominal)                    
                continue
            continue
        data.append(wHisto_i)
        data.append(rt.RooDataHist("RMRHistTree_%i" %i,"RMRHistTree_%i" %i,rt.RooArgList(rt.RooArgSet(MR,Rsq)),wHisto_i))
        del wHisto_i
        #print data.sum(False)

    if write:
        writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin)
                    
    return data

def printEfficiencies(tree, outputFile, config, flavour):
    """Backout the MC efficiency from the weights"""
    print 'ERROR:: This functionality produces incorrect results as we\'re missing a factor somewhere...'
    
    cross_section = cross_sections[flavour]
    
    for box in boxMap:
        ds = convertTree2Dataset(tree, outputFile, 'Dummy', config, box, 0, -1, -1, write = False)
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
            if not options.eff:
                if options.box != None:
                    convertTree2Dataset(input.Get('EVENTS'), decorator, options.box+'.root', cfg,options.box,options.min,options.max,options.toys)
                else:
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'Had.root', cfg,'Had',options.min,options.max,options.toys)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'Ele.root', cfg,'Ele',options.min,options.max,options.toys)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'Mu.root', cfg,'Mu',options.min,options.max,options.toys)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'MuMu.root', cfg,'MuMu',options.min,options.max,options.toys)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'MuEle.root', cfg,'MuEle',options.min,options.max,options.toys)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'EleEle.root', cfg,'EleEle',options.min,options.max,options.toys)
            else:
                printEfficiencies(input.Get('EVENTS'), decorator, cfg, options.flavour)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
