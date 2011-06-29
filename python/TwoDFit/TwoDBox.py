from RazorCombinedFit.Framework import Box
import RootTools
import ROOT as rt

class TwoDBox(Box.Box):
    
    def __init__(self, name, variables):
        super(TwoDBox,self).__init__(name, variables)
        
    def define(self, inputFile, cuts):
        
        rcuts = cuts.get('rcuts',[])
        rcuts.sort()
            
        #get the dataset to play with
        reduce = cuts.get('reduce',None)
        data = RootTools.getDataSet(inputFile,'RMRTree', reduce)
        
        print 'Rcuts',rcuts
        print 'Reduced dataset'
        data.Print("V")
            
            
        
        

