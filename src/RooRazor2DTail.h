//---------------------------------------------------------------------------
#ifndef ROO_Razor2DTail
#define ROO_Razor2DTail
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;
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

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
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
