//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <TMath.h>
#include <math.h>
#include <TH2D.h>

#include "RooRazor2DSignal.h"
#include "RooRealVar.h"

ClassImp(RooRazor2DSignal)
//---------------------------------------------------------------------------
RooRazor2DSignal::RooRazor2DSignal(const char *name, const char *title,
				   RooAbsReal &_x, 	RooAbsReal &_y, 
				   TH2D* _nominal, TH2D* _jes, TH2D* _pdf, TH2D* _btag,
				   RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag) : RooAbsPdf(name, title), 
  X("X", "X Observable", this, _x),
  Y("Y", "Y Observable", this, _y),
  xJes("xJes", "xJes", this, _xJes),
  xPdf("xPdf", "xPdf", this, _xPdf),
  xBtag("xBtag", "xBtag", this, _xBtag)
{
  Hnonimal = _nominal;
  Hjes = _jes;
  Hpdf = _pdf;
  Hbtag = _btag;
  iBinX = Hnonimal->GetXaxis()->GetNbins();
  iBinY = Hnonimal->GetYaxis()->GetNbins();
}
//---------------------------------------------------------------------------
/*
RooRazor2DSignal::RooRazor2DSignal(const RooRazor2DSignal& other, const char* name) :
   RooAbsPdf(other, name), 
   X("X", this, other.X), 
   Y("Y", this, other.Y), 
   X0("X0", this, other.X0),
   Y0("Y0", this, other.Y0),
   B("B", this, other.B)
{
}
*/
//---------------------------------------------------------------------------

Double_t RooRazor2DSignal::evaluate() const
{
  int iBin = Hnonimal->FindBin(X,Y);
  double nomVal = Hnonimal->GetBinContent(iBin);
  double jesVal = Hjes->GetBinContent(iBin);
  double pdfVal = Hpdf->GetBinContent(iBin);
  double btagVal = Hbtag->GetBinContent(iBin);
  double rhoJes = 1.;
  double rhoPdf = 1.;
  double rhoBtag = 1.;
  if(nomVal>0.) {
    rhoJes = pow(1.+jesVal,xJes);
    rhoPdf = pow(1.+pdfVal,xPdf);
    rhoBtag = pow(1.+btagVal,xBtag);
  }
  return nomVal*rhoJes*rhoPdf*rhoBtag;
}

// //---------------------------------------------------------------------------
Int_t RooRazor2DSignal::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
   return 0;
}

// //---------------------------------------------------------------------------
Double_t RooRazor2DSignal::analyticalIntegral(Int_t code, const char* rangeName) const{
  Double_t intPdf = 0.;
  for(int ix =1; ix<=iBinX; ix++) {
    for(int iy =1; iy<=iBinY; iy++) {
      intPdf +=  Hnonimal->GetBinContent(ix,iy)*
	pow(Hjes->GetBinContent(ix,iy),xJes)*
	pow(Hpdf->GetBinContent(ix,iy),xPdf)*
	pow(Hbtag->GetBinContent(ix,iy),xBtag);
    }
  }
   return intPdf;
}
// //---------------------------------------------------------------------------

