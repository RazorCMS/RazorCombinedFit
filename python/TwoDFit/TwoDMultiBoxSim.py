from RazorCombinedFit.Framework import MultiBox

class TwoDMultiBoxSim(MultiBox.MultiBox):
    
    def __init__(self, workspace):
        super(TwoDMultiBoxSim,self).__init__('TwoDMultiBoxSim',workspace)
        print '%s: Combining boxes simultanously' % self.name
        self.workspace.Print("V")
        
    def combine(self, boxes, inputFiles):
        print 'Combining boxes...',self.name
