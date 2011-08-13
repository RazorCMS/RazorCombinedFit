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
            boxes[box].defineSet("pdf1pars_QCD", self.config.getVariables(box, "pdf1_QCD"))
            boxes[box].defineSet("pdf2pars_QCD", self.config.getVariables(box, "pdf2_QCD"))
            boxes[box].defineSet("otherpars_QCD", self.config.getVariables(box, "others_QCD"))

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
            
    def limit(self, inputFiles, nToys = 5):
        """Set a limit based on the model dependent method"""
        
        lzV = rt.RooRealVar('Lz','Lz',0)
        lzD = rt.RooRealVar('LzData','LzData',0)
                
        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)
        
        if self.options.input is None:
            raise Exception('Limit setting code needs a fit result file as input. None given')
        
        def reset(box, fr):
            for p in RootTools.RootIterator.RootIterator(fr.floatParsInit()):
                box.workspace.var(p.GetName()).setVal(p.getVal())
                box.workspace.var(p.GetName()).setError(p.getError())
        
        def getLz(box, ds, fr, testForQuality = True):
            #L(H0|x)
            reset(box, fr)

            # fix all parameters
            for z in box.zeros:
                if box.name in box.zeros[z]:
                    box.fixPars(z)
                    box.switchOff(z)
                else:
                    box.fixPars(z)
                    box.floatYield(z)

            fr_H0x = box.fitDataSilent(box.getFitPDF(name=box.fitmodel), ds, rt.RooFit.PrintEvalErrors(-1), rt.RooFit.Extended(True))
            #L(H1|x)
            reset(box, fr)
            fr_H1x = box.fitDataSilent(box.getFitPDF(name=box.signalmodel), ds, rt.RooFit.PrintEvalErrors(-1), rt.RooFit.Extended(True))

            LH1x = fr_H1x.minNll()
            LH0x = fr_H0x.minNll()
            Lz = LH0x-LH1x
            if testForQuality and ( (fr_H0x.status() != 0 or fr_H0x.covQual() != 3) or (fr_H1x.status() != 0 or fr_H1x.covQual() != 3) ):
                return None 
            return Lz
        
        def floatPars(b):
            #float some 2nd components            
            for z in boxes[b].zeros:
                if boxes[b].name not in boxes[box].zeros[z]:
                    #float the second component slopes
                    boxes[b].fixParsExact("b2nd_%s" % z, False)
                    boxes[b].fixParsExact("MR02nd_%s" % z, False)
                    boxes[b].fixParsExact("R02nd_%s" % z, False)
                    boxes[b].fixParsExact("f2_%s" % z, False)
                    

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Starting limit setting for box %s' % box
                
            wsName = '%s/Box%s_workspace' % (box,box)
            print "Restoring the workspace from %s" % self.options.input
            boxes[box].restoreWorkspace(self.options.input, wsName)
            # add signal specific parameters 
            boxes[box].defineSet("others_Signal", self.config.getVariables(box, "others_Signal"))
            #add a signal model to the workspace
            signalModel = boxes[box].addSignalModel(fileIndex[box])
            #need to fix all parameters to their restored values
            #boxes[box].fixAllPars()

            print 'Variables for box %s' % box
            boxes[box].workspace.allVars().Print('V')
            print 'Workspace'
            boxes[box].workspace.Print('V')

            fr_central = boxes[box].workspace.obj('independentFR')    
            lzData = getLz(boxes[box],boxes[box].workspace.data('RMRTree'), fr_central, testForQuality=False)
            lzValues = []
            
            values = rt.RooDataSet('Lz_%s' % box, 'Lz_values', rt.RooArgSet(lzV,lzD))
            lzD.setVal(lzData)

            for i in xrange(nToys):
                print 'Setting limit %i experiment' % i

                sig_toy = rt.RooDataSet()
                if self.options.expectedlimit == False:
                    #generate a toy assuming only the signal model (same number of events as background only toy)
                    sig_toy = boxes[box].generateToyFR(boxes[box].signalmodel,fr_central)
                else:
                    #generate a toy assuming only the bkg model (same number of events as background only toy)
                    sig_toy = boxes[box].generateToyFR(boxes[box].fitmodel,fr_central)
                #boxes[box].fixAllPars()
                #floatPars(box)

                Lz = getLz(boxes[box],sig_toy, fr_central)
                if Lz is None:
                    print 'WARNING:: Limit setting fit %i is bad. Skipping...' % i
                    continue
                lzValues.append(Lz)
                lzV.setVal(Lz)
                values.add(rt.RooArgSet(lzV,lzD))
                
                frame_MR_sig = boxes[box].workspace.var('MR').frame()
                sig_toy.plotOn(frame_MR_sig)
                boxes[box].getFitPDF(name=boxes[box].fitmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kBlue))
                boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kGreen))
                boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kRed), rt.RooFit.LineStyle(8), rt.RooFit.Components(signalModel))
                self.store(frame_MR_sig,name='MR_%i_sig'%i, dir=box)
            
            #calculate the area integral of the distribution    
            lzValues.sort()#smallest to largest
            lzValuesSum = sum(map(abs,lzValues))
            
            zMin = min(lzValues)
            zMax = max(lzValues)
            hist_H1 = rt.TH1D('hist_H1','H1',120,zMin,zMax)
            for z in lzValues:
                hist_H1.Fill(z)
            
            lzSum = 0
            lzSig90 = 1e-12+(2*lzData)
            lzSig95 = 1e-12+(2*lzData)
            for lz in lzValues:
                lzSum += abs(lz)
                if lzSum >= 0.1*lzValuesSum:
                    lz90 = lz
                if lzSum >= 0.05*lzValuesSum:
                    lz95 = lz
                    break
                
            reject = (lzData>lzSig90,lzData>lzSig95)
            print 'Result for box %s: lambda_{data}=%f,lambda_{critical}(90,95)=%s, reject(90,95)=%s; ' % (box,lzData,str((lzSig90,lzSig95)),str(reject))

            self.store(hist_H1, dir=box)
            self.store(values, dir=box)


