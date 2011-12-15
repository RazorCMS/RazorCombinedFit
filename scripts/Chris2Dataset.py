from optparse import OptionParser
import os

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'Mu':3,'Ele':4,'Had':5}
cross_sections = {'SingleTop_s':4.21,'SingleTop_t':64.6,'SingleTop_tw':10.6,\
                               'TTj':157.5,'Zll':3048,'Znn':2*3048,'Wln':31314,\
                               'WW':43,'WZ':18.2,'ZZ':5.9,'Vgamma':173
                               }
lumi = 1.0

def writeTree2DataSet(data, outputFile, outputBox, rMin, mRmin, bMin):
    
    if bMin >= 0:
        output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_nBtag_'+str(bMin)+'_'+outputBox,'RECREATE')
    else:
        output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+'_'+outputBox,'RECREATE')
    print output.GetName()
    data.Write()
    output.Close()
    return data.numEntries()

def convertTree2Dataset(tree, outputFile, outputBox, config, box, min, max, bMin, run, write = True):
    """This defines the format of the RooDataSet"""
    
    workspace = rt.RooWorkspace(box)
    variables = config.getVariablesRange(box,"variables",workspace)
    workspace.factory('nBtag[0,0,2.0]')
    workspace.factory('W[0,0,+INF]')

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

    #iterate over selected entries in the input tree    
    tree.Draw('>>elist','MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (BOX_NUM == %i)' % (mRmin,mRmax,rsqMin,rsqMax,boxMap[box]),'entrylist')
    elist = rt.gDirectory.Get('elist')
    
    entry = -1;
    while True:
        entry = elist.Next()
        if entry == -1: break
        tree.GetEntry(entry)
        
        if bMin >= 0 and tree.BTAG_NUM < bMin: continue
        
        try:
            if tree.RUN_NUMBER <= run: continue
        except AttributeError:
            pass

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        a.setRealValue('MR',tree.MR)
        a.setRealValue('R',rt.TMath.Sqrt(tree.RSQ))
        a.setRealValue('Rsq',tree.RSQ)
        a.setRealValue('nBtag',tree.BTAG_NUM)
        try:
            a.setRealValue('W',tree.WPU)
        except AttributeError:
            a.setRealValue('W',1.0)
        data.add(a)
    numEntries = data.numEntries()
    if min < 0: min = 0
    if max < 0: max = numEntries
    
    rdata = data.reduce(rt.RooFit.EventRange(min,max))
    if write:
        writeTree2DataSet(rdata, outputFile, outputBox, rMin, mRmin, bMin)
    return rdata

def printEfficiencies(tree, outputFile, config, flavour):
    """Backout the MC efficiency from the weights"""
    print 'ERROR:: This functionality produces incorrect results as we\'re missing a factor somewhere...'
    
    cross_section = cross_sections[flavour]
    
    for box in boxMap:
        ds = convertTree2Dataset(tree, outputFile, 'Dummy', config, box, 0, -1, -1, write = False)
        row = ds.get(0)
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
    parser.add_option('-b','--btag',dest="btag",type="int",default=-1,
                  help="The maximum number of Btags to allow")     
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
            print decorator
            if not options.eff:
                #dump the trees for the different datasets
                if options.box != None:
                    convertTree2Dataset(input.Get('EVENTS'), decorator, options.box+'.root', cfg,options.box,options.min,options.max,options.btag,options.run)
                else:
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'Had.root', cfg,'Had',options.min,options.max,options.btag,options.run)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'Ele.root', cfg,'Ele',options.min,options.max,options.btag,options.run)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'Mu.root', cfg,'Mu',options.min,options.max,options.btag,options.run)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'MuMu.root', cfg,'MuMu',options.min,options.max,options.btag,options.run)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'MuEle.root', cfg,'MuEle',options.min,options.max,options.btag,options.run)
                    convertTree2Dataset(input.Get('EVENTS'), decorator, 'EleEle.root', cfg,'EleEle',options.min,options.max,options.btag,options.run)
            else:
                printEfficiencies(input.Get('EVENTS'), decorator, cfg, options.flavour)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
