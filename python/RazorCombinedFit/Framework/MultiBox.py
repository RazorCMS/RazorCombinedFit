from RazorCombinedFit.Framework import Box
import ROOT as rt
import RootTools

class MultiBox(Box.Box):
    """Similar to a box, but we expect several boxes which we combine"""
    
    def __init__(self, name, workspace):
        super(MultiBox,self).__init__(name, [], workspace)
    
    def mergeDataSets(self, categories, inputFiles):
        keys = inputFiles.keys()
        
        data = RootTools.getDataSet(inputFiles[keys[0]],'RMRTree')
        args = data.get(0)
        
        args = ['MergedDataSet','MergedDataSet',args,rt.RooFit.Index(categories),rt.RooFit.Import(keys[0],data)]
        for k in keys[1:]:
            d = RootTools.getDataSet(inputFiles[k],'RMRTree')
            args.append(rt.RooFit.Import(k,d))
        
        a = tuple(args)
        return rt.RooDataSet(*a)
                    
    def linkRealVar(self, var1, var2, expression = None, vars = None):
        """Not very nice: Replace var1 with a RooFormulaVar linking it with var2"""
        ws = rt.RooWorkspace(self.workspace.GetName())
        
        if expression is None: expression = '@0'
        
        args = rt.RooArgList()
        if vars is not None:
            for v in vars:
                args.add(self.workspace.var(v))
        else:
            args.add(self.workspace.var(var2))
        
        ex = rt.RooFormulaVar(var1,'Replace %s with %s' % (var1,var2),expression,args)
        
        getattr(ws,'import')(self.workspace.var(var2),rt.RooFit.Silence())
        getattr(ws,'import')(ex,rt.RooFit.Silence())
        
        for o in RootTools.RootIterator.RootIterator(self.workspace.componentIterator()):
            if not o.GetName() in [var1,var2]:
                getattr(ws,'import')(o,rt.RooFit.RecycleConflictNodes(),rt.RooFit.Silence())
        
        self.workspace = ws
        
    def combine(self, boxes, inputFiles):
        """Both arguments are dictionaries, where the key is the name of the box"""
        pass