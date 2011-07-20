//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <TMath.h>
#include <math.h>

#include "RooRazorLShape.h"
#include "RooRealVar.h"

ClassImp(RooRazorLShape)
//---------------------------------------------------------------------------
RooRazorLShape::RooRazorLShape(const char *name, const char *title,
			       RooAbsReal &_x, 	RooAbsReal &_y, 
			       RooAbsReal &_x0, RooAbsReal &_y0) : RooAbsPdf(name, title), 
  X("X", "X Observable", this, _x),
  Y("Y", "Y Observable", this, _y),
  X0("X0", "X Offset", this, _x0),
  Y0("Y0", "Y Offset", this, _y0)
{
}
//---------------------------------------------------------------------------
RooRazorLShape::RooRazorLShape(const RooRazorLShape& other, const char* name) :
   RooAbsPdf(other, name), 
   X("X", this, other.X), 
   Y("Y", this, other.Y), 
   X0("X0", this, other.X0),
   Y0("Y0", this, other.Y0)
{
}
//---------------------------------------------------------------------------
Double_t RooRazorLShape::evaluate() const
{
  if(X>X0 && Y > Y0) return 1.e-20;
  else return 1.;
}

// //---------------------------------------------------------------------------
Int_t RooRazorLShape::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{

   // integral on both X and Y
   if (matchArgs(allVars, analVars, X, Y)) return 1;
   return 0;
}

// //---------------------------------------------------------------------------
Double_t RooRazorLShape::analyticalIntegral(Int_t code, const char* rangeName) const{

   const Double_t xmin = X.min(rangeName); const Double_t xmax = X.max(rangeName);
   const Double_t ymin = Y.min(rangeName); const Double_t ymax = Y.max(rangeName);


   double integral = 0.;
   if(code ==1) { // integral on both X and Y
     (ymax-ymin)*(xmax-xmin) - (xmax-X0)*(ymax-Y0);
   }
   //   if(!(evaluate()/integral>1.7E-308)) integral = evaluate()/(1.7E-308);

   return integral;
}
// //---------------------------------------------------------------------------

