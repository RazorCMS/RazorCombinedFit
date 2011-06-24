//---------------------------------------------------------------------------
#ifndef ROO_AtLeast
#define ROO_AtLeast
//---------------------------------------------------------------------------
#include "RooConstVar.h"
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;
//---------------------------------------------------------------------------
class RooAtLeast : public RooAbsPdf
{
public:
   RooAtLeast():UpperBound(10000){} ;
   RooAtLeast(const char *name, const char *title,
      RooAbsReal &_x, const RooConstVar& _value);
   RooAtLeast(const RooAtLeast& other, const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooAtLeast(*this,newname); }
   inline virtual ~RooAtLeast() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:
   RooRealProxy X;
   double Value;
   const double UpperBound;
   
   Double_t evaluate() const;
private:
  ClassDef(RooAtLeast,1) // AtLeast function
};
//---------------------------------------------------------------------------
#endif
