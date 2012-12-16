import os
import sys
import ROOT as rt
from optparse import OptionParser

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
    parser.add_option('--scale-lumi',dest="scale_lumi",type="int", default=1,
                  help="[ONLY when saving toys] scale the toys statistics by a specificed lumi scale factor")
    parser.add_option('-s','--seed',dest="seed",type="int", default=0,
                  help="The random seed to start with")
    parser.add_option('-i','--input',dest="input", default=None,metavar='FILE',
                  help="An input file to read fit results and workspaces from")
    parser.add_option('--simultaneous',dest="simultaneous", default=False,action='store_true',
                  help="Run the simultaneous fit")
    parser.add_option('-l','--limit',dest="limit", default=False,action='store_true',
                  help="Run the model-dependent limit setting code")
    parser.add_option('--study',dest="study", default=False,action='store_true',
                  help="Run a simple RooMCStudy")    
    parser.add_option('-e','--expected-limit',dest="expectedlimit", default=False,action='store_true',
                  help="Run the model-dependent bkg-only toy MC to compute the expected limit")
    parser.add_option('-m','--model-independent-limit',dest="model_independent_limit", default=False,action='store_true',
                  help="Run the model-independent limit setting code")
    parser.add_option('-x','--xsec',dest="signal_xsec", type="float", default=-99,
                  help="Signal cross section (in pb) for SMSs limit setting")
    parser.add_option('--bjet',dest="doBjet", default=False, action='store_true',
                  help="Run the RazorB analysis")
    parser.add_option('--multijet',dest="doMultijet", default=False, action='store_true',
                  help="Run the Razor MultiJet analysis")
    parser.add_option('--boost',dest="doBoost", default=False, action='store_true',
                  help="Run the Razor Boost analysis")
    parser.add_option('--tau',dest="doTau", default=False, action='store_true',
                  help="Run the Razor Tau analysis")
    parser.add_option('--fit-region',dest="fitregion", type="string", default='FULL',
                  help="Perform the fit in the selected region: FULL, SidebandL, SidebandMR, SidebandRsq")
    parser.add_option('--nosave-workspace',dest="nosave_workspace", default=False,action='store_true',
                  help="Do not save the RooWorkspaces to save disk space for limit setting")
    parser.add_option('--fitmode',dest="fitMode",type="string",default='2D',
                  help="Type of fit to run - 2D, 3D, 4D are all valid options")
    parser.add_option('--btag',dest="btag",action="store_true",default=True,
                  help="Include the btag dimension in the fits")
    parser.add_option('--run-cls',dest="runCLS",action="store_true",default=False,
                  help="Run the 2012 profile style CLS code")        

    return parser

if __name__ == '__main__':

    parser = defineParser()
    (options,args) = parser.parse_args()    
    print 'Running analysis %s...' % options.analysis
    print '\t with the files %s' % ', '.join(args)
    

    (options,args) = parser.parse_args()


    seed = options.seed
    if seed < 0:
        pid = os.getpid()
        now = rt.TDatime()
        today = now.GetDate()
        clock = now.GetTime()
        seed = today+clock+pid+137
        
    rt.RooRandom.randomGenerator().SetSeed(seed)
    
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

    analysis = "INCLUSIVE"
    if options.doBjet: analysis = "BJET"
    if options.doMultijet: analysis = "MULTIJET"
    if options.doBoost: analysis = "BOOST"
    if options.doTau: analysis = "TAU"

    print options
    print args
    
    if options.analysis is not None:
        a = [OneDFit.OneDAnalysis(options.output, cfg),TwoDFit.TwoDAnalysis(options.output, cfg),
             DalglishFit.DalglishAnalysis(options.output, cfg), SingleBoxFit.SingleBoxAnalysis(options.output, cfg, analysis)]
        for aa in a:
            if aa.name == options.analysis:
                aa.options = options
                print "Running analysis '%s'" % aa.name
                if options.toys > 0 and not options.limit:
                    if options.study:
                        aa.toystudy(args, options.toys)
                    else:
                        aa.runtoys(args, options.toys)
                else:
                    aa.analysis(args)
                    if options.limit:
                        if not options.runCLS:
                            aa.limit(args,options.toys)
                        else:
                            aa.limit_profile(args,options.toys)
                aa.final()
        
    else:
        parser.error("You need to specify an analysis. See --help")    
    
