//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <math.h>

#include "RooRazor2DTail.h"
#include "RooRealVar.h"

ClassImp(RooRazor2DTail)
//---------------------------------------------------------------------------
RooRazor2DTail::RooRazor2DTail(const char *name, const char *title,
			       RooAbsReal &_x, 	RooAbsReal &_y, 
			       RooAbsReal &_x0, RooAbsReal &_y0, 
			       RooAbsReal &_b) : RooAbsPdf(name, title), 
  X("X", "X Observable", this, _x),
  Y("Y", "Y Observable", this, _y),
  X0("X0", "X Offset", this, _x0),
  Y0("Y0", "Y Offset", this, _y0),
  B("B", "Shape parameter", this, _b)
{
}
//---------------------------------------------------------------------------
RooRazor2DTail::RooRazor2DTail(const RooRazor2DTail& other, const char* name) :
   RooAbsPdf(other, name), 
   X("X", this, other.X), 
   Y("Y", this, other.Y), 
   X0("X0", this, other.X0),
   Y0("Y0", this, other.Y0),
   B("B", this, other.B)
{
}
//---------------------------------------------------------------------------
Double_t RooRazor2DTail::evaluate() const
{
  double myexp = B*(X-X0)-(Y*Y-Y0*Y0);
  if(-myexp > 700.) return 0.;
  else return (myexp-1)*exp(-myexp);
}

//---------------------------------------------------------------------------
Int_t RooRazor2DTail::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* /*rangeName*/) const 
{
  // is this correct?
  if (matchArgs(allVars, analVars, X) && matchArgs(allVars, analVars, Y)) return 1;
  return 0;
}
//---------------------------------------------------------------------------
Double_t RooRazor2DTail::analyticalIntegral(Int_t code, const char* rangeName) const
{

  assert(code==1) ;

  Double_t xmin = X.min(rangeName); Double_t xmax = X.max(rangeName);
  Double_t ymin = Y.min(rangeName); Double_t ymax = Y.max(rangeName);

  if(B == 0) return 0.;

  return 1/B*(exp(-B*ymin*xmin) + exp(-B*xmax*ymax) - exp(-B*xmin*ymax) - exp(-B*ymin*xmax));
}
//---------------------------------------------------------------------------

