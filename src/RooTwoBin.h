//---------------------------------------------------------------------------
#ifndef ROO_TwoBin
#define ROO_TwoBin
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
class RooTwoBin : public RooAbsPdf
{
public:
   RooTwoBin() {} ;
   RooTwoBin(const char *name, const char *title, RooAbsReal &_x, RooAbsReal &_x0);
   RooTwoBin(const RooTwoBin& other, const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooTwoBin(*this,newname); }
   inline virtual ~RooTwoBin() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

   RooRealProxy X;        // dependent variable
   RooRealProxy X0;       // 

   Double_t evaluate() const;
private:
  ClassDef(RooTwoBin,1) // Razor2DTail function
};
//---------------------------------------------------------------------------
#endif
