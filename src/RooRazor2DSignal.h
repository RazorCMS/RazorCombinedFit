//---------------------------------------------------------------------------
#ifndef ROO_Razor2DSignal
#define ROO_Razor2DSignal
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooWorkspace.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "TMath.h"
#include <TH2.h>
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"

//---------------------------------------------------------------------------
class RooRazor2DSignal : public RooAbsPdf
{
public:
   RooRazor2DSignal(){};
   RooRazor2DSignal(const char *name, const char *title,
		  RooAbsReal &_x, RooAbsReal &_y,
		  const RooWorkspace& ws,
		  const char* _nominal, const char* _jes, const char* _pdf, const char* _btag,
		  RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag);

   RooRazor2DSignal(const RooRazor2DSignal& other, const char* name);
   TObject* clone(const char* newname) const {
	   TNamed* result = new RooRazor2DSignal(*this, newname);
	   return result;
   }
   virtual ~RooRazor2DSignal(){
   }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

   RooRealProxy X;        // dependent variable
   RooRealProxy Y;        // dependent variable
   RooRealProxy xJes;   // xJes
   RooRealProxy xPdf;   // xPdf
   RooRealProxy xBtag;   // xBtag

   TH2* Hnonimal;
   TH2* Hjes;
   TH2* Hpdf;
   TH2* Hbtag;

   int iBinX;
   int iBinY;

   Double_t evaluate() const;

private:
  ClassDef(RooRazor2DSignal,1) // Razor2DSignal function
};
//---------------------------------------------------------------------------
#endif
