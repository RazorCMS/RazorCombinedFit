//---------------------------------------------------------------------------
#ifndef ROO_TwoSideGaussianWithOneXDependentExponentialWithInverseN
#define ROO_TwoSideGaussianWithOneXDependentExponentialWithInverseN
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;
//---------------------------------------------------------------------------
class RooTwoSideGaussianWithOneXDependentExponentialWithInverseN : public RooAbsPdf
{
public:
   RooTwoSideGaussianWithOneXDependentExponentialWithInverseN() {} ;
   RooTwoSideGaussianWithOneXDependentExponentialWithInverseN(const char *name, const char *title,
      RooAbsReal &_x, RooAbsReal &_x0,
      RooAbsReal &_sigma_l, RooAbsReal &_sigma_r, 
      RooAbsReal &_s1,   RooAbsReal &_a1, RooAbsReal &_n);
   RooTwoSideGaussianWithOneXDependentExponentialWithInverseN(const RooTwoSideGaussianWithOneXDependentExponentialWithInverseN& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooTwoSideGaussianWithOneXDependentExponentialWithInverseN(*this,newname); }
   inline virtual ~RooTwoSideGaussianWithOneXDependentExponentialWithInverseN() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
   RooRealProxy X;        // dependent variable
   RooRealProxy X0;       // center of gaussian
   RooRealProxy SigmaL;   // width of gaussian
   RooRealProxy SigmaR;   // width of gaussian
   RooRealProxy S1;        // coeff. of the exp(-s2*x)/(1+a1*x) tail - has to be greater than zero for now
   RooRealProxy A1;       // denominator coeff. of the exp(-s2*x)/(1+a1*x) 
   RooRealProxy N;        // inverse exponent of denominator of the exp(-s2*x)/((1+a1*x)^(1/n))
  

   Double_t evaluate() const;
private:
  ClassDef(RooTwoSideGaussianWithOneXDependentExponentialWithInverseN,1) // TwoSideGaussianWithOneXDependentExponentialWithInverseN function
};
//---------------------------------------------------------------------------
#endif
