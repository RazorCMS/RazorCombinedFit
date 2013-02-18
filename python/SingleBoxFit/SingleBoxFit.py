import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis
import RootTools
import math, os
import sys

class SingleBoxAnalysis(Analysis.Analysis):

    def __init__(self, outputFile, config, Analysis = "INCLUSIVE"):
        super(SingleBoxAnalysis,self).__init__('SingleBoxFit',outputFile, config)
        self.Analysis = Analysis
    
    def merge(self, workspace, box):
        """Import the contents of a box workspace into the master workspace while enforcing some name-spaceing"""
        for o in RootTools.RootIterator.RootIterator(workspace.componentIterator()):
            if hasattr(o,'Class') and o.Class().InheritsFrom('RooRealVar'):
                continue
            self.importToWS(o, rt.RooFit.RenameAllNodes(box),rt.RooFit.RenameAllVariables(box)) 

    def getboxes(self, fileIndex):
        """Refactor out the common box def for fitting and simple toys"""
        
        import RazorBox
        import RazorBjetBox
        import RazorMultiJetBox
        #import RazorBoostBox
        import RazorTauBox
        boxes = {}

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Configuring box %s' % box
            print 'Analysis:', self.Analysis
            if self.Analysis == "BJET": boxes[box] = RazorBjetBox.RazorBjetBox(box, self.config.getVariables(box, "variables"))
            elif self.Analysis == "MULTIJET": boxes[box] = RazorMultiJetBox.RazorMultiJetBox(box, self.config.getVariables(box, "variables"))
            elif self.Analysis == "BOOST": boxes[box] = RazorBoostBox.RazorBoostBox(box, self.config.getVariables(box, "variables"))
            elif self.Analysis == "TAU": boxes[box] = RazorTauBox.RazorTauBox(box, self.config.getVariables(box, "variables"))
            else: boxes[box] = RazorBox.RazorBox(box, self.config.getVariables(box, "variables"),self.options.fitMode,self.options.btag,self.options.fitregion)

            print 'box:', box
            print 'vars:', self.config.getVariables(box, "variables")
            print '>>> getVariablesRange:'
            
            self.config.getVariablesRange(box,"variables" ,boxes[box].workspace)
            

            print '>>> defineSet:'
            
            if self.options.input is not None:
                continue

            if self.Analysis=="INCLUSIVE":
                boxes[box].defineSet("pdfpars_TTj2b", self.config.getVariables(box, "pdf_TTj2b"))
                boxes[box].defineSet("otherpars_TTj2b", self.config.getVariables(box, "others_TTj2b"))
                boxes[box].defineSet("btagpars_TTj2b", self.config.getVariables(box, "btag_TTj2b"))
                
                boxes[box].defineSet("pdfpars_TTj1b", self.config.getVariables(box, "pdf_TTj1b"))
                boxes[box].defineSet("otherpars_TTj1b", self.config.getVariables(box, "others_TTj1b"))
                boxes[box].defineSet("btagpars_TTj1b", self.config.getVariables(box, "btag_TTj1b"))
                
                boxes[box].defineSet("pdfpars_Vpj", self.config.getVariables(box, "pdf_Vpj"))
                boxes[box].defineSet("otherpars_Vpj", self.config.getVariables(box, "others_Vpj"))
                boxes[box].defineSet("btagpars_Vpj", self.config.getVariables(box, "btag_Vpj"))
                
                boxes[box].defineFunctions(self.config.getVariables(box,"functions"))
                
            else:
                if self.Analysis != "MULTIJET" and self.Analysis != "BOOST":
                    # Vpj
                    boxes[box].defineSet("pdfpars_Vpj", self.config.getVariables(box, "pdf_Vpj"))
                    boxes[box].defineSet("otherpars_Vpj", self.config.getVariables(box, "others_Vpj"))
                # TTj
                boxes[box].defineSet("pdfpars_TTj", self.config.getVariables(box, "pdf_TTj"))
                boxes[box].defineSet("otherpars_TTj", self.config.getVariables(box, "others_TTj"))
                boxes[box].defineSet("pdfpars_UEC", self.config.getVariables(box, "pdf_UEC"))
                boxes[box].defineSet("otherpars_UEC", self.config.getVariables(box, "others_UEC"))
                if self.Analysis == "MULTIJET" or self.Analysis == "BOOST":
                    # QCD
                    boxes[box].defineSet("pdfpars_QCD", self.config.getVariables(box, "pdf_QCD"))
                    boxes[box].defineSet("otherpars_QCD", self.config.getVariables(box, "others_QCD"))
                
            print '>>> addDataset:'
            if not self.options.limit:
                boxes[box].addDataSet(fileName)
            print '>>> define:'
            boxes[box].define(fileName)
            print '>>> getBoxes done!'

        return boxes

    def toystudy(self, inputFiles, nToys):

        fit_range = "fR1,fR2,fR3,fR4"
        if self.options.full_region:
            fit_range = "FULL"
        elif self.options.doMultijet:
            fit_range = "fR1,fR2"
            print 'Using the fit range: %s' % fit_range 
        
        random = rt.RooRandom.randomGenerator()
        
        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)

        for box in boxes:
            if self.options.input is not None:
                wsName = '%s/Box%s_workspace' % (box,box)
                print "Restoring the workspace from %s" % self.options.input
                boxes[box].restoreWorkspace(self.options.input, wsName)

        for box in boxes:    
            data_yield = boxes[box].workspace.data('RMRTree').numEntries()
            
            study = boxes[box].getMCStudy(boxes[box].fitmodel, boxes[box].fitmodel,rt.RooFit.Range(fit_range))
            study.generateAndFit(nToys,data_yield)
            
            qual_ = rt.RooRealVar('quality','quality',-1)
            status_ = rt.RooRealVar('status','status',-1)
            args = rt.RooArgSet(qual_,status_)
            fit = rt.RooDataSet('Fit','Fit',args)            
            
            for i in xrange(nToys):
                fr = study.fitResult(i)
                args.setRealValue('quality',fr.covQual())
                args.setRealValue('status',fr.status())
                fit.add(args)
                
            fitPars = study.fitParDataSet()
            outpars = rt.RooDataSet('fitPars_%s' % box, 'fitPars_%s' % box, fitPars,fitPars.get(0))
            outpars.merge(fit)
            
            self.store(outpars, dir='%s_Toys' % box)
            
    def runtoys(self, inputFiles, nToys):
        
        random = rt.RooRandom.randomGenerator()
        
        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)

        totalYield = 0
        simName = None

        for box in boxes:
            
            if self.options.input is not None:
                wsName = '%s/Box%s_workspace' % (box,box)
                print "Restoring the workspace from %s" % self.options.input
                boxes[box].restoreWorkspace(self.options.input, wsName)
            
            totalYield += boxes[box].workspace.data('RMRTree').numEntries()
        
        #we only include the simultaneous fit if we're restoring
        if len(boxes) > 1 and self.options.simultaneous and self.options.input is not None:
            #merge the boxes together in some way
            import RazorMultiBoxSim
            multi = RazorMultiBoxSim.RazorMultiBoxSim(self)
            print "Restoring the workspace from %s" % self.options.input
            multi.restoreWorkspace(self.options.input, multi.name, name='simultaneousFRPDF')
            multi.setCombinedCut(boxes)
            self.workspace = multi.workspace
            
            #just append the sim pdf to the boxes
            simName = multi.name
            boxes[multi.name] = multi
            
        for box in boxes:    
            pdf = boxes[box].getFitPDF(name=boxes[box].fitmodel,graphViz=None)
            vars = rt.RooArgSet(boxes[box].workspace.set('variables'))

            if box != simName:
                #get the data yield without cuts
                data_yield = boxes[box].workspace.data('RMRTree').numEntries()
            else:
                data_yield = totalYield

            #if we just need to write out toys then skip everything else
            if self.options.save_toys_from_fit != "none":
                if box != simName:
                    f = boxes[box].workspace.obj('independentFR')
                else:
                    f = boxes[box].workspace.obj('simultaneousFR')
                if self.options.save_toys_from_fit.find("/") != -1:
                    boxes[box].writeBackgroundDataToys(f, data_yield*self.options.scale_lumi, box, nToys, self.options.nToyOffset, self.options.save_toys_from_fit)
                else:
                    boxes[box].writeBackgroundDataToys(f, data_yield*self.options.scale_lumi, box, nToys, self.options.nToyOffset)
                continue

            #use an MCStudy to store everything
            study = boxes[box].getMCStudy()
            
            pre_ = rt.RooRealVar('predicted','predicted',-1)
            obs_ = rt.RooRealVar('observed','observed',-1)
            qual_ = rt.RooRealVar('quality','quality',-1)
            status_ = rt.RooRealVar('status','status',-1)
            args = rt.RooArgSet(pre_,obs_,qual_,status_)
            yields = rt.RooDataSet('Yields','Yields',args)
            
            for i in xrange(nToys):
                gdata = pdf.generate(vars,rt.RooRandom.randomGenerator().Poisson(data_yield))
                gdata_cut = gdata.reduce(boxes[box].cut)
                
                if self.options.save_toys:
                    data_write = 'toydata_%s_%i.txt' % (box,i)
                    gdata.write(data_write)
                
                fr = boxes[box].fitData(pdf, gdata_cut)
                predictions = boxes[box].predictBackgroundData(fr, gdata, nRepeats = 5, verbose = False)
               
                if not fr.status() == 0 and fr.covQual() == 3:
                    print 'WARNING:: The toy fit %i did not converge with high quality. Consider this result suspect!' % i
                print 'Fit result %d for box %s' % (i,box)
                study.addFitResult(fr)
                self.store(fr,'toyfitresult_%i' % i, dir='%s_Toys' % box)

                args.setRealValue('predicted',predictions[0])
                args.setRealValue('observed',predictions[1])
                args.setRealValue('quality',fr.covQual())
                args.setRealValue('status',fr.status())
                yields.add(args)
            
            fitPars = study.fitParDataSet()
            outpars = rt.RooDataSet('fitPars_%s' % box, 'fitPars_%s' % box, fitPars,fitPars.get(0))
            
            self.store(outpars, dir='%s_Toys' % box)
            self.store(yields, dir='%s_Toys' % box)
            
    def analysis(self, inputFiles):
        """Run independent and then simultanious fits"""

        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)
        #print 'fileindex:', fileindex
        print 'boxes:', boxes

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():

            if self.options.input is None:

                print 'Variables for box %s' % box
                boxes[box].workspace.allVars().Print('V')
                print 'Workspace'
                boxes[box].workspace.Print('V')

                # perform the fit
                fit_range = boxes[box].fitregion
                if self.options.doMultijet:
                    fit_range = "fR1,fR2,fR3,fR4,fR5"
                print 'Using the fit range: %s' % fit_range
                #boxes[box].fit(fileName,boxes[box].cut, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True),rt.RooFit.Hesse(False),rt.RooFit.Minos(False))

                fr = boxes[box].fit(fileName,boxes[box].cut, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True), rt.RooFit.Range(fit_range))
                while fr.covQual()!=3:
                    zeroIntegral = True
                    components = ['TTj1b','TTj2b','Vpj']
                    componentsOn = [comp for comp in components if boxes[box].workspace.var('Ntot_%s'%comp).getVal() > 0.]
                    print "The components on are ", componentsOn
                    while zeroIntegral:
                        argList = fr.randomizePars()
                        for p in RootTools.RootIterator.RootIterator(argList):
                            boxes[box].workspace.var(p.GetName()).setVal(p.getVal())
                            boxes[box].workspace.var(p.GetName()).setError(p.getError())
                            boxes[box].fixParsExact(p.GetName(),False)
                            print "RANDOMIZE PARAMETER %s = %f +- %f"%(p.GetName(),p.getVal(),p.getError())
                        # check how many error messages we have before evaluating pdfs
                        errorCountBefore = rt.RooMsgService.instance().errorCount()
                        print "RooMsgService ERROR COUNT BEFORE = %i"%errorCountBefore
                        # evaluate each pdf, assumed to be called "RazPDF_{component}"
                        badPars = []
                        myvars = rt.RooArgSet(boxes[box].workspace.var('MR'),boxes[box].workspace.var('Rsq'))
                        for component in componentsOn:
                            pdfComp = boxes[box].workspace.pdf("RazPDF_%s"%component)
                            pdfValV = pdfComp.getValV(myvars)
                            badPars.append(boxes[box].workspace.var('n_%s'%component).getVal() <= 0)
                            badPars.append(boxes[box].workspace.var('b_%s'%component).getVal() <= 0)
                            badPars.append(boxes[box].workspace.var('MR0_%s'%component).getVal() >= boxes[box].workspace.var('MR').getMin())
                            badPars.append(boxes[box].workspace.var('R0_%s'%component).getVal()  >=  boxes[box].workspace.var('Rsq').getMin())
                            print badPars
                        # check how many error messages we have after evaluating pdfs
                        errorCountAfter = rt.RooMsgService.instance().errorCount()
                        print "RooMsgService ERROR COUNT AFTER  = %i"%errorCountAfter
                        zeroIntegral = (errorCountAfter>errorCountBefore) or any(badPars)
                        print zeroIntegral
                    fr = boxes[box].fit(fileName,boxes[box].cut, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True), rt.RooFit.Range(fit_range))
                
                self.store(fr, name = 'independentFR', dir=box)
                self.store(fr.correlationHist("correlation_%s" % box), dir=box)
                #store it in the workspace too
                getattr(boxes[box].workspace,'import')(fr,'independentFR')
                #store the name of the PDF used
                getattr(boxes[box].workspace,'import')(rt.TObjString(boxes[box].fitmodel),'independentFRPDF')
            
                #make any plots required
                boxes[box].plot(fileName, self, box)
                
            else:
                
                wsName = '%s/Box%s_workspace' % (box,box)
                print "Restoring the workspace from %s" % self.options.input
                boxes[box].restoreWorkspace(self.options.input, wsName)
                print 'Variables for box %s' % box
                boxes[box].workspace.allVars().Print('V')
                print 'Workspace'
                boxes[box].workspace.Print('V')
            
        if len(boxes) > 1 and self.options.simultaneous:
            #merge the boxes together in some way
            import RazorMultiBoxSim
            multi = RazorMultiBoxSim.RazorMultiBoxSim(self)
            #restore the simultaneous fits if required
            if self.options.input is None:
                multi.combine(boxes, fileIndex)
                multi.plot(fileName, self, 'Simultaneous')
                self.store(rt.TObjString(multi.workspace.GetName()),'simultaneousName')
            else:
                print "Restoring the workspace from %s" % self.options.input
                multi.restoreWorkspace(self.options.input, multi.name, name='simultaneousFRPDF')
                multi.setCombinedCut(boxes)
            self.workspace = multi.workspace
            
            #run the model independent limit setting code if needed
            if self.options.model_independent_limit:
                multi.predictBackground(boxes.keys(), multi.workspace.obj('simultaneousFR'), fileIndex)

        if self.options.model_independent_limit:
            for box, fileName in fileIndex.iteritems():
                boxes[box].predictBackground(boxes[box].workspace.obj('independentFR'), fileName)
        
        #skip saving the workspace if the option is set
        if not self.options.nosave_workspace:
            for box in boxes.keys():
                self.store(boxes[box].workspace,'Box%s_workspace' % box, dir=box)
            
    def limit(self, inputFiles, nToys, nToyOffset):
        """Set a limit based on the model dependent method"""
        
        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)
        
        if self.options.input is None:
            raise Exception('Limit setting code needs a fit result file as input. None given')

        def reset(box, fr, fixSigma = True, random = False):
            # fix all parameters
            box.fixAllPars()
            
            for z in box.zeros:
                box.fixPars(z)
                if box.name in box.zeros[z]:
                    box.switchOff(z)
            # float background shape parameters
            if not random:
                argList = fr.floatParsFinal()
                for p in RootTools.RootIterator.RootIterator(argList):
                    box.workspace.var(p.GetName()).setVal(p.getVal())
                    box.workspace.var(p.GetName()).setError(p.getError())
                    box.fixParsExact(p.GetName(),False)
                    print "INITIALIZE PARAMETER %s = %f +- %f"%(p.GetName(),p.getVal(),p.getError())
            else:
                zeroIntegral = True
                components = ['TTj1b','TTj2b','Vpj']
                componentsOn = [comp for comp in components if box.workspace.var('Ntot_%s'%comp).getVal() > 0.]
                print "The components on are ", componentsOn
                while zeroIntegral:
                    argList = fr.randomizePars()
                    for p in RootTools.RootIterator.RootIterator(argList):
                        box.workspace.var(p.GetName()).setVal(p.getVal())
                        box.workspace.var(p.GetName()).setError(p.getError())
                        box.fixParsExact(p.GetName(),False)
                        print "RANDOMIZE PARAMETER %s = %f +- %f"%(p.GetName(),p.getVal(),p.getError())
                    # check how many error messages we have before evaluating pdfs
                    errorCountBefore = rt.RooMsgService.instance().errorCount()
                    print "RooMsgService ERROR COUNT BEFORE = %i"%errorCountBefore
                    # evaluate each pdf, assumed to be called "RazPDF_{component}"
                    badPars = []
                    myvars = rt.RooArgSet(box.workspace.var('MR'),box.workspace.var('Rsq'))
                    for component in componentsOn:
                        pdfComp = box.workspace.pdf("RazPDF_%s"%component)
                        pdfValV = pdfComp.getValV(myvars)
                        badPars.append(box.workspace.var('n_%s'%component).getVal() <= 0)
                        badPars.append(box.workspace.var('b_%s'%component).getVal() <= 0)
                        badPars.append(box.workspace.var('MR0_%s'%component).getVal() >= box.workspace.var('MR').getMin())
                        badPars.append(box.workspace.var('R0_%s'%component).getVal()  >=  box.workspace.var('Rsq').getMin())
                        print badPars
                    # check how many error messages we have after evaluating pdfs
                    errorCountAfter = rt.RooMsgService.instance().errorCount()
                    print "RooMsgService ERROR COUNT AFTER  = %i"%errorCountAfter
                    zeroIntegral = (errorCountAfter>errorCountBefore) or any(badPars)
                    print zeroIntegral
            
            # fix signal nuisance parameters
            for p in RootTools.RootIterator.RootIterator(box.workspace.set('nuisance')):
                p.setVal(0.)
                box.fixParsExact(p.GetName(),True)
                
            # float poi or not
            box.fixParsExact("sigma",fixSigma)
        def setNorms(box, ds):
            # set normalizations
            N_TTj2b = box.workspace.var("Ntot_TTj2b").getVal()
            N_TTj1b = box.workspace.var("Ntot_TTj1b").getVal()
            N_Vpj = box.workspace.var("Ntot_Vpj").getVal()
            N_Signal = box.workspace.function("Ntot_Signal").getVal()
            Nds = ds.sumEntries()
            if Nds-N_Signal>0:
                box.workspace.var("Ntot_TTj2b").setVal((Nds-N_Signal)*N_TTj2b/(N_TTj2b+N_TTj1b+N_Vpj))
                box.workspace.var("Ntot_TTj1b").setVal((Nds-N_Signal)*N_TTj1b/(N_TTj2b+N_TTj1b+N_Vpj))
                box.workspace.var("Ntot_Vpj").setVal((Nds-N_Signal)*N_Vpj/(N_TTj2b+N_TTj1b+N_Vpj))
            
        def getLz(box, ds, fr, Extend=True, norm_region = 'LowRsq,LowMR,HighMR'):
            reset(box, fr, fixSigma=True)
            setNorms(box, ds)
            
            opt = rt.RooLinkedList()
            opt.Add(rt.RooFit.Range(norm_region))
            opt.Add(rt.RooFit.Extended(Extend))
            opt.Add(rt.RooFit.Save(True))
            opt.Add(rt.RooFit.Hesse(False))
            opt.Add(rt.RooFit.Minos(False))
            opt.Add(rt.RooFit.PrintLevel(-1))
            opt.Add(rt.RooFit.PrintEvalErrors(10))
            opt.Add(rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))


            #L(s,^th_s|x)
            print "retrieving -log L(x = %s|s,^th_s)" %(ds.GetName())
            covqualH0 = 0
            fitAttempts = 0
            while covqualH0!=3 and fitAttempts<5:
                reset(box, fr, fixSigma=True, random=(fitAttempts>0))
                box.workspace.var("sigma").setVal(self.options.signal_xsec)
                box.workspace.var("sigma").setConstant(True)
                frH0 = box.getFitPDF(name=box.signalmodelconst).fitTo(ds, opt)
                frH0.Print("v")
                statusH0 = frH0.status()
                covqualH0 = frH0.covQual()
                LH0x = frH0.minNll()
                print "-log L(x = %s|s,^th_s) = %f" %(ds.GetName(),LH0x)
                fitAttempts+=1

            
            #L(^s,^th|x)
            print "retrieving -log L(x = %s|^s,^th)" %(ds.GetName())
            covqualH1 = 0
            fitAttempts = 0
            while covqualH1!=3 and fitAttempts<5:
                if self.options.expectedlimit==True or ds.GetName=="RMRTree":
                    #this means we're doing background-only toys or data
                    #so we should reset to nominal fit pars
                    reset(box, fr, fixSigma=False, random=(fitAttempts>0))
                    box.workspace.var("sigma").setVal(1e-6)
                    box.workspace.var("sigma").setConstant(False)
                else:
                    #this means we're doing signal+background toy
                    #so we should reset to the fit with signal strength fixed
                    reset(box, frH0, fixSigma=False, random=(fitAttempts>0))
                    box.workspace.var("sigma").setVal(self.options.signal_xsec)
                    box.workspace.var("sigma").setConstant(False)
                frH1 = box.getFitPDF(name=box.signalmodelconst).fitTo(ds, opt)
                frH1.Print("v")
                statusH1 = frH1.status()
                covqualH1 = frH1.covQual()
                LH1x = frH1.minNll()
                print "-log L(x = %s|^s,^th) =  %f"%(ds.GetName(),LH1x)
                fitAttempts+=1

            if box.workspace.var("sigma")>self.options.signal_xsec:
                print "INFO: ^sigma > sigma"
                print " returning q = 0 as per LHC style CLs prescription"
                LH1x = LH0x
                
            if math.isnan(LH1x):
                print "WARNING: LH1DataSR is nan, most probably because there is no signal expected -> Signal PDF normalization is 0"
                print "         Since this corresponds to no signal/bkg discrimination, returning q = 0"
                LH1x = LH0x

                
            #del H1xNLL
            #del H0xNLL
            #del mH1
            #del mH0

            Lz = LH0x-LH1x
            print "**************************************************"
            print "-log L(x = %s|s,^th_s) = %f" %(ds.GetName(),LH0x)
            print "-log L(x = %s|^s,^th) = %f" %(ds.GetName(),LH1x)
            print "q = -log L(x = %s|s,^th_s) + log L(x = %s|^s,^th) = %f" %(ds.GetName(),ds.GetName(),Lz)
            print "MIGRAD/COVARIANCE MATRIX STATUS"
            print "H0 fit status = %i"%statusH0
            print "H0 cov. qual  = %i"%covqualH0
            print "H1 fit status = %i"%statusH1
            print "H1 cov. qual  = %i"%covqualH1
            print "**************************************************"

            return Lz, LH0x, LH1x, frH0, frH1

        
        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Starting limit setting for box %s' % box

            wsName = '%s/Box%s_workspace' % (box,box)
            print "Restoring the workspace from %s" % self.options.input
            boxes[box].restoreWorkspace(self.options.input, wsName)
            
            # add signal specific parameters and nuisance parameters
            boxes[box].defineSet("nuisance", self.config.getVariables(box, "nuisance_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("other", self.config.getVariables(box, "other_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("poi", self.config.getVariables(box, "poi"), workspace = boxes[box].workspace)
            boxes[box].workspace.factory("expr::lumi('@0 * pow( (1+@1), @2)', lumi_value, lumi_uncert, lumi_prime)")
            boxes[box].workspace.factory("expr::eff('@0 * pow( (1+@1), @2)', eff_value, eff_uncert, eff_prime)")

            # change upper limits of variables
            boxes[box].workspace.var("Ntot_TTj1b").setMax(1e9)
            boxes[box].workspace.var("Ntot_TTj2b").setMax(1e9)
            boxes[box].workspace.var("Ntot_Vpj").setMax(1e9)
            
            #add a signal model to the workspace
            signalModel = boxes[box].addSignalModel(fileIndex[box], self.options.signal_xsec)

            #set upper limit of signal xsec
            #boxes[box].workspace.var("sigma").setMax(self.options.signal_xsec)

            print 'Variables for box %s' % box
            boxes[box].workspace.allVars().Print('V')
            print 'Workspace'
            boxes[box].workspace.Print('V')
            fr_central = boxes[box].workspace.obj('independentFR')
            vars = boxes[box].workspace.set('variables')
            data = boxes[box].workspace.data('RMRTree')

            #add in the other signal regions
            norm_region = 'LowRsq,LowMR,HighMR'

            print "get Lz for data"

            myDataTree = rt.TTree("myDataTree", "myDataTree")
    
            # THIS IS CRAZY !!!!
            rt.gROOT.ProcessLine("struct MyDataStruct{Double_t var2;Int_t var3;Double_t var4;Double_t var5;Double_t var6;Int_t var7;Int_t var8;Int_t var9;Int_t var10;};")
            from ROOT import MyDataStruct

            sDATA = MyDataStruct()
            myDataTree.Branch("sigma_%s"%boxes[box].name, rt.AddressOf(sDATA,'var2'),'var2/D')
            myDataTree.Branch("iToy", rt.AddressOf(sDATA,'var3'),'var3/I')
            myDataTree.Branch("LzSR_%s"%boxes[box].name, rt.AddressOf(sDATA,'var4'),'var4/D')
            myDataTree.Branch("LH0xSR_%s"%boxes[box].name, rt.AddressOf(sDATA,'var5'),'var5/D')
            myDataTree.Branch("LH1xSR_%s"%boxes[box].name, rt.AddressOf(sDATA,'var6'),'var6/D')
            myDataTree.Branch("H0status_%s"%boxes[box].name, rt.AddressOf(sDATA,'var7'),'var7/I')
            myDataTree.Branch("H0covQual_%s"%boxes[box].name, rt.AddressOf(sDATA,'var8'),'var8/I')
            myDataTree.Branch("H1status_%s"%boxes[box].name, rt.AddressOf(sDATA,'var9'),'var9/I')
            myDataTree.Branch("H1covQual_%s"%boxes[box].name, rt.AddressOf(sDATA,'var10'),'var10/I')

            if boxes[box].name=="Jet":
                fr_jet = rt.TFile.Open(self.options.jet_input).Get("Jet/independentFR")
                subsetConstraint = ["b_TTj1b", "b_Vpj", "n_TTj1b", "n_Vpj"] # Preserve the same order as in the covariance matrix!
                subsetParams = rt.RooArgSet()
                listParams = rt.RooArgList()
                muParams = rt.RooArgList()
                for param in subsetConstraint:
                    realPar = boxes[box].workspace.var(param)
                    clonePar = realPar.clone("%s_centralvalue"%param)
                    subsetParams.add(realPar)
                    listParams.add(realPar)
                    clonePar.setConstant(True)
                    muParams.add(clonePar)
                mvaGauss = fr_jet.createHessePdf(subsetParams)
                mvaGauss.SetName("constraint")
                covMatrix = mvaGauss.covarianceMatrix()
                covMatrix *= 16 # multiply covariance matrix by 16 to enlarge the error by 4
                mvaGauss2xErr = rt.RooMultiVarGaussian("constraint2xErr","constraint2xErr",listParams,muParams,covMatrix)
                boxes[box].importToWS(mvaGauss2xErr)
                boxes[box].signalmodelconst = boxes[box].signalmodel+"Constrained"
                boxes[box].workspace.factory('PROD::%s(%s,%s)' % (boxes[box].signalmodelconst,boxes[box].signalmodel,mvaGauss2xErr.GetName()))
            else:
                boxes[box].signalmodelconst = boxes[box].signalmodel
                
            lzDataSR,LH0DataSR,LH1DataSR, frH0Data, frH1Data = getLz(boxes[box],data, fr_central, Extend=True, norm_region=norm_region)
            
            sDATA.var2 = boxes[box].workspace.var("sigma").getVal()
            sDATA.var3 = -1
            sDATA.var4 = lzDataSR
            sDATA.var5 = LH0DataSR
            sDATA.var6 = LH1DataSR
            sDATA.var7 = frH0Data.status()
            sDATA.var8 = frH0Data.covQual()
            sDATA.var9 = frH1Data.status()
            sDATA.var10 = frH1Data.covQual()
            
            myDataTree.Fill()
            
            myTree = rt.TTree("myTree", "myTree")
    
            # THIS IS CRAZY !!!!
            rt.gROOT.ProcessLine("struct MyStruct{Double_t var2;Int_t var3;Double_t var4;Double_t var5;Double_t var6;Int_t var7;Int_t var8;Int_t var9;Int_t var10;};")
            from ROOT import MyStruct

            s = MyStruct()
            myTree.Branch("sigma_%s"%boxes[box].name, rt.AddressOf(s,'var2'),'var2/D')
            myTree.Branch("iToy", rt.AddressOf(s,'var3'),'var3/I')
            myTree.Branch("LzSR_%s"%boxes[box].name, rt.AddressOf(s,'var4'),'var4/D')
            myTree.Branch("LH0xSR_%s"%boxes[box].name, rt.AddressOf(s,'var5'),'var5/D')
            myTree.Branch("LH1xSR_%s"%boxes[box].name, rt.AddressOf(s,'var6'),'var6/D')
            myTree.Branch("H0status_%s"%boxes[box].name, rt.AddressOf(s,'var7'),'var7/I')
            myTree.Branch("H0covQual_%s"%boxes[box].name, rt.AddressOf(s,'var8'),'var8/I')
            myTree.Branch("H1status_%s"%boxes[box].name, rt.AddressOf(s,'var9'),'var9/I')
            myTree.Branch("H1covQual_%s"%boxes[box].name, rt.AddressOf(s,'var10'),'var10/I')

            nuisFile = rt.TFile.Open(self.options.nuisanceFile,"read")
            nuisTree = nuisFile.Get("nuisTree")
            nuisTree.Draw('>>nuisElist','nToy>=%i'%nToyOffset,'entrylist')
            nuisElist = rt.gDirectory.Get('nuisElist')
        
            #prepare MultiGen
            #BEWARE: ROOT 5.34.01 - 5.34.03 has a bug that
            #wraps poisson TWICE around expectedEvents

            
            
            if self.options.expectedlimit == True:
                # use the fr for B hypothesis to generate toys
                fr_B = fr_central
                BModel = boxes[box].getFitPDF(name=boxes[box].fitmodel)
                #genSpecB = BModel.prepareMultiGen(vars,rt.RooFit.Extended(True))
            else:
                # use the fr for SpB hypothesis to generate toys
                fr_SpB = frH0Data
                SpBModel = boxes[box].getFitPDF(name=boxes[box].signalmodel)
                #genSpecSpB = SpBModel.prepareMultiGen(vars,rt.RooFit.Extended(True))
            
                    
            
            for i in xrange(nToyOffset,nToyOffset+nToys):
                print 'Setting limit %i experiment' % i
                tot_toy = rt.RooDataSet()
                if self.options.expectedlimit == False:
                    #generate a toy assuming signal + bkg model          
                    print "generate a toy assuming signal + bkg model"
                    nuisEntry = nuisElist.Next()
                    nuisTree.GetEntry(nuisEntry)
                    reset(boxes[box], fr_SpB, fixSigma = True)
                    for var in RootTools.RootIterator.RootIterator(boxes[box].workspace.set('nuisance')):
                        # for each nuisance, grab gaussian distributed variables from ROOT tree
                        varVal = eval('nuisTree.%s'%var.GetName())
                        var.setVal(varVal)
                        print "NUISANCE PAR %s = %f"%(var.GetName(),var.getVal())
                    boxes[box].workspace.var("sigma").setVal(self.options.signal_xsec)
                    tot_toy = SpBModel.generate(vars,rt.RooFit.Extended(True))
                    print "SpB Expected = %f" %SpBModel.expectedEvents(vars)
                    print "SpB Yield = %f" %tot_toy.numEntries()
                    tot_toy.SetName("sigbkg")

                else:                    
                    #generate a toy assuming only the bkg model
                    print "generate a toy assuming bkg model"
                    reset(boxes[box], fr_B, fixSigma = True)
                    boxes[box].workspace.var("sigma").setVal(0.)
                    tot_toy = BModel.generate(vars,rt.RooFit.Extended(True))
                    print "B Expected = %f" %BModel.expectedEvents(vars)
                    print "B Yield = %f" %tot_toy.numEntries()
                    tot_toy.SetName("bkg")

                print "%s entries = %i" %(tot_toy.GetName(),tot_toy.numEntries())
                print "get Lz for toys"
                
                LzSR, LH0xSR, LH1xSR, frH0, frH1 = getLz(boxes[box],tot_toy, fr_central, Extend=True, norm_region=norm_region)
                
                s.var2 = boxes[box].workspace.var("sigma").getVal()
                s.var3 = i
                s.var4 = LzSR
                s.var5 = LH0xSR
                s.var6 = LH1xSR
                s.var7 = frH0.status()
                s.var8 = frH0.covQual()
                s.var9 = frH1.status()
                s.var10 = frH1.covQual()
            
                myTree.Fill()
                
            print "now closing nuisance file"
            nuisFile.Close()
            print "now storing tree"
            self.store(myTree, dir=box)
            self.store(myDataTree, dir=box)
            print "now deleting objects"
            del nuisElist
            del nuisTree
            del nuisFile
            del sDATA
            del s

    def limit_profile(self, inputFiles, nToys):
        """Set a limit based on the model dependent method"""
        
        def mergeDatasets(datasets, cat, makeBinned = False):
            """Take all of the RooDatasets and merge them into a new one with a RooCategory column"""
            
            keys = datasets.keys()
            data = datasets[keys[0]]
            args = data.get(0)
            
            argset = rt.RooArgSet()
            for a in RootTools.RootIterator.RootIterator(args):
                if a.GetName() in ['MR','Rsq','nBtag']:
                    argset.add(a)
        
            args_tuple = ['RMRTree','RMRTree',argset,rt.RooFit.Index(cat),rt.RooFit.Import(keys[0],data)]
            for k in keys[1:]:
                args_tuple.append(rt.RooFit.Import(k,datasets[k]))
        
            a = tuple(args_tuple)
            merged = rt.RooDataSet(*a)
            if makeBinned:
                return merged.binnedClone('RMRTree')
            return merged
        
        open_files = []
        def getSignalPdf(workspace, inputFile, box):
            """Makes a signal PDF from the input histograms"""
            
            rootFile = rt.TFile.Open(inputFile)
            open_files.append(rootFile)
            wHisto = rootFile.Get('wHisto')
            btag =  rootFile.Get('wHisto_btagerr_pe')
            jes =  rootFile.Get('wHisto_JESerr_pe')
            pdf =  rootFile.Get('wHisto_pdferr_pe')
            
            def renameAndImport(histo):
                #make a memory resident copy
                newHisto = histo.Clone('%s_%s' % (histo.GetName(),box))
                newHisto.SetDirectory(0)
                RootTools.Utils.importToWS(workspace,newHisto)
                return newHisto
            
            wHisto = renameAndImport(wHisto)
            btag = renameAndImport(btag)
            jes = renameAndImport(jes)
            pdf = renameAndImport(pdf)
            
            #rootFile.Close()
            
            #set the per box eff value
            workspace.factory('eff_value_%s[%f]' % (box,wHisto.Integral()) )
            print 'eff_value for box %s is %f' % (box,workspace.var('eff_value_%s'%box).getVal())
            
            signal = rt.RooRazor3DSignal('SignalPDF_%s' % box,'Signal PDF for box %s' % box,
                                         workspace.var('MR'),workspace.var('Rsq'),workspace.var('nBtag'),
                                         workspace,
                                         wHisto.GetName(),jes.GetName(),pdf.GetName(),btag.GetName(),
                                         workspace.var('xJes_prime'),workspace.var('xPdf_prime'),workspace.var('xBtag_prime'))
            RootTools.Utils.importToWS(workspace,signal)
            return signal
        
        def SetConstants(pWs, pMc):
            #
            # Fix all variables in the PDF except observables, POI and
            # nuisance parameters. Note that global observables are fixed.
            # If you need global observables floated, you have to set them
            # to float separately.
            #
            pMc.SetWorkspace(pWs)

            pPdf = pMc.GetPdf()
            pVars = pPdf.getVariables()

            #these are the things to float
            pFloated = rt.RooArgSet(pMc.GetObservables())
            pFloated.add(pMc.GetParametersOfInterest())
            pFloated.add(pMc.GetNuisanceParameters())
            pFloated.add(pWs.set('shape'))
            
            for var in RootTools.RootIterator.RootIterator(pVars):
                pFloatedObj = pFloated.find(var.GetName())
                if pFloatedObj is not None and pFloatedObj:
                    var.setConstant(False)
                else:
                    var.setConstant(True)

        
        print 'Running the profile limit setting code'
            
        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)
        
        if self.options.input is None:
            raise Exception('Limit setting code needs a fit result file as input. None given')
        
        workspace = rt.RooWorkspace('newws')
        
        #create a RooCatagory with the name of each box in it
        workspace.factory('Boxes[%s]' % ','.join(fileIndex.keys()))
        
        #start by restoring all the workspaces etc
        for box, fileName in fileIndex.iteritems():
            wsName = '%s/Box%s_workspace' % (box,box)
            print "Restoring the workspace from %s" % self.options.input
            boxes[box].restoreWorkspace(self.options.input, wsName)
            
            #add nuisance parameters and variables if not already defined
            boxes[box].defineSet("nuisance", self.config.getVariables(box, "nuisance_parameters"), workspace = workspace)
            boxes[box].defineSet("shape", "", workspace = workspace)
            boxes[box].defineSet("other", self.config.getVariables(box, "other_parameters"), workspace = workspace)            
            boxes[box].defineSet("poi", self.config.getVariables(box, "poi"), workspace = workspace)            
            boxes[box].defineSet("variables", self.config.getVariables(box, "variables"), workspace = workspace)

            #add the log-normals for the lumi and efficiency (these are not in the signal PDF)
            #these are treated as global scaling parameters. There is a box by box scaling coefficent
            workspace.factory("expr::lumi('@0 * pow( (1+@1), @2)', lumi_value, lumi_uncert, lumi_prime)")
            workspace.factory("expr::eff('@0 * pow( (1+@1), @2)', eff_value, eff_uncert, eff_prime)") 
        
        workspace.extendSet('variables','Boxes')

        
        # # treating the n parameters as nuisances
        for box in fileIndex:
        #     workspace.extendSet("nuisance", workspace.factory('n_TTj1b_%s_prime[0,-5.,5.]' % box).GetName())
        #     workspace.extendSet("other", workspace.factory('n_TTj1b_%s_value[1.0]' % box).GetName())
        #     workspace.extendSet("nuisance", workspace.factory('n_TTj2b_%s_prime[0,-5.,5.]' % box).GetName())
        #     workspace.extendSet("other", workspace.factory('n_TTj2b_%s_value[1.0]' % box).GetName())
        #     workspace.extendSet("nuisance", workspace.factory('n_Vpj_%s_prime[0,-5.,5.]' % box).GetName())
        #     workspace.extendSet("other", workspace.factory('n_Vpj_%s_value[1.0]' % box).GetName())
        #     if not workspace.var('n_TTj1b_%s_uncert' % box):
        #         workspace.extendSet("other", workspace.factory('n_TTj1b_%s_uncert[0.1]' % box).GetName())
        #     if not workspace.var('n_TTj2b_%s_uncert' % box):
        #         workspace.extendSet("other", workspace.factory('n_TTj2b_%s_uncert[0.1]' % box).GetName())
        #     if not workspace.var('n_Vpj_%s_uncert' % box):
        #         workspace.extendSet("other", workspace.factory('n_Vpj_%s_uncert[0.1]' % box).GetName())
            if not workspace.var("lumi_fraction_%s" % box):
                workspace.extendSet("other", workspace.factory("lumi_fraction_%s[1.0]" % box).GetName())
                
        pdf_names = {}
        datasets = {}
        
        #start by restoring all the workspaces etc
        box_primes = []
        for box, fileName in fileIndex.iteritems():

            #this is the background only PDF used in the fit - we take the version with *no penalty terms* 
            background_pdf = boxes[box].getFitPDF(graphViz=None,name='fitmodel')
            
            # # replace the n parameters by a log normal
            # workspace.factory("expr::n_TTj1b_%s('@0 * pow( (1+@1), @2)', n_TTj1b_%s_value, n_TTj1b_%s_uncert, n_TTj1b_%s_prime)" % (box,box,box,box) )
            # box_primes.append('n_TTj1b_%s_prime' % box)
            # workspace.factory("expr::n_TTj2b_%s('@0 * pow( (1+@1), @2)', n_TTj2b_%s_value, n_TTj2b_%s_uncert, n_TTj2b_%s_prime)" % (box,box,box,box) )
            # box_primes.append('n_TTj2b_%s_prime' % box)
            # workspace.factory("expr::n_Vpj_%s('@0 * pow( (1+@1), @2)', n_Vpj_%s_value, n_Vpj_%s_uncert, n_Vpj_%s_prime)" % (box,box,box,box) )
            # box_primes.append('n_Vpj_%s_prime' % box)
            
            #we import this into the workspace, but we rename things so that they don't clash
            var_names = [v.GetName() for v in RootTools.RootIterator.RootIterator(boxes[box].workspace.set('variables'))]
            
            # # append the new n parameter expressions
            # var_names.append('n_TTj1b_%s' % box)
            # var_names.append('n_TTj2b_%s' % box)
            # var_names.append('n_Vpj_%s' % box)
            
            RootTools.Utils.importToWS(workspace,background_pdf,\
                                        rt.RooFit.RenameAllNodes(box),\
                                        rt.RooFit.RenameAllVariablesExcept(box,','.join(var_names)))
            
            #get the renamed PDF back from the workspace
            background_pdf = workspace.pdf('%s_%s' % (background_pdf.GetName(),box))
            
            #build the signal PDF for this box
            signal_pdf = getSignalPdf(workspace, fileName, box)
            
            #now extend the signal PDF
            #note that we scale the global effcienty and lumi by a fixed coefficient - so there is only one nuisance parameter
            workspace.factory("expr::S_%s('@0*@1*@2*@3*@4', lumi_fraction_%s, lumi, sigma, eff_value_%s, eff)" % (box,box,box) )
            signal_pdf_extended = workspace.factory("RooExtendPdf::%s_extended(%s,S_%s)" % (signal_pdf.GetName(),signal_pdf.GetName(),box) )
            
            #finally add the signal + background PDFs together to get the final PDF
            #everything is already extended so no additional coefficients
            full_pdf = rt.RooAddPdf('SplusBPDF_%s' % box, 'SplusBPDF_%s' % box, rt.RooArgList(signal_pdf_extended,background_pdf))
            RootTools.Utils.importToWS(workspace,full_pdf)

            #store the name of the final PDF            
            pdf_names[box] = full_pdf.GetName() 

            #store the dataset from this box
            datasets[box] = boxes[box].workspace.data('RMRTree')
            
            #add shape parameters
            [workspace.extendSet('shape',p.GetName()) for p in RootTools.RootIterator.RootIterator( background_pdf.getParameters(datasets[box]) ) if not p.isConstant()]
            
            #set the parameters constant
            [p.setConstant(True) for p in RootTools.RootIterator.RootIterator( full_pdf.getParameters(datasets[box]) ) ]


        # for box in fileIndex:
        #     workspace.var("n_TTj1b_%s" % box).setMin(0.)
        #     workspace.var("n_TTj2b_%s" % box).setMin(0.)
        #     workspace.var("n_Vpj_%s" % box).setMin(0.)
            
        #     workspace.var("n_TTj1b_%s" % box).setMax(30.)
        #     workspace.var("n_TTj2b_%s" % box).setMax(30.)
        #     workspace.var("n_Vpj_%s" % box).setMax(30.)
            
        #     workspace.var("b_TTj1b_%s" % box).setMin(0.)
        #     workspace.var("b_TTj2b_%s" % box).setMin(0.)
        #     workspace.var("b_Vpj_%s" % box).setMin(0.)
            
        #     workspace.var("b_TTj1b_%s" % box).setMax(30.)
        #     workspace.var("b_TTj2b_%s" % box).setMax(30.)
        #     workspace.var("b_Vpj_%s" % box).setMax(30.)
            
        #     workspace.var("R0_TTj1b_%s" % box).setMax(0.25)
        #     workspace.var("R0_TTj2b_%s" % box).setMax(0.25)
        #     workspace.var("R0_Vpj_%s" % box).setMax(0.25)
            
        #     workspace.var("R0_TTj1b_%s" % box).setMin(-3.)
        #     workspace.var("R0_TTj2b_%s" % box).setMin(-3.)
        #     workspace.var("R0_Vpj_%s" % box).setMin(-3.)
            
        #     workspace.var("MR0_TTj1b_%s" % box).setMax(450)
        #     workspace.var("MR0_TTj2b_%s" % box).setMax(450)
        #     workspace.var("MR0_Vpj_%s" % box).setMax(450)
            
        #     workspace.var("MR0_TTj1b_%s" % box).setMin(-3000.)
        #     workspace.var("MR0_TTj2b_%s" % box).setMin(-3000.)
        #     workspace.var("MR0_Vpj_%s" % box).setMin(-3000)
        
        print 'Starting to build the combined PDF'


        workspace.cat('Boxes').setRange('FULL',','.join(fileIndex.keys()))


        #make a RooDataset with *all* of the data
        pData = mergeDatasets(datasets, workspace.cat('Boxes'), makeBinned = False)
        print 'Merged dataset'
        pData.Print('V')
        RootTools.Utils.importToWS(workspace,pData)
        
        #we now combine the boxes into a RooSimultaneous. Only a few of the parameters are shared
        workspace.Print('V')
        #Syntax: SIMUL::name(cat,a=pdf1,b=pdf2]   -- Create simultaneous p.d.f index category cat. Make pdf1 to state a, pdf2 to state b
        sim_map = ['%s=%s' % (box,pdf_name) for box, pdf_name in pdf_names.iteritems()]
        print 'SIMUL::CombinedLikelihood(Boxes,%s)' % ','.join(sim_map)
        simultaneous = workspace.factory('SIMUL::CombinedLikelihood(Boxes,%s)' % ','.join(sim_map))
        assert simultaneous and simultaneous is not None
        
        print 'Now adding the Gaussian penalties'

        #multiply the likelihood by some gaussians
        pdf_products = [simultaneous.GetName()]
        
        #used for the global observables
        workspace.defineSet('global','')
        for var in RootTools.RootIterator.RootIterator(workspace.set('nuisance')):
            #check that the number of box related nuisance parameters defined is the same as the number of boxes
            if var.GetName() in box_primes:
                box_primes.remove(var.GetName())
                
            #make a Gaussian for each nuisance parameter
            workspace.factory('RooGaussian::%s_pdf(nom_%s[0,-5,5],%s,%s_sigma[1.])' % (var.GetName(),var.GetName(),var.GetName(),var.GetName()))
            pdf_products.append('%s_pdf' % var.GetName())
            
            #keep track of the Gaussian means, as these are global observables
            workspace.extendSet('global','nom_%s' % var.GetName())
            
        if box_primes:
            raise Exception('There are nuisance parameters defined for boxes that we are not running on: %s' % str(box_primes))
        del box_primes
        
        print 'Now multiplying the likelihood by the penalties'
        
        #multiply the various PDFs together
        print 'PROD::%s_penalties(%s)' % (simultaneous.GetName(),','.join(pdf_products))        
        simultaneous_product = workspace.factory('PROD::%s_penalties(%s)' % (simultaneous.GetName(),','.join(pdf_products)))
        #store the name in case we need it later
        #RootTools.Utils.importToWS(workspace,rt.TObjString(simultaneous_product.GetName()),'fullSplusBPDF')
        simultaneous_product.graphVizTree('fullSplusBPDF.dot')

        
        # print 'This is the final PDF'
        # pdf_params = simultaneous_product.getParameters(pData)
        # print 'Parameters'
        # for var in RootTools.RootIterator.RootIterator(pdf_params):
        #     print '\tisConstant=%r\t\t' % var.isConstant(),
        #     var.Print()
        # #fr = simultaneous_product.fitTo(pData,rt.RooFit.Save(True))
        # #fr.Print("V")

        
        #set the global observables to float from their nominal values - is this needed
        #for p in RootTools.RootIterator.RootIterator(workspace.set('global')): p.setConstant(False)

        #the signal + background model
        pSbModel = rt.RooStats.ModelConfig("SbModel")
        pSbModel.SetWorkspace(workspace)
        pSbModel.SetPdf(simultaneous_product)
        pSbModel.SetParametersOfInterest(workspace.set('poi'))
        pSbModel.SetNuisanceParameters(workspace.set('nuisance'))
        pSbModel.SetGlobalObservables(workspace.set('global'))
        pSbModel.SetObservables(workspace.set('variables'))
        SetConstants(workspace, pSbModel)


        #the background only model
        poiValueForBModel = 0.0
        pBModel = rt.RooStats.ModelConfig(pSbModel)
        pBModel.SetName("BModel")
        pBModel.SetWorkspace(workspace)
        
        
        print 'Starting the limit setting procedure'
        
        #find a reasonable range for the POI    
        stop_xs = 0.0
        yield_at_xs = [(stop_xs,0.0)]
        #with 15 signal events, we *should* be able to set a limit
        mrMean = signal_pdf.mean(workspace.var('MR')).getVal()
        print "signal mrMean = %f"%mrMean
        if mrMean < 800:
            eventsToExclude = 150
        elif mrMean < 1000:
            eventsToExclude = 100
        elif mrMean < 1600:
            eventsToExclude = 50
        else:
            eventsToExclude = 25
        
        while yield_at_xs[-1][0] < eventsToExclude:
            stop_xs += 1e-4
            workspace.var('sigma').setVal(stop_xs)
            signal_yield = 0
            background_yield = 0
            for box in fileIndex:
                signal_yield += workspace.function('S_%s' % box).getVal()
            yield_at_xs.append( (signal_yield, workspace.var('sigma').getVal()) )
        poi_max = yield_at_xs[-1][1]
        print 'Estimated POI Max:',poi_max

        poi_min = 0.00
        print 'For now use :[%f, %f]'%(poi_min,poi_max)
        
        #see e.g. http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/SusyAnalysis/RooStatsTemplate/roostats_twobin.C?view=co
        
        #find global maximum with the signal+background model
        #with conditional MLEs for nuisance parameters
        #and save the parameter point snapshot in the Workspace
        #- safer to keep a default name because some RooStats calculators
        #    will anticipate it
        pNll = pSbModel.GetPdf().createNLL(pData)
        pProfile = pNll.createProfile(rt.RooArgSet())
        minSplusB = pProfile.getVal() # this will do fit and set POI and nuisance parameters to fitted values
        print '\nS+B: %f' % minSplusB 
        
        #save a snap-shot for signal+background
        pPoiAndNuisance = rt.RooArgSet()
        pPoiAndNuisance.add(pSbModel.GetParametersOfInterest())
        pPoiAndNuisance.add(pSbModel.GetNuisanceParameters())
        pSbModel.SetSnapshot(pPoiAndNuisance)
        
        del pNll, pProfile, pPoiAndNuisance
        
        #find a parameter point for generating pseudo-data
        #with the background-only data.
        #save the parameter point snapshot in the Workspace
        pNll = pBModel.GetPdf().createNLL(pData)
        pProfile = pNll.createProfile(workspace.set('poi'))
        workspace.var('sigma').setVal(poiValueForBModel)
        minBonly = pProfile.getVal() #this will do fit and set nuisance parameters to profiled values
        print '\nB only: %f' % minBonly
        print 'pBModel.GetNuisanceParameters() ='
        pBModel.GetNuisanceParameters().Print("v")
        
        #save a snap-shot for background only
        pPoiAndNuisance = rt.RooArgSet()
        pPoiAndNuisance.add(pBModel.GetParametersOfInterest())
        pPoiAndNuisance.add(pBModel.GetNuisanceParameters())
        pBModel.SetSnapshot(pPoiAndNuisance)  

        del pNll, pProfile, pPoiAndNuisance

        workspace.Print("v")

        # pBModel.GetSnapshot().Print("v")
        # pSbModel.GetSnapshot().Print("v")

        # import final stuff to workspace
        RootTools.Utils.importToWS(workspace,pSbModel)
        RootTools.Utils.importToWS(workspace,pBModel)
            

        #self.store(workspace, dir='CombinedLikelihood')
        
        #for some reason, it does not like it when we write everything to the same file
        workspace_name = '%s_CombinedLikelihood_workspace.root' % self.options.output.lower().replace('.root','')
        workspace.writeToFile(workspace_name,True)

        def runLimitSettingMacro(args):
            
            def quoteCintArgString(cintArg):
                return '\\"%s\\"' % cintArg
            
            import string, sys, os
    
            # Arguments to the ROOT script needs to be a comma separated list
            # enclosed in (). Strings should be enclosed in escaped double quotes.
            arglist = []
            for arg in args:
                if type(arg)==type('str'):
                    arglist.append(quoteCintArgString(arg))
                elif type(arg)==type(True):
                    arglist.append(int(arg))
                else:
                    arglist.append(arg)
            rootarg='('+string.join([str(s) for s in arglist],',')+')'
            macro = os.path.join(os.environ['RAZORFIT_BASE'],'macros/photons/StandardHypoTestInvDemo.C')
            return 'root -l -b -q "%s%s"' % (macro,rootarg)
      
        calculator_type = 2 #asymtotic
        if self.options.toys:
            calculator_type = 0
        cmd = runLimitSettingMacro([workspace_name,workspace.GetName(),pSbModel.GetName(),pBModel.GetName(),pData.GetName(),calculator_type,3,True,60,poi_min,poi_max,self.options.toys])
        logfile_name = '%s_CombinedLikelihood_workspace.log' % self.options.output.lower().replace('.root','')
        os.system('%s | tee %s' % (cmd,logfile_name))
        #print "sigma error = %f"%workspace.var('sigma').getError()
        #print '%s | tee %s' % (cmd,logfile_name)
        
#        from ROOT import StandardHypoTestInvDemo
#        #StandardHypoTestInvDemo("fileName","workspace name","S+B modelconfig name","B model name","data set name",calculator type, test statistic type, use CLS, 
#        #                                number of points, xmin, xmax, number of toys, use number counting)
#        calculator_type = 2 #asymtotic
#        if self.options.toys:
#            calculator_type = 0
#        print 'StandardHypoTestInvDemo("%s","%s","%s","%s","%s",2,3,0.0,%f)'\
#                                            % (workspace_name,workspace.GetName(),pSbModel.GetName(),pBModel.GetName(),pData.GetName(),poi_max)
#        result = StandardHypoTestInvDemo(workspace_name,workspace.GetName(),pSbModel.GetName(),pBModel.GetName(),pData.GetName(),
#                                        2,3,True,15,0.0,poi_max,self.options.toys)
#        #set to the median expected limit
#        workspace.var('sigma').setVal(result.GetExpectedUpperLimit(0))
#        signal_yield = 0.
#        for box in fileIndex:
#            signal_yield += workspace.function('S_%s' % box).getVal()
#        print 'Signal yield at median expected limit (%f): %f' % ( workspace.var('sigma').getVal(),signal_yield )
#        self.store(result, dir='CombinedLikelihood')
