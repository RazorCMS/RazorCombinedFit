import ROOT as rt
import RazorCombinedFit
from RazorCombinedFit.Framework import Analysis
import RootTools

class SingleBoxAnalysis(Analysis.Analysis):
    
    def __init__(self, outputFile, config):
        super(SingleBoxAnalysis,self).__init__('SingleBoxFit',outputFile, config)
    
    def merge(self, workspace, box):
        """Import the contents of a box workspace into the master workspace while enforcing some name-spaceing"""
        for o in RootTools.RootIterator.RootIterator(workspace.componentIterator()):
            if hasattr(o,'Class') and o.Class().InheritsFrom('RooRealVar'):
                continue
            self.importToWS(o, rt.RooFit.RenameAllNodes(box),rt.RooFit.RenameAllVariables(box)) 

    def getboxes(self, fileIndex):
        """Refactor out the common box def for fitting and simple toys"""
        
        import RazorBox
        boxes = {}

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Configuring box %s' % box
            boxes[box] = RazorBox.RazorBox(box, self.config.getVariables(box, "variables"))
            self.config.getVariablesRange(box,"variables" ,boxes[box].workspace)
            # Wln
            boxes[box].defineSet("pdf1pars_Wln", self.config.getVariables(box, "pdf1_Wln"))
            boxes[box].defineSet("pdf2pars_Wln", self.config.getVariables(box, "pdf2_Wln"))
            boxes[box].defineSet("otherpars_Wln", self.config.getVariables(box, "others_Wln"))
            # Zll
            boxes[box].defineSet("pdf1pars_Zll", self.config.getVariables(box, "pdf1_Zll"))
            boxes[box].defineSet("pdf2pars_Zll", self.config.getVariables(box, "pdf2_Zll"))
            boxes[box].defineSet("otherpars_Zll", self.config.getVariables(box, "others_Zll"))
            # Znn
            boxes[box].defineSet("pdf1pars_Znn", self.config.getVariables(box, "pdf1_Znn"))
            boxes[box].defineSet("pdf2pars_Znn", self.config.getVariables(box, "pdf2_Znn"))
            boxes[box].defineSet("otherpars_Znn", self.config.getVariables(box, "others_Znn"))
            # TTj
            boxes[box].defineSet("pdf1pars_TTj", self.config.getVariables(box, "pdf1_TTj"))
            boxes[box].defineSet("pdf2pars_TTj", self.config.getVariables(box, "pdf2_TTj"))
            boxes[box].defineSet("otherpars_TTj", self.config.getVariables(box, "others_TTj"))
            # QCD
            #boxes[box].defineSet("pdf1pars_QCD", self.config.getVariables(box, "pdf1_QCD"))
            #boxes[box].defineSet("pdf2pars_QCD", self.config.getVariables(box, "pdf2_QCD"))
            #boxes[box].defineSet("otherpars_QCD", self.config.getVariables(box, "others_QCD"))

            if not self.options.limit: boxes[box].addDataSet(fileName)
            boxes[box].define(fileName)

        return boxes
            
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
                    boxes[box].writeBackgroundDataToys(f, data_yield, box, nToys)
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
                fr = boxes[box].fit(fileName,boxes[box].cut, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True), rt.RooFit.Range("fR1,fR2,fR3,fR4"))
                #fr = boxes[box].fit(fileName,boxes[box].cut, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
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
        
        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box, dir=box)
            
    def limit(self, inputFiles, nToys):
        """Set a limit based on the model dependent method"""
        
        lzV = rt.RooRealVar('Lz','Lz',0)
        lzD = rt.RooRealVar('LzData','LzData',0)
                
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
            H0xNLL = box.getFitPDF(name=box.fitmodel).createNLL(ds)
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

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Starting limit setting for box %s' % box
                
            wsName = '%s/Box%s_workspace' % (box,box)
            print "Restoring the workspace from %s" % self.options.input
            boxes[box].restoreWorkspace(self.options.input, wsName)
            # add signal specific parameters 
            #boxes[box].defineSet("others_Signal", self.config.getVariables(box, "others_Signal"))
            #add a signal model to the workspace
            signalModel = boxes[box].addSignalModel(fileIndex[box])
            #need to fix all parameters to their restored values
            #boxes[box].fixAllPars()

            print 'Variables for box %s' % box
            boxes[box].workspace.allVars().Print('V')
            print 'Workspace'
            boxes[box].workspace.Print('V')

            fr_central = boxes[box].workspace.obj('independentFR')    
            
            vars = boxes[box].workspace.set('variables')
            data = boxes[box].workspace.data('RMRTree')
            print "get Lz for data"
            lzData,LH0DataH0,LH1Data = getLz(boxes[box],boxes[box].workspace.data('RMRTree'), fr_central, testForQuality=False)
            lzValues = []
            LH1xValues = []
            LH0xValues = []
            
            values = rt.RooDataSet('Lz_%s' % box, 'Lz_values', rt.RooArgSet(lzV,lzD))
            lzD.setVal(lzData)

            myTree = rt.TTree("myTree", "myTree")
    
            # THIS IS CRAZY !!!!
            rt.gROOT.ProcessLine(
                "struct MyStruct{\
                Double_t var1;\
                Double_t var2;\
                Double_t var3;\
                };")
            from ROOT import MyStruct

            s = MyStruct()
            myTree.Branch("Lz", rt.AddressOf(s,'var1'),'var1/D')
            myTree.Branch("LH0x", rt.AddressOf(s,'var2'),'var2/D')
            myTree.Branch("LH1x", rt.AddressOf(s,'var3'),'var3/D')
           
            print "calculate number of bkg events to generate"
            bkgGenNum = boxes[box].getFitPDF(name=boxes[box].fitmodel,graphViz=None).expectedEvents(vars) 
            #bkgGenNum = boxes[box].workspace.function("Ntot_TTj").getVal()+boxes[box].workspace.function("Ntot_Wln").getVal()+boxes[box].workspace.function("Ntot_Zll").getVal()+boxes[box].workspace.function("Ntot_Znn").getVal()

            for i in xrange(nToys):
                print 'Setting limit %i experiment' % i

                tot_toy = rt.RooDataSet()
                if self.options.expectedlimit == False:
                    #generate a toy assuming signal + bkg model (same number of events as background only toy)             
                    print "generate a toy assuming signal + bkg model"              
                    #sigData = RootTools.getDataSet(fileIndex[box],'RMRHistTree')
                    sigData = RootTools.getDataSet(fileIndex[box],'RMRHistTree_%i'%i)
                    sigGenPdf = rt.RooHistPdf('%sPdf_%i' % ('Signal',i),'%sPdf_%i' % ('Signal',i),vars,sigData)
                    #get nominal number of entries, including 17% SIGNAL NORMALIZATION SYSTEMATIC                
                    print "calculate number of sig events to generate"
                    sigGenNum = boxes[box].workspace.var('Lumi').getVal()*sigData.sum(False)/1000
                    print "sigGenNum =  %f" % sigGenNum
                    print "bkgGenNum = %f" % bkgGenNum
                    print "numEntriesData = %i" % data.numEntries()
                    PSigGenNum = rt.RooRandom.randomGenerator().Poisson(sigGenNum)
                    sig_toy = sigGenPdf.generate(vars,PSigGenNum)
                    bkg_toy = boxes[box].generateToyFRWithYield(boxes[box].fitmodel,fr_central,bkgGenNum)
                    print "sig_toy.numEntries() = %f" %sig_toy.numEntries()
                    print "bkg_toy.numEntries() = %f" %bkg_toy.numEntries()

                    #sum the toys
                    tot_toy = bkg_toy.Clone()
                    tot_toy.append(sig_toy)
                    tot_toy.SetName("sigbkg")
                    #sigData.Delete()
                    #sigGenPdf.Delete()
                    #sig_toy.Delete()
                    #bkg_toy.Delete()
                    del sigData
                    del sigGenPdf
                    del sig_toy
                    del bkg_toy
                else:                    
                    #generate a toy assuming only the bkg model (same number of events as background only toy)
                    print "generate a toy assuming bkg model"
                    tot_toy = boxes[box].generateToyFRWithYield(boxes[box].fitmodel,fr_central,bkgGenNum)
                    tot_toy.SetName("bkg")

                print "%s entries = %i" %(tot_toy.GetName(),tot_toy.numEntries())
                print "get Lz for toys"
                Lz, LH0x,LH1x = getLz(boxes[box],tot_toy, fr_central)
                if Lz is None:
                    print 'WARNING:: Limit setting fit %i is bad. Skipping...' % i
                    continue
                lzValues.append(Lz)
                LH0xValues.append(LH0x)
                LH1xValues.append(LH1x)
                lzV.setVal(Lz)
                values.add(rt.RooArgSet(lzV,lzD))
                s.var1 = Lz
                s.var2 = LH0x
                s.var3 = LH1x
                myTree.Fill()
                ### plotting:
                #frame_MR_sig = boxes[box].workspace.var('MR').frame()
                #sig_toy.plotOn(frame_MR_sig)
                #boxes[box].getFitPDF(name=boxes[box].fitmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kBlue))
                #boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kGreen))
                #boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Components(signalModel))
                #self.store(frame_MR_sig,name='MR_%i_sig'%i, dir=box)
            
            #calculate the area integral of the distribution    
            lzValues.sort()#smallest to largest
            #lzValuesSum = sum(map(abs,lzValues))
            
            zMin = min(lzValues)
            zMax = max(lzValues)
            hist_H1 = rt.TH1D('hist_H1','H1',120,zMin,zMax)
            for z in lzValues:
                hist_H1.Fill(z)
            
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

            self.store(hist_H1, dir=box)
            self.store(values, dir=box)
            self.store(myTree, dir=box)


