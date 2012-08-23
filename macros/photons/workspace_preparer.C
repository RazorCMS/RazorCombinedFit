/*
 * Max Horton
 * CERN Summer Student 2012
 * Caltech Class of 2014
 * maxwell.christian.horton@gmail.com
 * 
 * This code sets up a workspace with pdfs and variables / expressions.
 * The workspace is used in a call to the RooStats StandardHypoTestInv.C,
 * to calculate CLs for inputs.
 *
 * Adapted from roostats_twobin.C, by Fedor Ratnikov and Gena Kukartsev
 */


#include "TStopwatch.h"
#include "TCanvas.h"
#include "TROOT.h"
/*
#include "RooPlot.h"
#include "RooAbsPdf.h"
#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "RooGlobalFunc.h"
#include "RooFitResult.h"
#include "RooRandom.h"
#include "RooArgSet.h"

#include "RooStats/RooStatsUtils.h"
#include "RooStats/ProfileLikelihoodCalculator.h"
#include "RooStats/LikelihoodInterval.h"
#include "RooStats/LikelihoodIntervalPlot.h"
#include "RooStats/BayesianCalculator.h"
#include "RooStats/MCMCCalculator.h"
#include "RooStats/MCMCInterval.h"
#include "RooStats/MCMCIntervalPlot.h"
#include "RooStats/ProposalHelper.h"
#include "RooStats/SimpleInterval.h"
#include "RooStats/FeldmanCousins.h"
#include "RooStats/PointSetInterval.h"
*/

using namespace RooFit;
using namespace RooStats;


// Functions
void workspace_preparer(char *four_hist_file_name= "gaussian_counting_signal.root", 
                        char *background_pdf_name_in_file = "background",
                        char *data_set_name_in_file = "data", 
                        char *write_workspace_name = "newws",
                        char *ws_container_name = "razor_output.root");
void SetConstants(RooWorkspace * w, RooStats::ModelConfig * mc);
void SetConstant(const RooArgSet * vars, Bool_t value );

/*
 * Prepares the workspace to be used by the hypothesis test calculator
 */
void workspace_preparer(char *four_hist_file_name, char *background_pdf_name_in_file, char *data_set_name_in_file, char *write_workspace_name, char *ws_container_name){

  /* Obtain the necessary packages */
  // I have made assumptions about locations / naming conventions
  gSystem->Load("libRazor");
  TFile *bkg_file = new TFile(ws_container_name);
  TDirectoryFile *had = bkg_file->Get("Had");
  had->cd();
  RooWorkspace * pWs = BoxHad_workspace;


  /* Create the file containing the four histograms needed to make model*/
  TFile *four_hist_file = new TFile(four_hist_file_name);

  /* Draw the Razor variables from the workspace */
  RooRealVar MR = *pWs->var("MR");
  RooRealVar Rsq = *pWs->var("Rsq");

  /* Arglists needed later for pdf creation */
  RooArgList pdf_arg_list(MR, Rsq, "input_args_list");
  RooArgSet pdf_arg_set(MR, Rsq, "input_pdf_args_set");

  /* Create histogram arguments */
  TH2D *nom = (TH2D *) four_hist_file->Get("wHisto");
  TH2D *jes = (TH2D *) four_hist_file->Get("JESerr");
  TH2D *pdf = (TH2D *) four_hist_file->Get("PDFerr");
  TH2D *btag = (TH2D *) four_hist_file->Get("BTAGerr");

  /* Factory all the variables */
  // Parameter of interest
  pWs->factory("poi[.00001, 0, .00002]");
  // Luminosity (lognormal)
  pWs->factory("Gaussian::lumi_pdf(prime_lumi[0, -5, 5], 
                nom_lumi[0, -5, 5], 1)");
  pWs->factory("expr::lumi('4980* pow(1.1, @0)', prime_lumi)");
  // Efficiency (lognormal)
  pWs->factory("Gaussian::eff_pdf(prime_eff[0, -5, 5], 
                nom_eff[0, -5, 5], 1)");
  pWs->factory("expr::eff('1* pow(1.1, @0)', prime_eff)");
  // Lognormal gaussian-distributed terms used in signal hist.
  pWs->factory("Gaussian::xJes_pdf(prime_xJes[0, -5, 5], 
                nom_xJes[0, -5, 5], 1)");
  pWs->factory("Gaussian::xPdf_pdf(prime_xPdf[0, -5, 5], 
                nom_xPdf[0, -5, 5], 1)");
  pWs->factory("Gaussian::xBtag_pdf(prime_xBtag[0, -5, 5], 
                nom_xBtag[0, -5, 5], 1)");

  RooRealVar xJeslivevar = *pWs->var("prime_xJes");
  RooRealVar xPdflivevar = *pWs->var("prime_xPdf");
  RooRealVar xBtaglivevar = *pWs->var("prime_xBtag");

  /* Make the signal pdf */
  RooRazor2DSignal unextended_sig_pdf("unext_sig", "unext_sig", MR, Rsq, nom, jes, pdf, btag, xJeslivevar, xPdflivevar, xBtaglivevar);
  pWs->factory("expr::S('@0*@1*@2', lumi, poi, eff)");
  RooAbsReal *S = pWs->function("S");
  RooExtendPdf *signalpart = new RooExtendPdf("signalpart", "signalpart",
                                              unextended_sig_pdf, *S);

  /* Background pdf stuff.  It's already in the pWs, since Josh is a nice guy. */
  RooExtendPdf *backgroundpart = pWs->pdf(background_pdf_name_in_file);

  RooArgList *pdf_list = new RooArgList(*signalpart, *backgroundpart,
                                        "list");
  // Add the signal and background pdfs to make a TotalPdf
  RooAddPdf *TotalPdf = new RooAddPdf("TotalPdf", "TotalPdf", *pdf_list);



  /* Multiply in the nuisances. */
  RooArgList *pdf_prod_list = new RooArgList(*TotalPdf, 
                                             *pWs->pdf("lumi_pdf"),
                                             *pWs->pdf("xJes_pdf"),
                                             *pWs->pdf("xPdf_pdf"),
                                             *pWs->pdf("xBtag_pdf"),
                                             *pWs->pdf("eff_pdf"));
  // This creates the final model pdf.
  RooProdPdf *model= new RooProdPdf("model", "model", *pdf_prod_list);

  /* Make a fresh workspace. */
  RooWorkspace *zedws = new RooWorkspace("newws");
  zedws->import(*model);

  // Don't delete pWs yet.  We will use it once more later.

  // observables
  RooArgSet obs(*zedws->var("MR"), *zedws->var("Rsq"), "obs");

  // global observables
  RooArgSet globalObs(*zedws->var("nom_lumi"), *zedws->var("nom_eff"), *zedws->var("nom_xJes"), *zedws->var("nom_xPdf"), *zedws->var("nom_xBtag"), "global_obs");

  //fix global observables to their nominal values
  zedws->var("nom_lumi")->setConstant();
  zedws->var("nom_eff")->setConstant();
  zedws->var("nom_xJes")->setConstant();
  zedws->var("nom_xPdf")->setConstant();
  zedws->var("nom_xBtag")->setConstant();

  //Set Parameters of interest
  RooArgSet poi(*zedws->var("poi"), "poi");


  //Set Nuisances
  RooArgSet nuis(*zedws->var("prime_lumi"), *zedws->var("prime_eff"), *zedws->var("prime_xJes"), *zedws->var("prime_xPdf"), *zedws->var("prime_xBtag"));

  RooDataSet *pData = (RooDataSet *) pWs->data(data_set_name_in_file);
  zedws->import(*pData);
  

  // Craft the signal+background model
  ModelConfig * pSbModel = new ModelConfig("SbModel");
  pSbModel->SetWorkspace(*zedws);


  pSbModel->SetPdf(*zedws->pdf("model"));
  //pSbModel->SetPriorPdf(*zedws->pdf("prior")); Omitted because we aren't using priors.
  pSbModel->SetParametersOfInterest(poi);
  pSbModel->SetNuisanceParameters(nuis);
  pSbModel->SetObservables(obs);
  pSbModel->SetGlobalObservables(globalObs);

  // set all but obs, poi and nuisance to const
  SetConstants(zedws, pSbModel);
  zedws->import(*pSbModel);


  // background-only model
  // use the same PDF as s+b, with sig=0
  // POI value under the background hypothesis
  // (We will set the value to 0 later)

  Double_t poiValueForBModel = 0.0;
  ModelConfig* pBModel = new ModelConfig(*(RooStats::ModelConfig *)zedws->obj("SbModel"));
  pBModel->SetName("BModel");
  pBModel->SetWorkspace(*zedws);
  zedws->import(*pBModel);

  // find global maximum with the signal+background model
  // with conditional MLEs for nuisance parameters
  // and save the parameter point snapshot in the Workspace
  //  - safer to keep a default name because some RooStats calculators
  //    will anticipate it
  RooAbsReal * pNll = pSbModel->GetPdf()->createNLL(*pData);
  RooAbsReal * pProfile = pNll->createProfile(RooArgSet());
  pProfile->getVal(); // this will do fit and set POI and nuisance parameters to fitted values
  RooArgSet * pPoiAndNuisance = new RooArgSet();
  if(pSbModel->GetNuisanceParameters())
    pPoiAndNuisance->add(*pSbModel->GetNuisanceParameters());
  pPoiAndNuisance->add(*pSbModel->GetParametersOfInterest());
  cout << "\nWill save these parameter points that correspond to the fit to data" << endl;
  pPoiAndNuisance->Print("v");
  pSbModel->SetSnapshot(*pPoiAndNuisance);
  delete pProfile;
  delete pNll;
  delete pPoiAndNuisance;


  // Find a parameter point for generating pseudo-data
  // with the background-only data.
  // Save the parameter point snapshot in the Workspace
  pNll = pBModel->GetPdf()->createNLL(*pData);
  pProfile = pNll->createProfile(poi);
  ((RooRealVar *)poi.first())->setVal(poiValueForBModel);
  pProfile->getVal(); // this will do fit and set nuisance parameters to profiled values
  pPoiAndNuisance = new RooArgSet();
  if(pBModel->GetNuisanceParameters())
    pPoiAndNuisance->add(*pBModel->GetNuisanceParameters());
  pPoiAndNuisance->add(*pBModel->GetParametersOfInterest());
  cout << "\nShould use these parameter points to generate pseudo data for bkg only" << endl;
  pPoiAndNuisance->Print("v");
  pBModel->SetSnapshot(*pPoiAndNuisance);
  delete pProfile;
  delete pNll;
  delete pPoiAndNuisance;

  // save workspace to file
  zedws->writeToFile(write_workspace_name);

  // clean up
  //delete newworkspace;
  delete zedws;
  delete pData;
  delete pSbModel;
  delete pBModel;


} // ----- end of tutorial ----------------------------------------



// helper functions

void SetConstants(RooWorkspace * pWs, RooStats::ModelConfig * pMc){
  //
  // Fix all variables in the PDF except observables, POI and
  // nuisance parameters. Note that global observables are fixed.
  // If you need global observables floated, you have to set them
  // to float separately.
  //

  pMc->SetWorkspace(*pWs);

  RooAbsPdf * pPdf = pMc->GetPdf(); // we do not own this

  RooArgSet * pVars = pPdf->getVariables(); // we do own this

  RooArgSet * pFloated = new RooArgSet(*pMc->GetObservables());
  pFloated->add(*pMc->GetParametersOfInterest());
  pFloated->add(*pMc->GetNuisanceParameters());

  TIterator * pIter = pVars->createIterator(); // we do own this

  for(TObject * pObj = pIter->Next(); pObj; pObj = pIter->Next() ){
    std::string _name = pObj->GetName();
    RooRealVar * pFloatedObj = (RooRealVar *)pFloated->find(_name.c_str());
    if (pFloatedObj){
      ((RooRealVar *)pObj)->setConstant(kFALSE);
    }
    else{
      ((RooRealVar *)pObj)->setConstant(kTRUE);
    }
  }

  delete pIter;
  delete pVars;
  delete pFloated;

  return;
}



void SetConstant(const RooArgSet * vars, Bool_t value ){
  //
  // Set the constant attribute for all vars in the set
  //

  TIterator * pIter = vars->createIterator(); // we do own this

  for(TObject * pObj = pIter->Next(); pObj; pObj = pIter->Next() ){
    ((RooRealVar *)pObj)->setConstant(value);
  }

  delete pIter;

  return;
}


