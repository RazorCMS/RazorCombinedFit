from RootTools import RootFile
import ROOT as rt

class Analysis(object):
    
    """Baseclass for constructing an analysis"""
    def __init__(self, name, outputFile, config):
        self.name = name
        #use this for storing root objects
        self.rootFile = RootFile.RootFile(outputFile)
        self.workspace = rt.RooWorkspace(self.name)
        self.config = config
    
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
        
    
    def analysis(self, inputFiles):
        return None
        
    def final(self):
        self.store(self.workspace)
        #write out any stored objects at the end
        self.rootFile.write()
