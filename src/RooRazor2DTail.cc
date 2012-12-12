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
 double myexp = B*fabs(X-X0)*fabs(Y-Y0);
 double mycoeff = B*fabs(X-X0)*fabs(Y-Y0) - 1.;
  if(myexp < -700) {
    std::cout << "MYEXP = "<< myexp << ", < -700 -- BAD" << std::endl;
    return  1.7e-308;}
  if(mycoeff < 0) {
    std::cout << "MYCOEFF = " << mycoeff <<", IS NEGATIVE -- BAD" << std::endl;
    return  1.7e-308;}
  return mycoeff*exp(-myexp);
}

// //---------------------------------------------------------------------------
Int_t RooRazor2DTail::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
  // integral on both X and Y
  if (matchArgs(allVars, analVars, X, Y)) return 1;
  // integral over X
  else if (matchArgs(allVars, analVars, X)) return 2;
  // integral over Y
  else if (matchArgs(allVars, analVars, Y)) return 3;
  // integrating nothing
  return 0;
}

// //---------------------------------------------------------------------------
Double_t RooRazor2DTail::analyticalIntegral(Int_t code, const char* rangeName) const{

   const Double_t xmin = X.min(rangeName); const Double_t xmax = X.max(rangeName);
   const Double_t ymin = Y.min(rangeName); const Double_t ymax = Y.max(rangeName);

   if(B == 0) return 1.;

   double integral = 0.;
   if(code ==1) { // integral on both X and Y
     integral = (1/B)*(exp(-B*(xmax-X0)*(ymax-Y0))-exp(-B*(xmin-X0)*(ymax-Y0))-exp(-B*(xmax-X0)*(ymin-Y0))+exp(-B*(xmin-X0)*(ymin-Y0)));
   } else if(code == 2) { // integral on X
     integral = -(xmax-X0)*exp(-B*(xmax-X0)*(Y-Y0)) + (xmin-X0)*exp(-B*(xmin-X0)*(Y-Y0));
   } else if(code == 3) { // integral on Y
     integral = -(ymax-Y0)*exp(-B*(ymax-Y0)*(X-X0)) + (ymin-Y0)*exp(-B*(ymin-Y0)*(X-X0));
   } else {
     cout << "WARNING IN RooRazor2DTail: integration code is not correct" << endl;
     cout << "                           what are you integrating on?" << endl;
     return 1.;
   }

   return integral;
}
// //---------------------------------------------------------------------------

