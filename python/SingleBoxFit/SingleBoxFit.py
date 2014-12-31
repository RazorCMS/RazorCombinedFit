import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis
import RootTools
import math
# import os


class SingleBoxAnalysis(Analysis.Analysis):

    def __init__(self, outputFile, config, Analysis="INCLUSIVE"):
        super(SingleBoxAnalysis, self).__init__('SingleBoxFit', outputFile, config)
        self.Analysis = Analysis

    def merge(self, workspace, box):
        """Import the contents of a box workspace into the master workspace while enforcing some name-spaceing"""
        for o in RootTools.RootIterator.RootIterator(workspace.componentIterator()):
            if hasattr(o, 'Class') and o.Class().InheritsFrom('RooRealVar'):
                continue
            self.importToWS(o, rt.RooFit.RenameAllNodes(box), rt.RooFit.RenameAllVariables(box))

    def getboxes(self, fileIndex):
        """Refactor out the common box def for fitting and simple toys"""

        import RazorBox
        boxes = {}

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Configuring box %s' % box
            print 'Analysis:', self.Analysis
            boxes[box] = RazorBox.RazorBox(box, self.config.getVariables(box, "variables"),
                                           self.options.fitMode,
                                           self.options.btag,
                                           self.options.fitregion)

            print 'box:', box
            print 'vars:', self.config.getVariables(box, "variables")
            print '>>> getVariablesRange:'

            self.config.getVariablesRange(box, "variables", boxes[box].workspace)

            print '>>> defineSet:'

            if self.options.input is not None:
                continue

            boxes[box].defineSet("pdfpars_TTj2b", self.config.getVariables(box, "pdf_TTj2b"))
            boxes[box].defineSet("otherpars_TTj2b", self.config.getVariables(box, "others_TTj2b"))
            boxes[box].defineSet("btagpars_TTj2b", self.config.getVariables(box, "btag_TTj2b"))

            boxes[box].defineSet("pdfpars_TTj1b", self.config.getVariables(box, "pdf_TTj1b"))
            boxes[box].defineSet("otherpars_TTj1b", self.config.getVariables(box, "others_TTj1b"))
            boxes[box].defineSet("btagpars_TTj1b", self.config.getVariables(box, "btag_TTj1b"))

            boxes[box].defineSet("pdfpars_Vpj", self.config.getVariables(box, "pdf_Vpj"))
            boxes[box].defineSet("otherpars_Vpj", self.config.getVariables(box, "others_Vpj"))
            boxes[box].defineSet("btagpars_Vpj", self.config.getVariables(box, "btag_Vpj"))

            boxes[box].defineFunctions(self.config.getVariables(box, "functions"))

            print '>>> addDataset:'
            if not self.options.limit:
                boxes[box].addDataSet(fileName)

            ##adding pdfs->RazorBox.py##
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
                wsName = '%s/Box%s_workspace' % (box, box)
                print "Restoring the workspace from %s" % self.options.input
                boxes[box].restoreWorkspace(self.options.input, wsName)
            if self.options.signal_injection:
                totalYield += boxes[box].workspace.data('sigbkg').numEntries()
            else:
                totalYield += boxes[box].workspace.data('RMRTree').numEntries()

        boxes[box].workspace.Print("v")
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
            pdf = boxes[box].getFitPDF(name=boxes[box].fitmodel, graphViz=None)
            vars = rt.RooArgSet(boxes[box].workspace.set('variables'))

            if box != simName:
                #get the data yield without cuts
                if self.options.signal_injection:
                    data_yield = boxes[box].workspace.data('sigbkg').numEntries()
                else:
                    data_yield = boxes[box].workspace.data('RMRTree').numEntries()
            else:
                data_yield = totalYield

            #if we just need to write out toys then skip everything else
            if self.options.save_toys_from_fit != "none":
                if box != simName:
                    if self.options.signal_injection:
                        f = boxes[box].workspace.obj('independentFRsigbkg')
                    else:
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

            pre_ = rt.RooRealVar('predicted', 'predicted', -1)
            obs_ = rt.RooRealVar('observed', 'observed', -1)
            qual_ = rt.RooRealVar('quality', 'quality', -1)
            status_ = rt.RooRealVar('status', 'status', -1)
            args = rt.RooArgSet(pre_, obs_, qual_, status_)
            yields = rt.RooDataSet('Yields', 'Yields', args)

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

        # start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():

            # if no input fit result file
            if self.options.input is None:
                print 'Variables for box %s' % box
                boxes[box].workspace.allVars().Print('V')
                print 'Workspace'
                boxes[box].workspace.Print('V')

                # perform the fit
                fit_range = boxes[box].fitregion
                print 'Using the fit range: %s' % fit_range

                fr = boxes[box].fit(fileName, boxes[box].cut,
                                    rt.RooFit.PrintEvalErrors(-1),
                                    rt.RooFit.Extended(True),
                                    rt.RooFit.Range(fit_range))

                self.store(fr, name='independentFR', dir=box)
                self.store(fr.correlationHist("correlation_%s" % box), dir=box)
                getattr(boxes[box].workspace, 'import')(fr, 'independentFR')
                getattr(boxes[box].workspace, 'import')\
                    (rt.TObjString(boxes[box].fitmodel), 'independentFRPDF')

                boxes[box].plot(fileName, self, box,
                                data=boxes[box].workspace.data('RMRTree'),
                                fitmodel=boxes[box].fitmodel,
                                frName='independentFR')
            else:
                wsName = '%s/Box%s_workspace' % (box, box)
                print "Restoring the workspace from %s" % self.options.input
                boxes[box].restoreWorkspace(self.options.input, wsName)
                print 'Variables for box %s' % box
                boxes[box].workspace.allVars().Print('V')
                print 'Workspace'
                boxes[box].workspace.Print('V')

#        if self.options.model_independent_limit:
#            for box, fileName in fileIndex.iteritems():
#                boxes[box].predictBackground(boxes[box].workspace.obj('independentFR'), fileName)

        # skip saving the workspace if the option is set
        if not self.options.nosave_workspace:
            for box in boxes.keys():
                self.store(boxes[box].workspace, 'Box%s_workspace'
                           % box, dir=box)

    def signal_injection(self, inputFiles):
        """Run signal injection fit"""
        print "Run signal injection fit"
        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)

        print 'boxes:', boxes

        workspace = rt.RooWorkspace('newws')

        def reset(box, fr, fixSigma=True, random=False):
            # fix all parameters
            box.fixAllPars()

            for z in box.zeros:
                box.fixPars(z)
                if box.name in box.zeros[z]:
                    box.switchOff(z)
            # float background shape parameters
            if not random:
                zeroIntegral = False
                argList = fr.floatParsFinal()
                for p in RootTools.RootIterator.RootIterator(argList):
                    box.workspace.var(p.GetName()).setVal(p.getVal())
                    box.workspace.var(p.GetName()).setError(p.getError())
                    box.fixParsExact(p.GetName(), False)
                    print "INITIALIZE PARAMETER %s = %f +- %f" % (p.GetName(), p.getVal(), p.getError())
            else:
                zeroIntegral = True
                randomizeAttempts = 0
                components = ['TTj1b', 'TTj2b', 'Vpj']
                componentsOn = [comp for comp in components if box.workspace.var('Ntot_%s' % comp).getVal()]
                print "The components on are ", componentsOn
                while zeroIntegral and randomizeAttempts < 5:
                    argList = fr.randomizePars()
                    for p in RootTools.RootIterator.RootIterator(argList):
                        box.workspace.var(p.GetName()).setVal(p.getVal())
                        box.workspace.var(p.GetName()).setError(p.getError())
                        box.fixParsExact(p.GetName(), False)
                        print "RANDOMIZE PARAMETER %s = %f +- %f" % (p.GetName(), p.getVal(), p.getError())
                    # check how many error messages we have before evaluating pdfs
                    errorCountBefore = rt.RooMsgService.instance().errorCount()
                    print "RooMsgService ERROR COUNT BEFORE = %i" % errorCountBefore
                    # evaluate each pdf, assumed to be called "RazPDF_{component}"
                    # if box.name == "Jet1b":
                    #     pdfname = "PDF"
                    # pdfname = "RazPDF"
                    badPars = []
                    # myvars = rt.RooArgSet(box.workspace.var('MR'), box.workspace.var('Rsq'))
                    for component in componentsOn:
                        # pdfComp = box.workspace.pdf("%s_%s" % (pdfname, component))
                        # pdfValV = pdfComp.getValV(myvars)
                        badPars.append(box.workspace.var('n_%s' % component).getVal() <= 0)
                        badPars.append(box.workspace.var('b_%s' % component).getVal() <= 0)
                        badPars.append(box.workspace.var('MR0_%s' % component).getVal() >= box.workspace.var('MR').getMin())
                        badPars.append(box.workspace.var('R0_%s' % component).getVal() >= box.workspace.var('Rsq').getMin())
                        print badPars
                    # check how many error messages we have after evaluating pdfs
                    errorCountAfter = rt.RooMsgService.instance().errorCount()
                    print "RooMsgService ERROR COUNT AFTER  = %i" % errorCountAfter
                    zeroIntegral = (errorCountAfter > errorCountBefore) or any(badPars)
                    randomizeAttempts += 1

            # fix signal nuisance parameters
            for p in RootTools.RootIterator.RootIterator(box.workspace.set('nuisance')):
                p.setVal(0.)
                box.fixParsExact(p.GetName(), True)

            # float poi or not
            box.fixParsExact("sigma", fixSigma)

            return not zeroIntegral

        def getProfile(box, ds, fr, Extend=True, norm_region='LowRsq,LowMR,HighMR'):
            #reset(box, fr, fixSigma=False)
            #setNorms(box, ds)

            opt = rt.RooLinkedList()
            opt.Add(rt.RooFit.Range(norm_region))
            opt.Add(rt.RooFit.Extended(True))
            #opt.Add(rt.RooFit.Save(True))
            #opt.Add(rt.RooFit.Hesse(True))
            #opt.Add(rt.RooFit.Minos(False))
            #opt.Add(rt.RooFit.PrintLevel(-1))
            #opt.Add(rt.RooFit.PrintEvalErrors(10))
            opt.Add(rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))

            box.workspace.var("sigma").setVal(self.options.signal_xsec)
            box.workspace.var("sigma").setConstant(False)

            box.workspace.var("sigma").setVal(self.options.signal_xsec)



            pNll = box.getFitPDF(name=box.signalmodel).createNLL(ds,opt)
            minuit = rt.RooMinuit(pNll)
            minuit.migrad()
            minuit.hesse()
            fr_SpB = minuit.save()
            fr_SpB.Print("v")
            bestFit = fr_SpB.minNll()

            pN2ll = rt.RooFormulaVar("pN2ll","2*@0-2*%f"%bestFit,rt.RooArgList(pNll))
            print "bestFit", pNll.getVal()

            tlines = []
            if ds.GetName()=="sigbkg":
                if self.options.signal_xsec==0.01:
                    box.fixPars("TTj2b")
                    myRange = rt.RooFit.Range(0.007,0.016)
                    myLabel = "sigbkg"+str(self.options.signal_xsec)
                    tline = rt.TLine(0.007,1,0.016,1)
                    tline.SetLineColor(rt.kRed)
                    tline.SetLineWidth(2)
                    tlines.append(tline)
                    tline = rt.TLine(0.007,4,0.016,4)
                    tline.SetLineColor(rt.kRed)
                    tline.SetLineWidth(2)
                    tlines.append(tline)
                elif self.options.signal_xsec==0.003:
                    box.fixPars("Ntot_TTj1b")
                    myRange = rt.RooFit.Range(0.0006,0.0059)
                    myLabel = "sigbkg"+str(self.options.signal_xsec)
                    tline = rt.TLine(0.0006,1,0.0059,1)
                    tline.SetLineColor(rt.kRed)
                    tline.SetLineWidth(2)
                    tlines.append(tline)
                    tline = rt.TLine(0.0006,4,0.0059,4)
                    tline.SetLineColor(rt.kRed)
                    tline.SetLineWidth(2)
                    tlines.append(tline)
                elif self.options.signal_xsec==0.005:
                    myRange = rt.RooFit.Range(0.002,0.0092)
                    myLabel = "sigbkg"+str(self.options.signal_xsec)
                elif self.options.signal_xsec==0.0:
                    box.fixPars("Ntot_TTj2b")
                    myRange = rt.RooFit.Range(-0.0005,0.0018)
                    myLabel = "bkg"
                    tline = rt.TLine(-0.0005,1,0.0018,1)
                    tline.SetLineColor(rt.kRed)
                    tline.SetLineWidth(2)
                    tlines.append(tline)
                    tline = rt.TLine(-0.0005,4,0.0018,4)
                    tline.SetLineColor(rt.kRed)
                    tline.SetLineWidth(2)
                    tlines.append(tline)
            else:
                myRange = rt.RooFit.Range(-0.0023,0.001)
                myLabel = "data"
                tline = rt.TLine(-0.0023,1,0.001,1)
                tline.SetLineColor(rt.kRed)
                tline.SetLineWidth(2)
                tlines.append(tline)
                tline = rt.TLine(-0.0023,4,0.001,4)
                tline.SetLineColor(rt.kRed)
                tline.SetLineWidth(2)
                tlines.append(tline)

            box.workspace.set('poi').Print("V")
            pProfile = pN2ll.createProfile(box.workspace.set('poi'))
            rt.gStyle.SetOptTitle(0)

            frame = box.workspace.var('sigma').frame(rt.RooFit.Bins(10),myRange,rt.RooFit.Title(""))
            pN2ll.plotOn(frame,rt.RooFit.ShiftToZero(),rt.RooFit.LineStyle(2),rt.RooFit.Name("pN2ll"))
            pProfile.plotOn(frame,rt.RooFit.LineColor(rt.kBlack),rt.RooFit.Name("pProfile"))
            for tline in tlines:
                frame.addObject(tline,"")

            prof = rt.TCanvas("prof","prof",500,400)
            frame.SetMinimum(0)
            frame.SetMaximum(6)
            frame.SetXTitle("#sigma [pb]")
            frame.SetYTitle("-2 #Delta log L")
            frame.SetTitleSize(0.05,"X")
            frame.SetTitleOffset(0.8,"X")
            frame.SetTitleSize(0.05,"Y")
            frame.SetTitleOffset(0.8,"Y")

            frame.Draw()
            leg = rt.TLegend(0.2,0.7,0.6,0.8)
            leg.SetTextFont(42)
            leg.SetFillColor(rt.kWhite)
            leg.SetLineColor(rt.kWhite)

            leg.AddEntry("pProfile", "Stat + Syst","l")
            leg.AddEntry("pN2ll", "Stat Only","l")
            leg.Draw()

            l = rt.TLatex()
            l.SetTextAlign(12)
            l.SetTextSize(0.05)
            l.SetTextFont(42)
            l.SetNDC()
            if ds.GetName()=="sigbkg":
                l.DrawLatex(0.2,0.85,"#sigma*=%s pb"%str(self.options.signal_xsec))
            else:
                l.SetTextSize(0.045)
                l.DrawLatex(0.15,0.85,"CMS Preliminary, #sqrt{s} = 8 TeV, #int L = 19.3 fb^{-1}")
                l.SetTextSize(0.05)
            l.DrawLatex(0.1,0.95,"T1bbbb m_{#tilde{g}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV, %s Box"%(1325,50,box.name))

            prof.Print("profileLL"+myLabel+".pdf")

            return fr_SpB


        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            # restore the workspace now
            wsName = '%s/Box%s_workspace' % (box,box)
            print "Restoring the workspace from %s" % self.options.input
            boxes[box].restoreWorkspace(self.options.input, wsName)

            variables = boxes[box].workspace.set('variables')
            data = boxes[box].workspace.data('RMRTree')
            fr_B = boxes[box].workspace.obj('independentFR')

            # add signal specific parameters and nuisance parameters
            boxes[box].defineSet("nuisance", self.config.getVariables(box, "nuisance_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("other", self.config.getVariables(box, "other_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("poi", self.config.getVariables(box, "poi"), workspace = boxes[box].workspace)
            boxes[box].workspace.factory("expr::lumi('@0 * pow( (1+@1), @2)', lumi_value, lumi_uncert, lumi_prime)")
            boxes[box].workspace.factory("expr::eff('@0 * pow( (1+@1), @2)', eff_value, eff_uncert, eff_prime)")

            for p in RootTools.RootIterator.RootIterator(boxes[box].workspace.set('nuisance')):
                p.setVal(0.)
                boxes[box].fixParsExact(p.GetName(),True)

            # change upper limits of variables
            #boxes[box].workspace.var("Ntot_TTj1b").setMax(1e6)
            #boxes[box].workspace.var("Ntot_TTj2b").setMax(1e6)
            #boxes[box].workspace.var("Ntot_Vpj").setMax(1e6)

            #add a signal model to the workspace
            signalModel = boxes[box].addSignalModel(fileIndex[box], self.options.signal_xsec)

            print 'Variables for box %s' % box
            boxes[box].workspace.allVars().Print('V')
            print 'Workspace'
            boxes[box].workspace.Print('V')

            # get the signal+background toy (no nuisnaces)
            SpBModel = boxes[box].getFitPDF(name=boxes[box].signalmodel)
            boxes[box].workspace.var("sigma").setVal(self.options.signal_xsec)

            # injecting signal
            N_TTj1b = boxes[box].workspace.var("Ntot_TTj1b").getVal()
            N_TTj2b = boxes[box].workspace.var("Ntot_TTj2b").getVal()
            boxes[box].workspace.var("Ntot_TTj1b").setVal(0)
            boxes[box].workspace.var("Ntot_TTj2b").setVal(0)
            sig_toy = SpBModel.generate(variables,rt.RooFit.Extended(True))
            boxes[box].workspace.var("Ntot_TTj1b").setVal(N_TTj1b)
            boxes[box].workspace.var("Ntot_TTj2b").setVal(N_TTj2b)
            tot_toy = data.Clone()
            tot_toy.append(sig_toy)
            tot_toy.SetName("sigbkg")

            #tot_toy = SpBModel.generate(variables,rt.RooFit.Extended(True))
            #tot_toy.SetName("sigbkg")
            #tot_toy = data

            print "SpB Expected = %f" %SpBModel.expectedEvents(variables)
            print "SpB Yield = %f" %tot_toy.numEntries()

            if self.options.likelihood_scan:
                fr_SpB = getProfile(boxes[box], tot_toy, fr_B, Extend=True)

            else:
                boxes[box].importToWS(SpBModel)
                boxes[box].importToWS(tot_toy)

                #RootTools.Utils.importToWS(workspace,boxes[box].workspace.obj("wHisto_pdferr_nom_MultiJet"))
                #RootTools.Utils.importToWS(workspace,boxes[box].workspace.obj("wHisto_pdferr_pe_MultiJet"))
                #RootTools.Utils.importToWS(workspace,boxes[box].workspace.obj("wHisto_btagerr_pe_MultiJet"))
                #RootTools.Utils.importToWS(workspace,boxes[box].workspace.obj("wHisto_JESerr_pe_MultiJet"))
                #RootTools.Utils.importToWS(workspace,boxes[box].workspace.obj("wHisto_ISRerr_pe_MultiJet"))
                #RootTools.Utils.importToWS(workspace,SpBModel)
                RootTools.Utils.importToWS(workspace,tot_toy)
                RootTools.Utils.importToWS(workspace,boxes[box].getFitPDF(name=boxes[box].fitmodel))

                # backgrounds
                boxes[box].defineSet("variables", self.config.getVariables(box, "variables"),workspace)

                boxes[box].defineSet("pdfpars_TTj2b", self.config.getVariables(box, "pdf_TTj2b"),workspace)
                boxes[box].defineSet("otherpars_TTj2b", self.config.getVariables(box, "others_TTj2b"),workspace)
                boxes[box].defineSet("btagpars_TTj2b", self.config.getVariables(box, "btag_TTj2b"),workspace)

                boxes[box].defineSet("pdfpars_TTj1b", self.config.getVariables(box, "pdf_TTj1b"),workspace)
                boxes[box].defineSet("otherpars_TTj1b", self.config.getVariables(box, "others_TTj1b"),workspace)
                boxes[box].defineSet("btagpars_TTj1b", self.config.getVariables(box, "btag_TTj1b"))

                boxes[box].defineSet("pdfpars_Vpj", self.config.getVariables(box, "pdf_Vpj"),workspace)
                boxes[box].defineSet("otherpars_Vpj", self.config.getVariables(box, "others_Vpj"),workspace)
                boxes[box].defineSet("btagpars_Vpj", self.config.getVariables(box, "btag_Vpj"),workspace)

                boxes[box].defineFunctions(self.config.getVariables(box,"functions"))

                # define the fit range
                fit_range = boxes[box].fitregion

                opt = rt.RooLinkedList()
                opt.Add(rt.RooFit.Range(fit_range))
                opt.Add(rt.RooFit.Extended(True))
                opt.Add(rt.RooFit.Save(True))
                opt.Add(rt.RooFit.Hesse(True))
                opt.Add(rt.RooFit.Minos(False))
                opt.Add(rt.RooFit.PrintLevel(-1))
                opt.Add(rt.RooFit.PrintEvalErrors(0))
                #opt.Add(rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))

                #fr = boxes[box].getFitPDF(name=boxes[box].fitmodel).fitTo(tot_toy, opt)
                #boxes[box].fixPars("TTj2b")
                fr = boxes[box].getFitPDF(name=boxes[box].fitmodel).fitTo(tot_toy, opt)
                #fr = boxes[box].getFitPDF(name=boxes[box].fitmodel).fitTo(data, opt)
                fr.SetName('independentFRsigbkg')
                fr.Print("v")

                boxes[box].importToWS(fr)
                RootTools.Utils.importToWS(workspace,fr)

                self.store(fr, name = 'independentFRsigbkg', dir=box)
                self.store(fr.correlationHist("correlation_%s_sigbkg" % box), dir=box)

                # make any plots required
                #reset(boxes[box], fr_B, fixSigma = True)
                #boxes[box].plot(fileName, self, box, data=data, fitmodel=boxes[box].fitmodel, frName='independentFR')
                boxes[box].plot(fileName, self, box, data=tot_toy, fitmodel=boxes[box].fitmodel, frName='independentFRsigbkg')


            #skip saving the workspace if the option is set
            if not self.options.nosave_workspace:
                for box in boxes.keys():
                    self.store(workspace,'Box%s_workspace' % box, dir=box)

    def limit(self, inputFiles, nToys, nToyOffset):
        """Set a limit based on the model dependent method"""

        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)

        if self.options.input is None:
            raise Exception('Limit setting code needs a fit result file as input. None given')

        def reset(box, fr, fixSigma=True, random=False):
            # fix all parameters
            box.fixAllPars()

            for z in box.zeros:
                box.fixPars(z)
                if box.name in box.zeros[z]:
                    box.switchOff(z)
            # float background shape parameters
            if not random:
                zeroIntegral = False
                argList = fr.floatParsFinal()
                for p in RootTools.RootIterator.RootIterator(argList):
                    box.workspace.var(p.GetName()).setVal(p.getVal())
                    box.workspace.var(p.GetName()).setError(p.getError())
                    box.fixParsExact(p.GetName(), False)
                    print "INITIALIZE PARAMETER %s = %f +- %f" % (p.GetName(), p.getVal(), p.getError())
            else:
                zeroIntegral = True
                randomizeAttempts = 0
                components = ['TTj1b', 'TTj2b', 'Vpj']
                componentsOn = [comp for comp in components if box.workspace.var('Ntot_%s' % comp).getVal()]
                print "The components on are ", componentsOn
                while zeroIntegral and randomizeAttempts < 5:
                    argList = fr.randomizePars()
                    for p in RootTools.RootIterator.RootIterator(argList):
                        box.workspace.var(p.GetName()).setVal(p.getVal())
                        box.workspace.var(p.GetName()).setError(p.getError())
                        box.fixParsExact(p.GetName(), False)
                        print "RANDOMIZE PARAMETER %s = %f +- %f" % (p.GetName(), p.getVal(), p.getError())
                    # check how many error messages we have before evaluating pdfs
                    errorCountBefore = rt.RooMsgService.instance().errorCount()
                    print "RooMsgService ERROR COUNT BEFORE = %i" % errorCountBefore
                    # evaluate each pdf, assumed to be called "RazPDF_{component}"
                    if box.name == "Jet1b":
                        pdfname = "PDF"
                    pdfname = "RazPDF"
                    badPars = []
                    myvars = rt.RooArgSet(box.workspace.var('MR'), box.workspace.var('Rsq'))
                    for component in componentsOn:
                        pdfComp = box.workspace.pdf("%s_%s" % (pdfname, component))
                        pdfValV = pdfComp.getValV(myvars)
                        badPars.append(box.workspace.var('n_%s' % component).getVal() <= 0)
                        badPars.append(box.workspace.var('b_%s' % component).getVal() <= 0)
                        badPars.append(box.workspace.var('MR0_%s' % component).getVal() >= box.workspace.var('MR').getMin())
                        badPars.append(box.workspace.var('R0_%s' % component).getVal() >= box.workspace.var('Rsq').getMin())
                        print badPars
                    # check how many error messages we have after evaluating pdfs
                    errorCountAfter = rt.RooMsgService.instance().errorCount()
                    print "RooMsgService ERROR COUNT AFTER  = %i" % errorCountAfter
                    zeroIntegral = (errorCountAfter > errorCountBefore) or any(badPars)
                    randomizeAttempts += 1

            # fix signal nuisance parameters
            for p in RootTools.RootIterator.RootIterator(box.workspace.set('nuisance')):
                p.setVal(0.)
                box.workspace.var(p.GetName()).setConstant(True)

            # float poi or not
            box.workspace.var("sigma").setConstant(fixSigma)

            return not zeroIntegral

        def setNorms(box, ds):
            # set normalizations
            print "setting norms"
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
            opt.Add(rt.RooFit.PrintEvalErrors(0))
            #opt.Add(rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))


            #L(s,^th_s|x)
            print "retrieving -log L(x = %s|s,^th_s)" %(ds.GetName())
            covqualH0 = 0
            fitAttempts = 0
            while covqualH0<3 and fitAttempts<3:
                reset(box, fr, fixSigma=True, random=(fitAttempts>0))
                box.workspace.var("sigma").setVal(self.options.signal_xsec)
                box.workspace.var("sigma").setConstant(True)
                frH0 = box.getFitPDF(name=box.signalmodel).fitTo(ds, opt)
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
            while covqualH1<3 and fitAttempts<3:
                if self.options.expectedlimit==True or ds.GetName=="RMRTree":
                    #this means we're doing background-only toys or data
                    #so we should reset to nominal fit pars
                    reset(box, fr, fixSigma=False, random=(fitAttempts>0))
                    if self.options.pulls: box.workspace.var("sigma").setVal(0)
                    else: box.workspace.var("sigma").setVal(1e-6)
                    box.workspace.var("sigma").setConstant(False)
                else:
                    #this means we're doing signal+background toy
                    #so we should reset to the fit with signal strength fixed
                    resetGood = reset(box, frH0, fixSigma=False, random=(fitAttempts>0))
                    if not resetGood:
                        #however, if for some reason the randomization is bad, try this
                        reset(box, fr, fixSigma=False, random=(fitAttempts>0))
                    box.workspace.var("sigma").setVal(self.options.signal_xsec)
                    box.workspace.var("sigma").setConstant(False)
                frH1 = box.getFitPDF(name=box.signalmodel).fitTo(ds, opt)
                frH1.Print("v")
                statusH1 = frH1.status()
                covqualH1 = frH1.covQual()
                LH1x = frH1.minNll()
                print "-log L(x = %s|^s,^th) =  %f"%(ds.GetName(),LH1x)
                fitAttempts+=1

            if box.workspace.var("sigma").getVal()>=self.options.signal_xsec and not self.options.pulls:
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

            self.config.getVariablesRange(box,"variables" ,boxes[box].workspace)

            # add signal specific parameters and nuisance parameters
            boxes[box].defineSet("nuisance", self.config.getVariables(box, "nuisance_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("other", self.config.getVariables(box, "other_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("poi", self.config.getVariables(box, "poi"), workspace = boxes[box].workspace)
            boxes[box].workspace.factory("expr::lumi('@0 * pow( (1+@1), @2)', lumi_value, lumi_uncert, lumi_prime)")
            boxes[box].workspace.factory("expr::eff('@0 * pow( (1+@1), @2)', eff_value, eff_uncert, eff_prime)")

            # change upper limits of variables
            boxes[box].workspace.var("Ntot_TTj1b").setMax(1e6)
            boxes[box].workspace.var("Ntot_TTj2b").setMax(1e6)
            boxes[box].workspace.var("Ntot_Vpj").setMax(1e6)

            #add a signal model to the workspace
            signalModel = boxes[box].addSignalModel(fileIndex[box], self.options.signal_xsec)


            # change upper limit of sigma
            if not self.options.pulls: boxes[box].workspace.var("sigma").setMax(10*self.options.signal_xsec)
            boxes[box].workspace.var("sigma").Print("v")


            print 'Variables for box %s' % box
            boxes[box].workspace.allVars().Print('V')
            print 'Workspace'
            boxes[box].workspace.Print('V')

            fr_central = boxes[box].workspace.obj('independentFR')
            variables = boxes[box].workspace.set('variables')
            data = boxes[box].workspace.data('RMRTree')

            #add in the other signal regions
            norm_region = 'LowRsq,LowMR,HighMR'

            print "get Lz for data"

            myDataTree = rt.TTree("myDataTree", "myDataTree")

            # THIS IS CRAZY !!!!
            rt.gROOT.ProcessLine("struct MyDataStruct{Double_t var1;Double_t var2;Int_t var3;Double_t var4;Double_t var5;Double_t var6;Int_t var7;Int_t var8;Int_t var9;Int_t var10;};")
            from ROOT import MyDataStruct

            sDATA = MyDataStruct()
            myDataTree.Branch("sigma_%s"%boxes[box].name, rt.AddressOf(sDATA,'var1'),'var1/D')
            myDataTree.Branch("sigma_err_%s"%boxes[box].name, rt.AddressOf(sDATA,'var2'),'var2/D')
            myDataTree.Branch("iToy", rt.AddressOf(sDATA,'var3'),'var3/I')
            myDataTree.Branch("LzSR_%s"%boxes[box].name, rt.AddressOf(sDATA,'var4'),'var4/D')
            myDataTree.Branch("LH0xSR_%s"%boxes[box].name, rt.AddressOf(sDATA,'var5'),'var5/D')
            myDataTree.Branch("LH1xSR_%s"%boxes[box].name, rt.AddressOf(sDATA,'var6'),'var6/D')
            myDataTree.Branch("H0status_%s"%boxes[box].name, rt.AddressOf(sDATA,'var7'),'var7/I')
            myDataTree.Branch("H0covQual_%s"%boxes[box].name, rt.AddressOf(sDATA,'var8'),'var8/I')
            myDataTree.Branch("H1status_%s"%boxes[box].name, rt.AddressOf(sDATA,'var9'),'var9/I')
            myDataTree.Branch("H1covQual_%s"%boxes[box].name, rt.AddressOf(sDATA,'var10'),'var10/I')

            lzDataSR,LH0DataSR,LH1DataSR, frH0Data, frH1Data = getLz(boxes[box], data, fr_central, Extend=True, norm_region=norm_region)

            sDATA.var1 = boxes[box].workspace.var("sigma").getVal()
            sDATA.var2 = boxes[box].workspace.var("sigma").getError()
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
            rt.gROOT.ProcessLine("struct MyStruct{Double_t var1;Double_t var2;Int_t var3;Double_t var4;Double_t var5;Double_t var6;Int_t var7;Int_t var8;Int_t var9;Int_t var10;};")
            from ROOT import MyStruct

            s = MyStruct()
            myTree.Branch("sigma_%s"%boxes[box].name, rt.AddressOf(s,'var1'),'var1/D')
            myTree.Branch("sigma_err_%s"%boxes[box].name, rt.AddressOf(s,'var2'),'var2/D')
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

            if self.options.expectedlimit:
                # use the fr for B hypothesis to generate toys
                fr_B = fr_central
                BModel = boxes[box].getFitPDF(name=boxes[box].fitmodel)
                reset(boxes[box], fr_B, fixSigma = True)
                boxes[box].workspace.var('sigma').setVal(0.0)
                genSpecB = BModel.prepareMultiGen(variables,rt.RooFit.Extended(True))
            else:
                # use the fr for SpB hypothesis to generate toys
                fr_SpB = frH0Data
                SpBModel = boxes[box].getFitPDF(name=boxes[box].signalmodel)
                reset(boxes[box], fr_SpB, fixSigma = True)
                boxes[box].workspace.var('sigma').setVal(self.options.signal_xsec)
                genSpecSpB = SpBModel.prepareMultiGen(variables,rt.RooFit.Extended(True))



            for i in xrange(nToyOffset,nToyOffset+nToys):
                print 'Setting limit %i experiment' % i
                tot_toy = rt.RooDataSet()
                if not self.options.expectedlimit:
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
                    #tot_toy = SpBModel.generate(variables,rt.RooFit.Extended(True))
                    tot_toy = SpBModel.generate(genSpecSpB)
                    print "SpB Expected = %f" %SpBModel.expectedEvents(variables)
                    print "SpB Yield = %f" %tot_toy.numEntries()
                    tot_toy.SetName("sigbkg")

                else:
                    #generate a toy assuming only the bkg model
                    print "generate a toy assuming bkg model"
                    reset(boxes[box], fr_B, fixSigma = True)
                    boxes[box].workspace.var("sigma").setVal(0.)
                    #tot_toy = BModel.generate(variables,rt.RooFit.Extended(True))
                    tot_toy = BModel.generate(genSpecB)
                    print "B Expected = %f" %BModel.expectedEvents(variables)
                    print "B Yield = %f" %tot_toy.numEntries()
                    tot_toy.SetName("bkg")

                print "%s entries = %i" %(tot_toy.GetName(),tot_toy.numEntries())
                print "get Lz for toys"

                LzSR, LH0xSR, LH1xSR, frH0, frH1 = getLz(boxes[box],tot_toy, fr_central, Extend=True, norm_region=norm_region)

                s.var1 = boxes[box].workspace.var("sigma").getVal()
                s.var2 = boxes[box].workspace.var("sigma").getError()
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
