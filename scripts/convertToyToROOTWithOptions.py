from optparse import OptionParser
import ROOT as rt
import sys, os

def defineParser():
    parser = OptionParser()

    parser.add_option('-d','--dir',dest="dir",type="string",default="",
                  help="The output directory to use")
    parser.add_option('-n','--num',dest="num",type="int", default=3500,
                  help="The number of toys to convert")
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('--box',dest="box",type="string",default='Had',
                  help="Name of the box to use when reading the config")
    parser.add_option('-i','--input',dest="input",type="string",default='frtoydata_%s_%d.txt',
                  help="Name of the config file to use")
    return parser
    
    
if __name__ == '__main__':
    
    parser = defineParser()
    (options,args) = parser.parse_args()
    
    MR = rt.RooRealVar("MR", "MR", 300., 7000.)
    Rsq = rt.RooRealVar("Rsq", "Rsq", 0.09, 0.5)

    if options.config is not None:
    
        from RazorCombinedFit.Framework import Config
        cfg = Config.Config(options.config)
        
        workspace = rt.RooWorkspace(options.box)
        for value in cfg.getVariables(options.box):
            workspace.factory(value)
        cfg.getVariablesRange(options.box, 'variables', workspace)
        
        MR = workspace.var('MR')
        Rsq = workspace.var('Rsq')

    dir = options.dir

    for i in xrange(options.num):
        tree = rt.TTree()
        #tree.ReadFile(sys.argv[i],"MR/D:Rsq/D")
        filename = options.input % (options.box,i)
        if not os.path.exists(filename):
            print "File '%s' does not exist." % filename
            sys.exit(-1)
        tree.ReadFile(filename,"MR/D:Rsq/D")
        if tree.GetEntries() <1: continue
        mydata =  rt.RooDataSet("RMRTree","RMRTree",tree, rt.RooArgSet(MR, Rsq))
        myfile = rt.TFile.Open(filename.replace('.txt','.root'), "recreate")
        mydata.Write()
        myfile.Close()
        del tree
        del mydata
        continue


        
        
