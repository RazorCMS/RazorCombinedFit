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
        
        boxes['Mu'] = TwoDBox.TwoDBox('Mu', self.config.getVariables('Mu'))
        boxes['Mu'].define(fileIndex['Mu'],{'rcuts':self.config.getRCuts('Mu')})
        print 'Variables'
        boxes['Mu'].workspace.allVars().Print('V')
        print 'Workspace'
        boxes['Mu'].workspace.Print('V')

        # perform the fit
        frMu = boxes['Mu'].fit(fileIndex['Mu'],None, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
        self.store(frMu)

        # plot the result
        frameMR = boxes['Mu'].plotMR(fileIndex['Mu'])
        self.store(frameMR)
        frameR = boxes['Mu'].plotRsq(fileIndex['Mu'])
        self.store(frameR)
        frame2D = boxes['Mu'].plotRsqMR(fileIndex['Mu'])
        self.store(frame2D)

        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box)

