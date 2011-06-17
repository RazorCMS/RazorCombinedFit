import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis

class OneDAnalysis(Analysis.Analysis):
    
    def __init__(self, outputFile):
        super(OneDAnalysis,self).__init__('OneDFit',outputFile)
    
    def analysis(self, inputFiles):
        
        fileIndex = self.indexInputFiles(inputFiles)
        
        import SingleRValueBox
        boxes = {}
        
        boxes['Had'] = SingleRValueBox.SingleRValueBox('Had', ['MR[250,1500]'])
        boxes['Had'].define(fileIndex['Had'],{})
        boxes['Had'].workspace.Print('V')