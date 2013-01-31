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
  Hnominal(_nominal),
  Hjes(_jes),
  Hpdf(_pdf),
  Hbtag(_btag),
  iBinX(_nominal->GetXaxis()->GetNbins()),
  iBinY(_nominal->GetYaxis()->GetNbins()){
}

RooRazor2DSignal::RooRazor2DSignal(const RooRazor2DSignal& other, const char* name) :
   RooAbsPdf(other, name), 
   X("X", this, other.X), 
   Y("Y", this, other.Y), 
   xJes("xJes", this, other.xJes),
   xPdf("xPdf", this, other.xPdf),
   xBtag("xBtag", this, other.xBtag),
   Hnominal(other.Hnominal),
   Hjes(other.Hjes),
   Hpdf(other.Hpdf),
   Hbtag(other.Hbtag),
   iBinX(other.iBinX),
   iBinY(other.iBinY)
{
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
  Hnominal(_nominal),
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
	if(ws.obj(Hnominal->GetName()) == 0){
		ws.import(*Hnominal);
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
	Hnominal = dynamic_cast<TH2D*>(ws.obj(Hnominal->GetName()));
	Hjes = dynamic_cast<TH2D*>(ws.obj(Hjes->GetName()));
	Hpdf = dynamic_cast<TH2D*>(ws.obj(Hpdf->GetName()));
	Hbtag = dynamic_cast<TH2D*>(ws.obj(Hbtag->GetName()));

	return false;
}


Double_t RooRazor2DSignal::evaluate() const
{
  int xbin = Hnominal->GetXaxis()->FindBin(X);
  int ybin = Hnominal->GetYaxis()->FindBin(Y);

  double nomVal = Hnominal->GetBinContent(xbin, ybin);
  double jesVal = Hjes->GetBinContent(xbin, ybin);
  double pdfVal = Hpdf->GetBinContent(xbin, ybin);
  double btagVal = Hbtag->GetBinContent(xbin, ybin);
  double rhoJes = 1.;
  double rhoPdf = 1.;
  double rhoBtag = 1.;
 
  double dx = Hnominal->GetXaxis()->GetBinWidth(xbin);
  double dy = Hnominal->GetYaxis()->GetBinWidth(ybin);

  double area = dx*dy;

  if(nomVal>0.) {
	//1.0 to the power anything is 1.0, so empty bins don't do anything
    rhoJes = pow(1.0 + jesVal,xJes);
    rhoPdf = pow(1.0 + pdfVal,xPdf);
    rhoBtag = pow(1.0 + btagVal,xBtag);
  }
  double result = nomVal*rhoJes*rhoPdf*rhoBtag / area;
  return (result == 0.0) ? 1.7e-308 : result;
}

// //---------------------------------------------------------------------------
Int_t RooRazor2DSignal::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{  
  // integral on both X and Y
  if (matchArgs(allVars, analVars, X, Y)) return 1;
  // integral over X
  else if (matchArgs(allVars, analVars, X)) return 2;
  // integral over Y
  else if (matchArgs(allVars, analVars, Y)) return 3;
  // integrating nothing
  return 0;
}


// //---------------------------------------------------------------------------
Double_t RooRazor2DSignal::analyticalIntegral(Int_t code, const char* rangeName) const {
  const Double_t xmin = X.min(rangeName);
  const Double_t xmax = X.max(rangeName);
  const Double_t ymin = Y.min(rangeName);
  const Double_t ymax = Y.max(rangeName);

  int xBinMin = Hnominal->GetXaxis()->FindBin(xmin);
  int xBinMax = Hnominal->GetXaxis()->FindBin(xmax);
  int yBinMin = Hnominal->GetYaxis()->FindBin(ymin);
  int yBinMax = Hnominal->GetYaxis()->FindBin(ymax);

  if (code==1){
    // integral on both X and Y
    Double_t intPdf = 0.;
    
    for (int ix = xBinMin; ix <= xBinMax; ix++) {
      for (int iy = yBinMin; iy <= yBinMax; iy++) {
	  intPdf += getBinIntegral2D(xmin,xmax,ymin,ymax,ix,iy,code);
      }
    }
    return  (intPdf == 0.0) ? 1 : intPdf;
  }
  else if (code==2){
    // integral over X
    Double_t intPdf = 0.;

    int iy = Hnominal->GetYaxis()->FindBin(Y);
    
    for (int ix = xBinMin; ix <= xBinMax; ix++) {
      intPdf += getBinIntegral2D(xmin,xmax,ymin,ymax,ix,iy, code);
    }
    return  (intPdf == 0.0) ? 1 : intPdf;
  }
  else if (code==3){
    // integral over Y
    Double_t intPdf = 0.;
    
    int ix = Hnominal->GetXaxis()->FindBin(X);

    for (int iy = yBinMin; iy <= yBinMax; iy++) {
      intPdf += getBinIntegral2D(xmin,xmax,ymin,ymax,ix,iy, code);
    }
    return  (intPdf == 0.0) ? 1 : intPdf;
  }
  else {
    cout << "WARNING IN RooRazor2DTaiSignal: integration code is not correct" << endl;
    cout << "                           what are you integrating on?" << endl;
    return 1.;
  }

}
// //---------------------------------------------------------------------------

