from RootTools import RootFile, RootIterator
import ROOT as rt

class Analysis(object):
    
    """Baseclass for constructing an analysis"""
    def __init__(self, name, outputFile, config):
        self.name = name
        #use this for storing root objects
        self.rootFile = RootFile.RootFile(outputFile)
        self.workspace = rt.RooWorkspace(self.name)
        self.config = config
        
        #the sigma bounds of a Gaussian
        self.sigmas = {1:0.6826894921,2:0.9544997361,3:0.9973002039,4:0.9999366575,5:0.9999994267}
    
    def importToWS(self, *args):
        """Utility function to call the RooWorkspace::import methods"""
        return getattr(self.workspace,'import')(*args)
    
    def store(self, o, name = None, dir = None):
        """Store a ROOT object"""
        self.rootFile.add(o, name, dir)    
    
    def getFileTag(self, fileName):
        """Assume filename format is foo_tag.root or whatever"""
        if fileName.endswith('.root'):
            f = fileName[:-5]
            tags = f.split('_')
            if len(tags) > 1:
                return tags[-1]
        return fileName
    
    def indexInputFiles(self, inputFiles):
        """Split the input files by their tags"""
        index = {}
        for f in inputFiles:
            tag = self.getFileTag(f)
            index[tag] = f
        return index
        
    def limit(self, inputFiles):
        """Set a limit based on the model dependent method"""
        return None
    
    def analysis(self, inputFiles):
        return None
    
    def runtoys(self, inputFiles, nToys):
        pass
    
    def toystudy(self, inputFiles, nToys):
        pass
        
    def final(self):
        self.store(self.workspace)
        #write out any stored objects at the end
        self.rootFile.write()
        
    def merge(self, workspace, box):
        """Import the contents of a box workspace into the master workspace while enforcing some namespaceing"""
        for o in RootIterator.RootIterator(workspace.componentIterator()):
            if hasattr(o,'Class') and o.Class().InheritsFrom('RooRealVar'):
                continue
            self.importToWS(o, rt.RooFit.RenameAllNodes(box),rt.RooFit.RenameAllVariables(box))
