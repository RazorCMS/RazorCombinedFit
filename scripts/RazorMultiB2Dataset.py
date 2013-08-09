from optparse import OptionParser
import os

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

boxMap = {'MuEle':[0],'MuMu':[1],'EleEle':[2]}
lumi = 19.3

def writeTree2DataSet(data, outputFile, outputBox, gammaRmin, mDRmin, label):
    
    output = rt.TFile.Open(outputFile+"_MDR"+str(mDRmin)+'_gammaR'+str(gammaRmin)+'_'+label+outputBox,'RECREATE')
    print output.GetName()
    data.Write()
    output.Close()
    return data.numEntries()

def convertTree2Dataset(tree, outputFile, outputBox, config, box, min, max, run, useWeight, isMC, write = True):
    """This defines the format of the RooDataSet"""
    workspace = rt.RooWorkspace(box)
    variables = config.getVariablesRange(box,"variables",workspace)
    workspace.factory('W[0,0,+INF]')

    args = workspace.allVars()
    data = rt.RooDataSet('RMRTree','Selected MDR gammaR',args)
    
    #we cut away events outside our MDR gammaR window
    
    mDRmin = args['MDR'].getMin()
    mDRmax = args['MDR'].getMax()
    
    gammaRmin = args['gammaR'].getMin()
    gammaRmax = args['gammaR'].getMax()
    
    nBtagmin = args['nBtag'].getMin()
    nBtagmax = args['nBtag'].getMax()

    dPhillmin = args['dPhill'].getMin()
    dPhillmax = args['dPhill'].getMax()
    
    #nbins = 5
    #cutoffs = []
    #for i in range(nbins):
    #    cutoffs.append(dPhillmax / nbins)
        
    label = ""
    if useWeight:
        label += "WEIGHT_"

    #iterate over selected entries in the input tree
    boxCut = "(" + "||".join(["BOX_NUM==%i"%cut for cut in boxMap[box]]) + ")"
    print 'iterated over input tree entries'
    

    tree.Draw('>>elist','gammaRList[1] >= %f && gammaRList[1] <= %f && dPhi_ll >= %f && dPhi_ll < %f && %s' % (gammaRmin,gammaRmax,dPhillmin,dPhillmax,boxCut),'entrylist')

       
    elist = rt.gDirectory.Get('elist')
    print elist
    entry = -1;
    while True:
        entry = elist.Next()
        print entry
        if entry == -1: break
        tree.GetEntry(entry)
        

        runrange = run.split(":")
        if len(runrange) == 2:
            minrun = int(runrange[0])
            maxrun = int(runrange[1])
            if tree.RUN_NUM < minrun: continue
            if tree.RUN_NUM > maxrun: continue

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        
        a.setRealValue('MDR',tree.shatR_bl*(1.0/(2000.*tree.gammaRList[1])))
        a.setRealValue('gammaR',tree.gammaRList[1])
        a.setRealValue('nBtag',tree.nBtag)
        a.setRealValue('dPhill',tree.dPhi_ll)
        if useWeight:
            try:
                a.setRealValue('W',tree.WXSEC*lumi/5.0)
            except AttributeError:
                a.setRealValue('W',1.0)
        else:
            a.setRealValue('W',1.0)
        data.add(a)
        
    numEntries = data.numEntries()
    if min < 0: min = 0
    if max < 0: max = numEntries
    
    rdata = data.reduce(rt.RooFit.EventRange(min,max))
    wdata = rt.RooDataSet(rdata.GetName(),rdata.GetTitle(),rdata,rdata.get(),"MDR>=0.","W")
    print "Number of Entries in Box %s = %d"%(box,rdata.numEntries())
    print "Sum of Weights in Box %s = %.1f"%(box,wdata.sumEntries())
    if write:
        if useWeight:
            writeTree2DataSet(wdata, outputFile, outputBox, gammaRmin, mDRmin, label)
        else:  
            writeTree2DataSet(rdata, outputFile, outputBox, gammaRmin, mDRmin, label)
    return rdata

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('--max',dest="max",type="int",default=-1,
                  help="The last event to take from the input Dataset")
    parser.add_option('--min',dest="min",type="int",default=0,
                  help="The first event to take from the input Dataset") 
    parser.add_option('-f','--flavour',dest="flavour",default='TTj',
                  help="The flavour of MC used as input")
    parser.add_option('-r','--run',dest="run",default="none",type="string",
                  help="The run range in the format min_run_number:max_run_number")
    parser.add_option('-d','--dir',dest="outdir",default="./",type="string",
                  help="Output directory to store datasets")
    parser.add_option('-x','--box',dest="box",default=None,type="string",
                  help="Specify only one box")
    parser.add_option('-w','--weight',dest="useWeight",default=False,action='store_true',
                  help="Use weights, if available, default is WXSEC")
    parser.add_option('--MC',dest="isMC",default=False,action='store_true',
                  help="Slightly different variables for MC")
      
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
            #dump the trees for the different datasets
            if options.box != None:
                convertTree2Dataset(input.Get('outTree'), decorator, options.box+'.root', cfg,options.box,options.min,options.max,options.run,options.useWeight,options.isMC)
            else:
                convertTree2Dataset(input.Get('outTree'), decorator, 'MuEle.root', cfg,'MuEle',options.min,options.max,options.run,options.useWeight,options.isMC)
                convertTree2Dataset(input.Get('outTree'), decorator, 'MuMu.root', cfg,'MuMu',options.min,options.max,options.run,options.useWeight,options.isMC)
                convertTree2Dataset(input.Get('outTree'), decorator, 'EleEle.root', cfg,'EleEle',options.min,options.max,options.run,options.useWeight,options.isMC)
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
