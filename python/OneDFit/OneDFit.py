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
        
        frHad = boxes['Had'].fit(fileIndex['Had'],None, rt.RooFit.PrintEvalErrors(-1))
        self.store(frHad)
        
        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box)