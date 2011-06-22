//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <math.h>

#include "RooSameAs.h"
#include "RooRealVar.h"

ClassImp(RooSameAs)

//---------------------------------------------------------------------------
RooSameAs::RooSameAs(const char *name, const char *title,
      RooAbsReal &_x, const RooConstVar& _value, const RooConstVar& _tolerance) :
   RooAbsPdf(name, title),
   X("X", "Dependent", this, _x),
   Value(_value.getVal()),
   Tolerance(_tolerance.getVal())
{
}
//---------------------------------------------------------------------------
RooSameAs::RooSameAs(const RooSameAs& other, const char* name) :
   RooAbsPdf(other, name), X("X", this, other.X), Value(other.Value),
   Tolerance(other.Tolerance)
{
}
//---------------------------------------------------------------------------
Double_t RooSameAs::evaluate() const
{
   if(X - Value < Tolerance && X - Value > -Tolerance)
      return 1;
   return 0;
}
//---------------------------------------------------------------------------
Int_t RooSameAs::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* /*rangeName*/) const 
{
   if(matchArgs(allVars, analVars, X))
      return 1;
   return 0;
}
//---------------------------------------------------------------------------
Double_t RooSameAs::analyticalIntegral(Int_t code, const char* rangeName) const
{
   assert(code == 1);

   if(X.max(rangeName) < Value - Tolerance || X.min(rangeName) > Value + Tolerance)
      return 0;

   double Max = X.max(rangeName);
   double Min = X.min(rangeName);
   if(Max > Value + Tolerance)
      Max = Value + Tolerance;
   if(Min < Value - Tolerance)
      Min = Value - Tolerance;

   return Max - Min;
}
//---------------------------------------------------------------------------

