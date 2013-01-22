#ifndef _StandardHypoTestInvDemo_H_
#define _StandardHypoTestInvDemo_H_

#include "RooStats/HypoTestInverterResult.h"

/*

  Other Parameter to pass in tutorial
  apart from standard for filename, ws, modelconfig and data

  type = 0 Freq calculator
  type = 1 Hybrid calculator
  type = 2 Asymptotic calculator
  type = 3 Asymptotic calculator using nominal Asimov data sets (not using fitted parameter values but nominal ones)

  testStatType = 0 LEP
  = 1 Tevatron
  = 2 Profile Likelihood
  = 3 Profile Likelihood one sided (i.e. = 0 if mu < mu_hat)
  = 4 Profiel Likelihood signed ( pll = -pll if mu < mu_hat)
  = 5 Max Likelihood Estimate as test statistic
  = 6 Number of observed event as test statistic

  useCLs          scan for CLs (otherwise for CLs+b)

  npoints:        number of points to scan , for autoscan set npoints = -1

  poimin,poimax:  min/max value to scan in case of fixed scans
  (if min >  max, try to find automatically)

  ntoys:         number of toys to use

  useNumberCounting:  set to true when using number counting events

  nuisPriorName:   name of prior for the nnuisance. This is often expressed as constraint term in the global model
  It is needed only when using the HybridCalculator (type=1)
  If not given by default the prior pdf from ModelConfig is used.

  extra options are available as global paramwters of the macro. They major ones are:

  plotHypoTestResult   plot result of tests at each point (TS distributions) (defauly is true)
  useProof             use Proof   (default is true)
  writeResult          write result of scan (default is true)
  rebuild              rebuild scan for expected limits (require extra toys) (default is false)
  generateBinned       generate binned data sets for toys (default is false) - be careful not to activate with
  a too large (>=3) number of observables
  nToyRatio            ratio of S+B/B toys (default is 2)


*/

RooStats::HypoTestInverterResult*
StandardHypoTestInvDemo(const char * infile = "ws_twobin.root",
                        const char * wsName = "newws",
                        const char * modelSBName = "SbModel",
                        const char * modelBName = "BModel",
                        const char * dataName = "data",
                        int calculatorType = 2,//was 0
                        int testStatType = 3,//was 0
                        bool useCLs = true ,
                        int npoints = 10,
                        double poimin = 0,
                        double poimax = 1000,
                        int ntoys=1000,
                        bool useNumberCounting = false,
                        const char * nuisPriorName = 0,
                        char *cls_name = "cls.png",
                        char *bells_name = "bells.png");

#endif
