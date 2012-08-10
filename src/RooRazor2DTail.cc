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
  if(myexp> 700 ) return  1.7e-308;// very bad
  
 return fabs(myexp-1)*exp(-myexp);
}

// //---------------------------------------------------------------------------
Int_t RooRazor2DTail::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{


   // const Double_t xmin = X.min(rangeName)-X0; const Double_t xmax = X.max(rangeName)-X0;
   // const Double_t ymin = Y.min(rangeName)-Y0; const Double_t ymax = Y.max(rangeName)-Y0;

   // std::cout << "RooRazor2DTail::getAnalyticalIntegral" << std::endl;
   // std::cout << "X: " << X << std::endl;
   // std::cout << "Y: " << Y << std::endl;
   // std::cout << "X0: " << X0 << std::endl;
   // std::cout << "Y0: " << Y0 << std::endl;
   // std::cout << "B: " << B << std::endl;

   // std::cout << "xmin: " << xmin << "\t xmax: " << xmax << std::endl;
   // std::cout << "ymin: " << ymin << "\t ymax: " << ymax << std::endl;

   // std::cout << "Full 1: " << analyticalIntegral(1,rangeName) << std::endl;
   // std::cout << "Proj 2: " << analyticalIntegral(2,rangeName) << std::endl;
   // std::cout << "Proj 3: " << analyticalIntegral(3,rangeName) << std::endl;

   const Double_t xmin = X.min(rangeName); const Double_t xmax = X.max(rangeName);
   const Double_t ymin = Y.min(rangeName); const Double_t ymax = Y.max(rangeName);

   // integral on both X and Y
   if (matchArgs(allVars, analVars, X, Y)) return 1;
   // // // integral over X
   //else if (matchArgs(allVars, analVars, X) && Y0<(1+B*X0-B*xmin*Y)/(B*X0-B*xmin)) return 2;
   //   else if (matchArgs(allVars, analVars, X) && Y0>=(1+B*X0-B*xmin*Y)/(B*X0-B*xmin)) return 3;
   // // // integral over Y
   //   else if (matchArgs(allVars, analVars, Y) && X0<(1+B*Y0-B*ymin*X)/(B*Y0-B*ymin)) return 4;
   //   else if (matchArgs(allVars, analVars, Y) && X0>=(1+B*Y0-B*ymin*X)/(B*Y0-B*ymin)) return 5;
   return 0;
}

// //---------------------------------------------------------------------------
Double_t RooRazor2DTail::analyticalIntegral(Int_t code, const char* rangeName) const{

   const Double_t xmin = X.min(rangeName); const Double_t xmax = X.max(rangeName);
   const Double_t ymin = Y.min(rangeName); const Double_t ymax = Y.max(rangeName);

   if(B == 0) return 0.;

   double integral = 0.;
   if(code ==1) { // integral on both X and Y
     integral = fabs(1/B*exp(-B*X0*Y0)*(exp(B*(xmax*(Y0-ymax)+X0*ymax))-
					exp(B*(xmin*(Y0-ymax)+X0*ymax))-
					exp(B*(xmax*(Y0-ymin)+X0*ymin))+
					exp(B*(xmin*(Y0-ymin)+X0*ymin))));
   } else if(code == 2) { // integral on X
     integral = exp(B*(X0-xmax-xmin)*(Y-Y0))*(exp(B*xmin*(Y-Y0))*(X0-xmax)-exp(B*xmax*(Y-Y0))*(X0-xmin));
   } else if(code == 3) { // integral on X
     integral = exp(-1-B*(xmax*Y+X0*Y0))*(exp(B*xmax*Y+B*X0*Y0)+B*exp(1+B*X0*Y+B*xmax*Y0)*(X0-xmax)*(Y-Y0))/(B*(Y-Y0));
   } else if(code == 4) { // integral on Y
     integral = exp(B*(Y0-ymax-ymin)*(X-X0))*(exp(B*ymin*(X-X0))*(Y0-ymax)-exp(B*ymax*(X-X0))*(Y0-ymin));
   } else if(code == 5) {
     integral = exp(-1-B*(ymax*X+Y0*X0))*(exp(B*ymax*X+B*Y0*X0)+B*exp(1+B*Y0*X+B*ymax*X0)*(Y0-ymax)*(X-X0))/(B*(X-X0));
   } else {
     cout << "WARNING IN RooRazor2DTail: integration code is not correct" << endl;
     cout << "                           what are you integrating on?" << endl;
     return 0;
   }
   //   if(!(evaluate()/integral>1.7E-308)) integral = evaluate()/(1.7E-308);

   return integral;
}
// //---------------------------------------------------------------------------

