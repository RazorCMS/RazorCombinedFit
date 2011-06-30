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
        
        boxes['EleEle'] = TwoDBox.TwoDBox('EleEle', self.config.getVariables('EleEle'))
        boxes['EleEle'].define(fileIndex['EleEle'],{'rcuts':self.config.getRCuts('EleEle')})
        print 'Variables'
        boxes['EleEle'].workspace.allVars().Print('V')
        print 'Workspace'
        boxes['EleEle'].workspace.Print('V')
        
        frEleEle = boxes['EleEle'].fit(fileIndex['EleEle'],None, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
        self.store(frEleEle)
        
        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box)
