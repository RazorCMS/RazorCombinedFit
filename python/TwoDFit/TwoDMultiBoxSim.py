from RazorCombinedFit.Framework import MultiBox
import ROOT as rt

class TwoDMultiBoxSim(MultiBox.MultiBox):
    
    def __init__(self, workspace):
        super(TwoDMultiBoxSim,self).__init__('TwoDMultiBoxSim',workspace)
        
    def combine(self, boxes, inputFiles):
        print 'Combining boxes...',self.name
        
        self.workspace.factory('Boxes[%s]' % ','.join(boxes.keys()))
        data = self.mergeDataSets(self.workspace.cat('Boxes'),inputFiles)
        
        self.workspace.Print("V")
        
        #bind the total to the correct range
        self.workspace.factory('Ntot[%f,%f,%f]' % (
                                                        self.workspace.var('Ntot_EleEle').getVal()+self.workspace.var('Ntot_Mu').getVal(),
                                                        self.workspace.var('Ntot_EleEle').getMin()+self.workspace.var('Ntot_Mu').getMin(),
                                                        self.workspace.var('Ntot_EleEle').getMax()+self.workspace.var('Ntot_Mu').getMax()
                                                                           )
                                )
        self.linkRealVar('Ntot_EleEle','Ntot_Mu',expression='@0 - @1', vars=['Ntot','Ntot_Mu'])
        
        self.linkRealVar('MR02nd_EleEle','MR02nd_Mu')
        self.linkRealVar('R02nd_EleEle','R02nd_Mu')
        self.linkRealVar('b2nd_EleEle','b2nd_Mu')

        self.linkRealVar('MR_EleEle','MR_Mu')
        self.linkRealVar('Rsq_EleEle','Rsq_Mu')
        
        self.workspace.factory('SIMUL::fitmodel(Boxes,Mu=fitmodel_Mu,EleEle=fitmodel_EleEle)')
        fit = self.getFitPDF(graphViz='combined')
        self.workspace.pdf('fitmodel')
        
        dataName = data.GetName()
        self.importToWS(data,rt.RooFit.RenameVariable('MR', 'MR_Mu'),rt.RooFit.RenameVariable('Rsq', 'Rsq_Mu'))
        data = self.workspace.data(dataName)
        self.workspace.Print("V")
        
        
        #self.fit(data)