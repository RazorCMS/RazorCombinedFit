//---------------------------------------------------------------------------
#include "RooFit.h"
#include "Riostream.h"
#include <TMath.h>
#include <cassert>
#include <cmath>

#include "RooRazor3DSignal.h"
#include "RooRealVar.h"

ClassImp(RooRazor3DSignal)
//---------------------------------------------------------------------------
RooRazor3DSignal::RooRazor3DSignal(const char *name, const char *title,
				   RooAbsReal &_x, 	RooAbsReal &_y,     RooAbsReal &_z,
				   const RooWorkspace& ws,
				   const char* _nominal, const char* _jes, const char* _pdf, const char* _btag,
				   RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag) : RooAbsPdf(name, title), 
  X("X", "X Observable", this, _x),
  Y("Y", "Y Observable", this, _y),
  Z("Z", "Z Observable", this, _z),
  xJes("xJes", "xJes", this, _xJes),
  xPdf("xPdf", "xPdf", this, _xPdf),
  xBtag("xBtag", "xBtag", this, _xBtag),
  Hnominal(0),
  Hjes(0),
  Hpdf(0),
  Hbtag(0),
  iBinX(0),
  iBinY(0),
  iBinZ(0)
{
  //check if the histograms are in the workspace or not
  if(ws.obj(_nominal)){
    Hnominal = dynamic_cast<TH3*>(ws.obj(_nominal));
    iBinX = Hnominal->GetXaxis()->GetNbins();
    iBinY = Hnominal->GetYaxis()->GetNbins();
    iBinZ = Hnominal->GetZaxis()->GetNbins();
  }
  if(ws.obj(_jes)){
    Hjes = dynamic_cast<TH3*>(ws.obj(_jes));
  }
  if(ws.obj(_pdf)){
    Hpdf = dynamic_cast<TH3*>(ws.obj(_pdf));
  }
  if(ws.obj(_btag)){
    Hbtag = dynamic_cast<TH3*>(ws.obj(_btag));
  }
}
RooRazor3DSignal::RooRazor3DSignal(const RooRazor3DSignal& other, const char* name) :
   RooAbsPdf(other, name), 
   X("X", this, other.X), 
   Y("Y", this, other.Y), 
   Z("Z", this, other.Z),
   xJes("xJes", this, other.xJes),
   xPdf("xPdf", this, other.xPdf),
   xBtag("xBtag", this, other.xBtag),
   Hnominal(other.Hnominal),
   Hjes(other.Hjes),
   Hpdf(other.Hpdf),
   Hbtag(other.Hbtag),
   iBinX(other.iBinX),
   iBinY(other.iBinY),
   iBinZ(other.iBinZ)
{
}
Double_t RooRazor3DSignal::evaluate() const
{
  int xbin = Hnominal->GetXaxis()->FindBin(X);
  int ybin = Hnominal->GetYaxis()->FindBin(Y);
  int zbin = Hnominal->GetZaxis()->FindBin(Z);

  double nomVal = Hnominal->GetBinContent(xbin, ybin, zbin);
  double jesVal = Hjes->GetBinContent(xbin, ybin, zbin);
  double pdfVal = Hpdf->GetBinContent(xbin, ybin, zbin);
  double btagVal = Hbtag->GetBinContent(xbin, ybin, zbin);
  double rhoJes = 1.;
  double rhoPdf = 1.;
  double rhoBtag = 1.;
  
  double dx = Hnominal->GetXaxis()->GetBinWidth(xbin);
  double dy = Hnominal->GetYaxis()->GetBinWidth(ybin);
  double dz = Hnominal->GetZaxis()->GetBinWidth(zbin);

  double volume = dx*dy*dz;
  
  if(nomVal>0.) {
	//1.0 to the power anything is 1.0, so empty bins don't do anything
    rhoJes = pow(1.0 + fabs(jesVal),xJes*jesVal/fabs(jesVal));
    rhoPdf = pow(1.0 + fabs(pdfVal),xPdf*pdfVal/fabs(pdfVal));
    rhoBtag = pow(1.0 + fabs(btagVal),xBtag*btagVal/fabs(btagVal));
  }
  double result = nomVal*rhoJes*rhoPdf*rhoBtag/volume;
  return result >= 0. ? result : 0;
}

// //---------------------------------------------------------------------------
Int_t RooRazor3DSignal::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
  // integral on all X Y and Z
  if (matchArgs(allVars, analVars, X, Y, Z)) return 1;
  // integral on both X and Y
  else if (matchArgs(allVars, analVars, X, Y)) return 2;
  // integral on both Y and Z
  else if (matchArgs(allVars, analVars, Y, Z)) return 3;
  // integral on both X and Z
  else if (matchArgs(allVars, analVars, X, Z)) return 4;
  // integral over X
  else if (matchArgs(allVars, analVars, X)) return 5;
  // integral over Y
  else if (matchArgs(allVars, analVars, Y)) return 6;
  // integral over Z
  else if (matchArgs(allVars, analVars, Z)) return 7;
  // integrating nothing
  return 0;
}


// //---------------------------------------------------------------------------
Double_t RooRazor3DSignal::analyticalIntegral(Int_t code, const char* rangeName) const {
  const Double_t xmin = X.min(rangeName);
  const Double_t xmax = X.max(rangeName);
  const Double_t ymin = Y.min(rangeName);
  const Double_t ymax = Y.max(rangeName);
  const Double_t zmin = Z.min(rangeName);
  const Double_t zmax = Z.max(rangeName);

  int xBinMin = Hnominal->GetXaxis()->FindBin(xmin);
  int xBinMax = Hnominal->GetXaxis()->FindBin(xmax);
  int yBinMin = Hnominal->GetYaxis()->FindBin(ymin);
  int yBinMax = Hnominal->GetYaxis()->FindBin(ymax);
  int zBinMin = Hnominal->GetZaxis()->FindBin(zmin);
  int zBinMax = Hnominal->GetZaxis()->FindBin(zmax);

  if (code==1){
    // integral on all X Y and Z
    Double_t intPdf = 0.;
    
    for (int ix = xBinMin; ix <= xBinMax; ix++) {
      for (int iy = yBinMin; iy <= yBinMax; iy++) {
	for (int iz = zBinMin; iz <= zBinMax; iz++) {
	  intPdf += getBinIntegral3D(xmin,xmax,ymin,ymax,zmin,zmax,ix,iy,iz, code);
	}
      }
    }
    return  intPdf;
  }
  else if (code==2){
    // integral on both X and Y
    Double_t intPdf = 0.;

    int iz = Hnominal->GetZaxis()->FindBin(Z);
    
    for (int ix = xBinMin; ix <= xBinMax; ix++) {
      for (int iy = yBinMin; iy <= yBinMax; iy++) {
	intPdf += getBinIntegral3D(xmin,xmax,ymin,ymax,zmin,zmax,ix,iy,iz, code);
      }
    }
    return  intPdf;
  }
  else if (code==3){
    // integral on both Y and Z
    Double_t intPdf = 0.;
    
    int ix = Hnominal->GetXaxis()->FindBin(X);

    for (int iy = yBinMin; iy <= yBinMax; iy++) {
      for (int iz = zBinMin; iz <= zBinMax; iz++) {
	intPdf += getBinIntegral3D(xmin,xmax,ymin,ymax,zmin,zmax,ix,iy,iz, code);
      }
    }
    return  intPdf;
  }
  else if (code==4){
    // integral on all both X and Z
    Double_t intPdf = 0.;

    int iy = Hnominal->GetYaxis()->FindBin(Y);
    
    for (int ix = xBinMin; ix <= xBinMax; ix++) {
      for (int iz = zBinMin; iz <= zBinMax; iz++) {
	intPdf += getBinIntegral3D(xmin,xmax,ymin,ymax,zmin,zmax,ix,iy,iz, code);
      }
    }
    return  intPdf;
  }
  else if (code==5){
    // integral over X
    Double_t intPdf = 0.;

    int iy = Hnominal->GetYaxis()->FindBin(Y);
    int iz = Hnominal->GetZaxis()->FindBin(Z);
    
    for (int ix = xBinMin; ix <= xBinMax; ix++) {
      intPdf += getBinIntegral3D(xmin,xmax,ymin,ymax,zmin,zmax,ix,iy,iz, code);
    }
    return  intPdf;
  }
  else if (code==6){
    // integral over Y
    Double_t intPdf = 0.;
    
    int ix = Hnominal->GetXaxis()->FindBin(X);
    int iz = Hnominal->GetZaxis()->FindBin(Z);

    for (int iy = yBinMin; iy <= yBinMax; iy++) {
      intPdf += getBinIntegral3D(xmin,xmax,ymin,ymax,zmin,zmax,ix,iy,iz, code);
    }
    return  intPdf;
  }
  else if (code==7){
    // integral over Z
    Double_t intPdf = 0.;

    int ix = Hnominal->GetXaxis()->FindBin(X);
    int iy = Hnominal->GetYaxis()->FindBin(Y);
    
    for (int iz = zBinMin; iz <= zBinMax; iz++) {
      intPdf += getBinIntegral3D(xmin,xmax,ymin,ymax,zmin,zmax,ix,iy,iz, code);
    }
    return  intPdf;
  }
  else {
    cout << "WARNING IN RooRazor3DTaiSignal: integration code is not correct" << endl;
    cout << "                           what are you integrating on?" << endl;
    return 1.;
  }

}
// //---------------------------------------------------------------------------

