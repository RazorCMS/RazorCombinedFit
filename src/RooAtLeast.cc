//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <math.h>

#include "RooAtLeast.h"
#include "RooRealVar.h"

ClassImp(RooAtLeast)
//---------------------------------------------------------------------------
RooAtLeast::RooAtLeast(const char *name, const char *title,
      RooAbsReal &_x, const RooConstVar& _value) :
   RooAbsPdf(name, title),
   X("X", "Dependent", this, _x),
   Value(_value.getVal()),
   UpperBound(10000)
{
}
//---------------------------------------------------------------------------
RooAtLeast::RooAtLeast(const RooAtLeast& other, const char* name) :
   RooAbsPdf(other, name), X("X", this, other.X), Value(other.Value),UpperBound(other.UpperBound)
{
}
//---------------------------------------------------------------------------
Double_t RooAtLeast::evaluate() const
{
   if(X >= Value && X < UpperBound)
      return 1;
   return 0;
}
//---------------------------------------------------------------------------
Int_t RooAtLeast::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* /*rangeName*/) const 
{
	if(matchArgs(allVars, analVars, X))
		return 1;
	return 0;
}
//---------------------------------------------------------------------------
Double_t RooAtLeast::analyticalIntegral(Int_t code, const char* rangeName) const
{
	  assert(code == 1);

	if (X >= Value && X < UpperBound)
		return 0;

	double Max = X.max(rangeName);
	double Min = X.min(rangeName);
	if (Max > UpperBound)
		Max = UpperBound;
	if (Min < Value)
		Min = Value;
	return Max - Min;

}
//---------------------------------------------------------------------------

