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
#include <TH2D.h>
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"

//---------------------------------------------------------------------------
class RooRazor2DSignal : public RooAbsPdf
{
public:
   RooRazor2DSignal(){};
   RooRazor2DSignal(const char *name, const char *title,
		  RooAbsReal &_x, RooAbsReal &_y, 
		  TH2D* _nominal, TH2D* _jes, TH2D* _pdf, TH2D* _btag,
		  RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag);
   TObject* clone(const char* newname) const {
	   TNamed* result = new RooRazor2DSignal(*this);
	   result->SetName(newname);
	   return result;
   }
   ~RooRazor2DSignal() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

   RooRealProxy X;        // dependent variable
   RooRealProxy Y;        // dependent variable
   RooRealProxy xJes;   // xJes
   RooRealProxy xPdf;   // xPdf
   RooRealProxy xBtag;   // xBtag

   TH2D* Hnonimal;
   TH2D* Hjes;
   TH2D* Hpdf;
   TH2D* Hbtag;

   int iBinX;
   int iBinY;

   Double_t evaluate() const;
   Bool_t importWorkspaceHook(RooWorkspace& ws);

private:
  ClassDef(RooRazor2DSignal,1) // Razor2DSignal function
};
//---------------------------------------------------------------------------
#endif
