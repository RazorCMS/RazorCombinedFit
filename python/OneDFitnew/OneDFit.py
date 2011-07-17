import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis
import RootTools

class OneDAnalysis(Analysis.Analysis):
    
    def __init__(self, outputFile, config):
        super(OneDAnalysis,self).__init__('OneDFit',outputFile, config)
     
    def analysis(self, inputFiles):
        
        fileIndex = self.indexInputFiles(inputFiles)
        
        import OneDBox
        boxes = {}

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Configuring box %s' % box
            boxes[box] = OneDBox.OneDBox(box, self.config.getVariables(box, "variables"))
            boxes[box].defineSet("pdf1pars", self.config.getVariables(box, "pdf1"))
            boxes[box].defineSet("pdf2pars", self.config.getVariables(box, "pdf2"))
            boxes[box].defineSet("otherpars", self.config.getVariables(box, "others"))
            boxes[box].defineSet("otherpars2", self.config.getVariables(box, "others2"))
            #boxes[box].defineSet("mean", self.config.getVariables(box, "mean"))
            #boxes[box].defineSet("sigma", self.config.getVariables(box, "sigma"))
            
            boxes[box].define(fileName)
            
            print 'Variables for box %s' % box
            boxes[box].workspace.allVars().Print('V')
            print 'Workspace'
            boxes[box].workspace.Print('V')

            # perform the fit
            fr = boxes[box].fit1D(fileName,None, "RMRTree2",rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
            self.store(fr, dir=box)
            self.store(fr.correlationHist("correlation_%s" % box), dir=box)
            #store it in the workspace too
            getattr(boxes[box].workspace,'import')(fr,'independentFR')
            
        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box, dir=box)

