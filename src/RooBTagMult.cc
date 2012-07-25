//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <TMath.h>
#include <math.h>

#include "RooBTagMult.h"
#include "RooRealVar.h"

ClassImp(RooBTagMult)
//---------------------------------------------------------------------------
RooBTagMult::RooBTagMult(const char *name, const char *title,
			       RooAbsReal &_x,
			       RooAbsReal &_f1,
			       RooAbsReal &_f2,
			       RooAbsReal &_f3,
			       RooAbsReal &_f4) : RooAbsPdf(name, title), 
  X("X", "X Observable", this, _x),
  f1("f1", "nBtag=1 fraction", this, _f1),
  f2("f2", "nBtag=2 fraction", this, _f2),
  f3("f3", "nBtag=3 fraction", this, _f3),
  f4("f4", "nBtag=4 fraction", this, _f4)
{
}
//---------------------------------------------------------------------------
RooBTagMult::RooBTagMult(const RooBTagMult& other, const char* name) :
   RooAbsPdf(other, name), 
   X("X", this, other.X), 
   f1("f1", this, other.f1),
   f2("f2", this, other.f2),
   f3("f3", this, other.f3),
   f4("f4", this, other.f4)
{
}
//---------------------------------------------------------------------------
Double_t RooBTagMult::evaluate() const
{
  double thisf4 = f4;
  double thisf1 = f1;
  double thisf2 = f2;
  double thisf3 = f3;
  if(thisf4+thisf1+thisf2+thisf3 > 1.) return 1.E-10;
    // {
    //   double scale = thisf4+thisf1+thisf2+thisf3+0.0000001;
    //   thisf4 *= 1./scale;
    //   thisf1 *= 1./scale;
    //   thisf2 *= 1./scale;
    //   thisf3 *= 1./scale;
    // }
  double thisf0 = max(0.0000001,1.-thisf4-thisf1-thisf2-thisf3);
  if(X<1.) return thisf0/(thisf0+thisf1+thisf2+thisf3+thisf4);
  else if(X<2.) return thisf1/(thisf0+thisf1+thisf2+thisf3+thisf4);
  else if(X<3.) return thisf2/(thisf0+thisf1+thisf2+thisf3+thisf4);
  else if(X<4.) return thisf3/(thisf0+thisf1+thisf2+thisf3+thisf4);
  else return thisf4/(thisf0+thisf1+thisf2+thisf3+thisf4);
}

// //---------------------------------------------------------------------------
Int_t RooBTagMult::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
  return 1;
}

// //---------------------------------------------------------------------------
Double_t RooBTagMult::analyticalIntegral(Int_t code, const char* rangeName) const{
   return 1.;
}
// //---------------------------------------------------------------------------

