//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <math.h>

#include "RooTwoSideGaussianWithOneXDependentExponential.h"
#include "RooRealVar.h"

ClassImp(RooTwoSideGaussianWithOneXDependentExponential)
//---------------------------------------------------------------------------
RooTwoSideGaussianWithOneXDependentExponential::RooTwoSideGaussianWithOneXDependentExponential(const char *name,
   const char *title,
   RooAbsReal &_x, RooAbsReal &_x0,						       
   RooAbsReal &_sigma_l, RooAbsReal &_sigma_r, 
   RooAbsReal &_s1, RooAbsReal &_a1) :
   RooAbsPdf(name, title), 
   X("X", "Dependent", this, _x),
   X0("X0", "Gaussian Mean", this, _x0),
   SigmaL("SigmaL", "Left sigma", this, _sigma_l),
   SigmaR("SigmaR", "Right sigma", this, _sigma_r),
   S1("S1", "Exponent of the tail term", this, _s1),
   A1("A1", "Denominator of the tail term", this, _a1)
{
}
//---------------------------------------------------------------------------
RooTwoSideGaussianWithOneXDependentExponential::RooTwoSideGaussianWithOneXDependentExponential(const RooTwoSideGaussianWithOneXDependentExponential& other, const char* name) :
   RooAbsPdf(other, name), X("X", this, other.X), X0("X0", this, other.X0),
   SigmaL("SigmaL", this, other.SigmaL), SigmaR("SigmaR", this, other.SigmaR),
   S1("S1", this, other.S1), A1("A1", this, other.A1) 
{
}
//---------------------------------------------------------------------------
Double_t RooTwoSideGaussianWithOneXDependentExponential::evaluate() const
{

  double value = 0.;
  double XC = S1 * SigmaR * SigmaR + X0;

  if (X < X0)   // Left-hand side, normal gaussian
    value = exp(-((X - X0) * (X - X0)) / (2 * SigmaL * SigmaL));
  else if ((X >= X0 && X < XC) || (S1 < 0))   // if S1 < 0, normal two-sided gaussian, no tail
    value = exp(-((X - X0) * (X - X0)) / (2 * SigmaR * SigmaR));
  else   // fun: X > XC > X0
    {
      double A = exp(-((XC - X0) * (XC - X0)) / (2 * SigmaR * SigmaR)) ;
      value = A * (exp(-S1 * ((X - XC) / (1.0 + A1 * (X - XC)))));
    }

   return value;
}
//---------------------------------------------------------------------------
Int_t RooTwoSideGaussianWithOneXDependentExponential::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const 
{
  return 0;
  // integral on X
  if (matchArgs(allVars, analVars, X)) return 1;
  return 0;
}
//---------------------------------------------------------------------------
Double_t RooTwoSideGaussianWithOneXDependentExponential::analyticalIntegral(Int_t code, const char* rangeName) const
{
   const Double_t xmin = X.min(rangeName); const Double_t xmax = X.max(rangeName);
   double XC = S1 * SigmaR * SigmaR + X0;

   double integral = 0.;
   double xlow1 = 0.;
   double xhigh1 = 0.;
   double xlow2 = 0.;
   double xhigh2 = 0.;
   double xlow3 = 0.;
   double xhigh3 = 0.;

   if(code==1) { 
     if(xmin < X0 && xmax <=X0)
       {
	 xlow1 = xmin;
	 xhigh1 = xmax;
       }

     //integral += ROOT::Math::normal_cdf(SigmaL,xhigh1,X0) - ROOT::Math::normal_cdf(SigmaL,xlow1,X0);
     //integral += ROOT::Math::normal_cdf(SigmaR,xhigh2,X0) - ROOT::Math::normal_cdf(SigmaR,xlow2,X0);

   }
   return integral;
   
}
//---------------------------------------------------------------------------
