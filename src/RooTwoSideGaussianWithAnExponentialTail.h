//---------------------------------------------------------------------------
#ifndef ROO_TwoSideGaussianWithAnExponentialTail
#define ROO_TwoSideGaussianWithAnExponentialTail
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;
//---------------------------------------------------------------------------
class RooTwoSideGaussianWithAnExponentialTail : public RooAbsPdf
{
public:
   RooTwoSideGaussianWithAnExponentialTail() {} ;
   RooTwoSideGaussianWithAnExponentialTail(const char *name, const char *title,
      RooAbsReal &_x, RooAbsReal &_x0,
      RooAbsReal &_sigma_l, RooAbsReal &_sigma_r, RooAbsReal &_x);
   RooTwoSideGaussianWithAnExponentialTail(const RooTwoSideGaussianWithAnExponentialTail& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooTwoSideGaussianWithAnExponentialTail(*this,newname); }
   inline virtual ~RooTwoSideGaussianWithAnExponentialTail() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
   RooRealProxy X;        // dependent variable
   RooRealProxy X0;       // center of gaussian
   RooRealProxy SigmaL;   // width of gaussian
   RooRealProxy SigmaR;   // width of gaussian
   RooRealProxy S;        // exponent of the tail - has to be greater than zero for now

   Double_t evaluate() const;
private:
  ClassDef(RooTwoSideGaussianWithAnExponentialTail,1) // TwoSideGaussianWithAnExponentialTail function
};
//---------------------------------------------------------------------------
#endif
