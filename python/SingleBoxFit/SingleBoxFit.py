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

        for box in boxes:
            
            if self.options.input is not None:
                wsName = '%s/Box%s_workspace' % (box,box)
                print "Restoring the workspace from %s" % self.options.input
                boxes[box].restoreWorkspace(self.options.input, wsName)
            
            pdf = boxes[box].getFitPDF(name=boxes[box].fitmodel,graphViz=None)
            vars = boxes[box].workspace.set('variables')
            
            #use an MCStudy to store everything
            study = boxes[box].getMCStudy()
            #get the data yield without cuts
            data_yield = boxes[box].workspace.data('RMRTree').numEntries()
            
            pre_ = rt.RooRealVar('predicted','predicted',-1)
            obs_ = rt.RooRealVar('observed','observed',-1)
            qual_ = rt.RooRealVar('quality','quality',-1)
            status_ = rt.RooRealVar('status','status',-1)
            args = rt.RooArgSet(pre_,obs_,qual_,status_)
            yields = rt.RooDataSet('Yields','Yields',args)
            
            for i in xrange(nToys):
                gdata = pdf.generate(vars,rt.RooRandom.randomGenerator().Poisson(data_yield))
                gdata_cut = gdata.reduce(boxes[box].cut)
                
                #data_write = 'toydata_%s_%i.txt' % (box,i)
                #gdata.write(data_write)
                
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
            
        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box, dir=box)

        
    
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
                fr = boxes[box].fit(fileName,boxes[box].cut, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True), rt.RooFit.Range("B1,B2,B3"))
                #fr = boxes[box].fit(fileName,boxes[box].cut, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
                self.store(fr, dir=box)
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
            multi.combine(boxes, fileIndex)
            if self.options.model_independent_limit:
                multi.predictBackground(boxes.keys(), multi.workspace.obj('simultaniousFR'), fileIndex)
            self.workspace = multi.workspace

        if self.options.model_independent_limit:
            for box, fileName in fileIndex.iteritems():
                boxes[box].predictBackground(boxes[box].workspace.obj('independentFR'), fileName)
        
        for box in boxes.keys():
            self.store(boxes[box].workspace,'Box%s_workspace' % box, dir=box)
            
    def limit(self, inputFiles, nToys = 10):
        """Set a limit based on the model dependent method"""
                
        fileIndex = self.indexInputFiles(inputFiles)
        boxes = self.getboxes(fileIndex)
        
        if self.options.input is None:
            raise Exception('Limit setting code needs a fit result file as input. None given')
        
        def getLz(box, ds):
            #L(H0|x)
            fr_H0x = box.fitDataSilent(box.getFitPDF(name=box.fitmodel), ds, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
            #L(H1|x)
            fr_H1x = box.fitDataSilent(box.getFitPDF(name=box.signalmodel), ds, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))

            LH1x = fr_H1x.minNll()
            LH0x = fr_H0x.minNll()
            Lz = LH0x-LH1x
            return Lz

        #start by setting all box configs the same
        for box, fileName in fileIndex.iteritems():
            print 'Starting limit setting for box %s' % box
                
            wsName = '%s/Box%s_workspace' % (box,box)
            print "Restoring the workspace from %s" % self.options.input
            boxes[box].restoreWorkspace(self.options.input, wsName)
            # add signal specific parameters 
            boxes[box].defineSet("pdf1pars_QCD", self.config.getVariables(box, "others_Signal"))
            #add a signal model to the workspace
            signalModel = boxes[box].addSignalModel(fileIndex[box])
            #need to fix all parameters to their restored values
            boxes[box].fixAllPars()

            print 'Variables for box %s' % box
            boxes[box].workspace.allVars().Print('V')
            print 'Workspace'
            boxes[box].workspace.Print('V')
            
            hist_H0 = rt.TH1D('hist_H0','H0',120,-11,11)
            hist_H1 = rt.TH1D('hist_H1','H1',120,-11,11)
            
            lzData = getLz(boxes[box],boxes[box].workspace.data('RMRTree'))
            lzValues = []
            
            for i in xrange(nToys):
                print 'Setting limit %i experiment' % i
#                #generate a toy assuming only the background model
#                bg_toy = boxes[box].generateToy(boxes[box].fitmodel)
#                #L(H0|H0)
#                fr_H0H0 = boxes[box].fitDataSilent(boxes[box].getFitPDF(name=boxes[box].fitmodel), bg_toy, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
#                #L(H1|H0)
#                fr_H1H0 = boxes[box].fitDataSilent(boxes[box].getFitPDF(name=boxes[box].signalmodel), bg_toy, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
#             
#                LH1H0 = fr_H1H0.minNll()
#                LH0H0 = fr_H0H0.minNll()
#                LzH0 = LH0H0/LH1H0
#                print 'LzH0',LzH0
#                hist_H0.Fill(LzH0)
#                
#                frame_MR_bg = boxes[box].workspace.var('MR').frame()
#                bg_toy.plotOn(frame_MR_bg)
#                boxes[box].getFitPDF(name=boxes[box].fitmodel).plotOn(frame_MR_bg, rt.RooFit.LineColor(rt.kBlue))
#                boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_bg, rt.RooFit.LineColor(rt.kGreen))
#                boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_bg, rt.RooFit.LineColor(rt.kGreen), rt.RooFit.LineStyle(8), rt.RooFit.Components(signalModel))
#                self.store(frame_MR_bg,name='MR_%i_bg'%i, dir=box)
#
#                #delete the background toy data as its taking up memory for no reason
#                entries = bg_toy.numEntries()
#                del bg_toy
             
                #generate a toy assuming only the signal model (same number of events as background only toy)
                sig_toy = boxes[box].generateToy(boxes[box].signalmodel)
                Lz = getLz(boxes[box],sig_toy)
                lzValues.append(Lz)
                
#                #L(H0|H1)
#                fr_H0H1 = boxes[box].fitDataSilent(boxes[box].getFitPDF(name=boxes[box].fitmodel), sig_toy, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
#                #L(H1|H1)
#                fr_H1H1 = boxes[box].fitDataSilent(boxes[box].getFitPDF(name=boxes[box].signalmodel), sig_toy, rt.RooFit.PrintEvalErrors(-1),rt.RooFit.Extended(True))
#                
                frame_MR_sig = boxes[box].workspace.var('MR').frame()
                sig_toy.plotOn(frame_MR_sig)
                boxes[box].getFitPDF(name=boxes[box].fitmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kBlue))
                boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kGreen))
                boxes[box].getFitPDF(name=boxes[box].signalmodel).plotOn(frame_MR_sig, rt.RooFit.LineColor(rt.kGreen), rt.RooFit.LineStyle(8), rt.RooFit.Components(signalModel))
                self.store(frame_MR_sig,name='MR_%i_sig'%i, dir=box)
#
#                LH1H1 = fr_H1H1.minNll()
#                LH0H1 = fr_H0H1.minNll()
#                LzH1 = LH0H1-LH1H1
#                print 'LzH1',LzH1
                hist_H1.Fill(Lz)
            
            #calculate the area integral of the distribution    
            lzValues.sort()#smallest to largest
            lzValuesSum = sum(map(abs,lzValues))
            
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
            print 'Result: lambda_{data}=%f,lambda_{critical}(90,95)=%s, reject(90,95)=%s; ' % (lzData,str((lzSig90,lzSig95)),str(reject))

            self.store(hist_H0, dir=box)
            self.store(hist_H1, dir=box)


