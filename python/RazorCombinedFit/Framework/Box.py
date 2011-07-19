import ROOT as rt
import RootTools

class Box(object):
    
    def __init__(self, name, variables, workspace = None):
        self.name = name
        
        if workspace is None:
            self.workspace = rt.RooWorkspace(name)
        else:
            self.workspace = workspace
        
        self.workspace.defineSet('variables','')
        for v in variables:
            r = self.workspace.factory(v)
            self.workspace.extendSet('variables',r.GetName())
            
        self.fitmodel = 'fitmodel'

    def defineSet(self, name, variables):
        self.workspace.defineSet(name,'')
        for v in variables:
            r = self.workspace.factory(v)
            self.workspace.extendSet(name,r.GetName())            
        
    def getFitPDF(self, name=None,graphViz='graphViz'):
        if name is None:
            pdf = self.workspace.pdf(self.fitmodel)
        else:
            pdf = self.workspace.pdf(name)
        #save as a dotty file for easy inspection
        if graphViz is not None:
            pdf.graphVizTree('%s_%s.dot' % (pdf.GetName(),graphViz))
        return pdf
    
    def getMCStudy(self, fitmodel=None, genmodel=None, *options):
        if fitmodel is None:
            fitmodel = self.fitmodel
        if genmodel is None:
            genmodel = self.fitmodel
        
        fit = self.getFitPDF(fitmodel,graphViz=None)
        gen = self.getFitPDF(genmodel,graphViz=None)
        vars = self.workspace.set('variables')
        
        #make a list of arguments for FitOptions using unpacking
        opt = []
        #always save the fit result
        opt.append(rt.RooFit.Save(True))
        #automagically determine the number of cpus
        opt.append(rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))
        for o in options:
            opt.append(o)
        opt = tuple(opt)
        
        study = rt.RooMCStudy(gen,vars,rt.RooFit.Extended(True),rt.RooFit.FitModel(fit),rt.RooFit.FitOptions(*opt))
        return study
        
    
    def importToWS(self, *args):
        """Utility function to call the RooWorkspace::import methods"""
        return getattr(self.workspace,'import')(*args)
    
    def fit(self, inputFile, reduce = None, *options):
        """Take the dataset and fit it with the top level pdf. Return the fitresult"""

        data = RootTools.getDataSet(inputFile,'RMRTree', reduce)
        return self.fitData(self.getFitPDF(), data, *options)
    
    def fitData(self, pdf, data, *options):
        """Take the dataset and fit it with the top level pdf. Return the fitresult"""
        
        opt = rt.RooLinkedList()
        #always save the fit result
        opt.Add(rt.RooFit.Save(True))
        #automagically determine the number of cpus
        opt.Add(rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))
        for o in options:
            opt.Add(o)
        
        result = pdf.fitTo(data, opt)
        result.Print('V')
        if result.status() != 0 or result.covQual() != 3:
            print 'WARNING:: The fit did not converge with high quality. Consider this result suspect!'
        
        return result 

    def plotObservables(self, inputFile, name = None):
        """Make control plots for variables defined in the 'variables' part of the config"""

        if name is None:
            name = self.fitmodel

        data = RootTools.getDataSet(inputFile,'RMRTree')
        fitmodel = self.workspace.pdf(name)
        
        plots = []
        
        parameters = self.workspace.set("variables")
        for p in RootTools.RootIterator.RootIterator(parameters):
            frame = p.frame()
            frame.SetName("autoVarPlot_%s" % p.GetName())

            data.plotOn(frame)
            fitmodel.plotOn(frame, rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))
            fitmodel.paramOn(frame)
            plots.append(frame)
            
        return plots

    def fixVariable(self, var, mean, sigma, model=None):
        """Add a Gaussian penalty term for a semi-fixed parameter"""
        
        if model is None:
            model = self.fitmodel
        
        var_m = '%s_mean[%f]' % (var,mean)
        if self.workspace.var('%s_s' % var):
            var_s = '%s_s' % var
        else:
            var_s = '%s_s[%f]' % (var,sigma)
        
        self.workspace.factory('RooGaussian::%s_penalty(%s,%s,%s)' % (var,var,var_m,var_s))
        fitmodel = self.workspace.pdf(model)
        modelName = '%s_fix%s' % (model, var)
        self.workspace.factory('PROD::%s(%s,%s_penalty)' % (modelName,model,var))
        self.fitmodel = modelName
        print 'Added a Gaussian penalty term for %s: %f\pm %f' % (var,mean,sigma)

    def fixPars(self, label, doFix=rt.kTRUE, setVal=None):
        parSet = self.workspace.allVars()
        for par in RootTools.RootIterator.RootIterator(parSet):
            if label in par.GetName():
                par.setConstant(doFix)
                if setVal is not None: par.setVal(setVal)
    
    def fixParsPenalty(self, label):
        
        allVars = self.workspace.allVars()
        pars = {}
        for p in RootTools.RootIterator.RootIterator(allVars): pars[p.GetName()] = p
        for name, par in pars.iteritems():
            if label in par.GetName():
                if pars.has_key('%s_s' % name):
                    sigma = pars['%s_s' % name].getVal() 
                    self.fixVariable(par.GetName(), par.getVal(),sigma)
                    par.setConstant(False)
    
        
    def define(self, inputFile, cuts):
        pass
    
    def plot(self, inputFile, store, box):
        [store.store(p, dir = box) for p in self.plotObservables(inputFile)]
    
