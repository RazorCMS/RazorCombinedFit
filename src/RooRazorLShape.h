//---------------------------------------------------------------------------
#ifndef ROO_RazorLShape
#define ROO_RazorLShape
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
class RooRazorLShape : public RooAbsPdf
{
public:
   RooRazorLShape() {} ;
   RooRazorLShape(const char *name, const char *title,
		  RooAbsReal &_x, RooAbsReal &_y, 
		  RooAbsReal &_x0, RooAbsReal &_y0);
   RooRazorLShape(const RooRazorLShape& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooRazorLShape(*this,newname); }
   inline virtual ~RooRazorLShape() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

   RooRealProxy X;        // dependent variable
   RooRealProxy Y;        // dependent variable
   RooRealProxy X0;       // X offset
   RooRealProxy Y0;       // Y offset

   Double_t evaluate() const;
private:
  ClassDef(RooRazorLShape,1) // RazorLShape function
};
//---------------------------------------------------------------------------
#endif
