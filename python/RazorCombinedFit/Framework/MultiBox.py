from RazorCombinedFit.Framework import Box
import ROOT as rt
import RootTools

class MultiBox(Box.Box):
    """Similar to a box, but we expect several boxes which we combine"""
    
    def __init__(self, name, analysis):
        super(MultiBox,self).__init__(name, [], analysis.workspace)
        self.analysis = analysis
    
    def mergeDataSets(self, categories, inputFiles, lepton = None, dilepton = None):
        keys = inputFiles.keys()
        
        data = RootTools.getDataSet(inputFiles[keys[0]],'RMRTree')
        args = data.get(0)
        
        if lepton is not None:
            args.add(lepton)
        if dilepton is not None:
            args.add(dilepton)

        args = ['MergedDataSet','MergedDataSet',args,rt.RooFit.Index(categories),rt.RooFit.Import(keys[0],data)]
        for k in keys[1:]:
            d = RootTools.getDataSet(inputFiles[k],'RMRTree')
            args.append(rt.RooFit.Import(k,d))
        
        a = tuple(args)
        data = rt.RooDataSet(*a)
        
        if lepton is not None:
            a = rt.RooArgSet(lepton)
            aa = rt.RooDataSet('Leptons','Leptons',a)
            
            for i in xrange(data.numEntries()):
                row = data.get(i)
                box = row.getCatLabel('Boxes')
                if box in ['Mu','Ele','MuMu','EleEle','MuEle']:
                    lepton.setLabel('Lepton')
                else:
                    lepton.setLabel('Hadron')
                aa.add(rt.RooArgSet(lepton))
            data.merge(aa)
        
        if dilepton is not None:
            a = rt.RooArgSet(dilepton)
            aa = rt.RooDataSet('DiLeptons','DiLeptons',a)
            for i in xrange(data.numEntries()):
                row = data.get(i)
                box = row.getCatLabel('Boxes')
                if box in ['MuMu','EleEle','MuEle']:
                    dilepton.setLabel('DiLepton')
                elif box in ['Mu','Ele']:
                    dilepton.setLabel('SingleLepton')
                else:
                    dilepton.setLabel('NonLepton')
                aa.add(rt.RooArgSet(dilepton))
            data.merge(aa)
        
        return data

                    
    def linkRealVar(self, var1, var2, expression = None, vars = None):
        """Not very nice: Replace var1 with a RooFormulaVar linking it with var2"""
        ws = rt.RooWorkspace(self.workspace.GetName())
        
        if expression is None: expression = '@0'
        
        args = rt.RooArgList()
        if vars is not None:
            for v in vars:
                args.add(self.workspace.var(v))
        else:
            args.add(self.workspace.var(var2))
        
        ex = rt.RooFormulaVar(var1,'Replace %s with %s' % (var1,var2),expression,args)
        
        getattr(ws,'import')(self.workspace.var(var2),rt.RooFit.Silence())
        getattr(ws,'import')(ex,rt.RooFit.Silence())
        
        for o in RootTools.RootIterator.RootIterator(self.workspace.componentIterator()):
            if not o.GetName() in [var1,var2]:
                getattr(ws,'import')(o,rt.RooFit.RecycleConflictNodes(),rt.RooFit.Silence())
        
        self.workspace = ws
        
    def fix(self, boxes, var, box, pars, constant = False):
        """Copy the value from the independent box fit to the split var using the fit results"""

        v = self.workspace.var( '%s_%s' % (var, box) )
        if not v:
            raise Exception('Variable %s_%s not found in the workspace' % (var, box) )
            
        if not pars.has_key(var):
            vv = boxes[box].workspace.var(var)
            if vv.isConstant():
                constant = True
        else:
            vv = pars[var]

        v.setRange(vv.getMin(),vv.getMax())
        v.setVal(vv.getVal())
        v.setConstant(constant)

    
    def predictBackground(self, boxes, fr, fileIndex, nRepeats = 100):
        if fr.status() != 0 or fr.covQual() != 3:
            print 'Skipping background prediction for box %s as the fit did not converge properly' % self.name
            return

        Boxes = self.workspace.cat('Boxes')
        data = self.mergeDataSets(self.workspace.cat('Boxes'),fileIndex)

        total_yield = data.numEntries()
        
        pdf = self.workspace.pdf(self.fitmodel)
        vars = self.workspace.set('variables')
        vars.add(Boxes)
        
        background_prediction = {}
        for box in boxes:
            background_prediction[box] = 0
        
        parSet = self.workspace.allVars()
        for i in xrange(nRepeats):
            pars = {}
            for p in RootTools.RootIterator.RootIterator(fr.randomizePars()): pars[p.GetName()] = p
            for name, value in pars.iteritems():
                self.fixPars(name,value.isConstant(),value.getVal())
            ds = pdf.generate(vars,rt.RooRandom.randomGenerator().Poisson(total_yield))
            
            for box in boxes:
                box_data = ds.reduce('Boxes == Boxes::%s' % box)
                before = box_data.numEntries()    
                box_data = box_data.reduce(self.cut)
                after = box_data.numEntries()
            
                background_prediction[box] += (before-after)
        
        for box in boxes:
            background_prediction[box] /= (1.0*nRepeats)
            
            data_box = data.reduce('Boxes == Boxes::%s' % box)
            total_yield_box = data_box.numEntries()
            background_yield = data_box.reduce(self.cut).numEntries()
            
            print 'Sim: Background observed in the %s box: %i' % (box,total_yield_box-background_yield)
            print 'Sim: Background prediction after %i repeats: %f' % (nRepeats,background_prediction[box])
        
        #now set the parameters back
        pars = {}
        for p in RootTools.RootIterator.RootIterator(fr.floatParsFinal()): pars[p.GetName()] = p
        for name, value in pars.iteritems():
            self.fixPars(name,value.isConstant(),value.getVal())


        
    def combine(self, boxes, inputFiles):
        """Both arguments are dictionaries, where the key is the name of the box"""
        pass