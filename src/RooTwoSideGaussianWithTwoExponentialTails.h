//---------------------------------------------------------------------------
#ifndef ROO_TwoSideGaussianWithTwoExponentialTails
#define ROO_TwoSideGaussianWithTwoExponentialTails
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;
//---------------------------------------------------------------------------
class RooTwoSideGaussianWithTwoExponentialTails : public RooAbsPdf
{
public:
   RooTwoSideGaussianWithTwoExponentialTails() {} ;
   RooTwoSideGaussianWithTwoExponentialTails(const char *name, const char *title,
      RooAbsReal &_x, RooAbsReal &_x0,
      RooAbsReal &_sigma_l, RooAbsReal &_sigma_r, RooAbsReal &_s1,
      RooAbsReal &_s2, RooAbsReal &_f);
   RooTwoSideGaussianWithTwoExponentialTails(const RooTwoSideGaussianWithTwoExponentialTails& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooTwoSideGaussianWithTwoExponentialTails(*this,newname); }
   inline virtual ~RooTwoSideGaussianWithTwoExponentialTails() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
   RooRealProxy X;        // dependent variable
   RooRealProxy X0;       // center of gaussian
   RooRealProxy SigmaL;   // width of gaussian
   RooRealProxy SigmaR;   // width of gaussian
   RooRealProxy S1;       // exponent 1 of the tail - has to be greater than zero for now
   RooRealProxy S2;       // exponent 2 of the tail - has to be greater than zero for now
   RooRealProxy F;        // fraction of second component

   Double_t evaluate() const;
private:
  ClassDef(RooTwoSideGaussianWithTwoExponentialTails,1) // TwoSideGaussianWithTwoExponentialTails function
};
//---------------------------------------------------------------------------
#endif
