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
  xBtag("xBtag", "xBtag", this, _xBtag),
  Hnonimal(_nominal),
  Hjes(_jes),
  Hpdf(_pdf),
  Hbtag(_btag),
  iBinX(_nominal->GetXaxis()->GetNbins()),
  iBinY(_nominal->GetYaxis()->GetNbins()){
}

//Reads the histograms from the workspace and/or imports them
Bool_t RooRazor2DSignal::importWorkspaceHook(RooWorkspace& ws){

	std::cout << "RooRazor2DSignal::importWorkspaceHook" << std::endl;

	//check if the histograms are in the workspace or not
	if(ws.obj(Hnonimal->GetName()) == 0){
		ws.import(*Hnonimal);
	}
	if(ws.obj(Hjes->GetName()) == 0){
		ws.import(*Hjes);
	}
	if(ws.obj(Hpdf->GetName()) == 0){
		ws.import(*Hpdf);
	}
	if(ws.obj(Hbtag->GetName()) == 0){
		ws.import(*Hbtag);
	}

	//update the pointers to the workspace versions
	Hnonimal = dynamic_cast<TH2D*>(ws.obj(Hnonimal->GetName()));
	Hjes = dynamic_cast<TH2D*>(ws.obj(Hjes->GetName()));
	Hpdf = dynamic_cast<TH2D*>(ws.obj(Hpdf->GetName()));
	Hbtag = dynamic_cast<TH2D*>(ws.obj(Hbtag->GetName()));

	return kFALSE;

}

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
  Double_t result = nomVal*rhoJes*rhoPdf*rhoBtag;
  //the signal PDF is often empty at low MR. Truncate so we don't get zeros everywhere
  return (result == 0.0) ? 1e-8 : result;
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

