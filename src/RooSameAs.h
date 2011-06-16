//---------------------------------------------------------------------------
#ifndef ROO_SameAs
#define ROO_SameAs
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;
//---------------------------------------------------------------------------
class RooSameAs : public RooAbsPdf
{
public:
   RooSameAs() {} ;
   RooSameAs(const char *name, const char *title,
      RooAbsReal &_x, double _value, double _tolerance = 0.5);
   RooSameAs(const RooSameAs& other, const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooSameAs(*this,newname); }
   inline virtual ~RooSameAs() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
   RooRealProxy X;
   double Value;
   double Tolerance;

   Double_t evaluate() const;
private:
  ClassDef(RooSameAs,1) // SameAs function
};
//---------------------------------------------------------------------------
#endif
