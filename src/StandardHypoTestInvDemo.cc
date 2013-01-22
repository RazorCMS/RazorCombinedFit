// Slight adaptation of roostats package.
// Modification: added a name argument to the method, so that graphs can be saved with a name.
// -Max Horton
// Maxwell.christian.horton@gmail.com



/* -*- mode: c++ -*- */
// Standard tutorial macro for performing an inverted  hypothesis test for computing an interval
//
// This macro will perform a scan of the p-values for computing the interval or limit
//
//Author:  L. Moneta
//
// Usage: 
//
// root>.L StandardHypoTestInvDemo.C
// root> StandardHypoTestInvDemo("fileName","workspace name","S+B modelconfig name","B model name","data set name",calculator type, test statistic type, use CLS, 
//                                number of points, xmin, xmax, number of toys, use number counting)
//
//
// type = 0 Freq calculator 
// type = 1 Hybrid calculator
// type = 2 Asymptotic calculator  
// type = 3 Asymptotic calculator using nominal Asimov data sets (not using fitted parameter values but nominal ones)
//
// testStatType = 0 LEP
//              = 1 Tevatron 
//              = 2 Profile Likelihood two sided
//              = 3 Profile Likelihood one sided (i.e. = 0 if mu < mu_hat) - (WR: We should use this one)
//              = 4 Profile Likelihood signed ( pll = -pll if mu < mu_hat) 
//              = 5 Max Likelihood Estimate as test statistic
//              = 6 Number of observed event as test statistic
//
 


#include "TFile.h"
#include "RooWorkspace.h"
#include "RooAbsPdf.h"
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooStats/ModelConfig.h"
#include "RooRandom.h"
#include "TGraphErrors.h"
#include "TGraphAsymmErrors.h"



#include "TCanvas.h"
#include "TLine.h"
#include "TROOT.h"
#include "TSystem.h"

#include "RooStats/AsymptoticCalculator.h"
#include "RooStats/HybridCalculator.h"
#include "RooStats/FrequentistCalculator.h"
#include "RooStats/ToyMCSampler.h"
#include "RooStats/HypoTestPlot.h"

#include "RooStats/NumEventsTestStat.h"
#include "RooStats/ProfileLikelihoodTestStat.h"
#include "RooStats/SimpleLikelihoodRatioTestStat.h"
#include "RooStats/RatioOfProfiledLikelihoodsTestStat.h"
#include "RooStats/MaxLikelihoodEstimateTestStat.h"
#include "RooStats/NumEventsTestStat.h"

#include "RooStats/HypoTestInverter.h"
#include "RooStats/HypoTestInverterResult.h"
#include "RooStats/HypoTestInverterPlot.h"

#include "HypoTestInvTool.h"
#include "StandardHypoTestInvDemo.h"

using namespace RooFit;
using namespace RooStats;


bool plotHypoTestResult = true;          // plot test statistic result at each point
bool writeResult = true;                 // write HypoTestInverterResult in a file 
TString resultFileName;                  // file with results (by default is built automatically using the workspace input file name)
bool optimize = true;                    // optmize evaluation of test statistic 
bool useVectorStore = true;              // convert data to use new roofit data store 
bool generateBinned = false;             // generate binned data sets 
double nToysRatio = 2;                   // ratio Ntoys S+b/ntoysB
double maxPOI = -1;                      // max value used of POI (in case of auto scan) 
bool useProof = false;                    // use Proof Light when using toys (for freq or hybrid)
int nworkers = 4;                        // number of worker for Proof
bool rebuild = false;                    // re-do extra toys for computing expected limits and rebuild test stat
                                         // distributions (N.B this requires much more CPU (factor is equivalent to nToyToRebuild)
int nToyToRebuild = 100;                 // number of toys used to rebuild 
int randomSeed = -1;                     // random seed (if = -1: use default value, if = 0 always random )
                                         // NOTE: Proof uses automatically a random seed

std::string massValue = "";              // extra string to tag output file of result 
int   printLevel = 0;                    // print level for debugging PL test statistics and calculators  

HypoTestInverterResult*
StandardHypoTestInvDemo(const char * infile,
                        const char * wsName,
                        const char * modelSBName,
                        const char * modelBName,
                        const char * dataName,
                        int calculatorType,
                        int testStatType,
                        bool useCLs,
                        int npoints,
                        double poimin,
                        double poimax,
                        int ntoys,
                        bool useNumberCounting,
                        const char * nuisPriorName,
                        char *cls_name,
                        char *bells_name){

   TString fileName(infile);
   if (fileName.IsNull()) { 
      fileName = "results/example_combined_GaussExample_model.root";
      std::cout << "Use standard file generated with HistFactory : " << fileName << std::endl;
   }
  
   // open file and check if input file exists
   TFile * file = TFile::Open(fileName); 
  
   // if input file was specified but not found, quit
   if(!file && !TString(infile).IsNull()){
      cout <<"file " << fileName << " not found" << endl;
      return 0;
   } 
  
   // if default file not found, try to create it
   if(!file ){
      // Normally this would be run on the command line
      cout <<"will run standard hist2workspace example"<<endl;
      gROOT->ProcessLine(".! prepareHistFactory .");
      gROOT->ProcessLine(".! hist2workspace config/example.xml");
      cout <<"\n\n---------------------"<<endl;
      cout <<"Done creating example input"<<endl;
      cout <<"---------------------\n\n"<<endl;
    
      // now try to access the file again
      file = TFile::Open(fileName);
    
   }
  
   if(!file){
      // if it is still not there, then we can't continue
      cout << "Not able to run hist2workspace to create example input" <<endl;
      return 0;
   }

   HypoTestInvTool calc;
   calc.output_name_cls = cls_name;
   calc.output_name_bells = bells_name;

   // set parameters
   calc.SetParameter("PlotHypoTestResult", plotHypoTestResult);
   calc.SetParameter("WriteResult", writeResult);
   calc.SetParameter("Optimize", optimize);
   calc.SetParameter("UseVectorStore", useVectorStore);
   calc.SetParameter("GenerateBinned", generateBinned);
   calc.SetParameter("NToysRatio", nToysRatio);
   calc.SetParameter("MaxPOI", maxPOI);
   calc.SetParameter("UseProof", useProof);
   calc.SetParameter("NWorkers", nworkers);
   calc.SetParameter("Rebuild", rebuild);
   calc.SetParameter("NToyToRebuild", nToyToRebuild);
   calc.SetParameter("MassValue", massValue.c_str());
   calc.SetParameter("MinimizerType", calc.minimizerType.c_str());
   calc.SetParameter("PrintLevel", printLevel);
   calc.SetParameter("InitialFit",calc.initialFit);
   calc.SetParameter("ResultFileName",resultFileName);
   calc.SetParameter("RandomSeed",randomSeed);


   RooWorkspace * w = dynamic_cast<RooWorkspace*>( file->Get(wsName) );
   HypoTestInverterResult * r = 0;  
   std::cout << w << "\t" << fileName << std::endl;
   if (w != NULL) {
      r = calc.RunInverter(w, modelSBName, modelBName,
                           dataName, calculatorType, testStatType, useCLs,
                           npoints, poimin, poimax,  
                           ntoys, useNumberCounting, nuisPriorName );    
      if (!r) { 
         std::cerr << "Error running the HypoTestInverter - Exit " << std::endl;
         return r;
      }
   }
   else { 
      // case workspace is not present look for the inverter result
      std::cout << "Reading an HypoTestInverterResult with name " << wsName << " from file " << fileName << std::endl;
      r = dynamic_cast<HypoTestInverterResult*>( file->Get(wsName) ); //
      if (!r) { 
         std::cerr << "File " << fileName << " does not contain a workspace or an HypoTestInverterResult - Exit " 
                   << std::endl;
         file->ls();
         return r;
      }
   }		
  
   calc.AnalyzeResult( r, calculatorType, testStatType, useCLs, npoints, infile );
  
   return r;
}

void ReadResult(const char * fileName, const char * resultName="", bool useCLs=true) { 
   // read a previous stored result from a file given the result name

   StandardHypoTestInvDemo(fileName, resultName,"","","",0,0,useCLs);
}


#ifdef USE_AS_MAIN
int main() {
    StandardHypoTestInvDemo();
}
#endif

