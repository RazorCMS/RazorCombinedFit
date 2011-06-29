import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis

class TwoDAnalysis(Analysis.Analysis):
    
    def __init__(self, outputFile, config):
        super(TwoDAnalysis,self).__init__('TwoDFit',outputFile, config)
    
    def analysis(self, inputFiles):
        
        fileIndex = self.indexInputFiles(inputFiles)
        
        import TwoDBox
        boxes = {}
        
        boxes['Had'] = TwoDBox.TwoDBox('Had', self.config.getVariables('Had'))
        boxes['Had'].define(fileIndex['Had'],{'rcuts':self.config.getRCuts('Had')})
        print 'Variables'
        boxes['Had'].workspace.allVars().Print('V')
        print 'Workspace'
        boxes['Had'].workspace.Print('V')
        
        #TODO: Will segfault as no PDF is returned
        #frHad = boxes['Had'].fit(fileIndex['Had'],None, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
        #self.store(frHad)
        
        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box)