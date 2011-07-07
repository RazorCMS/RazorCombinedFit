from RazorCombinedFit.Framework import Box

class MultiBox(Box.Box):
    """Similar to a box, but we expect several boxes which we combine"""
    
    def __init__(self, name, workspace):
        super(MultiBox,self).__init__(name, [], workspace)
        
    def combine(self, boxes, inputFiles):
        """Both arguments are dictionaries, where the key is the name of the box"""
        pass