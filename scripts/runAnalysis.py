from optparse import OptionParser
import ROOT as rt

class Marker(object):
    pass

def defineParser():
    parser = OptionParser()
    parser.add_option('-b','--batch',dest="batch",action="store_true", default=True,
                  help="Run in batch mode for plotting")    
    parser.add_option('-a','--analysis',dest="analysis",type="string",
                  help="Name of the analysis to run")
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('-o','--output',dest="output",type="string", default='razor_output.root',
                  help="Name of the root file to store everything in")
    parser.add_option('-t','--toys',dest="toys",type="int", default=0,
                  help="The number of toys to run")
    parser.add_option('--save-toys',dest="save_toys",action="store_true", default=False,
                  help="Save the toys as text files for future use.")
    parser.add_option('--save-toys-from-fit',dest="save_toys_from_fit",type="string", default="none",
                  help="Save the toys as text files for future use. Sample from covariance matrix.")
    parser.add_option('-s','--seed',dest="seed",type="int", default=0,
                  help="The random seed to start with")
    parser.add_option('-i','--input',dest="input", default=None,metavar='FILE',
                  help="An input file to read fit results and workspaces from")
    parser.add_option('--simultaneous',dest="simultaneous", default=False,action='store_true',
                  help="Run the simultaneous fit")
    parser.add_option('-l','--limit',dest="limit", default=False,action='store_true',
                  help="Run the model-dependent limit setting code")
    parser.add_option('-m','--model-independent-limit',dest="model_independent_limit", default=False,action='store_true',
                  help="Run the model-independent limit setting code")
    return parser

if __name__ == '__main__':

    parser = defineParser()
    (options,args) = parser.parse_args()    
    print 'Running analysis %s...' % options.analysis
    print '\t with the files %s' % ', '.join(args)
    

    (options,args) = parser.parse_args()
    
    rt.RooRandom.randomGenerator().SetSeed(options.seed)
    
    if options.config is None:
        import inspect, os
    
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(Marker)))
        options.config = os.path.join(topDir,'..','config','boxConfig.cfg')    
    
    from RazorCombinedFit.Framework import Config
    cfg = Config.Config(options.config)
    
    #from OneDFit import OneDFit
    from OneDFitnew import OneDFit
    from TwoDFit import TwoDFit
    from DalglishFit import DalglishFit
    from SingleBoxFit import SingleBoxFit
    
    if options.analysis is not None:
        a = [OneDFit.OneDAnalysis(options.output, cfg),TwoDFit.TwoDAnalysis(options.output, cfg),
             DalglishFit.DalglishAnalysis(options.output, cfg), SingleBoxFit.SingleBoxAnalysis(options.output, cfg)]
        for aa in a:
            if aa.name == options.analysis:
                aa.options = options
                print "Running analysis '%s'" % aa.name
                if options.toys > 0:
                    aa.runtoys(args, options.toys)
                else:
                    aa.analysis(args)
                    if options.limit:    
                        aa.limit(args)
                aa.final()
        
    else:
        parser.error("You need to specify an analysis. See --help")    
    
