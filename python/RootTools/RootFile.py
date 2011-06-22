import ROOT as rt

class RootFile(object):
    
    def __init__(self, fileName):
        self.fileName = fileName
        self.plots = {}
        
    def add(self, plot, name = None):
        if name is None: name = plot.GetName()
        l = self.plots.get(name,[])
        l.append(plot)
        self.plots[name] = l

    def write(self):
        out = None
        try:
            out = rt.TFile.Open(self.fileName,'RECREATE')
            for name, plots in self.plots.iteritems():
                if not plots:
                    continue
                elif len(plots) == 1:
                    plots[0].Write(name)
                else:
                    index = 0
                    for i in xrange(len(plots)):
                        p = plots[i]
                        p.Write('%s_%i' % (name,i))
            #needed so that the object can be deleted 
            self.plots.clear()
        finally:
            if out is not None: out.Close()
                    