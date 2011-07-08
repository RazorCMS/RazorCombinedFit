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

    def defineSet(self, name, variables):
        self.workspace.defineSet(name,'')
        for v in variables:
            r = self.workspace.factory(v)
            self.workspace.extendSet(name,r.GetName())            
        
    def getFitPDF(self, name='fitmodel',graphViz='graphViz'):
        pdf = self.workspace.pdf(name)
        #save as a dotty file for easy inspection
        pdf.graphVizTree('%s_%s.dot' % (pdf.GetName(),graphViz))
        return pdf
    
    def importToWS(self, *args):
        """Utility function to call the RooWorkspace::import methods"""
        return getattr(self.workspace,'import')(*args)
    
    def fit(self, inputFile, reduce = None, *options):
        """Take the dataset and fit it with the top level pdf. Return the fitresult"""
        
        if inputFile.__class__.__name__ == 'RooDataSet':
            data = inputFile
        else:
            data = RootTools.getDataSet(inputFile,'RMRTree', reduce)

        opt = rt.RooLinkedList()
        #always save the fit result
        opt.Add(rt.RooFit.Save(True))
        #automagically determine the number of cpus
        opt.Add(rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))
        for o in options:
            opt.Add(o)
        
        pdf = self.getFitPDF()
        result = pdf.fitTo(data, opt)
        result.Print('V')
        if result.status() != 0 or result.covQual() != 3:
            print 'WARNING:: The fit did not converge with high quality. Consider this result suspect!'
        
        return result 

    def plotObservables(self, inputFile):
        """Make control plots for variables defined in the 'variables' part of the config"""

        data = RootTools.getDataSet(inputFile,'RMRTree')
        fitmodel = self.workspace.pdf("fitmodel")
        
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
        
        
    def define(self, inputFile, cuts):
        pass
    
    def plot(self, inputFile, store, box):
        [store.store(p, dir = box) for p in self.plotObservables(inputFile)]
    
