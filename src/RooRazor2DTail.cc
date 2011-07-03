//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <TMath.h>
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
  double myexp = B*(X-X0)*(Y-Y0);
  return fabs(myexp-1)*exp(-myexp);
}

// //---------------------------------------------------------------------------
// Int_t RooRazor2DTail::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* /*rangeName*/) const 
// {
//   // integral on both X and Y
//   if (matchArgs(allVars, analVars, X, Y)) return 1;
//   return 0;
// }
// //---------------------------------------------------------------------------
// Double_t RooRazor2DTail::analyticalIntegral(Int_t code, const char* rangeName) const
// {

//   assert(code==1) ;

//   Double_t xmin = X.min(rangeName)-X0; Double_t xmax = X.max(rangeName)-X0;
//   Double_t ymin = Y.min(rangeName)-Y0; Double_t ymax = Y.max(rangeName)-Y0;

//   if(B == 0) return 0.;

//   return 1/B*(exp(-B*xmin*ymin)+exp(-B*xmax*ymax)-exp(-B*xmax*ymin)-exp(-B*xmin*ymax));

//   // return 
//   //   sqrt(xmin*pihalf/B)*(TMath::Erf(sqrt(xmin*B)*ymax) - TMath::Erf(sqrt(xmin*B)*ymin)) -
//   //   sqrt(xmax*pihalf/B)*(TMath::Erf(sqrt(xmax*B)*ymax) - TMath::Erf(sqrt(xmax*B)*ymin)) -
//   //   (ymax-ymin)/Y0*(TMath::Exp(Y0*xmax)-TMath::Exp(Y0*xmin));
// }
// //---------------------------------------------------------------------------

