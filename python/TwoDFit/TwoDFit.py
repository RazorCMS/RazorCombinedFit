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

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Configuring box %s' % box
            boxes[box] = TwoDBox.TwoDBox(box, self.config.getVariables(box))
            boxes[box].define(fileName,{'rcuts':self.config.getRCuts(box)})
            print 'Variables for box %s' % box
            boxes[box].workspace.allVars().Print('V')
            print 'Workspace'
            boxes[box].workspace.Print('V')

            # perform the fit
            fr = boxes[box].fit(fileName,None, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
            self.store(fr, dir=box)
            self.store(fr.correlationHist("correlation_%s" % box), dir=box)
            
            #make any plots required
            boxes[box].plot(fileName, self, box)

        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box, dir=box)

