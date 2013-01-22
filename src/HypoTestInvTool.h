#ifndef _HYPOTESTINVTOOL_
#define _HYPOTESTINVTOOL_

// internal class to run the inverter and more
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

//using namespace RooFit;
//using namespace RooStats;


namespace RooStats {

   class HypoTestInvTool{

   public:
      HypoTestInvTool();
      ~HypoTestInvTool(){};

      HypoTestInverterResult *
      RunInverter(RooWorkspace * w,
                  const char * modelSBName, const char * modelBName,
                  const char * dataName,
                  int type,  int testStatType,
                  bool useCLs,
                  int npoints, double poimin, double poimax, int ntoys,
                  bool useNumberCounting = false,
                  const char * nuisPriorName = 0);



      void
      AnalyzeResult( HypoTestInverterResult * r,
                     int calculatorType,
                     int testStatType,
                     bool useCLs,
                     int npoints,
                     const char * fileNameBase = 0 );

      void SetParameter(const char * name, const char * value);
      void SetParameter(const char * name, bool value);
      void SetParameter(const char * name, int value);
      void SetParameter(const char * name, double value);

      //options
      bool noSystematics;              // force all systematics to be off (i.e. set all nuisance parameters as constat to their nominal values)
      std::string  minimizerType;         // minimizer type (default is what is in ROOT::Math::MinimizerOptions::DefaultMinimizerType()
      int initialFit;                     // do a first  fit to the model (-1 : default, 0 skip fit, 1 do always fit)
      char *output_name_cls;
      char *output_name_bells;

   private:

      bool mPlotHypoTestResult;
      bool mWriteResult;
      bool mOptimize;
      bool mUseVectorStore;
      bool mGenerateBinned;
      bool mUseProof;
      bool mRebuild;
      int     mNWorkers;
      int     mNToyToRebuild;
      int     mPrintLevel;
      int     mInitialFit;
      int     mRandomSeed;
      double  mNToysRatio;
      double  mMaxPoi;
      std::string mMassValue;
      std::string mMinimizerType;                  // minimizer type (default is what is in ROOT::Math::MinimizerOptions::DefaultMinimizerType()
      TString     mResultFileName;
   };

} // end namespace RooStats

#endif
