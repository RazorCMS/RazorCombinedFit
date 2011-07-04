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
  return (myexp-1)*exp(-myexp);
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

   // integral on both X and Y
   if (matchArgs(allVars, analVars, X, Y)) return 1;
   // // integral over X
   // if (matchArgs(allVars, analVars, X)) return 2;
   // // integral over Y
   // if (matchArgs(allVars, analVars, Y)) return 3;
	return 0;
}

// //---------------------------------------------------------------------------
Double_t RooRazor2DTail::analyticalIntegral(Int_t code, const char* rangeName) const{

   const Double_t xmin = X.min(rangeName); const Double_t xmax = X.max(rangeName);
   const Double_t ymin = Y.min(rangeName); const Double_t ymax = Y.max(rangeName);

   if(B == 0) return 0.;

   return 1/B*exp(-B*X0*Y0)*(exp(B*(xmax*(Y0-ymax)+X0*ymax))-
			     exp(B*(xmin*(Y0-ymax)+X0*ymax))-
			     exp(B*(xmax*(Y0-ymin)+X0*ymin))+
			     exp(B*(xmin*(Y0-ymin)+X0*ymin)));
   
}
// //---------------------------------------------------------------------------

