//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <math.h>

#include "RooTwoSideGaussianWithTwoExponentialTails.h"
#include "RooRealVar.h"

ClassImp(RooTwoSideGaussianWithTwoExponentialTails)
//---------------------------------------------------------------------------
RooTwoSideGaussianWithTwoExponentialTails::RooTwoSideGaussianWithTwoExponentialTails(const char *name,
   const char *title,
   RooAbsReal &_x, RooAbsReal &_x0,
   RooAbsReal &_sigma_l, RooAbsReal &_sigma_r,
   RooAbsReal &_s1, RooAbsReal &_s2, RooAbsReal &_f) :
   RooAbsPdf(name, title), 
   X("X", "Dependent", this, _x),
   X0("X0", "Gaussian Mean", this, _x0),
   SigmaL("SigmaL", "Left sigma", this, _sigma_l),
   SigmaR("SigmaR", "Right sigma", this, _sigma_r),
   S1("S1", "Exponent 1 of the tail", this, _s1),
   S2("S2", "Exponent 2 of the tail", this, _s2),
   F("F", "Size of second component", this, _f)
{
}
//---------------------------------------------------------------------------
RooTwoSideGaussianWithTwoExponentialTails::RooTwoSideGaussianWithTwoExponentialTails(const RooTwoSideGaussianWithTwoExponentialTails& other, const char* name) :
   RooAbsPdf(other, name), X("X", this, other.X), X0("X0", this, other.X0),
   SigmaL("SigmaL", this, other.SigmaL), SigmaR("SigmaR", this, other.SigmaR),
   S1("S1", this, other.S1), S2("S2", this, other.S2), F("F", this, other.F)
{
}
//---------------------------------------------------------------------------
Double_t RooTwoSideGaussianWithTwoExponentialTails::evaluate() const
{
   double value = 0;

   double XC = (S1 + F * S2) / (1 + F) * SigmaR * SigmaR + X0;

   if(X < X0)   // Left-hand side, normal gaussian
      value = exp(-((X - X0) * (X - X0)) / (2 * SigmaL * SigmaL));
   else if((X >= X0 && X < XC) || (S1 < 0) || (S2 < 0))   // if S1 or S2 < 0, normal two-sided gaussian, no tail
      value = exp(-((X - X0) * (X - X0)) / (2 * SigmaR * SigmaR));
   else   // fun: X > XC > X0
   {
      double A = exp(-((XC - X0) * (XC - X0)) / (2 * SigmaR * SigmaR)) / (1 + F);
      value = A * (exp(-S1 * (X - XC)) + F * exp(-S2 * (X - XC)));
   }

   return value;
}
//---------------------------------------------------------------------------
Int_t RooTwoSideGaussianWithTwoExponentialTails::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* /*rangeName*/) const 
{
   return 0;
}
//---------------------------------------------------------------------------
Double_t RooTwoSideGaussianWithTwoExponentialTails::analyticalIntegral(Int_t code, const char* rangeName) const
{
   return 0;
}
//---------------------------------------------------------------------------

