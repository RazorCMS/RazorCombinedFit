//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <TMath.h>
#include <math.h>

#include "RooTwoBin.h"
#include "RooRealVar.h"

ClassImp(RooTwoBin)
//---------------------------------------------------------------------------
RooTwoBin::RooTwoBin(const char *name, const char *title,
			       RooAbsReal &_x, 	 
			       RooAbsReal &_x0) : RooAbsPdf(name, title), 
  X("X", "X Observable", this, _x),
  X0("X0", "X Offset", this, _x0)
{
}
//---------------------------------------------------------------------------
RooTwoBin::RooTwoBin(const RooTwoBin& other, const char* name) :
   RooAbsPdf(other, name), 
   X("X", this, other.X), 
   X0("X0", this, other.X0)
{
}
//---------------------------------------------------------------------------
Double_t RooTwoBin::evaluate() const
{
  cout << X << " " << X0 << endl;
  if(X==X0) return 1.;
  return 0.;
}

// //---------------------------------------------------------------------------
Int_t RooTwoBin::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
   return 1;
}

// //---------------------------------------------------------------------------
Double_t RooTwoBin::analyticalIntegral(Int_t code, const char* rangeName) const{
   return 1.;
}
// //---------------------------------------------------------------------------

