//---------------------------------------------------------------------------
#ifndef ROO_TwoSideGaussianWithThreeExponentialTails
#define ROO_TwoSideGaussianWithThreeExponentialTails
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;
//---------------------------------------------------------------------------
class RooTwoSideGaussianWithThreeExponentialTails : public RooAbsPdf
{
public:
   RooTwoSideGaussianWithThreeExponentialTails() {} ;
   RooTwoSideGaussianWithThreeExponentialTails(const char *name, const char *title,
      RooAbsReal &_x, RooAbsReal &_x0,
      RooAbsReal &_sigma_l, RooAbsReal &_sigma_r, RooAbsReal &_s1,  RooAbsReal &_s2,  RooAbsReal &_s3, 
      RooAbsReal &_f1, RooAbsReal &_f2);
   RooTwoSideGaussianWithThreeExponentialTails(const RooTwoSideGaussianWithThreeExponentialTails& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooTwoSideGaussianWithThreeExponentialTails(*this,newname); }
   inline virtual ~RooTwoSideGaussianWithThreeExponentialTails() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
   RooRealProxy X;        // dependent variable
   RooRealProxy X0;       // center of gaussian
   RooRealProxy SigmaL;   // width of gaussian
   RooRealProxy SigmaR;   // width of gaussian
   RooRealProxy S1;        // coeff. of the 1st exp(-s1*x) tail - has to be greater than zero for now
   RooRealProxy S2;        // coeff. of the exp(-s2*x) tail - has to be greater than zero for now
   RooRealProxy S3;        // coeff. of the exp(-s3*x) tail - has to be greater than zero for now
   RooRealProxy F1;        // fraction of the 2nd exp(-x) tail 
   RooRealProxy F2;        // fraction of the 3rd exp(-x) tail 

   Double_t evaluate() const;
private:
  ClassDef(RooTwoSideGaussianWithThreeExponentialTails,1) // TwoSideGaussianWithThreeExponentialTails function
};
//---------------------------------------------------------------------------
#endif
