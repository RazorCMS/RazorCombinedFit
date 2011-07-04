//---------------------------------------------------------------------------
#ifndef ROO_Razor2DTail
#define ROO_Razor2DTail
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "TMath.h"
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"

//---------------------------------------------------------------------------
class RooRazor2DTail : public RooAbsPdf
{
public:
   RooRazor2DTail() {} ;
   RooRazor2DTail(const char *name, const char *title,
		  RooAbsReal &_x, RooAbsReal &_y, 
		  RooAbsReal &_x0, RooAbsReal &_y0,
		  RooAbsReal &_b);
   RooRazor2DTail(const RooRazor2DTail& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooRazor2DTail(*this,newname); }
   inline virtual ~RooRazor2DTail() { }

#if 0
   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;
#endif

protected:

   Double_t Chop(const Double_t x) const{
	   return (TMath::Abs(x - 0) < 1e-10) ? TMath::Sign(0.0,x) : x;
   }
   Double_t Power(const Double_t x, const Double_t y) const{
	   return Chop(TMath::Power(x,y));
   }
   Double_t Gamma(const Double_t a, const Double_t x) const{
	   return Chop(ROOT::Math::inc_gamma(a,x));
   }
   Double_t ExpIntegralEi(const Double_t z) const{
	   return Chop(ROOT::Math::expint(z));
   }


   RooRealProxy X;        // dependent variable
   RooRealProxy Y;        // dependent variable
   RooRealProxy X0;       // X offset
   RooRealProxy Y0;       // Y offset
   RooRealProxy B;        // shape parameter

   Double_t evaluate() const;
private:
  ClassDef(RooRazor2DTail,1) // Razor2DTail function
};
//---------------------------------------------------------------------------
#endif
