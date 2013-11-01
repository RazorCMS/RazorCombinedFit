//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <TMath.h>
#include <math.h>

#include "RooRazor1DTail_SYS.h"
#include "RooRealVar.h"

ClassImp(RooRazor1DTail_SYS)
//---------------------------------------------------------------------------
RooRazor1DTail_SYS::RooRazor1DTail_SYS(const char *name, const char *title,
			       RooAbsReal &_xy,
			       RooAbsReal &_b, RooAbsReal &_n) : RooAbsPdf(name, title), 
  XY("XY", "XY Observable", this, _xy),
  B("B", "Shape parameter", this, _b),
  N("N", "Shape parameter", this, _n)
{
}
//---------------------------------------------------------------------------
RooRazor1DTail_SYS::RooRazor1DTail_SYS(const RooRazor1DTail_SYS& other, const char* name) :
   RooAbsPdf(other, name), 
   XY("XY", this, other.XY), 
   B("B", this, other.B),
   N("N", this, other.N)
{
}
//---------------------------------------------------------------------------
Double_t RooRazor1DTail_SYS::evaluate() const
{
  double myexp = B*N*pow(fabs(XY),1./N);
  double mycoeff = B*pow(fabs(XY),1./N) - 1.;
  if(myexp < -700.) {
    //std::cout << "MYEXP = "<< myexp << ", < -700 -- BAD" << std::endl;
    return  1.7e-308;}
  if(mycoeff <= 0.) {
    //std::cout << "MYCOEFF = " << mycoeff <<", IS NEGATIVE -- BAD" << std::endl;
    return  1.7e-308;}
  if(XY <= 0. || B <= 0. || N <= 0.) {
    //std::cout << "PARAMETERS OUT OF PHYSICAL, INTEGRABLE RANGES -- BAD" << std::endl;
    return  1.7e-308;}
  return mycoeff*exp(-myexp);
}

// //---------------------------------------------------------------------------
Int_t RooRazor1DTail_SYS::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
  // integral on XY
  if (matchArgs(allVars, analVars, XY)) return 1;
  // integrating nothing
  return 0;
}

// //---------------------------------------------------------------------------
Double_t RooRazor1DTail_SYS::analyticalIntegral(Int_t code, const char* rangeName) const{

  const Double_t xymin = XY.min(rangeName); const Double_t xymax = XY.max(rangeName);

   if(B <= 0. || N <= 0. || XY <= 0.) return 1.;

   double integral = 0.;
   if(code ==1) { // integral on XY
     integral = xymax*exp(-B*N*pow(xymax,1/N)) - xymin*exp(-B*N*pow(xymin,1/N));
   } else {
     cout << "WARNING IN RooRazor1DTail_SYS: integration code is not correct" << endl;
     cout << "                           what are you integrating on?" << endl;
     return 1.;
   }

   return integral;
}
// //---------------------------------------------------------------------------

