from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path

class Marker:
    pass 

def writeCocktail(box, files):
    """Write a cocktail file using the weights from the datasets"""
    
    components = [os.path.basename(f).split('_')[0] for f in files]
    if len(components) != len(set(components)):
        raise Exception('Some components not unique for box %s: %s' % (box,components))
    
    ds = []
    for f in files:
        ds.append(RootTools.getDataSet(f,'RMRTree'))
    if not ds:
        raise Exception('Not enough datasets found: %i' % len(ds))
    print files
    print ds
    row = ds[0].get()
    row.Print("V")
    
    mRmin = row['MR'].getMin()
    rsqMin = row['Rsq'].getMin()
    rMin = rt.TMath.Sqrt(rsqMin)
    
    tData = rt.RooDataSet('RMRTree','Total Dataset',row)
    for d in ds:
        tData.append(d)
    wData = rt.RooDataSet('RMRTree','Weighted Cocktail',tData,row,'MR>0','W')

    output = rt.TFile.Open("SMCocktail_MR"+str(mRmin)+"_R"+str(rMin)+"_"+box+'.root','RECREATE')
    print 'Writing',output.GetName()
    wData.Write()
    output.Close()
   
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
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(writeCocktail)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    cfg = Config.Config(options.config)
    
    print 'Input files are %s' % ', '.join(args)

    boxes = {}
    for f in args:
        if f.lower().endswith('.root'):
            input = rt.TFile(f)
            decorator = f[:-5]
            
            box = decorator.split('_')[-1]
            if not boxes.has_key(box):
                boxes[box] = []
            boxes[box].append(f)
            
        else:
            "File '%s' of unknown type. Looking for .root files only" % f

    for box, files in boxes.iteritems():
        writeCocktail(box, files)
