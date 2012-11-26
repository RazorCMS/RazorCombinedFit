//---------------------------------------------------------------------------
#include "RooFit.h"
#include "Riostream.h"
#include <TMath.h>
#include <cassert>
#include <cmath>

#include "RooRazor2DTurnOn.h"
#include "RooRealVar.h"

ClassImp(RooRazor2DTurnOn)
//---------------------------------------------------------------------------
//this is used in the case where there is only one error histogram
RooRazor2DTurnOn::RooRazor2DTurnOn(const char *name, const char *title,
				   RooAbsReal &_x, 	RooAbsReal &_y,
				   TH2D* _nominal, TH2D* _error,
				   RooAbsReal &_xError) : RooAbsPdf(name, title),
  X("X", "X Observable", this, _x),
  Y("Y", "Y Observable", this, _y),
  xError("xError", "xError", this, _xError),
  Hnonimal(_nominal),
  Herror(_error)
{}


//Reads the histograms from the workspace and/or imports them
Bool_t RooRazor2DTurnOn::importWorkspaceHook(RooWorkspace& ws){
  
  std::cout << "RooRazor2DTurnOn::importWorkspaceHook" << std::endl;
  
  //check if the histograms are in the workspace or not
  if(ws.obj(Hnonimal->GetName()) == 0){
    ws.import(*Hnonimal);
  }
  if(ws.obj(Herror->GetName()) == 0){
    ws.import(*Herror);
  }
  
  //update the pointers to the workspace versions
  Hnonimal = dynamic_cast<TH2D*>(ws.obj(Hnonimal->GetName()));
  Herror = dynamic_cast<TH2D*>(ws.obj(Herror->GetName()));
  return kTRUE;
}


Double_t RooRazor2DTurnOn::evaluate() const
{
  int iBin = Hnonimal->FindBin(X,Y);
  double nomVal = Hnonimal->GetBinContent(iBin);
  double errVal = Herror->GetBinContent(iBin);
 
  double toReturn = nomVal+errVal*xError;
  if(toReturn < 1e-12) return 1e-12;
  if(toReturn > 1.) return 1.;
  return toReturn;
}

// //---------------------------------------------------------------------------
Int_t RooRazor2DTurnOn::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
   return 1;
}

// //---------------------------------------------------------------------------
// This pdf represents a weight in the event (and associated error)
// So it does NOT need to be normalized. Its value represents an
// event-by-event weight 
Double_t RooRazor2DTurnOn::analyticalIntegral(Int_t code, const char* rangeName) const {  
  return 1.;
}
// //---------------------------------------------------------------------------

