import ConfigParser, os

class Config(object):
    
    def __init__(self, fileName):
        if not os.path.exists(fileName):
            raise IOError("File not found: '%s'" % fileName)
        self.config = ConfigParser.ConfigParser()
        self.config.read(fileName)
        
    def getVariables(self, box):
        if box not in self.config.sections():
            raise KeyError("The box '%s' was not found" % box)
        return eval(self.config.get(box,'variables'))
    
        
        
        