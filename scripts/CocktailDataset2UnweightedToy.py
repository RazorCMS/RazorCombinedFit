#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config
import os.path

def getUnweightedToy(box, files, outdir):
    """Get the cocktail dataset from the file"""
    
    components = [os.path.basename(f).split('_')[0] for f in files]
    if len(components) != len(set(components)):
        raise Exception('Some components not unique for box %s: %s' % (box,components))

    f = files[0]
    wdata = RootTools.getDataSet(f,'RMRTree')
    if not wdata:
        raise Exception('No dataset found')
        
    row = wdata.get()
    row.Print("V")

    MR = row['MR']
    Rsq = row['Rsq']
    nBtag = row['nBtag']
    CHARGE = row['CHARGE']
    
    varSet = rt.RooArgSet(MR,Rsq,nBtag,CHARGE)
    varList = rt.RooArgList(MR,Rsq,nBtag)
    uwdata = rt.RooDataSet('RMRTree','Unweighted Cocktail',varSet)
    

    
    mRmin = row['MR'].getMin()
    mRmax = row['MR'].getMax()
    rsqMin = row['Rsq'].getMin()
    rsqMax = row['Rsq'].getMax()
    nbtagMin = row['nBtag'].getMin()
    nbtagMax = row['nBtag'].getMax()
    
    rMin = rt.TMath.Sqrt(rsqMin)
    
    myTH3 = rt.TH3D("h%s"%box, "h%s"%box, 100, mRmin, mRmax, 100, rsqMin, rsqMax, int(nbtagMax-nbtagMin), nbtagMin, nbtagMax)
    #myTH2 = rt.TH2D("h", "h", 100, mRmin, mRmax, 100, rsqMin, rsqMax)

    # fills automatically with weight
    wdata.fillHistogram(myTH3, varList,"MR>0")
    
    
    print wdata.weight()
    Nev = myTH3.Integral()
    Nent = myTH3.GetEntries()
    print "weighted events %.1f"% Nev
    print "entries  %d"% Nent
    Npois = rt.RooRandom.randomGenerator().Poisson(Nev)
    for i in range(0,int(Nev)):
        myMR = rt.Double()
        myRsq = rt.Double()
        mynBtag = rt.Double()
        myTH3.GetRandom3(myMR,myRsq,mynBtag)
        mynBtag = int(mynBtag)
        varSet.setRealValue('MR',myMR)
        varSet.setRealValue('Rsq',myRsq)
        varSet.setRealValue('nBtag',mynBtag)
        varSet.setRealValue('CHARGE',1.0)
        uwdata.add(varSet)
   
    output = rt.TFile.Open(outdir+"/SMCocktail_GENTOY_MR"+str(mRmin)+"_R"+str(rMin)+"_"+box+'.root','RECREATE')
    print 'Writing',output.GetName()
    uwdata.Write()
    myTH3.Write()
    output.Close()
   
   
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
        getUnweightedToy(box, files, options.outdir)
