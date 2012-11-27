//---------------------------------------------------------------------------
#ifndef ROO_Razor2DTurnOn
#define ROO_Razor2DTurnOn
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
class RooRazor2DTurnOn : public RooAbsPdf
{
 public:
  RooRazor2DTurnOn(){};
  RooRazor2DTurnOn(const char *name, const char *title,
		   RooAbsReal &_x, RooAbsReal &_y,
		   TH2D* _nominal, TH2D* _error,
		   RooAbsReal &_xError);
  TObject* clone(const char* newname) const {
    TNamed* result = new RooRazor2DTurnOn(*this);
    result->SetName(newname);
    return result;
  }
  ~RooRazor2DTurnOn() { }

  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
  Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

 protected:

  RooRealProxy X;        // dependent variable
  RooRealProxy Y;        // dependent variable
  RooRealProxy xError;   // error nuisance parameter
  
   TH2D* Hnonimal;
   TH2D* Herror;

   Double_t evaluate() const;
   Bool_t importWorkspaceHook(RooWorkspace& ws);

private:
  ClassDef(RooRazor2DTurnOn,1) // Razor2DTurnOn function
};
//---------------------------------------------------------------------------
#endif
