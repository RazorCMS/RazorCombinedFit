import ROOT as rt

class Box(object):
    
    def __init__(self, name, variables):
        self.name = name
        self.workspace = rt.RooWorkspace(name)
        for v in variables:
            self.workspace.factory(v)
        
    def define(self, inputFile, cuts):
        pass