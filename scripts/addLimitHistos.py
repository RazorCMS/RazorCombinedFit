# Script to produce two histograms in a ROOT file hlz_b (lz values with b-only toys) and hlz_sb (lz values with s+b toys)
# example usage (on lxcms132) : python scripts/addLimitHistos.py -x Had -o Limit_Had.root /data/woodson/SIGNALMODELTOYS/*_Had_*.root

from optparse import OptionParser
import os
import ROOT as rt
import RootTools
from RazorCombinedFit.Framework import Config

boxMap = {'MuEle':0,'MuMu':1,'EleEle':2,'Mu':3,'Ele':4,'Had':5}

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-o','--output',dest="outputname",type="string",default=None,
                  help="Name of the output file to use")
    parser.add_option('-d','--dir',dest="outdir",default="./",type="string",
                  help="Output directory to store datasets")
    parser.add_option('-x','--box',dest="box",default=None,type="string",
                  help="Specify only one box")
    
    (options,args) = parser.parse_args()
    
    print 'Input files are %s' % ', '.join(args)

    hlz_b = rt.TH1D("hlz_b","hlz_b",300,-100,200)
    hlz_sb = rt.TH1D("hlz_sb","hlz_sb",300,-100,200)

    for f in args:
        if f.lower().endswith('.root'):
            input = rt.TFile.Open(f)
            tree=input.Get(options.box+"/myTree")
            tree.Draw('>>elist','','entrylist')
            elist = rt.gDirectory.Get('elist')
            entry = -1;
            while True:
                entry = elist.Next()
                if entry == -1: break
                tree.GetEntry(entry)
                if f.find('BkgSig') == -1: hlz_b.Fill(tree.Lz)
                else: hlz_sb.Fill(tree.Lz)
            input.Close()
        else:
            "File '%s' of unknown type. Looking for .root files only" % f
    
    output = rt.TFile.Open(options.outputname,'RECREATE')
    print 'Writing',output.GetName()
    hlz_b.Write()
    hlz_sb.Write()
    output.Close()
