from RazorCombinedFit.Framework import MultiBox
import ROOT as rt
import RootTools

class RazorMultiBoxSim(MultiBox.MultiBox):
    
    def __init__(self, workspace):
        super(RazorMultiBoxSim,self).__init__('RazorMultiBoxSim',workspace)
        
    def combine(self, boxes, inputFiles):
        print 'Combining boxes...',self.name
        
        flavours = ['Wln','Zll','Znn','TTj']
        
        #create the RooCategory for the different boxes
        self.workspace.factory('Boxes[%s]' % ','.join(boxes.keys()))
        #this is a merged dataset with each box as a category
        data = self.mergeDataSets(self.workspace.cat('Boxes'),inputFiles)
        
        #start with box with largest yields
        masterBox = None
        maximumYield = -1e6
        for box in boxes:
            sum = 0
            for f in flavours:
                Ntot = boxes[box].workspace.var('Ntot_%s' % f).getVal()
                sum += Ntot
            if sum > maximumYield:
                maximumYield = sum
                masterBox = box

        #we produce a new workspace from the box with the largest statistics
        ws = rt.RooWorkspace(boxes[masterBox].workspace)
        ws.SetName('Combined_%s' % '_'.join(boxes.keys()))
        ws.SetTitle(ws.GetName())
        
        splits = []
        for v in ['MR01st_%s','R01st_%s','b1st_%s','Ntot_%s','f2_%s']:
            for f in flavours:
                splits.append(v % f)
        #make a RooSimultanious with a category for each box, splitting the 1st component parameters and the fraction
        ws.factory('SIMCLONE::fitmodel_sim(fitmodel, $SplitParam({%s}, Boxes[%s]))' % ( ','.join(splits), ','.join(boxes.keys()) ) )
        self.workspace = ws        
            
        for box in boxes:
            pars = {}
            for p in RootTools.RootIterator.RootIterator(boxes[box].workspace.obj('independentFR').floatParsFinal()): pars[p.GetName()] = p
            
            for f in flavours:
                self.fix(boxes,'MR01st_%s' % f, box, pars, False)
                self.fix(boxes,'R01st_%s' % f, box, pars, False)
                self.fix(boxes,'b1st_%s' % f, box, pars, False)
                self.fix(boxes,'Ntot_%s' % f, box, pars, True)
                self.fix(boxes, 'f2_%s' % f, box, pars, False)
        
        fr = self.fitData(ws.pdf('fitmodel_sim'),data)
        self.importToWS(fr,'simultaniousFR')
        self.analysis.store(fr, dir='%s_dir' % self.workspace.GetName())
        
        fitmodel = self.workspace.pdf('fitmodel_sim')
        parameters = self.workspace.set("variables")
        Boxes = self.workspace.cat('Boxes')
        plots = []

        #use a binned dataset to make the plots as it is faster        
        hvars = rt.RooArgSet(Boxes)
        for p in RootTools.RootIterator.RootIterator(parameters):
            p.setBins(100)
            hvars.add(p)

        #ranges = {'MR':(200,1500),'Rsq':(0.04,0.8)}
        ranges = {}

        #go box by box
        for box in boxes:
            for p in RootTools.RootIterator.RootIterator(parameters):

                if p.GetName() == 'R': continue

                #set the ranges to more restrictive ones for plotting
                if ranges.has_key(p.GetName()):
                    r = ranges[p.GetName()]
                    frame = p.frame(r[0],r[1],50)
                else:
                    frame = p.frame()
                frame.SetName("autoVarPlotSim_%s_%s" % (p.GetName(), box) )
             
                #create a binned dataset in the parameter   
                hdata = rt.RooDataHist('projData_%s' % box,'projData',hvars,data.reduce('Boxes == Boxes::%s' % box))
                hdata.plotOn(frame)
                
                #for comparison plot the independent fit result (do this first)
                independent = boxes[box].workspace.pdf('fitmodel')
                independent.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()),rt.RooFit.LineColor(rt.kRed))
                for f in flavours:
                    independent.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),
                                       rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()),rt.RooFit.Components("ePDF1st_%s" % f),rt.RooFit.LineStyle(8),rt.RooFit.LineColor(rt.kRed))
                    independent.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),
                                       rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()),rt.RooFit.Components("ePDF2nd_%s" % f),rt.RooFit.LineStyle(9),rt.RooFit.LineColor(rt.kRed))
                
                #plot the results of the simultanious fits
                fitmodel.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))
                for f in flavours:
                    fitmodel.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),
                                    rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()),rt.RooFit.Components("ePDF1st_%s_%s" % (f,box) ),rt.RooFit.LineStyle(8))
                    fitmodel.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),
                                    rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()),rt.RooFit.Components("ePDF2nd_%s_%s" % (f,box) ),rt.RooFit.LineStyle(9))
                
                plots.append(frame)
        
        for p in plots: self.analysis.store(p, dir='%s_dir' % self.workspace.GetName())

        