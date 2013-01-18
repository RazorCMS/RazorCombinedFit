//---------------------------------------------------------------------------
#include "RooFit.h"
#include "Riostream.h"
#include <TMath.h>
#include <cassert>
#include <cmath>

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

//this is used in the case where there is only one error histogram
RooRazor2DSignal::RooRazor2DSignal(const char *name, const char *title,
				   RooAbsReal &_x, 	RooAbsReal &_y,
				   TH2D* _nominal, TH2D* _error,
				   RooAbsReal &_xError) : RooAbsPdf(name, title),
  X("X", "X Observable", this, _x),
  Y("Y", "Y Observable", this, _y),
  xJes("xError", "xError", this, _xError),
  xPdf("xDummy1", "Dummy 1", this, _xError),
  xBtag("xDummy2", "Dummy 2", this, _xError),
  Hnonimal(_nominal),
  Hjes(_error),
  Hpdf(dynamic_cast<TH2D*>(_error->Clone())),
  Hbtag(dynamic_cast<TH2D*>(_error->Clone())),
  iBinX(_nominal->GetXaxis()->GetNbins()),
  iBinY(_nominal->GetYaxis()->GetNbins()){
	Hpdf->Reset();//set to zero
	Hbtag->Reset();//set to zero
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

	return false;
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
 
  int xbin = Hnonimal->GetXaxis()->FindBin(X);
  int ybin = Hnonimal->GetYaxis()->FindBin(Y);
  double dx = Hnonimal->GetXaxis()->GetBinWidth(xbin);
  double dy = Hnonimal->GetYaxis()->GetBinWidth(ybin);

  double area = dx*dy;

  if(nomVal>0.) {
	//1.0 to the power anything is 1.0, so empty bins don't do anything
    rhoJes = pow(1.0 + jesVal,xJes);
    rhoPdf = pow(1.0 + pdfVal,xPdf);
    rhoBtag = pow(1.0 + btagVal,xBtag);
  }
  double result = nomVal*rhoJes*rhoPdf*rhoBtag / area;
  return (result == 0.0) ? 1e-120 : result;
}

// //---------------------------------------------------------------------------
Int_t RooRazor2DSignal::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
   return 1;
}


// //---------------------------------------------------------------------------
	Double_t RooRazor2DSignal::analyticalIntegral(Int_t code, const char* rangeName) const {

		assert(code == 1);

		Double_t intPdf = 0.;
		const Double_t xmin = X.min(rangeName);
		const Double_t xmax = X.max(rangeName);
		const Double_t ymin = Y.min(rangeName);
		const Double_t ymax = Y.max(rangeName);

		for (int ix = 1; ix <= iBinX; ix++) {
			for (int iy = 1; iy <= iBinY; iy++) {
				double nom = Hnonimal->GetBinContent(ix, iy);
				double jes = pow(1.0 + Hjes->GetBinContent(ix, iy), xJes);
				double pdf = pow(1.0 + Hpdf->GetBinContent(ix, iy), xPdf);
				double btag = pow(1.0 + Hbtag->GetBinContent(ix, iy), xBtag);
				intPdf += nom * jes * pdf * btag;
			}
		}

		return intPdf / ((xmax - xmin) * (ymax - ymin));
	}
// //---------------------------------------------------------------------------

