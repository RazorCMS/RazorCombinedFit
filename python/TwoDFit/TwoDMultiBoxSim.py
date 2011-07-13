from RazorCombinedFit.Framework import MultiBox
import ROOT as rt
import RootTools

class TwoDMultiBoxSim(MultiBox.MultiBox):
    
    def __init__(self, workspace):
        super(TwoDMultiBoxSim,self).__init__('TwoDMultiBoxSim',workspace)
        
    def combine(self, boxes, inputFiles):
        print 'Combining boxes...',self.name
        
        #create the RooCategory for the different boxes
        self.workspace.factory('Boxes[%s]' % ','.join(boxes.keys()))
        #this is a merged dataset with each box as a category
        data = self.mergeDataSets(self.workspace.cat('Boxes'),inputFiles)

        masterBox = None
        maximumYield = -1e6
        for box in boxes:
            Ntot = boxes[box].workspace.var('Ntot').getVal()
            if Ntot > maximumYield:
                maximumYield = Ntot
                masterBox = box


        #we produce a new workspace from the box with the largest statistics
        ws = rt.RooWorkspace(boxes[masterBox].workspace)
        ws.SetName('Combined_%s' % '_'.join(boxes.keys()))
        ws.SetTitle(ws.GetName())
        
        #make a RooSimultanious with a category for each box, splitting the 1st component parameters and the fraction
        ws.factory('SIMCLONE::fitmodel_sim(fitmodel, $SplitParam({MR01st,R01st,b1st,Ntot,f2}, Boxes[%s]))' % ','.join(boxes.keys()))
        
        def fix(var, box, pars, constant = False):
            """Copy the value from the independent box fit to the split var using the fit results"""
            v = ws.var( '%s_%s' % (var, box) )
            v.setRange(pars[var].getMin(),pars[var].getMax())
            v.setVal(pars[var].getVal())
            v.setConstant(constant)
            
        def varstr(var):
            return '%s:\t %f \pm %s [%f,%f]' % (v.GetName(),v.getVal(),v.getError(),v.getMin(),v.getMax())
        
        for box in boxes:
            pars = {}
            for p in RootTools.RootIterator.RootIterator(boxes[box].workspace.obj('independentFR').floatParsFinal()): pars[p.GetName()] = p
            
            fix('MR01st', box, pars, False)
            fix('R01st', box, pars, False)
            fix('b1st', box, pars, False)
            fix('Ntot', box, pars, True)
            fix('f2', box, pars, False)
        
        #print 'Variables for combined box'
        #for v in RootTools.RootIterator.RootIterator(ws.allVars()): print varstr(v) 
        
        fr = self.fitData(ws.pdf('fitmodel_sim'),data)
        self.workspace = ws
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
                independent.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),
                                rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()),rt.RooFit.Components("ePDF1st"),rt.RooFit.LineStyle(8),rt.RooFit.LineColor(rt.kRed))
                independent.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),
                                rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()),rt.RooFit.Components("ePDF2nd"),rt.RooFit.LineStyle(9),rt.RooFit.LineColor(rt.kRed))
                
                #plot the results of the simultanious fits
                fitmodel.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))
                fitmodel.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),
                                rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()),rt.RooFit.Components("ePDF1st_%s" % box),rt.RooFit.LineStyle(8))
                fitmodel.plotOn(frame,rt.RooFit.ProjWData(rt.RooArgSet(p),hdata),
                                rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()),rt.RooFit.Components("ePDF2nd_%s" % box),rt.RooFit.LineStyle(9))
                
                plots.append(frame)
        
        for p in plots: self.analysis.store(p, dir='%s_dir' % self.workspace.GetName())

        