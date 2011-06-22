import ROOT as rt
import RootTools

class Box(object):
    
    def __init__(self, name, variables):
        self.name = name
        self.workspace = rt.RooWorkspace(name)
        for v in variables:
            self.workspace.factory(v)
    
    def getFitPDF(self):
        pdf = self.workspace.pdf('fitmodel')
        #save as a dotty file for easy inspection
        pdf.graphVizTree('%s_graphViz.dot' % pdf.GetName())
        return pdf
    
    def fit(self, inputFile, reduce = None, *options):
        """Take the dataset and fit it with the top level pdf. Return the fitresult"""
        
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
        return result 
        
    def define(self, inputFile, cuts):
        pass