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
		RooAbsReal &_x, RooAbsReal &_y,
		const RooWorkspace& ws,
				   const char* _nominal, const char* _jes, const char* _pdf, const char* _btag,  const char* _lepSF, const char* _ISR,
				   RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag, RooAbsReal &_xLepSF, RooAbsReal &_xISR):
		RooAbsPdf(name, title),
		X("X","X Observable", this, _x),
		Y("Y", "Y Observable", this, _y),
		xJes("xJes", "xJes", this, _xJes	),
		xPdf("xPdf", "xPdf", this, _xPdf),
		xBtag("xBtag", "xBtag", this, _xBtag),
		xLepSF("xLepSF", "xLepSF", this, _xLepSF),
		xISR("xISR", "xISR", this, _xISR),
		Hnominal(0),
		Hjes(0),
		Hpdf(0),
		Hbtag(0),
		HISR(0),
		iBinX(0),
		iBinY(0) {

	//check if the histograms are in the workspace or not
	if(ws.obj(_nominal)){
		Hnominal = dynamic_cast<TH2*>(ws.obj(_nominal));
		iBinX = Hnominal->GetXaxis()->GetNbins();
		iBinY = Hnominal->GetYaxis()->GetNbins();
	}
	if(ws.obj(_jes)){
		Hjes = dynamic_cast<TH2*>(ws.obj(_jes));
	}
	if(ws.obj(_pdf)){
		Hpdf = dynamic_cast<TH2*>(ws.obj(_pdf));
	}
	if(ws.obj(_btag)){
		Hbtag = dynamic_cast<TH2*>(ws.obj(_btag));
	}
	if(ws.obj(_lepSF)){
		HlepSF = dynamic_cast<TH2*>(ws.obj(_lepSF));
	}
	if(ws.obj(_ISR)){
		HISR = dynamic_cast<TH2*>(ws.obj(_ISR));
	}
}

RooRazor2DSignal::RooRazor2DSignal(const RooRazor2DSignal& other, const char* name) :
   RooAbsPdf(other,name),
   X("X",this,other.X),
   Y("Y",this,other.Y),
   xJes("xJes",this,other.xJes),
   xPdf("xPdf",this,other.xPdf),
   xBtag("xBtag",this,other.xBtag),
   xLepSF("xLepSF",this,other.xLepSF),
   xISR("xISR",this,other.xISR),
   Hnominal(other.Hnominal),
   Hjes(other.Hjes),
   Hpdf(other.Hpdf),
   Hbtag(other.Hbtag),
   HlepSF(other.HlepSF),
   HISR(other.HISR),
   iBinX(other.iBinX),
   iBinY(other.iBinY) {
 }


Double_t RooRazor2DSignal::evaluate() const
{
  int xbin = Hnominal->GetXaxis()->FindBin(X);
  int ybin = Hnominal->GetYaxis()->FindBin(Y);

  double nomVal   = Hnominal->GetBinContent(xbin, ybin);
  double jesVal   = Hjes->GetBinContent(xbin, ybin);
  double pdfVal   = Hpdf->GetBinContent(xbin, ybin);
  double btagVal  = Hbtag->GetBinContent(xbin, ybin);
  double lepSFVal = HlepSF->GetBinContent(xbin, ybin);
  double ISRVal   = HISR->GetBinContent(xbin, ybin);
  double rhoJes   = 1.;
  double rhoPdf   = 1.;
  double rhoBtag  = 1.;
  double rhoLepSF = 1.;
  double rhoISR   = 1.;
 
  double dx = Hnominal->GetXaxis()->GetBinWidth(xbin);
  double dy = Hnominal->GetYaxis()->GetBinWidth(ybin);

  double area = dx*dy;

  if(nomVal>0.) {
	//1.0 to the power anything is 1.0, so empty bins don't do anything
    (fabs(jesVal) < 1.0e-10) ? rhoJes  = 1.0 : rhoJes  = pow(1.0 + fabs(jesVal),xJes*TMath::Sign(1.,jesVal));
    (fabs(pdfVal) < 1.0e-10) ? rhoPdf  = 1.0 : rhoPdf  = pow(1.0 + fabs(pdfVal),xPdf*TMath::Sign(1.,pdfVal));
    (fabs(btagVal)< 1.0e-10) ? rhoBtag = 1.0 : rhoBtag = pow(1.0 + fabs(btagVal),xBtag*TMath::Sign(1.,btagVal));
    (fabs(lepSFVal)< 1.0e-10) ? rhoLepSF = 1.0 : rhoLepSF = pow(1.0 + fabs(lepSFVal),xLepSF*TMath::Sign(1.,lepSFVal));
    (fabs(ISRVal)< 1.0e-10) ? rhoISR = 1.0 : rhoISR = pow(1.0 + fabs(ISRVal),xISR*TMath::Sign(1.,ISRVal));
  }
  double result = nomVal*rhoJes*rhoPdf*rhoBtag*rhoLepSF*rhoISR / area;
  return result >= 0. ? result : 0;
  // return (result == 0.0) ? 1.7e-308 : result;
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
    return intPdf;
  }
  else if (code==2){
    // integral over X
    Double_t intPdf = 0.;

    int iy = Hnominal->GetYaxis()->FindBin(Y);
    
    for (int ix = xBinMin; ix <= xBinMax; ix++) {
      intPdf += getBinIntegral2D(xmin,xmax,ymin,ymax,ix,iy, code);
    }
    return intPdf;
  }
  else if (code==3){
    // integral over Y
    Double_t intPdf = 0.;
    
    int ix = Hnominal->GetXaxis()->FindBin(X);

    for (int iy = yBinMin; iy <= yBinMax; iy++) {
      intPdf += getBinIntegral2D(xmin,xmax,ymin,ymax,ix,iy, code);
    }
    return intPdf;
  }
  else {
    cout << "WARNING IN RooRazor2DTaiSignal: integration code is not correct" << endl;
    cout << "                           what are you integrating on?" << endl;
    return 1.;
  }

}
// //---------------------------------------------------------------------------

