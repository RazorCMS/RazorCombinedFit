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

if __name__ == '__main__':

    ws = rt.RooWorkspace("razorCombination");

    boxes = []
    sigYields = []

    # read the bkg file 
    fileBKG = open(sys.argv[1])
    bestBox = []
    bestError = 1000000.
    highLumiBox = []
    highLumi = 1.
    for line in fileBKG:
        entries = line.split(" ")
        mybox = [entries[0], int(entries[1]), float(entries[2]), float(entries[3]), float(entries[4])]
        boxes.append(mybox)
        if mybox[3]/mybox[2] < bestError:
            bestError = mybox[3]/mybox[2]
            bestBox = mybox
        if mybox[4] > highLumi:
            highLumi = mybox[4]
            highLumiBox = mybox
        continue

    # read the sig file 
    fileSIG = open(sys.argv[2])
    for line in fileSIG:
        entries = line.split(" ")
        mysigYield = [entries[0], float(entries[1])]
        sigYields.append(mysigYield)
        continue

    # we want a limit on the total xsection
    ws.factory("sigma[0., 0., 100]")
    # ... including the error on the lumi
    ws.factory("lumi[1000, 700, 1300]")
    # ... and on the bkg determination
    # IMPORTANT: ALL THE BKG ERRORS ARE CORRELATED so we have JUST ONE NUISANCE PARAMETER b
    ws.factory("b[1, 0, 10]")

    # for each box, add to the workspace a Poisson function
    # P(n |s+b)
    myModelString = "PROD::model("
    obs = rt.RooArgSet("obs")
    for box in boxes:
        # add the yield to the list of observables
        ws.factory("n_%s[%i]" %(box[0], box[1]))
        obs.add(ws.var("n_%s" %box[0]))
        # compute the signal as eps*L*sigma, taking eps from the signal file
        s = 0;
        for sigYield in sigYields:
            if sigYield[0] == box[0]: s = sigYield[1]
        # lumi_box = lumi for the highest-stat box. lumi_box = lumi * <lumi_box>/<lumi_highest> for the others
        ws.factory("expr::s_%s(@0*@1*@2*%f/%f, sigma, lumi, e_%s[%f])" %( box[0], box[4], highLumiBox[4], box[0], s))
        # b_box = b for the best box. b_box = b * <b_box>/<b_best> for the others
        ws.factory("expr::b_%s(%f/%f*@0, b)" %( box[0], box[3], bestBox[3]))
        # define s+b expression
        ws.factory("sum::splusb_%s(s_%s,b_%s)"  %( box[0], box[0], box[0]))
        # build the Poisson PDF
        ws.factory("Poisson::P_%s(n_%s, splusb_%s)" %(box[0], box[0], box[0]))
        # attach the PDF to the total likelihood, written as Prod_i(Poisson_i)
        myModelString = myModelString+("P_%s," %box[0])
        continue

    # import the list of counting observables n
    getattr(ws, 'import')(obs)

    # log-normal for systematics
    ws.factory("Lognormal::l_lumi(lumi,nom_lumi[%f],sum::kappa_lumi(1,d_lumi[0.06]))" %highLumiBox[4])
    ws.factory("Lognormal::l_b(b,nom_b[%f],sum::kappa_b(1,d_b[%f]))" %(bestBox[2], bestBox[3]));
    #ws.factory("Lognormal::l_eff_a(eff_a,nom_eff_a[0.20,0,1],sum::kappa_eff_a(1,d_eff_a[0.05]))");
    #ws.factory("Lognormal::l_eff_b(eff_b,nom_eff_b[0.05,0,1],sum::kappa_eff_b(1,d_eff_b[0.05]))");

    # add the systematics as a pdfs to the full model
    # multiplying the likelihood by each log-normal function
    # to me this is a Prior... 
    myModelString = myModelString+("l_lumi,")
    myModelString = myModelString+("l_b,")
    
    # list of nuisance and parameters of interest
    ws.defineSet("poi","sigma")
    ws.defineSet("nuis","b,lumi")
        
    # the priors
    ws.factory("Uniform::prior_poi({sigma})")
    ws.factory("Uniform::prior_nuis({b,lumi})")
    ws.factory("PROD::prior(prior_poi,prior_nuis)")

    # add the total model to the ws
    myModelString = myModelString[:-1]+(")")
    ws.factory(myModelString)
    ws.Print()

    # Build the model config object, needed for ROOTSTAT limit calculations
    modelConfig = rt.RooStats.ModelConfig("Razor")
    modelConfig.SetWorkspace(ws)
    modelConfig.SetPdf(ws.pdf("model"))
    modelConfig.SetPriorPdf(ws.pdf("prior"))
    modelConfig.SetParametersOfInterest(ws.set("poi"))
    modelConfig.SetNuisanceParameters(ws.set("nuis"))
    # import the model config object to the ws
    getattr(ws, 'import')(modelConfig)

    # generate the "dataset" with observables
    pData = rt.RooDataSet("data","",obs)
    pData.add(obs)
    # import the dataset top the ws
    getattr(ws, 'import')(pData)     
    # set everything to constant
    for box in boxes:
        ws.var("e_%s" % box[0]).setConstant(rt.kTRUE)
        ws.var("n_%s" % box[0]).setConstant(rt.kTRUE)
    ws.var("d_b").setConstant(rt.kTRUE)
    ws.var("d_lumi").setConstant(rt.kTRUE)
    ws.var("nom_b").setConstant(rt.kTRUE)
    ws.var("nom_lumi").setConstant(rt.kTRUE)
    # float the nuisance parameters and the poi
    ws.var("lumi").setConstant(rt.kFALSE)
    ws.var("b").setConstant(rt.kFALSE)
    ws.var("sigma").setConstant(rt.kFALSE)
    
    # Remind us how we got here...
    pData.Print()

    # FC
    

    #bayesian LIMIT calculator
    bc = rt.RooStats.BayesianCalculator(pData, modelConfig)
    bc.SetConfidenceLevel(0.95)
    bInt = bc.GetInterval()

    #print result
    print "Bayesian interval on sigma = [%f, %f]" %( bInt.LowerLimit(), bInt.UpperLimit())

    # save file
    outFile = rt.TFile.Open("outLimit.root", "recreate")
    ws.Write()
    outFile.Close()
