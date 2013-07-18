//---------------------------------------------------------------------------
#ifndef ROO_TwoSideGaussianWithOneExponentialTailAndOneXDependentExponential
#define ROO_TwoSideGaussianWithOneExponentialTailAndOneXDependentExponential
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;
//---------------------------------------------------------------------------
class RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential : public RooAbsPdf
{
public:
   RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential() {} ;
   RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential(const char *name, const char *title,
      RooAbsReal &_x, RooAbsReal &_x0,
      RooAbsReal &_sigma_l, RooAbsReal &_sigma_r, RooAbsReal &_s1,  RooAbsReal &_s2,  RooAbsReal &_a1, 
      RooAbsReal &_f1);
   RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential(const RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential(*this,newname); }
   inline virtual ~RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
   RooRealProxy X;        // dependent variable
   RooRealProxy X0;       // center of gaussian
   RooRealProxy SigmaL;   // width of gaussian
   RooRealProxy SigmaR;   // width of gaussian
   RooRealProxy S1;        // coeff. of the 1st exp(-s1*x) tail - has to be greater than zero for now
   RooRealProxy S2;        // coeff. of the exp(-s2*x)/(1+a1*x) tail - has to be greater than zero for now
   RooRealProxy A1;       // denominator coeff. of the exp(-s2*x)/(1+a1*x) 
   RooRealProxy F1;        // fraction of the 2nd exp(-s2*x)/(1+a1*x) tail 
 

   Double_t evaluate() const;
private:
  ClassDef(RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential,1) // TwoSideGaussianWithOneExponentialTailAndOneXDependentExponential function
};
//---------------------------------------------------------------------------
#endif
