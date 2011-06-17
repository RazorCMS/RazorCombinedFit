from RazorCombinedFit.Framework import Box
import RootTools

class SingleRValueBox(Box.Box):
    
    def __init__(self, name, variables):
        super(SingleRValueBox,self).__init__(name, variables)
        
    def define(self, inputFile, cuts):
        self.workspace.factory("RooTwoSideGaussianWithAnExponentialTail::fixedR(MR,X0[150,0,5000],SigmaL[50,0,5000],SigmaR[50,0,5000],S[0.01,0,0.5])")
        
        

