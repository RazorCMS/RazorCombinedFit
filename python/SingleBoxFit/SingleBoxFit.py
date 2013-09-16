import ROOT as rt
# import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis
import RootTools
import math, os
import sys

def line(x1, x2, y1, y2):
     tline = rt.TLine(x1, x2, y1, y2)
     tline.SetLineColor(rt.kRed)
     tline.SetLineWidth(2)
     return tline

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
        import RazorMultiJetBox
        boxes = {}

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Configuring box %s' % box
            if self.Analysis == "MULTIJET":
                try :
                    self.config.getVariables(box, "others_QCD")
                    boxes[box] = RazorMultiJetBox.RazorMultiJetBox(box, self.config.getVariables(box, "variables"))
                except TypeError :
                    boxes[box] = RazorMultiJetBox.RazorMultiJetBox(box, self.config.getVariables(box, "variables"), True)
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

            if self.options.signal_injection:
                 totalYield += boxes[box].workspace.data('sigbkg').numEntries()
            else :
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
            variables = rt.RooArgSet(boxes[box].workspace.set('variables'))

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
                gdata = pdf.generate(variables,rt.RooRandom.randomGenerator().Poisson(data_yield))
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
                fit_range = boxes[box].fitregion
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
        
        def setNorms(box, ds):
            # set normalizations
            N_TTj = box.workspace.var("Ntot_TTj").getVal()
            N_QCD = box.workspace.var("Ntot_QCD").getVal()
            N_Signal = box.workspace.function("Ntot_Signal").getVal()
            Nds = ds.sumEntries()
            if Nds-N_Signal>0:
                box.workspace.var("Ntot_TTj").setVal((Nds-N_Signal)*N_TTj/(N_TTj+N_QCD))
                box.workspace.var("Ntot_QCD").setVal((Nds-N_Signal)*N_QCD/(N_TTj+N_QCD))
  
        def getLz(box, ds, fr, Extend=True, norm_region = 'fR1,fR2,fR3,fR4,fR5'):
            self.reset(box, fr, fixSigma=True)
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
            while covqualH0!=3 and fitAttempts<3:
                self.reset(box, fr, fixSigma=True, random=(fitAttempts>0))
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
            while covqualH1!=3 and fitAttempts<3:
                if self.options.expectedlimit==True or ds.GetName=="RMRTree":
                    #this means we're doing background-only toys or data
                    #so we should reset to nominal fit pars
                    self.reset(box, fr, fixSigma=False, random=(fitAttempts>0))
                    box.workspace.var("sigma").setVal(2e-1)
                    box.workspace.var("sigma").setConstant(False)
                else:
                    #this means we're doing signal+background toy
                    #so we should reset to the fit with signal strength fixed
                    resetGood = self.reset(box, frH0, fixSigma=False, random=(fitAttempts>0))
                    if not resetGood:
                        #however, if for some reason the randomization is bad, try this
                        self.reset(box, fr, fixSigma=False, random=(fitAttempts>0))
                    box.workspace.var("sigma").setVal(self.options.signal_xsec)
                    box.workspace.var("sigma").setConstant(False)
                frH1 = box.getFitPDF(name=box.signalmodel).fitTo(ds, opt)
                frH1.Print("v")
                statusH1 = frH1.status()
                covqualH1 = frH1.covQual()
                LH1x = frH1.minNll()
                print "********************* sigma, fitAttempts:", box.workspace.var("sigma").getVal(), fitAttempts
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

            # add signal specific parameters 
            boxes[box].defineSet("nuisance", self.config.getVariables(box, "nuisance_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("other", self.config.getVariables(box, "other_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("poi", self.config.getVariables(box, "poi"), workspace = boxes[box].workspace)
            boxes[box].workspace.factory("expr::lumi('@0 * pow( (1+@1), @2)', lumi_value, lumi_uncert, lumi_prime)")
            boxes[box].workspace.factory("expr::eff('@0 * pow( (1+@1), @2)', eff_value, eff_uncert, eff_prime)")        
            #boxes[box].workspace.extendSet("nuisance", boxes[box].workspace.factory('n2nd_TTj_prime[0,-5.,5.]').GetName())
            #boxes[box].workspace.extendSet("other", boxes[box].workspace.factory('n2nd_TTj_value[1.0]').GetName())
            #boxes[box].workspace.extendSet("other", boxes[box].workspace.factory('n2nd_TTj_uncert[0.1]').GetName())

            #if not boxes[box].workspace.var('n2nd_TTj_%s_uncert' % box):
            #    boxes[box].workspace.extendSet("other", boxes[box].workspace.factory('n2nd_TTj_%s_uncert[0.1]' % box).GetName())
            #if not boxes[box].workspace.var("lumi_fraction_%s" % box):
            #    boxes[box].workspace.extendSet("other", workspace.factory("lumi_fraction_%s[1.0]" % box).GetName())

            #boxes[box].workspace.factory("expr::n2nd('@0 * pow( (1+@1), @2)', n2nd_TTj_value, n2nd_TTj_uncert, n2nd_TTj_prime)")
            
            # N_TTj = boxes[box].workspace.var("Ntot_TTj").setMax(1e9)
            # N_QCD = boxes[box].workspace.var("Ntot_QCD").setMax(1e9)

            #add a signal model to the workspace
            boxes[box].addSignalModel(fileIndex[box], self.options.signal_xsec)
            #print 'Variables for box %s' % box
            #boxes[box].workspace.allVars().Print('V')
            #print 'Workspace'
            boxes[box].workspace.Print('V')
           
            fr_central = boxes[box].workspace.obj('independentFR')    
            variables = boxes[box].workspace.set('variables')
            data = boxes[box].workspace.data('RMRTree')

            #add in the other signal regions
            norm_region = 'FULL'

            boxes[box].workspace("sigma").setMax(10*self.options.signal_xsec)
            
            BModel = boxes[box].getFitPDF(name=boxes[box].fitmodel)
            fr_B = fr_central
                
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

            boxes[box].signalmodelconst = boxes[box].signalmodel
            lzDataSR,LH0DataSR,LH1DataSR, frH0Data, frH1Data = getLz(boxes[box],data, fr_central, Extend=True, norm_region=norm_region)

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
 
            #prepare MultiGen
            #BEWARE: ROOT 5.34.01 - 5.34.03 has a bug that
            #wraps poisson TWICE around expectedEvents
            if self.options.expectedlimit == True:
                # use the fr for B hypothesis to generate toys
                self.reset(boxes[box], fr_B, fixSigma = True)
                boxes[box].workspace.var('sigma').setVal(0.0)
                genSpecB = BModel.prepareMultiGen(variables,rt.RooFit.Extended(True))
            else:
                # use the fr for SpB hypothesis to generate toys
                fr_SpB = frH0Data
                SpBModel = boxes[box].getFitPDF(name=boxes[box].signalmodel)
                self.reset(boxes[box], fr_SpB, fixSigma = True)
                boxes[box].workspace.var('sigma').setVal(self.options.signal_xsec)
                genSpecSpB = SpBModel.prepareMultiGen(variables,rt.RooFit.Extended(True))
 
            #print "calculate number of bkg events to generate"
            #bkgGenNum = boxes[box].getFitPDF(name=boxes[box].fitmodel,graphViz=None).expectedEvents(variables) 
            #fitDataSet = boxes[box].workspace.data('RMRTree').reduce(boxes[box].getVarRangeCutNamed(fit_range))
            
            for i in xrange(nToyOffset,nToyOffset+nToys):
                print 'Setting limit %i experiment' % i
                tot_toy = rt.RooDataSet()
                if self.options.expectedlimit == False:
                    #generate a toy assuming signal + bkg model          
                    print "generate a toy assuming signal + bkg model"
                    #### What should we use this for now?
                    ##eff = boxes[box].workspace.function("eff")
                    ##eff_box = boxes[box].workspace.var("eff_value_%s"%box)
                    ### by default this gaussian() method has mean = 0, variance = 1
                    ### and uses random seed set up in runAnalysis.py
                    ### (to make sure we don't replicate toys)
                    ##eff_prime =  boxes[box].workspace.var("eff_prime")
                    ##eff_prime.setVal(rt.RooRandom.gaussian())                    

                    nuisEntry = nuisElist.Next()
                    nuisTree.GetEntry(nuisEntry)
                    self.reset(boxes[box], fr_SpB, fixSigma = True)
                    for var in RootTools.RootIterator.RootIterator(boxes[box].workspace.set('nuisance')):
                        # for each nuisance, grab gaussian distributed variables from ROOT tree
                        varVal = eval('nuisTree.%s'%var.GetName())
                        var.setVal(varVal)
                        print "NUISANCE PAR %s = %f"%(var.GetName(),var.getVal())
                    #print  boxes[box].workspace.var("n2nd_TTj_prime").getVal()
                    #boxes[box].workspace.var("n2nd_TTj_prime").setVal(rt.RooRandom.gaussian())
                    #print  boxes[box].workspace.var("n2nd_TTj_prime").getVal()
                    #print boxes[box].workspace.var("n2nd_TTj").getVal()
                    #print boxes[box].workspace.function("n2nd").getVal()
                    #boxes[box].workspace.var("n2nd_TTj").setVal(boxes[box].workspace.function("n2nd").getVal())
                    #print boxes[box].workspace.var("n2nd_TTj").getVal()
                    boxes[box].workspace.var("sigma").setVal(self.options.signal_xsec)

                    #fr_SpB.Print("v")
                    print "SpB Expected = %f" %SpBModel.expectedEvents(variables)
                    #tot_toy = SpBModel.generate(variables,rt.RooFit.Extended(True))
                    tot_toy = SpBModel.generate(genSpecSpB)
                    print "SpB Yield = %f" %tot_toy.numEntries()
                    tot_toy.SetName("sigbkg")

                else:                    
                    #generate a toy assuming only the bkg model
                    print "generate a toy assuming bkg model"
                    self.reset(boxes[box], fr_B, fixSigma = True)
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
                del tot_toy
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

            # sigSum /= (1.*nToys)
            # print 'Mean total significance',sigSum
            # if significance.Integral() > 0.0:
            #     significance.Scale(sigSum/significance.Integral())
            # self.store(significance, dir=box)            

    def reset(self, box, fr, fixSigma=True, random = False):
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
                    box.fixParsExact(p.GetName(),False)
                    print "INITIALIZE PARAMETER %s = %f +- %f"%(p.GetName(),p.getVal(),p.getError())
            else:
                zeroIntegral = True
                randomizeAttempts = 0
                components = ['TTj','QCD']
                componentsOn = [comp for comp in components if box.workspace.var('Ntot_%s'%comp).getVal() > 0.]
                print "The components on are ", componentsOn
                while zeroIntegral and randomizeAttempts<5:
                    argList = fr.randomizePars()
                    for p in RootTools.RootIterator.RootIterator(argList):
                        box.workspace.var(p.GetName()).setVal(p.getVal())
                        box.workspace.var(p.GetName()).setError(p.getError())
                        box.fixParsExact(p.GetName(),False)
                        print "RANDOMIZE PARAMETER %s = %f +- %f"%(p.GetName(),p.getVal(),p.getError())
                    # check how many error messages we have before evaluating pdfs
                    errorCountBefore = rt.RooMsgService.instance().errorCount()
                    print "RooMsgService ERROR COUNT BEFORE = %i"%errorCountBefore
                    # evaluate each pdf, assumed to be called "PDF1st_{component}, etc."
                    badPars = []
                    myvars = rt.RooArgSet(box.workspace.var('MR'),box.workspace.var('Rsq'))
                    for component in componentsOn:
                        pdfComp = box.workspace.pdf("PDF1st_%s"%component)
                        pdfValV = pdfComp.getValV(myvars)
                        pdfComp = box.workspace.pdf("PDF2nd_%s"%component)
                        pdfValV = pdfComp.getValV(myvars)
                        #badPars.append(box.workspace.var('n_%s'%component).getVal() <= 0)
                        badPars.append(box.workspace.var('b1st_%s'%component).getVal() <= 0)
                        badPars.append(box.workspace.var('MR01st_%s'%component).getVal() >= box.workspace.var('MR').getMin())
                        badPars.append(box.workspace.var('R01st_%s'%component).getVal()  >=  box.workspace.var('Rsq').getMin())
                        badPars.append(box.workspace.var('b2nd_%s'%component).getVal() <= 0)
                        badPars.append(box.workspace.var('MR02nd_%s'%component).getVal() >= box.workspace.var('MR').getMin())
                        badPars.append(box.workspace.var('R02nd_%s'%component).getVal()  >=  box.workspace.var('Rsq').getMin())
                        print badPars
                    # check how many error messages we have after evaluating pdfs
                    errorCountAfter = rt.RooMsgService.instance().errorCount()
                    print "RooMsgService ERROR COUNT AFTER  = %i"%errorCountAfter
                    zeroIntegral = (errorCountAfter>errorCountBefore) or any(badPars)
                    randomizeAttempts+=1
            
            # fix signal nuisance parameters
            for p in RootTools.RootIterator.RootIterator(box.workspace.set('nuisance')):
                p.setVal(0.)
                box.fixParsExact(p.GetName(),True)
                
            # float poi or not
            box.fixParsExact("sigma",fixSigma)
            
            return not zeroIntegral

    def signal_injection(self, inputFiles):
        """Run signal injection fit"""

        #the SMS file
        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)
        
        print 'boxes:', boxes

        workspace = rt.RooWorkspace('newws')
        
    ##     def getProfile(box, ds, fr, Extend=True, norm_region = 'Full'):
          
##             opt = rt.RooLinkedList()
##             opt.Add(rt.RooFit.Range(norm_region))
##             opt.Add(rt.RooFit.Extended(True))
##             opt.Add(rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))
             
##             box.workspace.var("sigma").setVal(self.options.signal_xsec)
##             box.workspace.var("sigma").setConstant(False)
     
##             pNll = box.getFitPDF(name=box.signalmodel).createNLL(ds,opt)
##             rt.RooMinuit(pNll).migrad()
##             rt.RooMinuit(pNll).hesse()
##             fr_SpB = rt.RooMinuit(pNll).save()
##             bestFit = fr_SpB.minNll()
##             pN2ll = rt.RooFormulaVar("pN2ll","2*@0-2*%f"%bestFit,rt.RooArgList(pNll))

##             print "bestFit", pNll.getVal()
            
##             tlines = []
##             if ds.GetName()=="sigbkg":
##                 myLabel = "sigbkg"+str(self.options.signal_xsec)
##                 if self.options.signal_xsec==1.0:
##                     myRange = rt.RooFit.Range(0.6,1.6)
##                     tlines.append(line(0.6,1,1.6,1))
##                     tlines.append(line(0.6,4,1.6,4))
##                 elif self.options.signal_xsec==2.0:
##                     myRange = rt.RooFit.Range(1.6,2.6)
##                     tlines.append(line(1.6,4,2.6,4))
##                     tlines.append(line(1.6,4,2.6,4))
##                 elif self.options.signal_xsec==10.0:
##                     myRange = rt.RooFit.Range(9.6,10.6)
##                     tlines.append(line(9.6,1,10.6,1))
##                     tlines.append(line(9.6,4,10.6,4))
##                 elif self.options.signal_xsec==3.0:
##                     myRange = rt.RooFit.Range(2.6,3.6)
##                     tlines.append(line(2.6,1,3.6,1))
##                     tlines.append(line(2.6,4,3.6,4))
##                 elif self.options.signal_xsec==0.5:
##                     myRange = rt.RooFit.Range(0.2,0.65)
##                     tlines.append(line(0.0002,1,0.0065,1))
##                     tlines.append(line(0.0002,4,0.0065,4))
##                 elif self.options.signal_xsec==0.1:
##                     myRange = rt.RooFit.Range(0.06,0.5)
##                     tlines.append(line(0.06,1,0.5,1.))
##                     tlines.append(line(0.06,4,0.5,4))
##                 elif self.options.signal_xsec==0.0:
##                     myRange = rt.RooFit.Range(-0.0021,0.0015)
##                     tlines.append(line(-0.0021,1,0.0015,1))
##                     tlines.append(line(-0.0021,4,0.0015,4))
##                 else:
##                     myRange = rt.RooFit.Range(-0.00195,0.0015)
##                     myLabel = "data"
##                     tlines.append(line(-0.00195,1,0.0015,1))
##                     tlines.append(line(-0.00195,4,0.0015,4))
              
##             pProfile = pN2ll.createProfile(box.workspace.set('poi'))
##             rt.gStyle.SetOptTitle(0)
            
##             frame = box.workspace.var('sigma').frame(rt.RooFit.Bins(10),myRange,rt.RooFit.Title(""))
##             pN2ll.plotOn(frame,rt.RooFit.ShiftToZero(),rt.RooFit.LineStyle(2),rt.RooFit.Name("pN2ll"))
##             pProfile.plotOn(frame,rt.RooFit.LineColor(rt.kBlack),rt.RooFit.Name("pProfile"))
##             for tline in tlines:
##                 frame.addObject(tline,"")
                                
##             prof = rt.TCanvas("prof","prof",500,400)
##             frame.SetMinimum(0)
##             frame.SetMaximum(6)
##             frame.SetXTitle("#sigma [pb]")
##             frame.SetYTitle("-2 #Delta log L")
##             frame.SetTitleSize(0.05,"X")
##             frame.SetTitleOffset(0.8,"X")
##             frame.SetTitleSize(0.05,"Y")
##             frame.SetTitleOffset(0.8,"Y")
            
##             frame.Draw()
##             leg = rt.TLegend(0.2,0.7,0.6,0.8)
##             leg.SetTextFont(42)
##             leg.SetFillColor(rt.kWhite)
##             leg.SetLineColor(rt.kWhite)
            
##             leg.AddEntry("pProfile", "Stat + Syst","l")
##             leg.AddEntry("pN2ll", "Stat Only","l")
##             leg.Draw()
            
##             l = rt.TLatex()
##             l.SetTextAlign(12)
##             l.SetTextSize(0.05)
##             l.SetTextFont(42)
##             l.SetNDC()
##             if ds.GetName()=="sigbkg":
##                 l.DrawLatex(0.2,0.85,"#sigma*=%s pb"%str(self.options.signal_xsec))
##             else:
##                 l.SetTextSize(0.045)
##                 l.DrawLatex(0.15,0.85,"CMS Preliminary, #sqrt{s} = 8 TeV, #int L = 19.3 fb^{-1}")
##                 l.SetTextSize(0.05)
##             l.DrawLatex(0.1,0.95,"T2tt m_{#tilde{g}} = %.0f GeV; m_{#tilde{#chi}} = %.0f GeV, %s Box"%(150,25,box.name))
            
##             prof.Print("profileLL"+myLabel+".pdf")

##             return fr_SpB

            
        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            # restore the workspace now
            wsName = '%s/Box%s_workspace' % (box,box)
            print "Restoring the workspace from %s" % self.options.input
            boxes[box].restoreWorkspace(self.options.input, wsName)#

            variables = boxes[box].workspace.set('variables') #Rsq, MR
            data = boxes[box].workspace.data('RMRTree')
            fr_B = boxes[box].workspace.obj('independentFR')
            
            # add signal specific parameters and nuisance parameters
            boxes[box].defineSet("nuisance", self.config.getVariables(box, "nuisance_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("other", self.config.getVariables(box, "other_parameters"), workspace = boxes[box].workspace)
            boxes[box].defineSet("poi", self.config.getVariables(box, "poi"), workspace = boxes[box].workspace)
            boxes[box].workspace.factory("expr::lumi('@0 * pow( (1+@1), @2)', lumi_value, lumi_uncert, lumi_prime)")
            boxes[box].workspace.factory("expr::eff('@0 * pow( (1+@1), @2)', eff_value, eff_uncert, eff_prime)")
            #boxes[box].workspace.extendSet("nuisance", boxes[box].workspace.factory('n2nd_TTj_prime[0,-5.,5.]').GetName())
            #boxes[box].workspace.extendSet("other", boxes[box].workspace.factory('n2nd_TTj_value[1.0]').GetName())
            #boxes[box].workspace.extendSet("other", boxes[box].workspace.factory('n2nd_TTj_uncert[0.1]').GetName())
            #boxes[box].workspace.factory("expr::n2nd('@0 * pow( (1+@1), @2)', n2nd_TTj_value, n2nd_TTj_uncert, n2nd_TTj_prime)")
           
            for p in RootTools.RootIterator.RootIterator(boxes[box].workspace.set('nuisance')):
                p.setVal(0.)
                print p.GetName()
                boxes[box].fixParsExact(p.GetName(),True)
                #hmm fixing to 0 xbtag_prime, xISR_prime, LepSF. Jes, Pdf, eff, lumi, n2nd ??

            # change upper limits of variables
            boxes[box].workspace.var("Ntot_TTj").setMax(1e6)
            boxes[box].workspace.var("Ntot_QCD").setMax(1e6)

            #add a signal model to the workspace
            signalModel = boxes[box].addSignalModel(fileIndex[box], self.options.signal_xsec) #from RazorMultiJetBox
          
            # get the signal+background toy (no nuisnaces)
            SpBModel = boxes[box].getFitPDF(name=boxes[box].signalmodel)
            boxes[box].workspace.var("sigma").setVal(self.options.signal_xsec)

            
            tot_toy = SpBModel.generate(variables,rt.RooFit.Extended(True))
            print "SpB Expected = %f" %SpBModel.expectedEvents(variables)
            print "SpB Yield = %f" %tot_toy.numEntries()
            tot_toy.SetName("sigbkg")
            
            #boxes[box].importToWS(SpBModel)
            boxes[box].importToWS(tot_toy)#add RooDataSet with name sigbkg (Rsq, MR)
            
            if self.options.likelihood_scan:
                fr_SpB = getProfile(boxes[box], tot_toy, fr_B, Extend=True)
                
            else:
                RootTools.Utils.importToWS(workspace,boxes[box].getFitPDF(name=boxes[box].fitmodel))
                RootTools.Utils.importToWS(workspace,SpBModel)
                RootTools.Utils.importToWS(workspace,tot_toy)
                workspace.Print("v")

                # backgrounds
                boxes[box].defineSet("variables", self.config.getVariables(box, "variables"),workspace)

                boxes[box].defineSet("pdf1pars_TTj", self.config.getVariables(box, "pdf1_TTj"),workspace)
                boxes[box].defineSet("pdf2pars_TTj", self.config.getVariables(box, "pdf2_TTj"),workspace)
                boxes[box].defineSet("otherpars_TTj", self.config.getVariables(box, "others_TTj"),workspace)

                boxes[box].defineSet("pdf1pars_QCD", self.config.getVariables(box, "pdf1_QCD"),workspace)
                boxes[box].defineSet("pdf2pars_QCD", self.config.getVariables(box, "pdf2_QCD"),workspace)
                boxes[box].defineSet("otherpars_QCD", self.config.getVariables(box, "others_QCD"),workspace)

                ####WHAT IS THIS
                # boxes[box].defineFunctions(self.config.getVariables(box,"functions")) - we don't have any

                # define the fit range

                fit_range = boxes[box].fitregion

                opt = rt.RooLinkedList()
                #opt.Add(rt.RooFit.Range(fit_range))
                opt.Add(rt.RooFit.Range("FULL"))
                opt.Add(rt.RooFit.Extended(True))
                opt.Add(rt.RooFit.Save(True))
                opt.Add(rt.RooFit.Hesse(True))
                opt.Add(rt.RooFit.Minos(False))
                opt.Add(rt.RooFit.PrintLevel(-1))
                opt.Add(rt.RooFit.PrintEvalErrors(10))
                opt.Add(rt.RooFit.NumCPU(RootTools.Utils.determineNumberOfCPUs()))

                # fix sigma
                boxes[box].workspace.var("sigma").setVal(0.)
                boxes[box].workspace.var("sigma").setConstant(True)
                
                fr = boxes[box].getFitPDF(name=boxes[box].fitmodel).fitTo(tot_toy, opt)
                #fr = boxes[box].getFitPDF(name=boxes[box].signalmodel).fitTo(data, opt)
                fr.SetName('independentFRsigbkg')
                fr.Print("v")
                boxes[box].importToWS(fr)
                RootTools.Utils.importToWS(workspace,fr)

                self.store(fr, name = 'independentFRsigbkg', dir=box)
                self.store(fr.correlationHist("correlation_%s_sigbkg" % box), dir=box)
                # make any plots required
                boxes[box].plot(fileName, self,  box, data=tot_toy, fitmodel=boxes[box].fitmodel)#, frName='independentFRsigbkg')
                #boxes[box].plot(fileName, self,  box, data=tot_toy, fitmodel=boxes[box].signalmodel)#, frName='independentFRsigbkg')
                
               
            #skip saving the workspace if the option is set
            if not self.options.nosave_workspace:
                for box in boxes.keys():
                     self.store(workspace,'Box%s_workspace' % box, dir=box)
                     



    def limit_profile(self, inputFiles, massPoint):
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
            btag  =  rootFile.Get('wHisto_btagerr_pe')
            lepSF =  rootFile.Get('wHisto_leperr_pe')
            isr   =  rootFile.Get('wHisto_isrerr_pe')
            jes   =  rootFile.Get('wHisto_JESerr_pe')
            pdf   =  rootFile.Get('wHisto_pdferr_pe')
            
            def renameAndImport(histo):
                #make a memory resident copy
                newHisto = histo.Clone('%s_%s' % (histo.GetName(),box))
                newHisto.SetDirectory(0)
                RootTools.Utils.importToWS(workspace,newHisto)
                return newHisto
            
            wHisto  = renameAndImport(wHisto)
            btag    = renameAndImport(btag)
            lepSF   = renameAndImport(lepSF)
            isr     = renameAndImport(isr)
            jes     = renameAndImport(jes)
            pdf     = renameAndImport(pdf)
            
            #rootFile.Close()

            #set the per box eff value
            workspace.factory('eff_value_%s[%f]' % (box,wHisto.Integral()) )
            print 'eff_value for box %s is %f' % (box,workspace.var('eff_value_%s'%box).getVal())
            
            signal = rt.RooRazor2DSignal('SignalPDF_%s' % box,'Signal PDF for box %s' % box,\
                                         workspace.var('MR'),workspace.var('Rsq'),
                                         workspace,
                                         wHisto.GetName(),jes.GetName(),pdf.GetName(),btag.GetName(),lepSF.GetName(),isr.GetName(),
                                         workspace.var('xJes_prime'),workspace.var('xPdf_prime'),workspace.var('xBtag_prime'),workspace.var('xLepSF_prime'),workspace.var('xISR_prime'))
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
        
        # workspace.extendSet('variables','Boxes')
        
        for box in fileIndex:
            #workspace.extendSet("nuisance", workspace.factory('n2nd_TTj_%s_prime[0,-5.,5.]' % box).GetName())
            #workspace.extendSet("other", workspace.factory('n2nd_TTj_%s_value[1.0]' % box).GetName())
            #if not workspace.var('n2nd_TTj_%s_uncert' % box):
            #    workspace.extendSet("other", workspace.factory('n2nd_TTj_%s_uncert[0.1]' % box).GetName())
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
            #workspace.factory("expr::n2nd_TTj_%s('@0 * pow( (1+@1), @2)', n2nd_TTj_%s_value, n2nd_TTj_%s_uncert, n2nd_TTj_%s_prime)" % (box,box,box,box) )
            #box_primes.append('n2nd_TTj_%s_prime' % box)
            
            #we import this into the workspace, but we rename things so that they don't clash
            var_names = [v.GetName() for v in RootTools.RootIterator.RootIterator(boxes[box].workspace.set('variables'))]
            #var_names.append('n2nd_TTj_%s' % box)
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

            SpBPdfList = rt.RooArgList(signal_pdf_extended)
            if box not in boxes[box].zeros['TTj']:
                SpBPdfList.add(workspace.pdf("ePDF1st_TTj_%s"%box))
                SpBPdfList.add(workspace.pdf("ePDF2nd_TTj_%s"%box))
            if box not in boxes[box].zeros['QCD']:
                SpBPdfList.add(workspace.pdf("ePDF1st_QCD_%s"%box))
                SpBPdfList.add(workspace.pdf("ePDF2nd_QCD_%s"%box))
                
            full_pdf = rt.RooAddPdf('SplusBPDF_%s' % box, 'SplusBPDF_%s' % box, SpBPdfList )
            #full_pdf = rt.RooAddPdf('SplusBPDF_%s' % box, 'SplusBPDF_%s' % box, rt.RooArgList(signal_pdf_extended,background_pdf))
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
        #pData.Print('V')
        RootTools.Utils.importToWS(workspace,pData)
        
        #we now combine the boxes into a RooSimultanious. Only a few of the parameters are shared
        #workspace.Print('V')
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

        #### this is useless now, perhaps we need to have some meaningful number of events to exclude
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
        ####

        while yield_at_xs[-1][0] < eventsToExclude:
            stop_xs += 1e-4
            workspace.var('sigma').setVal(stop_xs)
            signal_yield = 0
            for box in fileIndex:
                signal_yield += workspace.function('S_%s' % box).getVal()
            yield_at_xs.append( (signal_yield, workspace.var('sigma').getVal()) )
        poi_max = yield_at_xs[-1][1]
        workspace.var('sigma').setVal(0.0)

        #poi_max = 0.02
        print 'Estimated POI Max:',poi_max

        #see e.g. http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/SusyAnalysis/RooStatsTemplate/roostats_twobin.C?view=co
        
        #find global maximum with the signal+background model
        #with conditional MLEs for nuisance parameters
        #and save the parameter point snapshot in the Workspace
        #- safer to keep a default name because some RooStats calculators
        #    will anticipate it
        pNll = pSbModel.GetPdf().createNLL(pData)
        pProfile = pNll.createProfile(rt.RooArgSet())
        #pSbModel.Print('V')
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
        #pBModel.Print('V')
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
    
            import string, os
    
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

        massPoint = "CLs_" + self.options.massPoint + ".root"
        cmd = runLimitSettingMacro([workspace_name,workspace.GetName(),pSbModel.GetName(),pBModel.GetName(),pData.GetName(),calculator_type,3,True,15,0.0,poi_max,self.options.toys,massPoint])
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

