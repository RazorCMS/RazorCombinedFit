import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis

class OneDAnalysis(Analysis.Analysis):
    
    def __init__(self, outputFile, config):
        super(OneDAnalysis,self).__init__('OneDFit',outputFile, config)
    
    def analysis(self, inputFiles):
        
        fileIndex = self.indexInputFiles(inputFiles)
        
        import SingleRValueBox
        boxes = {}
        
        boxes['Had'] = SingleRValueBox.SingleRValueBox('Had', self.config.getVariables('Had'))
        boxes['Had'].define(fileIndex['Had'],{'rcuts':self.config.getRCuts('Had'),'useC++':True})
        boxes['Had'].workspace.Print('V')
        
        boxes['Had'].fit(fileIndex['Had'])
        