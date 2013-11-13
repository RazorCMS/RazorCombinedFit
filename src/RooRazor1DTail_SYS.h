//---------------------------------------------------------------------------
#ifndef ROO_Razor1DTail_SYS
#define ROO_Razor1DTail_SYS
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "Riostream.h"
#include "TMath.h"
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"

//---------------------------------------------------------------------------
class RooRazor1DTail_SYS : public RooAbsPdf
{
public:
   RooRazor1DTail_SYS() {} ;
   RooRazor1DTail_SYS(const char *name, const char *title,
		      RooAbsReal &_xy,
		      RooAbsReal &_b, RooAbsReal &_n);
   RooRazor1DTail_SYS(const RooRazor1DTail_SYS& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooRazor1DTail_SYS(*this,newname); }
   inline virtual ~RooRazor1DTail_SYS() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

   RooRealProxy XY;        // dependent variable
   RooRealProxy B;        // shape parameter
   RooRealProxy N;        // shape parameter

   Double_t evaluate() const;
private:
  ClassDef(RooRazor1DTail_SYS,1) // Razor1DTail_SYS function
    
};
//---------------------------------------------------------------------------
#endif
