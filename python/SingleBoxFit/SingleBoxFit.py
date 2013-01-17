import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis
import RootTools
import math

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
            
    def limit(self, inputFiles, nToys):
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
            #L(H1|x)
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

        def getLzSR(box, ds, fr, Extend = True, norm_region = 'FULL'):
            reset(box, fr)

            #L(H0|x)
            print "retrieving L(H0|x = %s)"%ds.GetName()
            #H0xNLL = box.getFitPDF(name=box.fitmodel).createNLL(ds)
            H0xNLL = box.getFitPDF(name=box.BkgModelSR).createNLL(ds,rt.RooFit.Range(norm_region),rt.RooFit.SumCoefRange(norm_region),rt.RooFit.Extended(Extend))
            LH0x = H0xNLL.getVal()
            #L(H1|x)
            print "retrieving L(H1|x = %s)"%ds.GetName()
            H1xNLL = box.getFitPDF(name=box.SigPlusBkgModelSR).createNLL(ds,rt.RooFit.Range(norm_region),rt.RooFit.SumCoefRange(norm_region),rt.RooFit.Extended(Extend))
            LH1x = H1xNLL.getVal()

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
            #boxes[box].defineSet("others_Signal", self.config.getVariables(box, "others_Signal"))
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
            
            #add in the other signal regions
            if not self.options.doMultijet:
                IntS5 = 0.
                IntS6 = 0.
            else:
                IntS5 = boxes[box].getFitPDF("eBinPDF_Signal").createIntegral(vars,vars,0,'sR5').getVal()
                IntS6 = boxes[box].getFitPDF("eBinPDF_Signal").createIntegral(vars,vars,0,'sR6').getVal()

            NsSR = rt.RooRealVar("NsSR", "NsSR",NS*(IntS1+IntS2+IntS3+IntS4+IntS5+IntS6)/IntS)

            #add in the other signal regions
            norm_region = 'sR1,sR2,sR3,sR4'
            fit_range = ['fR1','fR2','fR3','fR4']
            if self.options.doMultijet:
                norm_region += ',sR5,sR6'
                fit_range.append('fR5')

            N_1stSR_TTj = rt.RooRealVar("N_1stSR_TTj","N_1stSR_TTj", boxes[box].getFitPDF("ePDF1st_TTj").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF1st_TTj").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF1st_TTj").createIntegral(vars,vars).getVal())
            N_2ndSR_TTj = rt.RooRealVar("N_2ndSR_TTj","N_2ndSR_TTj", boxes[box].getFitPDF("ePDF2nd_TTj").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF2nd_TTj").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF2nd_TTj").createIntegral(vars,vars).getVal())
            if not self.options.doMultijet:
                N_1stSR_Wln = rt.RooRealVar("N_1stSR_Wln","N_1stSR_Wln", boxes[box].getFitPDF("ePDF1st_Wln").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF1st_Wln").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF1st_Wln").createIntegral(vars,vars).getVal())
                N_2ndSR_Wln = rt.RooRealVar("N_2ndSR_Wln","N_2ndSR_Wln", boxes[box].getFitPDF("ePDF2nd_Wln").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF2nd_Wln").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF2nd_Wln").createIntegral(vars,vars).getVal())
                N_1stSR_Znn = rt.RooRealVar("N_1stSR_Znn","N_1stSR_Znn", boxes[box].getFitPDF("ePDF1st_Znn").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF1st_Znn").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF1st_Znn").createIntegral(vars,vars).getVal())
                N_2ndSR_Znn = rt.RooRealVar("N_2ndSR_Znn","N_2ndSR_Znn", boxes[box].getFitPDF("ePDF2nd_Znn").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF2nd_Znn").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF2nd_Znn").createIntegral(vars,vars).getVal())
                N_1stSR_Zll = rt.RooRealVar("N_1stSR_Zll","N_1stSR_Zll", boxes[box].getFitPDF("ePDF1st_Zll").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF1st_Zll").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF1st_Zll").createIntegral(vars,vars).getVal())
                N_2ndSR_Zll = rt.RooRealVar("N_2ndSR_Zll","N_2ndSR_Zll", boxes[box].getFitPDF("ePDF2nd_Zll").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF2nd_Zll").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF2nd_Zll").createIntegral(vars,vars).getVal())
            else:
                N_1stSR_QCD = rt.RooRealVar("N_1stSR_QCD","N_1stSR_QCD", boxes[box].getFitPDF("ePDF1st_QCD").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF1st_QCD").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF1st_QCD").createIntegral(vars,vars).getVal())
                N_2ndSR_QCD = rt.RooRealVar("N_2ndSR_QCD","N_2ndSR_QCD", boxes[box].getFitPDF("ePDF2nd_QCD").expectedEvents(vars)*
                                        boxes[box].getFitPDF("ePDF2nd_QCD").createIntegral(vars,vars,0,norm_region).getVal()/
                                        boxes[box].getFitPDF("ePDF2nd_QCD").createIntegral(vars,vars).getVal())

            eBinPDFSR_Signal = rt.RooExtendPdf("eBinPDFSR_Signal","eBinPDFSR_Signal",  boxes[box].workspace.pdf("SignalPdf"), NsSR, norm_region)
            ePDF1stSR_TTj = rt.RooExtendPdf("ePDF1stSR_TTj","ePDF1stSR_TTj", boxes[box].workspace.pdf("PDF1st_TTj"), N_1stSR_TTj, norm_region)
            ePDF2ndSR_TTj = rt.RooExtendPdf("ePDF2ndSR_TTj","ePDF2ndSR_TTj", boxes[box].workspace.pdf("PDF2nd_TTj"), N_2ndSR_TTj, norm_region)
            if not self.options.doMultijet:
                ePDF1stSR_Wln = rt.RooExtendPdf("ePDF1stSR_Wln","ePDF1stSR_Wln", boxes[box].workspace.pdf("PDF1st_Wln"), N_1stSR_Wln, norm_region)
                ePDF2ndSR_Wln = rt.RooExtendPdf("ePDF2ndSR_Wln","ePDF2ndSR_Wln", boxes[box].workspace.pdf("PDF2nd_Wln"), N_2ndSR_Wln, norm_region)
                ePDF1stSR_Znn = rt.RooExtendPdf("ePDF1stSR_Znn","ePDF1stSR_Znn", boxes[box].workspace.pdf("PDF1st_Znn"), N_1stSR_Znn, norm_region)
                ePDF2ndSR_Znn = rt.RooExtendPdf("ePDF2ndSR_Znn","ePDF2ndSR_Znn", boxes[box].workspace.pdf("PDF2nd_Znn"), N_2ndSR_Znn, norm_region)
                ePDF1stSR_Zll = rt.RooExtendPdf("ePDF1stSR_Zll","ePDF1stSR_Zll", boxes[box].workspace.pdf("PDF1st_Zll"), N_1stSR_Zll, norm_region)
                ePDF2ndSR_Zll = rt.RooExtendPdf("ePDF2ndSR_Zll","ePDF2ndSR_Zll", boxes[box].workspace.pdf("PDF2nd_Zll"), N_2ndSR_Zll, norm_region)
            else:
                ePDF1stSR_QCD = rt.RooExtendPdf("ePDF1stSR_QCD","ePDF1stSR_QCD", boxes[box].workspace.pdf("PDF1st_QCD"), N_1stSR_QCD, norm_region)
                ePDF2ndSR_QCD = rt.RooExtendPdf("ePDF2ndSR_QCD","ePDF2ndSR_QCD", boxes[box].workspace.pdf("PDF2nd_QCD"), N_2ndSR_QCD, norm_region)

            boxes[box].importToWS(NsSR)
            boxes[box].importToWS(eBinPDFSR_Signal)
            boxes[box].importToWS(N_1stSR_TTj)
            boxes[box].importToWS(N_2ndSR_TTj)
            boxes[box].importToWS(ePDF1stSR_TTj)
            boxes[box].importToWS(ePDF2ndSR_TTj)
            
            if not self.options.doMultijet:
                boxes[box].importToWS(N_1stSR_Wln)
                boxes[box].importToWS(N_2ndSR_Wln)
                boxes[box].importToWS(ePDF1stSR_Wln)
                boxes[box].importToWS(ePDF2ndSR_Wln)
                boxes[box].importToWS(N_1stSR_Znn)
                boxes[box].importToWS(N_2ndSR_Znn)
                boxes[box].importToWS(ePDF1stSR_Znn)
                boxes[box].importToWS(ePDF2ndSR_Znn)
                boxes[box].importToWS(N_1stSR_Zll)
                boxes[box].importToWS(N_2ndSR_Zll)
                boxes[box].importToWS(ePDF1stSR_Zll)
                boxes[box].importToWS(ePDF2ndSR_Zll)
            else:
                boxes[box].importToWS(N_1stSR_QCD)
                boxes[box].importToWS(N_2ndSR_QCD)

            NB = boxes[box].getFitPDF(boxes[box].fitmodel).expectedEvents(vars)
            IntB  = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars).getVal()
            IntB1 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR1').getVal()
            IntB2 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR2').getVal()
            IntB3 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR3').getVal()
            IntB4 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR4').getVal()
            
            #add the other signal regions
            if not self.options.doMultijet:
                IntB5 = 0.
                IntB6 = 0.
            else:
                IntB5 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR5').getVal()
                IntB6 = boxes[box].getFitPDF(boxes[box].fitmodel).createIntegral(vars,vars,0,'sR6').getVal()                

            BPdfList = rt.RooArgList(boxes[box].workspace.pdf("ePDF1stSR_TTj"))
            if N_2ndSR_TTj.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_TTj"))
            if not self.options.doMultijet:
                if N_1stSR_Wln.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF1stSR_Wln"))
                if N_2ndSR_Wln.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_Wln"))
                if N_1stSR_Znn.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF1stSR_Znn"))
                if N_2ndSR_Znn.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_Znn"))
                if N_1stSR_Zll.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF1stSR_Zll"))
                if N_2ndSR_Zll.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_Zll"))
            else:
                if N_1stSR_QCD.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF1stSR_QCD"))
                if N_2ndSR_QCD.getVal() > 0: BPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_QCD"))

            SpBPdfList = rt.RooArgList(boxes[box].workspace.pdf("ePDF1stSR_TTj"))
            # prevent nan when there is no signal expected
            if not math.isnan(NsSR.getVal()): SpBPdfList.add(boxes[box].workspace.pdf("eBinPDFSR_Signal"))
            if N_2ndSR_TTj.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_TTj"))
            if not self.options.doMultijet:
                if N_1stSR_Wln.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF1stSR_Wln"))
                if N_2ndSR_Wln.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_Wln"))
                if N_1stSR_Znn.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF1stSR_Znn"))
                if N_2ndSR_Znn.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_Znn"))
                if N_1stSR_Zll.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF1stSR_Zll"))
                if N_2ndSR_Zll.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_Zll"))
            else:
                if N_1stSR_QCD.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF1stSR_QCD"))
                if N_2ndSR_QCD.getVal() > 0: SpBPdfList.add(boxes[box].workspace.pdf("ePDF2ndSR_QCD"))
                

            SigPlusBkgModelSR = rt.RooAddPdf("SigPlusBkgModelSR","SigPlusBkgModelSR",SpBPdfList)
            BkgModelSR = rt.RooAddPdf("BkgModelSR","BkgModelSR",BPdfList)
            boxes[box].importToWS(SigPlusBkgModelSR)
            boxes[box].importToWS(BkgModelSR)
            boxes[box].SigPlusBkgModelSR = "SigPlusBkgModelSR"
            boxes[box].BkgModelSR = "BkgModelSR"

            print "get Lz for data"

            myDataTree = rt.TTree("myDataTree", "myDataTree")
    
            # THIS IS CRAZY !!!!
            #rt.gROOT.ProcessLine("struct MyDataStruct{Double_t var4;Double_t var5;Double_t var6;Double_t var7;Double_t var8;Double_t var9;};")
            rt.gROOT.ProcessLine("struct MyDataStruct{Double_t var4;Double_t var5;Double_t var6;};")
            from ROOT import MyDataStruct

            sDATA = MyDataStruct()
            myDataTree.Branch("LzSR", rt.AddressOf(sDATA,'var4'),'var4/D')
            myDataTree.Branch("LH0xSR", rt.AddressOf(sDATA,'var5'),'var5/D')
            myDataTree.Branch("LH1xSR", rt.AddressOf(sDATA,'var6'),'var6/D')

            #myDataTree.Branch("LzSRnoExt", rt.AddressOf(sDATA,'var7'),'var7/D')
            #myDataTree.Branch("LH0xSRnoExt", rt.AddressOf(sDATA,'var8'),'var8/D')
            #myDataTree.Branch("LH1xSRnoExt", rt.AddressOf(sDATA,'var9'),'var9/D')

            #myDataTree.Branch("NSpBsR1", rt.AddressOf(sDATA,'var10'), 'var10/D')
            #myDataTree.Branch("NSpBsR2", rt.AddressOf(sDATA,'var11'), 'var11/D')
            #myDataTree.Branch("NSpBsR3", rt.AddressOf(sDATA,'var12'), 'var12/D')
            #myDataTree.Branch("NSpBsR4", rt.AddressOf(sDATA,'var13'), 'var13/D')

            #myDataTree.Branch("NBsR1", rt.AddressOf(sDATA,'var14'), 'var14/D')
            #myDataTree.Branch("NBsR2", rt.AddressOf(sDATA,'var15'), 'var15/D')
            #myDataTree.Branch("NBsR3", rt.AddressOf(sDATA,'var16'), 'var16/D')
            #myDataTree.Branch("NBsR4", rt.AddressOf(sDATA,'var17'), 'var17/D')

            #myDataTree.Branch("NOBSsR1", rt.AddressOf(sDATA,'var18'), 'var18/D')
            #myDataTree.Branch("NOBSsR2", rt.AddressOf(sDATA,'var19'), 'var19/D')
            #myDataTree.Branch("NOBSsR3", rt.AddressOf(sDATA,'var20'), 'var20/D')
            #myDataTree.Branch("NOBSsR4", rt.AddressOf(sDATA,'var21'), 'var21/D')
            
            #lzData,LH0Data,LH1Data = getLz(boxes[box],boxes[box].workspace.data('RMRTree'), fr_central, testForQuality=False)
            lzDataSR,LH0DataSR,LH1DataSR = getLzSR(boxes[box],data, fr_central, Extend=True, norm_region=norm_region)
            #lzDataSRnoExt,LH0DataSRnoExt,LH1DataSRnoExt = getLzSR(boxes[box],data, fr_central, Extend=False, norm_region=norm_region)

            sDATA.var4 = lzDataSR
            sDATA.var5 = LH0DataSR
            sDATA.var6 = LH1DataSR
            #sDATA.var7 = lzDataSRnoExt
            #sDATA.var8 = LH0DataSRnoExt
            #sDATA.var9 = LH1DataSRnoExt

            #sDATA.var10 = NS*IntS1/(IntS)+NB*IntB1/(IntB)
            #sDATA.var11 = NS*IntS2/(IntS)+NB*IntB2/(IntB)
            #sDATA.var12 = NS*IntS3/(IntS)+NB*IntB3/(IntB)
            #sDATA.var13 = NS*IntS4/(IntS)+NB*IntB4/(IntB)

            #sDATA.var14 = NB*IntB1/(IntB)
            #sDATA.var15 = NB*IntB2/(IntB)
            #sDATA.var16 = NB*IntB3/(IntB)
            #sDATA.var17 = NB*IntB4/(IntB)

            #sDATA.var18 = boxes[box].workspace.data('RMRTree').reduce(boxes[box].getVarRangeCutNamed(["sR1"])).numEntries()
            #sDATA.var19 = boxes[box].workspace.data('RMRTree').reduce(boxes[box].getVarRangeCutNamed(["sR2"])).numEntries()
            #sDATA.var20 = boxes[box].workspace.data('RMRTree').reduce(boxes[box].getVarRangeCutNamed(["sR3"])).numEntries()
            #sDATA.var21 = boxes[box].workspace.data('RMRTree').reduce(boxes[box].getVarRangeCutNamed(["sR4"])).numEntries()

            myDataTree.Fill()

            #lzValues = []
            #LH1xValues = []
            #LH0xValues = []

            myTree = rt.TTree("myTree", "myTree")
    
            # THIS IS CRAZY !!!!
            #rt.gROOT.ProcessLine("struct MyStruct{Double_t var4;Double_t var5;Double_t var6;Double_t var7;Double_t var8;Double_t var9;};")
            rt.gROOT.ProcessLine("struct MyStruct{Double_t var4;Double_t var5;Double_t var6;};")
            from ROOT import MyStruct

            s = MyStruct()
            #myTree.Branch("Lz", rt.AddressOf(s,'var1'),'var1/D')
            #myTree.Branch("LH0x", rt.AddressOf(s,'var2'),'var2/D')
            #myTree.Branch("LH1x", rt.AddressOf(s,'var3'),'var3/D')
            myTree.Branch("LzSR", rt.AddressOf(s,'var4'),'var4/D')
            myTree.Branch("LH0xSR", rt.AddressOf(s,'var5'),'var5/D')
            myTree.Branch("LH1xSR", rt.AddressOf(s,'var6'),'var6/D')
            #myTree.Branch("LzSRnoExt", rt.AddressOf(s,'var7'),'var7/D')
            #myTree.Branch("LH0xSRnoExt", rt.AddressOf(s,'var8'),'var8/D')
            #myTree.Branch("LH1xSRnoExt", rt.AddressOf(s,'var9'),'var9/D')
            #myTree.Branch("NOBSsR1", rt.AddressOf(s,'var10'), 'var10/D')
            #myTree.Branch("NOBSsR2", rt.AddressOf(s,'var11'), 'var11/D')
            #myTree.Branch("NOBSsR3", rt.AddressOf(s,'var12'), 'var12/D')
            #myTree.Branch("NOBSsR4", rt.AddressOf(s,'var13'), 'var13/D')

            print "calculate number of bkg events to generate"
            bkgGenNum = boxes[box].getFitPDF(name=boxes[box].fitmodel,graphViz=None).expectedEvents(vars) 
            fitDataSet = boxes[box].workspace.data('RMRTree').reduce(boxes[box].getVarRangeCutNamed(fit_range))
            
            #use the same binning as the signal model
            significance = RootTools.getObject(fileIndex[box],'wHisto_%s_%i'%(boxes[box].name,0))
            significance = significance.Clone('%s_significance' % boxes[box].name)
            significance.Reset()
            sigSum = 0
            
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

            for i in xrange(nToys):
                print 'Setting limit %i experiment' % i

                tot_toy = rt.RooDataSet()
                if self.options.expectedlimit == False:
                    #generate a toy assuming signal + bkg model (same number of events as background only toy)             
                    print "generate a toy assuming signal + bkg model"              
                    sigNorm =  RootTools.getHistNorm(fileIndex[box],'wHisto_%s_%i'%(boxes[box].name,i))
                    #get nominal number of entries, including 17% SIGNAL NORMALIZATION SYSTEMATIC                
                    print "calculate number of sig events to generate"
                    if self.options.signal_xsec > 0.:   
                        # for SMS
                        sigGenNum = boxes[box].workspace.var('Lumi').getVal()*sigNorm*self.options.signal_xsec
                    else:
                        # for CMSSM
                        sigGenNum = boxes[box].workspace.var('Lumi').getVal()*sigNorm/1000
                    print "sigGenNum = %f" % sigGenNum
                    print "bkgGenNum = %f" % bkgGenNum
                    print "numEntriesData = %i" % data.numEntries()
                    PSigGenNum = rt.RooRandom.randomGenerator().Poisson(sigGenNum)
                    print 'PSigGenNum = %d' % PSigGenNum 

                    #this is a work around for a bug in RooHistPdf, where the number of events generated is not what we asked for                    
                    sigHist = RootTools.getObject(fileIndex[box],'wHisto_%s_%i'%(boxes[box].name,i))
                    sig_toy = boxes[box].sampleDatasetFromHistogram2D(boxes[box].workspace.var('MR'),\
                                                                        boxes[box].workspace.var('Rsq'),\
                                                                        sigHist, PSigGenNum)                   
                    bkg_toy = boxes[box].generateToyFRWithVarYield(boxes[box].fitmodel,fr_central)
                    
                    print "sig_toy.numEntries() = %f" %sig_toy.numEntries()
                    print "bkg_toy.numEntries() = %f" %bkg_toy.numEntries()
                    print "fitDataSet.numEntries() = %f" %fitDataSet.numEntries()

                    #sum the toys
                    tot_toy = bkg_toy.reduce("!(%s)" %boxes[box].getVarRangeCutNamed(fit_range))
                    
                    #make the significance plot
                    sigtoyHisto = calcSignificance(significance, sig_toy, tot_toy)
                    print 'significance = %f' % sigtoyHisto.Integral()
                    sigSum += sigtoyHisto.Integral()
                    significance.Add(sigtoyHisto)                     
                    
                    tot_toy.append(sig_toy)
                    tot_toy.append(fitDataSet)
                    print "Total Yield = %f" %tot_toy.numEntries()
                    tot_toy.SetName("sigbkg")

                    del sig_toy
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
                #LzSRnoExt, LH0xSRnoExt,LH1xSRnoExt = getLzSR(boxes[box],tot_toy, fr_central, Extend=False, norm_region=norm_region)
                #if LzSR is None:
                #    print 'WARNING:: Limit setting fit %i is bad. Skipping...' % i
                #    continue
                #lzValues.append(Lz)
                #LH0xValues.append(LH0x)
                #LH1xValues.append(LH1x)
                #lzV.setVal(Lz)
                #values.add(rt.RooArgSet(lzV,lzD,lzDH0,lzDH1))
                #valuesSR.add(rt.RooArgSet(lzDSR,lzDH0SR,lzDH1SR))
                #valuesSRnoExt.add(rt.RooArgSet(lzDSRnoExt,lzDH0SRnoExt,lzDH1SRnoExt))

                #s.var1 = Lz
                #s.var2 = LH0x
                #s.var3 = LH1x

                s.var4 = LzSR
                s.var5 = LH0xSR
                s.var6 = LH1xSR
                #s.var7 = LzSRnoExt
                #s.var8 = LH0xSRnoExt
                #s.var9 = LH1xSRnoExt

                #s.var10 = tot_toy.reduce(boxes[box].getVarRangeCutNamed(["sR1"])).numEntries()
                #s.var11 = tot_toy.reduce(boxes[box].getVarRangeCutNamed(["sR2"])).numEntries()
                #s.var12 = tot_toy.reduce(boxes[box].getVarRangeCutNamed(["sR3"])).numEntries()
                #s.var13 = tot_toy.reduce(boxes[box].getVarRangeCutNamed(["sR4"])).numEntries()

                del tot_toy

                myTree.Fill()
                ### plotting:
                #frame_MR_sig = boxes[box].workspace.var('MR').frame()
                #sig_toy.plotOn(frame_MR_sig)
                #boxes[box].getFitPDF(name=boxes[box].fitmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kBlue))
                #boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kGreen))
                #boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Components(signalModel))
                #self.store(frame_MR_sig,name='MR_%i_sig'%i, dir=box)
            
            #calculate the area integral of the distribution    
            #lzValues.sort()#smallest to largest
            #lzValuesSum = sum(map(abs,lzValues))
            
            #zMin = min(lzValues)
            #zMax = max(lzValues)
            #hist_H1 = rt.TH1D('hist_H1','H1',120,zMin,zMax)
            #for z in lzValues:
            #    hist_H1.Fill(z)
            
            #lzSum = 0
            #lzSig90 = 1e-12+(2*lzData)
            #lzSig95 = 1e-12+(2*lzData)
            #for lz in lzValues:
            #    lzSum += abs(lz)
            #    if lzSum >= 0.1*lzValuesSum:
            #        lz90 = lz
            #    if lzSum >= 0.05*lzValuesSum:
            #        lz95 = lz
            #        break
            #    
            #reject = (lzData>lzSig90,lzData>lzSig95)
            #print 'Result for box %s: lambda_{data}=%f,lambda_{critical}(90,95)=%s, reject(90,95)=%s; ' % (box,lzData,str((lzSig90,lzSig95)),str(reject))

            #self.store(hist_H1, dir=box)
            #self.store(values, dir=box)
            #self.store(valuesSR, dir=box)
            
            sigSum /= (1.*nToys)
            print 'Mean total significance',sigSum
            if significance.Integral() > 0.0:
                significance.Scale(sigSum/significance.Integral())
            self.store(significance, dir=box)            

            self.store(myTree, dir=box)
            self.store(myDataTree, dir=box)
            del sDATA
            del s

    def limit_profile(self, inputFiles, nToys):
        """Set a limit based on the model dependent method"""
        
        def mergeDatasets(datasets, cat):
            """Take all of the RooDatasets and merge them into a new one with a RooCategory column"""
            
            keys = datasets.keys()
            data = datasets[keys[0]]
            args = data.get(0)
            args.add(cat)
        
            args_tuple = ['RMRTree','RMRTree',args,rt.RooFit.Index(cat),rt.RooFit.Import(keys[0],data)]
            for k in keys[1:]:
                args_tuple.append(rt.RooFit.Import(k,datasets[k]))
        
            a = tuple(args_tuple)
            merged = rt.RooDataSet(*a)
        
            return merged
        
        def getSignalPdf(workspace, inputFile, box):
            """Makes a signal PDF from the input histograms"""
            
            wHisto = RootTools.getObject(inputFile,'wHisto')
            btag =  RootTools.getObject(inputFile,'BTAGerr')
            jes =  RootTools.getObject(inputFile,'JESerr')
            pdf =  RootTools.getObject(inputFile,'PDFerr')
            
            def renameAndImport(histo):
                histo.SetName('%s_%s' % (histo.GetName(),box))
                RootTools.Utils.importToWS(workspace,histo)
                return histo
            wHisto = renameAndImport(wHisto)
            btag = renameAndImport(btag)
            jes = renameAndImport(jes)
            pdf = renameAndImport(pdf)
            
            signal = rt.RooRazor2DSignal('SignalPDF_%s' % box,'Signal PDF for box %s' % box,\
                                         workspace.var('MR'),workspace.var('Rsq'),
                                         wHisto,jes,pdf,btag,
                                         workspace.var('xJes_prime'),workspace.var('xPdf_prime'),workspace.var('xBtag_prime'))
            RootTools.Utils.importToWS(workspace,signal)
            
            #set the per box eff value
            workspace.factory('eff_value_%s[%f]' % (box,wHisto.Integral()) )
            print 'eff_value for box %s is %f' % (box,workspace.var('eff_value_%s'%box).getVal())
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
        
        pdf_names = {}
        datasets = {}

        #start by restoring all the workspaces etc
        for box, fileName in fileIndex.iteritems():

            #this is the background only PDF used in the fit - we take the version with *penalty terms* 
            background_pdf = boxes[box].getFitPDF(graphViz=None,name=boxes[box].workspace.obj('independentFRPDF').GetName())
            
            #replace the n parameter by a log normal
            workspace.factory("expr::n2nd_TTj_%s('@0 * pow( (1+@1), @2)', n2nd_TTj_%s_value, n2nd_TTj_%s_uncert, n2nd_TTj_%s_prime)" % (box,box,box,box) )
            
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
            
            


        #make a RooDataset with *all* of the data
        pData = mergeDatasets(datasets, workspace.cat('Boxes'))
        RootTools.Utils.importToWS(workspace,pData)
        
        #we now combine the boxes into a RooSimultanious. Only a few of the parameters are shared
        simultaneous = rt.RooSimultaneous('CombinedLikelihood','CombinedLikelihood',workspace.cat('Boxes'))
        for box, pdf_name in pdf_names.iteritems():
            simultaneous.addPdf(workspace.pdf(pdf_name),box)
        RootTools.Utils.importToWS(workspace,simultaneous)
        
        #multiply the likelihood by some gaussians
        pdf_products = [simultaneous.GetName()]
        
        #used for the global observables
        workspace.defineSet('global','')
        for var in RootTools.RootIterator.RootIterator(workspace.set('nuisance')):
            #make a Gaussian for each nuisance parameter
            workspace.factory('RooGaussian::%s_pdf(nom_%s[0,-5,5],%s,%s_sigma[1.])' % (var.GetName(),var.GetName(),var.GetName(),var.GetName()))
            pdf_products.append('%s_pdf' % var.GetName())
            
            #keep track of the Gaussian means, as these are global observables
            workspace.extendSet('global','nom_%s' % var.GetName())

        #multiply the various PDFs together        
        simultaneous_product = workspace.factory('PROD::%s_penalties(%s)' % (simultaneous.GetName(),','.join(pdf_products)))
        #store the name in case we need it later
        RootTools.Utils.importToWS(workspace,rt.TObjString(simultaneous_product.GetName()),'fullSplusBPDF')
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
        RootTools.Utils.importToWS(workspace,pSbModel)
        
        print 'This is the final PDF'
        pdf_params = simultaneous_product.getParameters(pData)
        print 'Parameters'
        for var in RootTools.RootIterator.RootIterator(pdf_params):
            print '\tisConstant=%r\t\t' % var.isConstant(),
            var.Print()
        #pdf_params.Print("V")

        #fr = simultaneous_product.fitTo(pData,rt.RooFit.Save(True))
        #fr.Print("V")
        
        #print out the workspace contents and store to a ROOT file
        print 'Starting the limit setting procedure'
        workspace.Print("V")

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
        
        #save a snap-shot
        poiValueForBModel = 0.0
        pPoiAndNuisance = rt.RooArgSet()
        pPoiAndNuisance.add(pSbModel.GetNuisanceParameters())
        pPoiAndNuisance.add(pSbModel.GetParametersOfInterest())
        pSbModel.SetSnapshot(pPoiAndNuisance)
        
        del pNll, pProfile, pPoiAndNuisance
        
        #the background only model
        pBModel = rt.RooStats.ModelConfig(pSbModel)
        pBModel.SetName("BModel")
        pBModel.SetWorkspace(workspace)
        
        #Find a parameter point for generating pseudo-data
        #with the background-only data.
        #Save the parameter point snapshot in the Workspace
        pNll = pBModel.GetPdf().createNLL(pData)
        pProfile = pNll.createProfile(workspace.set('poi'))
        workspace.var('sigma').setVal(poiValueForBModel)
        minBonly = pProfile.getVal() #this will do fit and set nuisance parameters to profiled values
        print '\nB only: %f' % minBonly
        
        pPoiAndNuisance = rt.RooArgSet()
        pPoiAndNuisance.add(pBModel.GetNuisanceParameters())
        pPoiAndNuisance.add(pBModel.GetParametersOfInterest())
        pBModel.SetSnapshot(pPoiAndNuisance)        

        #this should be right at the bottom
        RootTools.Utils.importToWS(workspace,pBModel)
                                           
        #self.store(workspace, dir='CombinedLikelihood')
        
        #for some reason, it does not like it when we write everything to the same file
        workspace_name = '%s_CombinedLikelihood_workspace.root' % self.options.output.lower().replace('.root','')
        workspace.writeToFile(workspace_name,True)
        
        #StandardHypoTestInvDemo("fileName","workspace name","S+B modelconfig name","B model name","data set name",calculator type, test statistic type, use CLS, 
        #                                number of points, xmin, xmax, number of toys, use number counting)
        print 'StandardHypoTestInvDemo("%s","%s","%s","%s","%s")'\
                                            % (workspace_name,workspace.GetName(),pSbModel.GetName(),pBModel.GetName(),pData.GetName())
