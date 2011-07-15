from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

def convertTree2Dataset(tree, outputFile, outputBox, config, box, min, max):
    """This defines the format of the RooDataSet"""
    
    boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'Mu':3,'Ele':4,'Had':5}
    
    workspace = rt.RooWorkspace(box)
    variables = config.getVariables(box,"variables")
    for v in variables:
        workspace.factory(v)
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
    tree.Draw('>>elist','MR >= %f && MR <= %f && RSQ >= %f && RSQ <= %f && (BOX_NUM == %i)' % (mRmin,mRmax,rsqMin,rsqMax, boxMap[box]),'entrylist')
    elist = rt.gDirectory.Get('elist')
    
    entry = -1;
    while True:
        entry = elist.Next()
        if entry == -1: break
        tree.GetEntry(entry)

        #set the RooArgSet and save
        a = rt.RooArgSet(args)
        a.setRealValue('MR',tree.MR)
        a.setRealValue('R',rt.TMath.Sqrt(tree.RSQ))
        a.setRealValue('Rsq',tree.RSQ)
        a.setRealValue('nBtag',tree.BTAG_NUM)
        a.setRealValue('W',tree.WPU)
        data.add(a)
    numEntries = data.numEntries()
    if min < 0: min = 0
    if max < 0: max = numEntries
    
    rdata = data.reduce(rt.RooFit.EventRange(min,max))

    output = rt.TFile.Open(outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+"_"+outputBox,'RECREATE')
    print 'Writing',outputFile+"_MR"+str(mRmin)+"_R"+str(rMin)+"_"+outputBox
    rdata.Write()
    output.Close()
    
    return rdata.numEntries()
    
if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('--max',dest="max",type="int",default=-1,
                  help="The last event to take from the input Dataset")
    parser.add_option('--min',dest="min",type="int",default=0,
                  help="The first event to take from the input Dataset")  
    (options,args) = parser.parse_args()
    
    if options.config is None:
        import inspect, os
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(convertTree2Dataset)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    
    print 'Input files are %s' % ', '.join(args)
    for f in args:
        if f.lower().endswith('.root'):
            input = rt.TFile(f)
            decorator = f[:-5]
            
            #dump the trees for the different datasets
            convertTree2Dataset(input.Get('EVENTS'), decorator, 'Had.root', cfg,'Had',options.min,options.max)
            convertTree2Dataset(input.Get('EVENTS'), decorator, 'Ele.root', cfg,'Ele',options.min,options.max)
            convertTree2Dataset(input.Get('EVENTS'), decorator, 'Mu.root', cfg,'Mu',options.min,options.max)
            convertTree2Dataset(input.Get('EVENTS'), decorator, 'MuMu.root', cfg,'MuMu',options.min,options.max)
            convertTree2Dataset(input.Get('EVENTS'), decorator, 'MuEle.root', cfg,'MuEle',options.min,options.max)
            convertTree2Dataset(input.Get('EVENTS'), decorator, 'EleEle.root', cfg,'EleEle',options.min,options.max)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
