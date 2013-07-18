//---------------------------------------------------------------------------
#ifndef RooTwoSideGaussianWithOneExponentialTailAndOneInverseN
#define RooTwoSideGaussianWithOneExponentialTailAndOneInverseN
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;
//---------------------------------------------------------------------------
class RooTwoSideGaussianWithOneExponentialTailAndOneInverseN : public RooAbsPdf
{
public:
   RooTwoSideGaussianWithOneExponentialTailAndOneInverseN() {} ;
   RooTwoSideGaussianWithOneExponentialTailAndOneInverseN(const char *name, const char *title,
      RooAbsReal &_x, RooAbsReal &_x0,
      RooAbsReal &_sigma_l, RooAbsReal &_sigma_r, RooAbsReal &_s1,  RooAbsReal &_s2,  RooAbsReal &_n, 
      RooAbsReal &_f1);
   RooTwoSideGaussianWithOneExponentialTailAndOneInverseN(const RooTwoSideGaussianWithOneExponentialTailAndOneInverseN& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooTwoSideGaussianWithOneExponentialTailAndOneInverseN(*this,newname); }
   inline virtual ~RooTwoSideGaussianWithOneExponentialTailAndOneInverseN() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
   RooRealProxy X;        // dependent variable
   RooRealProxy X0;       // center of gaussian
   RooRealProxy SigmaL;   // width of gaussian
   RooRealProxy SigmaR;   // width of gaussian
   RooRealProxy S1;        // coeff. of the 1st exp(-s1*x) tail - has to be greater than zero for now
   RooRealProxy S2;        // coeff. of the exp(-s2*x) tail - has to be greater than zero for now
   RooRealProxy N;       //fix this commenting
   RooRealProxy F1;        // fraction of the 2nd exp(-x) tail 
 

   Double_t evaluate() const;
private:
  ClassDef(RooTwoSideGaussianWithOneExponentialTailAndOneInverseN,1) // TwoSideGaussianWithOneExponentialTailAndOneInverseN function
};
//---------------------------------------------------------------------------
#endif
