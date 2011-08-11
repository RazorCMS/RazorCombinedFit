#the code assumes that a file is given in the format
# BOXNAME   n    b    db
# where:
#    BOXNAME is the name of the box
#    n is the number of events observed in the box
#    b is the number of bkg events expected in the box
#    db is the error on the number of events observed in the box
#
# It also assumes a file for the signal point to evaluate, in the format
#     BOXNAME s
# where:
#    BOXNAME is the name of the box
#    s is the number of signal events expected in the box
#
# The full model is built as the product of the Poisson of each box
# and a limit is set 

import ROOT as rt
import sys
import RootTools
#this dependence is needed for the iterator. Can we avoid it (to make the code standalone)

def setWorkspace( boxes, sigYields, xsec, doBayes=rt.kFALSE):
    # find the best boxes
    highLumiBox = []
    highLumi = 1.

    for mybox in boxes:
        # box name (take out the signal-region name)
        boxName = mybox[0].split("_")[0]        
        if mybox[3] > highLumi:
            highLumi = mybox[3]
            highLumiBox = mybox
        continue


    ws = rt.RooWorkspace("razorCombination");
    # we want a limit on the signal strenght
    ws.factory("f[1, 0., 2.]")
    # keeping the xsec constant
    ws.factory("sigma[%f]" %float(xsec))
    # ... including the error on the lumi
    ws.factory("lumi[800, 700, 1000]")
    # ... and on the bkg determination
    # for which we read a 5D PDF to start with

    # list of nuisance and parameters of interest
    ws.defineSet("poi","sigma")
    ws.defineSet("nuis","lumi")
    # define the nuisance parameters for the bkg
    foundHAD = rt.kFALSE
    foundMu  = rt.kFALSE
    foundELE = rt.kFALSE
    foundELE_ELE = rt.kFALSE
    foundELE_MU = rt.kFALSE
    foundMU_MU = rt.kFALSE
    hadSigRegions = ['HAD_hS1', 'HAD_hS2', 'HAD_hS3', 'HAD_hS4', 'HAD_hS5'] 
    muSigRegions = ['MU_hS1', 'MU_hS2', 'MU_hS3', 'MU_hS4', 'MU_hS5'] 
    eleSigRegions = ['ELE_hS1', 'ELE_hS2', 'ELE_hS3', 'ELE_hS4', 'ELE_hS5'] 
    mumuSigRegions = ['MU-MU_hS1', 'MU-MU_hS2', 'MU-MU_hS3', 'MU-MU_hS4', 'MU-MU_hS5'] 
    eleeleSigRegions = ['ELE-ELE_hS1', 'ELE-ELE_hS2', 'ELE-ELE_hS3', 'ELE-ELE_hS4', 'ELE-ELE_hS5'] 
    elemuSigRegions = ['ELE-MU_hS1', 'ELE-MU_hS2', 'ELE-MU_hS3', 'ELE-MU_hS4', 'ELE-MU_hS5'] 
    bkgFiles = []
    for mybox in boxes:
        # HAD
        if mybox[0].split("_")[0] == "HAD" != -1 and foundHAD == rt.kFALSE:
            bkgFiles.append(mybox[2])
            foundHAD = True
            ws.defineSet("hadBkg","")
        for sigRegion in hadSigRegions:
            if mybox[0] == sigRegion:
                ws.factory("b_%s[1, 0, 100]" %mybox[0])
                ws.extendSet("hadBkg","b_%s" %mybox[0])
                ws.extendSet("nuis","b_%s" %mybox[0])
            continue
        # MU
        if mybox[0].split("_")[0] == "MU" != -1 and foundMU == rt.kFALSE:
            bkgFiles.append(mybox[2])
            foundMU = True
            ws.defineSet("muBkg","")
        for sigRegion in muSigRegions:
            if mybox[0] == sigRegion:
                ws.factory("b_%s[1, 0, 100]"%mybox[0])
                ws.extendSet("muBkg","b_%s" %mybox[0])
                ws.extendSet("nuis","b_%s" %mybox[0])
            continue
        # ELE
        if mybox[0].split("_")[0] == "ELE" != -1 and foundELE == rt.kFALSE:
            bkgFiles.append(mybox[2])
            foundELE = True
            ws.defineSet("eleBkg","")
        for sigRegion in eleSigRegions:
            if mybox[0] == sigRegion:
                ws.factory("b_%s[1, 0, 100]" %mybox[0])
                ws.extendSet("eleBkg","b_%s" %mybox[0])
                ws.extendSet("nuis","b_%s" %mybox[0])
            continue
        # MUMU
        if mybox[0].split("_")[0] == "MUMU" != -1 and foundMU_MU == rt.kFALSE:
            bkgFiles.append(mybox[2])
            foundMU_MU = True
            ws.defineSet("mumuBkg","")
        for sigRegion in mumuSigRegions:
            if mybox[0] == sigRegion:
                ws.factory("b_%s[1, 0, 100]" %mybox[0])
                ws.extendSet("mumuBkg","b_%s" %mybox[0])
                ws.extendSet("nuis","b_%s" %mybox[0])
            continue
        # ELEELE
        if mybox[0].split("_")[0] == "ELEELE" != -1 and foundELE_ELE == rt.kFALSE:
            bkgFiles.append(mybox[2])
            foundELE_ELE = True
            ws.defineSet("eleeleBkg","")
        for sigRegion in eleeleSigRegions:
            if mybox[0] == sigRegion:
                ws.factory("b_%s[1, 0, 100]" %mybox[0])
                ws.extendSet("eleeleBkg","b_%s" %mybox[0])
                ws.extendSet("nuis","b_%s" %mybox[0])
            continue
        # ELEMU
        if mybox[0].split("_")[0] == "ELEMU" != -1 and foundELE_ELE == rt.kFALSE:
            bkgFiles.append(mybox[2])
            foundELE_MU = True
            ws.defineSet("elemuBkg","")
        for sigRegion in elemuSigRegions:
            if mybox[0] == sigRegion:
                ws.factory("b_%s[1, 0, 100]" %mybox[0])
                ws.extendSet("elemuBkg","b_%s" %mybox[0])
                ws.extendSet("nuis","b_%s" %mybox[0])
            continue
        continue

    # build the string that will define the model in the workspace
    # at the end, pass it to the workspace factory
    myModelString = "PROD::model("
    # build the N-dim BKG PDF for each box as a RooHistPDF
    if foundHAD == True:
        # get the dataset with the expected bkg from toys
        for fileName in bkgFiles:
            if fileName.find("bkg_HAD.root") != -1: 
                myFile = rt.TFile.Open(fileName)
                hadBkgPdf = myFile.Get("HADBkgPdf")
                # import to ws
                getattr(ws, 'import')(hadBkgPdf)
                # add it to the model
                myModelString = myModelString + "hadBkgPdf,"
    if foundMU == True:
        # get the dataset with the expected bkg from toys
        for fileName in bkgFiles:
            if fileName.find("bkg_MU.root") != -1: 
                myFile = rt.TFile.Open(fileName)
                data = myFile.Get("BKG")
                muHistDataset = rt.RooDataHist("muBkgData", "muBkgData", ws.set("muBkg"), data) 
                # turn it into a hist PDF of the bkgs yields
                muBkgPdf = rt.RooHistPdf("muBkgPdf", "muBkgPdf", ws.set("muBkg"), muHistDataset)
                # import to ws
                getattr(ws, 'import')(muBkgPdf)
                # add it to the model
                myModelString = myModelString + "muBkgPdf,"
    if foundELE == True:
        # get the dataset with the expected bkg from toys
        for fileName in bkgFiles:
            if fileName.find("bkg_ELE.root") != -1:
                myFile = rt.TFile.Open(fileName)
                data = myFile.Get("BKG")
                eleHistDataset = rt.RooDataHist("eleBkgData", "eleBkgData", ws.set("eleBkg"), data)
                # turn it into a hist PDF of the bkgs yields
                eleBkgPdf = rt.RooHistPdf("eleBkgPdf", "eleBkgPdf", ws.set("eleBkg"), eleHistDataset)
                # import to ws
                getattr(ws, 'import')(eleBkgPdf)
                # add it to the model
                myModelString = myModelString + "eleBkgPdf,"
    if foundMU_MU == True:
        # get the dataset with the expected bkg from toys
        for fileName in bkgFiles:
            if fileName.find("bkg_MUMU.root") != -1:
                myFile = rt.TFile.Open(fileName)
                data = myFile.Get("BKG")
                mumuHistDataset = rt.RooDataHist("mumuBkgData", "mumuBkgData", ws.set("mumuBkg"), data)
                # turn it into a hist PDF of the bkgs yields
                mumuBkgPdf = rt.RooHistPdf("mumuBkgPdf", "mumuBkgPdf", ws.set("mumuBkg"), mumuHistDataset)
                # import to ws
                getattr(ws, 'import')(mumuBkgPdf)
                # add it to the model
                myModelString = myModelString + "mumuBkgPdf,"
    if foundELE_MU == True:
        # get the dataset with the expected bkg from toys
        for fileName in bkgFiles:
            if fileName.find("bkg_ELEMU.root") != -1:
                myFile = rt.TFile.Open(fileName)
                data = myFile.Get("BKG")
                elemuHistDataset = rt.RooDataHist("elemuBkgData", "elemuBkgData", ws.set("elemuBkg"), data)
                # turn it into a hist PDF of the bkgs yields
                elemuBkgPdf = rt.RooHistPdf("elemuBkgPdf", "elemuBkgPdf", ws.set("elemuBkg"), elemuHistDataset)
                # import to ws
                getattr(ws, 'import')(elemuBkgPdf)
                # add it to the model
                myModelString = myModelString + "elemuBkgPdf,"
    if foundELE_ELE == True:
        # get the dataset with the expected bkg from toys
        for fileName in bkgFiles:
            if fileName.find("bkg_ELEELE.root") != -1:
                myFile = rt.TFile.Open(fileName)
                data = myFile.Get("BKG")
                eleeleHistDataset = rt.RooDataHist("eleeleBkgData", "eleeleBkgData", ws.set("eleeleBkg"), data)
                # turn it into a hist PDF of the bkgs yields
                eleeleBkgPdf = rt.RooHistPdf("eleeleBkgPdf", "eleeleBkgPdf", ws.set("eleeleBkg"), eleeleHistDataset)
                # import to ws
                getattr(ws, 'import')(eleeleBkgPdf)
                # add it to the model
                myModelString = myModelString + "eleeleBkgPdf,"

    # for each box, add to the workspace a Poisson function
    # P(n |s+b)
    obs = ""
    for box in boxes:
        # box name (take out the signal-region name)
        boxName = box[0].split("_")[0]
        # add the yield to the list of observables
        ws.factory("n_%s[%i]" %(box[0], box[1]))
        obs = obs+"n_%s," %box[0]
        # compute the signal as eps*L*sigma, taking eps from the signal file
        s = 0;
        for sigYield in sigYields:
            if sigYield[0] == box[0]: s = sigYield[1]
        # lumi_box = lumi for the highest-stat box. lumi_box = lumi * <lumi_box>/<lumi_highest> for the others
        ws.factory("expr::s_%s('@0*@1*@2*@3*%f', sigma, lumi, e_%s[%f],f)" %( box[0], box[3]/highLumiBox[3], box[0], s))
        # define s+b expression
        ws.factory("sum::splusb_%s(s_%s,b_%s)"  %( box[0], box[0], box[0]))
        # build the Poisson PDF
        ws.factory("Poisson::P_%s(n_%s, splusb_%s)" %(box[0], box[0], box[0]))
        # attach the PDF to the total likelihood, written as Prod_i(Poisson_i)
        myModelString = myModelString+("P_%s," %box[0])
        continue

    # log-normal (PRIORS!!!!!!) for systematics
    ws.factory("Lognormal::l_lumi(lumi,nom_lumi[%f],sum::kappa_lumi(1,d_lumi[0.045]))" %highLumiBox[3])
    #ws.factory("Lognormal::l_eff_a(eff_a,nom_eff_a[0.20,0,1],sum::kappa_eff_a(1,d_eff_a[0.05]))");
    #ws.factory("Lognormal::l_eff_b(eff_b,nom_eff_b[0.05,0,1],sum::kappa_eff_b(1,d_eff_b[0.05]))");

    # observables
    ws.defineSet("obs",obs[:-1])
    # global observables
    ws.defineSet("globalObs","nom_lumi,d_lumi")
    for bestb in bestBox:
        if len(bestb[1]) > 0:
            ws.set("globalObs").add(ws.var("nom_b%s" %bestb[0]))
            ws.set("globalObs").add(ws.var("d_b%s" %bestb[0]))

    # store in a string the list of bkg pdfs
    priorBkg = ""
    if foundHAD == True: priorBkg = priorBkg+"hadBkgPdf,"
    if foundMU == True: priorBkg = priorBkg+"muBkgPdf,"
    if foundELE == True: priorBkg = priorBkg+"eleBkgPdf,"
    if foundMU_MU == True: priorBkg = priorBkg+"mumuBkgPdf,"
    if foundELE_MU == True: priorBkg = priorBkg+"elemuBkgPdf,"
    if foundELE_ELE == True: priorBkg = priorBkg+"eleeleBkgPdf,"

            
    # the priors: use the log-normal for the lumi and b parameters
    if doBayes == rt.kTRUE:
        ws.factory("Uniform::prior_poi({f})")
        priorALL = "PROD::prior(prior_poi,l_lumi,%s)" % priorBkg[:-1]
    else:               
        # put the sys pdfs in the likelihood
        # waiting for someone to explain me why this is a prior-less approach... 
        myModelString = myModelString+"l_lumi,%s" %priorBkg[:-1]

    # add the total model to the ws
    myModelString = myModelString[:-1]+(")")
    ws.factory(myModelString)
    # generate the "dataset" with observables
    pData = rt.RooDataSet("data","",ws.set("obs"))
    pData.add(ws.set("obs"))
    # import the dataset top the ws
    getattr(ws, 'import')(pData)     
    # set everything to constant
    ws.var("d_lumi").setConstant(rt.kTRUE)
    ws.var("nom_lumi").setConstant(rt.kTRUE)
    ws.var("sigma").setConstant(rt.kTRUE)
    for box in boxes:
        ws.var("e_%s" % box[0]).setConstant(rt.kTRUE)
        ws.var("n_%s" % box[0]).setConstant(rt.kTRUE)
    # float the nuisance parameters and the poi
    ws.var("lumi").setConstant(rt.kFALSE)
    ws.var("f").setConstant(rt.kFALSE)
    for box in boxes:
        ws.var("b%s" %box[0]).setConstant(rt.kFALSE)
    # print the workspace
    ws.Print()
    return ws

def calcLimit(ws, doBayes=rt.kFALSE):
    
    # signal+background model
    pSbModel = rt.RooStats.ModelConfig("SbModel")
    pSbModel.SetWorkspace(ws)
    pSbModel.SetPdf(ws.pdf("model"))
    if doBayes==rt.kTRUE: pSbModel.SetPriorPdf(ws.pdf("prior"))
    pSbModel.SetParametersOfInterest(ws.set("poi"))
    pSbModel.SetNuisanceParameters(ws.set("nuis"))
    pSbModel.SetObservables(ws.set("obs"))
    pSbModel.SetGlobalObservables(ws.set("globalObs"))
    #getattr(ws, 'import')(pSbModel)

    # background-only model
    # use the same PDF as s+b, with xsec=0
    # POI value under the background hypothesis
    poiValueForBModel = 0.0;
    pBModel = rt.RooStats.ModelConfig(pSbModel)
    pBModel.SetName("BModel")
    pBModel.SetWorkspace(ws)
    #getattr(ws, 'import')(pBModel)
    
    # compute CLs
    # find global maximum with the signal+background model
    # with conditional MLEs for nuisance parameters
    # and save the parameter point snapshot in the Workspace
    #  - safer to keep a default name because some RooStats calculators
    #    will anticipate it
    pNll = pSbModel.GetPdf().createNLL(ws.data("data"))
    pProfile = pNll.createProfile(rt.RooArgSet());
    # this will do fit and set POI and nuisance parameters to fitted values
    #pProfile.getVal()
    #pPoiAndNuisance = rt.RooArgSet()
    #if pSbModel.GetNuisanceParameters(): pPoiAndNuisance.add(pSbModel.GetNuisanceParameters())
    #pPoiAndNuisance.add(pSbModel.GetParametersOfInterest())
    #print "\nWill save these parameter points that correspond to the fit to data"
    #pPoiAndNuisance.Print("v");
    #pSbModel.SetSnapshot(pPoiAndNuisance)
    del pProfile
    del pNll
    #del pPoiAndNuisance

    # Find a parameter point for generating pseudo-data
    # with the background-only data.
    # Save the parameter point snapshot in the Workspace
    pNll = pBModel.GetPdf().createNLL(ws.data("data"))
    poi = ws.set("poi")
    pProfile = pNll.createProfile(poi)
    poi.first().setVal(poiValueForBModel)
    # this will do fit and set nuisance parameters to profiled values
    #pProfile.getVal() 
    #pPoiAndNuisance = rt.RooArgSet()
    #if pBModel.GetNuisanceParameters(): pPoiAndNuisance.add(pBModel.GetNuisanceParameters())
    #pPoiAndNuisance.add(pBModel.GetParametersOfInterest())
    #print "\nShould use these parameter points to generate pseudo data for bkg only"
    #pPoiAndNuisance.Print("v")
    #pBModel.SetSnapshot(pPoiAndNuisance)
    del pProfile
    del pNll
    #del pPoiAndNuisance

    # AND NOW WHAT???

    #bayesian LIMIT calculator
    #/////////////////////////////////////////////
    #// create and use the MCMCCalculator
    #// to find and plot the 95% credible interval
    #// on the parameter of interest as specified
    #// in the model config
    limit = 1000.
    if doBayes == rt.kTRUE:
        mcmc = rt.RooStats.MCMCCalculator(ws.data("data"),pSbModel)
        # 95% interval
        mcmc.SetConfidenceLevel(0.95) 
        # Metropolis-Hastings algorithm iterations
        mcmc.SetNumIters(1000000)         
        # first N steps to be ignored as burn-in
        mcmc.SetNumBurnInSteps(5)       
        
        # default is the shortest interval.  here use central for central interval
        mcmc.SetLeftSideTailFraction(0.5) 
        interval = mcmc.GetInterval()
        
        # print out the iterval on the first Parameter of Interest
        print "0.95 Credibility Interval on s = [%f, %f]" % (interval.LowerLimit( ws.var("sigma") ), interval.UpperLimit(ws.var("sigma")))
        limit = interval.UpperLimit(ws.var("sigma"))
        del interval

    # PL 
    else: 
        plc = rt.RooStats.ProfileLikelihoodCalculator(ws.data("data"), pSbModel)
        plc.SetConfidenceLevel(0.95)
        plInt = plc.GetInterval()
        ##### get ugly print out of the way. Fix.
        msglevel = rt.RooMsgService.instance().globalKillBelow()
        rt.RooMsgService.instance().setGlobalKillBelow(rt.RooFit.FATAL)
        plInt.LowerLimit(ws.var("sigma") ) 
        rt.RooMsgService.instance().setGlobalKillBelow(msglevel)

        print "Profile Likelihood interval on s = [%f, %f]" % (plInt.LowerLimit( ws.var("sigma") ), plInt.UpperLimit(ws.var("sigma")))
        limit = plInt.UpperLimit(ws.var("sigma"))
        del plInt
        del plc

    # cleanup and return
    del ws    
    return limit 


if __name__ == '__main__':
    boxes = []
    sigYields = []

    # read the bkg file 
    fileBKG = open(sys.argv[1])
    for line in fileBKG:
        entries = line.split(" ")
        mybox = [entries[0], int(entries[1]), entries[2], float(entries[3])]
        boxes.append(mybox)
        continue

    # read the sig file 
    fileSIG = open(sys.argv[2])
    xsec = 0
    for line in fileSIG:
        entries = line.split(" ")
        mysigYield = [entries[0], float(entries[1])]
        xsec = entries[2]
        sigYields.append(mysigYield)
        continue

    #plInt = calcLimit(setWorkspace(boxes, sigYields, xsec, rt.kTRUE), rt.kTRUE)
    plInt = calcLimit(setWorkspace(boxes, sigYields, xsec))
