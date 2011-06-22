from optparse import OptionParser

class Marker(object):
    pass

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-a','--analysis',dest="analysis",type="string",
                  help="Name of the analysis to run")
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('-o','--output',dest="output",type="string", default='razor_output.root',
                  help="Name of the root file to store everything in")
    (options,args) = parser.parse_args()
    
    print 'Running analysis %s...' % options.analysis
    print '\t with the files %s' % ', '.join(args)
    

    (options,args) = parser.parse_args()
    
    if options.config is None:
        import inspect, os
    
        topDir = os.path.abspath(os.path.dirname(inspect.getsourcefile(Marker)))
        options.config = os.path.join(topDir,'boxConfig.cfg')    
    
    from RazorCombinedFit.Framework import Config
    cfg = Config.Config(options.config)
    
    from OneDFit import OneDFit
    if options.analysis is not None:
        a = [OneDFit.OneDAnalysis(options.output, cfg)]
        for aa in a:
            if aa.name == options.analysis:
                print "Running analysis '%s'" % aa.name
                aa.analysis(args)
                aa.final()
        
    else:
        parser.error("You need to specify an analysis. See --help")    
    