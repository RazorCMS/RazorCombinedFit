import ConfigParser, os

class Config(object):
    
    def __init__(self, fileName):
        if not os.path.exists(fileName):
            raise IOError("File not found: '%s'" % fileName)
        self.config = ConfigParser.ConfigParser()
        self.config.read(fileName)
    
    def __checkBox(self, box):
        if box not in self.config.sections():
            raise KeyError("The box '%s' was not found" % box)
    
    def getVariables(self, box, lineTag):
        self.__checkBox(box)
        return eval(self.config.get(box,lineTag))
    
    def getRCuts(self, box):
        self.__checkBox(box)
        return eval(self.config.get(box,'rcuts'))
        
        
        
