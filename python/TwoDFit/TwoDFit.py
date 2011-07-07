import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis
import RootTools

class TwoDAnalysis(Analysis.Analysis):
    
    def __init__(self, outputFile, config):
        super(TwoDAnalysis,self).__init__('TwoDFit',outputFile, config)
    
    def merge(self, workspace, box):
        """Import the contents of a box workspace into the master workspace while enforcing some namespaceing"""
        for o in RootTools.RootIterator.RootIterator(workspace.componentIterator()):
            if hasattr(o,'Class') and o.Class().InheritsFrom('RooRealVar'):
                continue
            self.importToWS(o, rt.RooFit.RenameAllNodes(box),rt.RooFit.RenameAllVariables(box)) 
    
    def analysis(self, inputFiles):
        
        fileIndex = self.indexInputFiles(inputFiles)
        
        import TwoDBox
        boxes = {}

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Configuring box %s' % box
            boxes[box] = TwoDBox.TwoDBox(box, self.config.getVariables(box, "variables"))
            boxes[box].defineSet("pdf1pars", self.config.getVariables(box, "pdf1"))
            boxes[box].defineSet("pdf2pars", self.config.getVariables(box, "pdf2"))
            boxes[box].defineSet("otherpars", self.config.getVariables(box, "others"))
            boxes[box].define(fileName)
            
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
            
            #merge box with top level workspace
            self.merge(boxes[box].workspace, box)
        
        #merge the boxes together in some way
        import TwoDMultiBoxSim
        multi = TwoDMultiBoxSim.TwoDMultiBoxSim(self.workspace)
        multi.combine(boxes, fileIndex)
        
        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box, dir=box)

