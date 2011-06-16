//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <math.h>

#include "RooTwoSideGaussianWithAnExponentialTail.h"
#include "RooRealVar.h"

ClassImp(RooTwoSideGaussianWithAnExponentialTail)
//---------------------------------------------------------------------------
RooTwoSideGaussianWithAnExponentialTail::RooTwoSideGaussianWithAnExponentialTail(const char *name,
   const char *title,
   RooAbsReal &_x, RooAbsReal &_x0,
   RooAbsReal &_sigma_l, RooAbsReal &_sigma_r, RooAbsReal &_s) :
   RooAbsPdf(name, title), 
   X("X", "Dependent", this, _x),
   X0("X0", "Gaussian Mean", this, _x0),
   SigmaL("SigmaL", "Left sigma", this, _sigma_l),
   SigmaR("SigmaR", "Right sigma", this, _sigma_r),
   S("S", "Exponent of the tail", this, _s)
{
}
//---------------------------------------------------------------------------
RooTwoSideGaussianWithAnExponentialTail::RooTwoSideGaussianWithAnExponentialTail(const RooTwoSideGaussianWithAnExponentialTail& other, const char* name) :
   RooAbsPdf(other, name), X("X", this, other.X), X0("X0", this, other.X0),
   SigmaL("SigmaL", this, other.SigmaL), SigmaR("SigmaR", this, other.SigmaR),
   S("S", this, other.S)
{
}
//---------------------------------------------------------------------------
Double_t RooTwoSideGaussianWithAnExponentialTail::evaluate() const
{
   double value = 0;

   double XC = S * SigmaR * SigmaR + X0;

   if(X < X0)   // Left-hand side, normal gaussian
      value = exp(-((X - X0) * (X - X0)) / (2 * SigmaL * SigmaL));
   else if((X >= X0 && X < XC) || (S < 0))   // X between X0 and XC (or S < 0), normal two-sided gaussian, no tail
      value = exp(-((X - X0) * (X - X0)) / (2 * SigmaR * SigmaR));
   else   // fun: X > XC > X0
   {
      double A = exp(-((XC - X0) * (XC - X0)) / (2 * SigmaR * SigmaR));
      value = A * exp(-S * (X - XC));
   }

   return value;
}
//---------------------------------------------------------------------------
Int_t RooTwoSideGaussianWithAnExponentialTail::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* /*rangeName*/) const 
{
   return 0;
}
//---------------------------------------------------------------------------
Double_t RooTwoSideGaussianWithAnExponentialTail::analyticalIntegral(Int_t code, const char* rangeName) const
{
   return 0;
}
//---------------------------------------------------------------------------

