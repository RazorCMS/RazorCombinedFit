import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis
import RootTools
import math, os

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
        import RazorTauBox
        boxes = {}

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Configuring box %s' % box
            if self.Analysis == "BJET": boxes[box] = RazorBjetBox.RazorBjetBox(box, self.config.getVariables(box, "variables"))
            elif self.Analysis == "MULTIJET":
                try :
                    self.config.getVariables(box, "others_QCD")
                    boxes[box] = RazorMultiJetBox.RazorMultiJetBox(box, self.config.getVariables(box, "variables"))
                except TypeError :
                    boxes[box] = RazorMultiJetBox.RazorMultiJetBox(box, self.config.getVariables(box, "variables"), True)
            elif self.Analysis == "TAU": boxes[box] = RazorTauBox.RazorTauBox(box, self.config.getVariables(box, "variables"))
            else: boxes[box] = RazorBox.RazorBox(box, self.config.getVariables(box, "variables"))
            self.config.getVariablesRange(box,"variables" ,boxes[box].workspace)
            if self.Analysis != "MULTIJET":
                # Wln
                boxes[box].defineSet("pdf1pars_Wln", self.config.getVariables(box, "pdf1_Wln"))
                boxes[box].defineSet("pdf2pars_Wln", self.config.getVariables(box, "pdf2_Wln"))
                boxes[box].defineSet("otherpars_Wln", self.config.getVariables(box, "others_Wln"))
                # Zll
                boxes[box].defineSet("pdf1pars_Zll", self.config.getVariables(box, "pdf1_Zll"))
                boxes[box].defineSet("pdf2pars_Zll", self.config.getVariables(box, "pdf2_Zll"))
                boxes[box].defineSet("otherpars_Zll", self.config.getVariables(box, "others_Zll"))
                if self.Analysis != "TAU":
                    # Znn
                    boxes[box].defineSet("pdf1pars_Znn", self.config.getVariables(box, "pdf1_Znn"))
                    boxes[box].defineSet("pdf2pars_Znn", self.config.getVariables(box, "pdf2_Znn"))
                    boxes[box].defineSet("otherpars_Znn", self.config.getVariables(box, "others_Znn"))
            # TTj
            boxes[box].defineSet("pdf1pars_TTj", self.config.getVariables(box, "pdf1_TTj"))
            boxes[box].defineSet("pdf2pars_TTj", self.config.getVariables(box, "pdf2_TTj"))
            boxes[box].defineSet("otherpars_TTj", self.config.getVariables(box, "others_TTj"))
            if self.Analysis != "TAU" :
                try :
                    # QCD
                    boxes[box].defineSet("pdf1pars_QCD", self.config.getVariables(box, "pdf1_QCD"))
                    boxes[box].defineSet("pdf2pars_QCD", self.config.getVariables(box, "pdf2_QCD"))
                    boxes[box].defineSet("otherpars_QCD", self.config.getVariables(box, "others_QCD"))
                    boxes[box].define(fileName)
                except TypeError:
                    print 'no 2nd component found, ignoring'
                    boxes[box].define(fileName, True)
            if not self.options.limit: boxes[box].addDataSet(fileName)
           
        return boxes

    def toystudy(self, inputFiles, nToys):

        fit_range = "fR1,fR2,fR3,fR4"
        if self.options.full_region:
            fit_range = "FULL"
        elif self.options.doMultijet:
            fit_range = "fR1,fR2,fR3,fR4,fR5"
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
                    boxes[box].writeBackgroundDataToys(f, data_yield*self.options.scale_lumi, box, nToys, self.options.save_toys_from_fit)
                else:
                    boxes[box].writeBackgroundDataToys(f, data_yield*self.options.scale_lumi, box, nToys)
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

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():

            if self.options.input is None:

                print 'Variables for box %s' % box
                boxes[box].workspace.allVars().Print('V')
                print 'Workspace'
                boxes[box].workspace.Print('V')

                # perform the fit
                fit_range = "fR1,fR2,fR3,fR4"
                if self.options.full_region:
                    fit_range = "FULL"
                elif self.options.doMultijet:
                    fit_range = "fR1,fR2,fR3,fR4,fR5"
                print 'Using the fit range: %s' % fit_range    
                fr = boxes[box].fit(fileName,boxes[box].cut, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True), rt.RooFit.Range(fit_range))
                
                self.store(fr, name = 'independentFR', dir=box)
                self.store(fr.correlationHist("correlation_%s" % box), dir=box)
                #store it in the workspace too
                getattr(boxes[box].workspace,'import')(fr,'independentFR')
                #store the name of the PDF used
                getattr(boxes[box].workspace,'import')(rt.TObjString(boxes[box].fitmodel),'independentFRPDF')
                
                if self.options.binned:
                    fr_binned = boxes[box].fit_binned(fileName,boxes[box].cut, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True), rt.RooFit.Range(fit_range))
                    self.store(fr_binned, name = 'independentFRBinned', dir=box)
            
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
        
        def reset(box, fr):
            #for p in RootTools.RootIterator.RootIterator(fr.floatParsInit()):
            for p in RootTools.RootIterator.RootIterator(fr.floatParsFinal()):
                box.workspace.var(p.GetName()).setVal(p.getVal())
                box.workspace.var(p.GetName()).setError(p.getError())
                
            # fix all parameters
            for z in box.zeros:
                box.fixPars(z)
                if box.name in box.zeros[z]:
                    box.switchOff(z)

            box.fixParsExact("rSig",True)
            box.workspace.var("rSig").setVal(1.)

        def getLz(box, ds, fr, testForQuality = True):
            reset(box, fr)
            
            #L(H0|x)
            print "retrieving L(H0|x = %s)"%ds.GetName()
            #H0xNLL = box.getFitPDF(name=box.fitmodel).createNLL(ds)
            theRealFitModel = "fitmodel"
            H0xNLL = box.getFitPDF(name=theRealFitModel).createNLL(ds)
            LH0x = H0xNLL.getVal()
            print "retrieving L(H1|x = %s)"%ds.GetName()
            H1xNLL = box.getFitPDF(name=box.signalmodel).createNLL(ds)
            LH1x = H1xNLL.getVal()

            Lz = LH0x-LH1x
            print "**************************************************"
            print "L(H0|x = %s) = %f" %(ds.GetName(),LH0x)
            print "L(H1|x = %s) = %f" %(ds.GetName(),LH1x)
            print "Lz = L(H0|x = %s) - L(H1|x = %s) = %f" %(ds.GetName(),ds.GetName(),Lz)
            print "**************************************************"

            return Lz, LH0x,LH1x

        def getLzSR(box, ds, fr, Extend = True, norm_region = 'sR1,sR2,sR3,sR4,sR5,sR6'):
            reset(box, fr)

            #L(H0|x)
            print "retrieving L(H0|x = %s)"%ds.GetName()
            H0xNLLAll = box.getFitPDF(name="fitmodel").createNLL(ds,rt.RooFit.Range(norm_region),rt.RooFit.Extended(Extend))
            LH0xAll = H0xNLLAll.getVal()
            H0xNLL = box.getFitPDF(name=box.BkgModelSR).createNLL(ds,rt.RooFit.Range(norm_region),rt.RooFit.SumCoefRange(norm_region),rt.RooFit.Extended(Extend))
            LH0x = H0xNLL.getVal()
            print "-log(L) of bkgModel SR = %f"% LH0x 
            print "-log(L) of bkgModel All = %f"% LH0xAll
            #L(H1|x)
            print "retrieving L(H1|x = %s)"%ds.GetName()
            
            box.workspace.var("eff_prime").setVal(0.0)
            H1xNLLAll = box.getFitPDF(name="fitmodel_SignalCombined").createNLL(ds,rt.RooFit.Range(norm_region),rt.RooFit.Extended(Extend))
            LH1xAll  = H1xNLLAll.getVal()
            H1xNLL = box.getFitPDF(name=box.SigPlusBkgModelSR).createNLL(ds,rt.RooFit.Range(norm_region),rt.RooFit.SumCoefRange(norm_region),rt.RooFit.Extended(Extend))
            
            LH1x = H1xNLL.getVal()
            print "-log(L) of sig+bkgModel SR = %f"% LH1x 
            print "-log(L) of sig+bkgModel All = %f"% LH1xAll
            
            if math.isnan(LH1x):
                print "WARNING: LH1DataSR is nan, most probably because there is no signal expected -> Signal PDF normalization is 0"
                print "         Since this corresponds to no signal/bkg discrimination, returning L(H1)=L(H0)"
                LH1x = LH0x

            Lz = LH0x-LH1x
            print "**************************************************"
            print " Set Extend to %i" %Extend
            print "**************************************************"
            print "L_SR(H0|x = %s) = %f" %(ds.GetName(),LH0x)
            print "L_SR(H1|x = %s) = %f" %(ds.GetName(),LH1x)
            print "Lz = L_SR(H0|x = %s) - L_SR(H1|x = %s) = %f" %(ds.GetName(),ds.GetName(),Lz)
            print "**************************************************"

            del H0xNLL, H1xNLL            
            return Lz, LH0x,LH1x

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Starting limit setting for box %s' % box

            wsName = '%s/Box%s_workspace' % (box,box)
            print "Restoring the workspace from %s" % self.options.input
            boxes[box].restoreWorkspace(self.options.input, wsName)
            # add signal specific parameters 
            boxes[box].defineSet("nuisance_parameters", self.config.getVariables(box, "nuisance_parameters"))
            boxes[box].defineSet("other_parameters", self.config.getVariables(box, "other_parameters"))
            #add a signal model to the workspace
            signalModel = boxes[box].addSignalModel(fileIndex[box], self.options.signal_xsec)
            #need to fix all parameters to their restored values
            #boxes[box].fixAllPars()

            print 'Variables for box %s' % box
            boxes[box].workspace.allVars().Print('V')
            print 'Workspace'
            boxes[box].workspace.Print('V')
            fr_central = boxes[box].workspace.obj('independentFR')    
            vars = boxes[box].workspace.set('variables')
            data = boxes[box].workspace.data('RMRTree')

            # define the yields and the extended pdfs in the SRs
            NS = boxes[box].getFitPDF("eBinPDF_Signal").expectedEvents(vars)
            IntS  = boxes[box].getFitPDF("eBinPDF_Signal").createIntegral(vars,vars).getVal()
            IntS1 = boxes[box].getFitPDF("eBinPDF_Signal").createIntegral(vars,vars,0,'sR1').getVal()
            IntS2 = boxes[box].getFitPDF("eBinPDF_Signal").createIntegral(vars,vars,0,'sR2').getVal()
            IntS3 = boxes[box].getFitPDF("eBinPDF_Signal").createIntegral(vars,vars,0,'sR3').getVal()
            IntS4 = boxes[box].getFitPDF("eBinPDF_Signal").createIntegral(vars,vars,0,'sR4').getVal()
            IntS5 = boxes[box].getFitPDF("eBinPDF_Signal").createIntegral(vars,vars,0,'sR5').getVal()
            IntS6 = boxes[box].getFitPDF("eBinPDF_Signal").createIntegral(vars,vars,0,'sR6').getVal()

            NsSR = rt.RooRealVar("NsSR", "NsSR",NS*(IntS1+IntS2+IntS3+IntS4+IntS5+IntS6)/IntS)

            #add in the other signal regions
            norm_region = 'sR1,sR2,sR3,sR4,sR5,sR6'
            fit_range = ['fR1','fR2','fR3','fR4','fR5']

            N_1st_SR_TTj = rt.RooRealVar("N_1st_SR_TTj","N_1st_SR_TTj", boxes[box].getFitPDF("ePDF1st_TTj").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF1st_TTj").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF1st_TTj").createIntegral(vars,vars).getVal())
            N_2nd_SR_TTj = rt.RooRealVar("N_2nd_SR_TTj","N_2nd_SR_TTj", boxes[box].getFitPDF("ePDF2nd_TTj").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF2nd_TTj").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF2nd_TTj").createIntegral(vars,vars).getVal())
            N_1st_SR_QCD = rt.RooRealVar("N_1st_SR_QCD","N_1st_SR_QCD", boxes[box].getFitPDF("ePDF1st_QCD").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF1st_QCD").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF1st_QCD").createIntegral(vars,vars).getVal())
            N_2nd_SR_QCD = rt.RooRealVar("N_2nd_SR_QCD","N_2nd_SR_QCD", boxes[box].getFitPDF("ePDF2nd_QCD").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF2nd_QCD").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF2nd_QCD").createIntegral(vars,vars).getVal())

            eBinPDF_SR_Signal = rt.RooExtendPdf("eBinPDF_SR_Signal","eBinPDF_SR_Signal",  boxes[box].workspace.pdf("SignalPDF_%s"%boxes[box].name), NsSR, norm_region)
            ePDF1st_SR_TTj = rt.RooExtendPdf("ePDF1st_SR_TTj","ePDF1st_SR_TTj", boxes[box].workspace.pdf("PDF1st_TTj"), N_1st_SR_TTj, norm_region)
            ePDF2nd_SR_TTj = rt.RooExtendPdf("ePDF2nd_SR_TTj","ePDF2nd_SR_TTj", boxes[box].workspace.pdf("PDF2nd_TTj"), N_2nd_SR_TTj, norm_region)
           
            ePDF1st_SR_QCD = rt.RooExtendPdf("ePDF1st_SR_QCD","ePDF1st_SR_QCD", boxes[box].workspace.pdf("PDF1st_QCD"), N_1st_SR_QCD, norm_region)
            ePDF2nd_SR_QCD = rt.RooExtendPdf("ePDF2nd_SR_QCD","ePDF2nd_SR_QCD", boxes[box].workspace.pdf("PDF2nd_QCD"), N_2nd_SR_QCD, norm_region)

            boxes[box].importToWS(NsSR)
            boxes[box].importToWS(eBinPDF_SR_Signal)
            boxes[box].importToWS(N_1st_SR_TTj)
            boxes[box].importToWS(N_2nd_SR_TTj)
            boxes[box].importToWS(ePDF1st_SR_TTj)
            boxes[box].importToWS(ePDF2nd_SR_TTj)
            boxes[box].importToWS(N_1st_SR_QCD)
            boxes[box].importToWS(N_2nd_SR_QCD)

            NB = boxes[box].getFitPDF(boxes[box].fitmodel).expectedEvents(vars)
            IntB  = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars).getVal()
            IntB1 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR1').getVal()
            IntB2 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR2').getVal()
            IntB3 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR3').getVal()
            IntB4 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR4').getVal()
            
            IntB5 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR5').getVal()
            IntB6 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR6').getVal()                

            BPdfList = rt.RooArgList(boxes[box].workspace.pdf("ePDF1st_SR_TTj"))
            if N_2nd_SR_TTj.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF2nd_SR_TTj"))
            if N_1st_SR_QCD.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF1st_SR_QCD"))
            if N_2nd_SR_QCD.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF2nd_SR_QCD"))

            SpBPdfList = rt.RooArgList(boxes[box].workspace.pdf("ePDF1st_SR_TTj"))
            # prevent nan when there is no signal expected
            if not math.isnan(NsSR.getVal()): SpBPdfList.add(boxes[box].workspace.pdf("eBinPDF_SR_Signal"))
            if N_2nd_SR_TTj.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF2nd_SR_TTj"))
            if N_1st_SR_QCD.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF1st_SR_QCD"))
            if N_2nd_SR_QCD.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF2nd_SR_QCD"))
                

            SigPlusBkgModelSR = rt.RooAddPdf("SigPlusBkgModelSR","SigPlusBkgModelSR",SpBPdfList)
            BkgModelSR = rt.RooAddPdf("BkgModelSR","BkgModelSR",BPdfList)
            boxes[box].importToWS(SigPlusBkgModelSR)
            boxes[box].importToWS(BkgModelSR)
            boxes[box].SigPlusBkgModelSR = "SigPlusBkgModelSR"
            boxes[box].BkgModelSR = "BkgModelSR"

            print "get Lz for data"
            
            myDataTree = rt.TTree("myDataTree", "myDataTree")
    
            # THIS IS CRAZY !!!!
            rt.gROOT.ProcessLine("struct MyDataStruct{Double_t var4;Double_t var5;Double_t var6;};")
            from ROOT import MyDataStruct

            sDATA = MyDataStruct()
            myDataTree.Branch("LzSR", rt.AddressOf(sDATA,'var4'),'var4/D')
            myDataTree.Branch("LH0xSR", rt.AddressOf(sDATA,'var5'),'var5/D')
            myDataTree.Branch("LH1xSR", rt.AddressOf(sDATA,'var6'),'var6/D')
            #lzData,LH0Data,LH1Data = getLz(boxes[box],boxes[box].workspace.data('RMRTree'), fr_central, testForQuality=False)
            lzDataSR,LH0DataSR,LH1DataSR = getLzSR(boxes[box],data, fr_central, Extend=True, norm_region=norm_region)
            #lzDataSRnoExt,LH0DataSRnoExt,LH1DataSRnoExt = getLzSR(boxes[box],data, fr_central, Extend=False, norm_region=norm_region)

            sDATA.var4 = lzDataSR
            sDATA.var5 = LH0DataSR
            sDATA.var6 = LH1DataSR
            myDataTree.Fill()

            myTree = rt.TTree("myTree", "myTree")
    
            # THIS IS CRAZY !!!!
            rt.gROOT.ProcessLine("struct MyStruct{Double_t var4;Double_t var5;Double_t var6;};")
            from ROOT import MyStruct

            s = MyStruct()
            myTree.Branch("LzSR", rt.AddressOf(s,'var4'),'var4/D')
            myTree.Branch("LH0xSR", rt.AddressOf(s,'var5'),'var5/D')
            myTree.Branch("LH1xSR", rt.AddressOf(s,'var6'),'var6/D')

            print "calculate number of bkg events to generate"
            bkgGenNum = boxes[box].getFitPDF(name=boxes[box].fitmodel,graphViz=None).expectedEvents(vars) 
            fitDataSet = boxes[box].workspace.data('RMRTree').reduce(boxes[box].getVarRangeCutNamed(fit_range))
            
            # #use the same binning as the signal model
            # significance = RootTools.getObject(fileIndex[box],'wHisto_%s_%i'%(boxes[box].name,0))
            # significance = significance.Clone('%s_significance' % boxes[box].name)
            # significance.Reset()
            # sigSum = 0
            
            def calcSignificance(binning, sig_toy, bkg_toy):
                """Make a histogram of S/sqrt(S+B) from the signal and background datasets"""

                def fill(h, ds):
                    for i in xrange(ds.numEntries()):
                        row = ds.get(i)
                        h.Fill(row.getRealValue('MR'),row.getRealValue('Rsq'))

                #make the histograms
                sigHist = binning.Clone('S')
                sigHist.Reset()
                fill(sigHist,sig_toy)
                
                bgHist = binning.Clone('B')
                bgHist.Reset()
                fill(bgHist,bkg_toy)
                
                significanceToy = binning.Clone('SignificanceToy')
                significanceToy.Reset()
                
                #calculate the significance
                xaxis = sigHist.GetXaxis()
                yaxis = sigHist.GetYaxis()
    
                for i in xrange(1,xaxis.GetNbins()+1):
                    for j in xrange(1,yaxis.GetNbins()+1):
                        bin = sigHist.GetBin(i,j)
            
                        S = sigHist.GetBinContent(bin)
                        B = bgHist.GetBinContent(bin)
            
                        sig = 0.0
                        if B > 0.0:
                            sig = S/rt.TMath.Sqrt(B)
                        significanceToy.SetBinContent(bin,sig)                
                
                return significanceToy            


            boxes[box].workspace.factory("expr::eff('@0 * pow( (1+@1), @2)', eff_value, eff_uncert, eff_prime)")
            
            for i in xrange(nToyOffset,nToyOffset+nToys):
                print 'Setting limit %i experiment' % i

                tot_toy = rt.RooDataSet()
                if self.options.expectedlimit == False:
                    #generate a toy assuming signal + bkg model (same number of events as background only toy)             
                    print "generate a toy assuming signal + bkg model"
                    eff = boxes[box].workspace.function("eff")
                    eff_box = boxes[box].workspace.var("eff_value_%s"%box)
                    # by default this gaussian() method has mean = 0, variance = 1
                    # and uses random seed set up in runAnalysis.py
                    # (to make sure we don't replicate toys)
                    eff_prime =  boxes[box].workspace.var("eff_prime")
                    eff_prime.setVal(rt.RooRandom.gaussian())
                    
                    print "EFFICIENCY FOR THIS TOY IS %f"%((eff.getVal())*(eff_box.getVal()))
                    print " efficiency percent uncertainty = %f"%boxes[box].workspace.var('eff_uncert').getVal()
                    print " nominal efficiency = %f "%eff_box.getVal()
                    
                    sigNorm =  ((eff.getVal())*(eff_box.getVal()))
                    
                    #get nominal number of entries, including 30% SIGNAL NORMALIZATION SYSTEMATIC
                    # for now fluctuate only signal efficiency uncertainty
                    
                    print "calculate number of sig events to generate"
                    if self.options.signal_xsec > 0.:   
                        # for SMS
                        sigGenNum = boxes[box].workspace.var('lumi_value').getVal()*sigNorm*self.options.signal_xsec
                    else:
                        # for CMSSM
                        sigGenNum = boxes[box].workspace.var('lumi_value').getVal()*sigNorm/1000
                    print "sigGenNum = %f" % sigGenNum
                    
                    print "numEntriesData = %i" % data.numEntries()
                    PSigGenNum = rt.RooRandom.randomGenerator().Poisson(sigGenNum)
                    print 'PSigGenNum = %d' % PSigGenNum


                    if PSigGenNum>0: sig_toy = eBinPDF_SR_Signal.generate(vars,PSigGenNum)
                    bkg_toy = boxes[box].generateToyFRWithYield(boxes[box].fitmodel,fr_central, 1)
                    
                    if PSigGenNum>0: print "sig_toy.numEntries() = %f" %sig_toy.numEntries()
                    print "bkg_toy.numEntries() = %f" %bkg_toy.numEntries()
                    print "numEntriesData = %i" % data.numEntries()
                    print "fitDataSet.numEntries() = %f" %fitDataSet.numEntries()

                    #sum the toys
                    tot_toy = bkg_toy.reduce("(%s)" %boxes[box].getVarRangeCutNamed(norm_region.split(",")))
                    if PSigGenNum>0: tot_toy.append(sig_toy)
                    
                    print "Total Yield = %f" %tot_toy.numEntries()
                    tot_toy.SetName("sigbkg")

                    if PSigGenNum>0: del sig_toy
                    del bkg_toy
                else:                    
                    #generate a toy assuming only the bkg model (same number of events as background only toy)
                    print "generate a toy assuming bkg model"
                    bkg_toy = boxes[box].generateToyFRWithVarYield(boxes[box].fitmodel,fr_central)
                    tot_toy = bkg_toy.reduce("!(%s)" %boxes[box].getVarRangeCutNamed(fit_range))
                    tot_toy.append(fitDataSet)
                    tot_toy.SetName("bkg")
                    del bkg_toy

                print "%s entries = %i" %(tot_toy.GetName(),tot_toy.numEntries())
                print "get Lz for toys"
                #Lz, LH0x,LH1x = getLz(boxes[box],tot_toy, fr_central)
                LzSR, LH0xSR,LH1xSR = getLzSR(boxes[box],tot_toy, fr_central, Extend=True, norm_region=norm_region)


                s.var4 = LzSR
                s.var5 = LH0xSR
                s.var6 = LH1xSR
                del tot_toy

                myTree.Fill()
                
            # sigSum /= (1.*nToys)
            # print 'Mean total significance',sigSum
            # if significance.Integral() > 0.0:
            #     significance.Scale(sigSum/significance.Integral())
            # self.store(significance, dir=box)            

            self.store(myTree, dir=box)
            self.store(myDataTree, dir=box)
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
                if a.GetName() in ['MR','Rsq']:
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
            
            signal = rt.RooRazor2DSignal('SignalPDF_%s' % box,'Signal PDF for box %s' % box,\
                                         workspace.var('MR'),workspace.var('Rsq'),
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
        
        for box in fileIndex:
            workspace.extendSet("nuisance", workspace.factory('n2nd_TTj_%s_prime[0,-5.,5.]' % box).GetName())
            workspace.extendSet("other", workspace.factory('n2nd_TTj_%s_value[1.0]' % box).GetName())
            if not workspace.var('n2nd_TTj_%s_uncert' % box):
                workspace.extendSet("other", workspace.factory('n2nd_TTj_%s_uncert[0.1]' % box).GetName())
            if not workspace.var("lumi_fraction_%s" % box):
                workspace.extendSet("other", workspace.factory("lumi_fraction_%s[1.0]" % box).GetName())
        
        pdf_names = {}
        datasets = {}

        #start by restoring all the workspaces etc
        box_primes = []
        for box, fileName in fileIndex.iteritems():

            #this is the background only PDF used in the fit - we take the version with *penalty terms* 
            background_pdf = boxes[box].getFitPDF(graphViz=None,name=boxes[box].workspace.obj('independentFRPDF').GetName())
            
            #replace the n parameter by a log normal
            workspace.factory("expr::n2nd_TTj_%s('@0 * pow( (1+@1), @2)', n2nd_TTj_%s_value, n2nd_TTj_%s_uncert, n2nd_TTj_%s_prime)" % (box,box,box,box) )
            box_primes.append('n2nd_TTj_%s_prime' % box)
            
            #we import this into the workspace, but we rename things so that they don't clash
            var_names = [v.GetName() for v in RootTools.RootIterator.RootIterator(boxes[box].workspace.set('variables'))]
            var_names.append('n2nd_TTj_%s' % box)
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
            
            


        print 'Starting to build the combined PDF'

        #set the binning
        workspace.var('MR').setBins(rt.TMath.Nint(abs(workspace.var('MR').getMax() - workspace.var('MR').getMin() )/50.) )
        workspace.var('Rsq').setBins(30)
        workspace.cat('Boxes').setRange('FULL',','.join(fileIndex.keys()))

        #make a RooDataset with *all* of the data
        pData = mergeDatasets(datasets, workspace.cat('Boxes'), makeBinned = False)
        print 'Merged dataset'
        pData.Print('V')
        RootTools.Utils.importToWS(workspace,pData)
        
        #we now combine the boxes into a RooSimultanious. Only a few of the parameters are shared
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
        

        
        print 'This is the final PDF'
        pdf_params = simultaneous_product.getParameters(pData)
        print 'Parameters'
        for var in RootTools.RootIterator.RootIterator(pdf_params):
            print '\tisConstant=%r\t\t' % var.isConstant(),
            var.Print()
        #fr = simultaneous_product.fitTo(pData,rt.RooFit.Save(True))
        #fr.Print("V")
        
        #print out the workspace contents and store to a ROOT file
        print 'Starting the limit setting procedure'
        workspace.Print("V")
        
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
            for box in fileIndex:
                signal_yield += workspace.function('S_%s' % box).getVal()
            yield_at_xs.append( (signal_yield, workspace.var('sigma').getVal()) )
        poi_max = yield_at_xs[-1][1]
        workspace.var('sigma').setVal(0.0)
        print 'Estimated POI Max:',poi_max

        #see e.g. http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/SusyAnalysis/RooStatsTemplate/roostats_twobin.C?view=co
        
        #find global maximum with the signal+background model
        #with conditional MLEs for nuisance parameters
        #and save the parameter point snapshot in the Workspace
        #- safer to keep a default name because some RooStats calculators
        #    will anticipate it
        pNll = pSbModel.GetPdf().createNLL(pData)
        pProfile = pNll.createProfile(rt.RooArgSet())
        pSbModel.Print('V')
        minSplusB = pProfile.getVal() # this will do fit and set POI and nuisance parameters to fitted values
        print '\nS+B: %f' % minSplusB 
        
        #save a snap-shot
        pPoiAndNuisance = rt.RooArgSet()
        pPoiAndNuisance.add(pSbModel.GetNuisanceParameters())
        pPoiAndNuisance.add(pSbModel.GetParametersOfInterest())
        pSbModel.SetSnapshot(pPoiAndNuisance)
        
        del pNll, pProfile, pPoiAndNuisance
        
        #Find a parameter point for generating pseudo-data
        #with the background-only data.
        #Save the parameter point snapshot in the Workspace
        pNll = pBModel.GetPdf().createNLL(pData)
        pProfile = pNll.createProfile(workspace.set('poi'))
        workspace.var('sigma').setVal(poiValueForBModel)
        pBModel.Print('V')
        minBonly = pProfile.getVal() #this will do fit and set nuisance parameters to profiled values
        print '\nB only: %f' % minBonly
        
        pPoiAndNuisance = rt.RooArgSet()
        pPoiAndNuisance.add(pBModel.GetNuisanceParameters())
        pPoiAndNuisance.add(pBModel.GetParametersOfInterest())
        pBModel.SetSnapshot(pPoiAndNuisance)        

        #this should be right at the bottom
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
            return 'root -l "%s%s"' % (macro,rootarg)
        
        calculator_type = 2 #asymtotic
        if self.options.toys:
            calculator_type = 0
        cmd = runLimitSettingMacro([workspace_name,workspace.GetName(),pSbModel.GetName(),pBModel.GetName(),pData.GetName(),calculator_type,3,True,60,0.0,poi_max,self.options.toys])
        logfile_name = '%s_CombinedLikelihood_workspace.log' % self.options.output.lower().replace('.root','')
        os.system('%s | tee %s' % (cmd,logfile_name))
                
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
