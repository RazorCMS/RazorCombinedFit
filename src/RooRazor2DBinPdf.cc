//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <TMath.h>
#include <cassert>
#include <cmath>
#include <math.h>

#include "RooRazor2DBinPdf.h"
#include "RooRealVar.h"

ClassImp(RooRazor2DBinPdf)
//---------------------------------------------------------------------------
RooRazor2DBinPdf::RooRazor2DBinPdf(const char *name, const char *title,
				   RooAbsReal& _th1x,
				   RooAbsReal& _x0, RooAbsReal& _y0,
				   RooAbsReal& _b, RooAbsReal& _n,
				   RooAbsReal& _xCut, RooAbsReal& _yCut,
				   TH2* _Hnominal) : RooAbsPdf(name, title),
  th1x("th1x", "th1x Observable", this, _th1x),
  X0("X0", "X Offset", this, _x0),
  Y0("Y0", "Y Offset", this, _y0),
  B("B", "B Shape parameter", this, _b),
  N("N", "N Shape parameter", this, _n),
  xCut("xCut", "X Cut parameter",this, _xCut),
  yCut("yCut", "Y Cut parameter",this, _yCut),
  xBins(0),
  yBins(0),
  xMax(0),
  yMax(0),
  xMin(0),
  yMin(0)
{
  xBins = _Hnominal->GetXaxis()->GetNbins();
  yBins = _Hnominal->GetYaxis()->GetNbins();
  xMin = _Hnominal->GetXaxis()->GetBinLowEdge(1);
  yMin = _Hnominal->GetYaxis()->GetBinLowEdge(1);
  xMax = _Hnominal->GetXaxis()->GetBinUpEdge(xBins);
  yMax = _Hnominal->GetYaxis()->GetBinUpEdge(yBins);
  memset(&xArray, 0, sizeof(xArray));
  memset(&yArray, 0, sizeof(yArray));
  for (Int_t i=0; i<xBins+1; i++){
    xArray[i] =  _Hnominal->GetXaxis()->GetBinLowEdge(i+1);
  }
  for (Int_t j=0; j<yBins+1; j++){
    yArray[j] =  _Hnominal->GetYaxis()->GetBinLowEdge(j+1);
  }
}
//---------------------------------------------------------------------------
RooRazor2DBinPdf::RooRazor2DBinPdf(const RooRazor2DBinPdf& other, const char* name) :
   RooAbsPdf(other, name),
   th1x("th1x", this, other.th1x),
   X0("X0", this, other.X0),
   Y0("Y0", this, other.Y0),
   B("B", this, other.B),
   N("N", this, other.N),
   xCut("xCut", this, other.xCut),
   yCut("yCut", this, other.yCut),
   xBins(other.xBins),
   yBins(other.yBins),
   xMax(other.xMax),
   yMax(other.yMax),
   xMin(other.xMin),
   yMin(other.yMin)
{
  for (Int_t i=0; i<xBins+1; i++){
    xArray[i] = other.xArray[i];
  }
  for (Int_t j=0; j<yBins+1; j++){
    yArray[j] =  other.yArray[j];
  }
}
//---------------------------------------------------------------------------
Double_t RooRazor2DBinPdf::evaluate() const
{
  Double_t integral = 0.0;
  Double_t total_integral = 1.0;

  if(B <= 0. || N <= 0. || X0 >= xMin || Y0 >= yMin) return 0.0;

  Int_t nBins = xBins*yBins;

  Int_t iBin = (Int_t) th1x;
  if(iBin < 0 || iBin >= nBins) {
    //cout << "in bin " << iBin << " which is outside of range" << endl;
    return 0.0;
  }

  // Int_t zBin = iBin % zBins;
  // Int_t yBin = ( (iBin - zBin)/(zBins) ) % (yBins);
  // Int_t xBin =  (iBin - zBin - yBin*zBins ) / (zBins*yBins);

  Int_t yBin = iBin % yBins;
  Int_t xBin = ( (iBin - yBin)/(yBins) ) % (xBins);

  //cout << "in bin " << iBin << " which is in range" << endl;
  //cout << "(" << xBin+1 << "," << yBin+1 << "," << zBin+1 << ")" << endl;

  Double_t xLow = xArray[xBin];
  Double_t xHigh = xArray[xBin+1];
  Double_t yLow = yArray[yBin];
  Double_t yHigh = yArray[yBin+1];

  if(xLow < xCut && yLow < yCut) {
    return 0.0;
  }

  integral = Gfun(xLow,yLow)-Gfun(xLow,yHigh)-Gfun(xHigh,yLow)+Gfun(xHigh,yHigh);
  total_integral = Gfun(xMin,yMin)-Gfun(xMin,yMax)-Gfun(xMax,yMin)+Gfun(xMax,yMax);
    //total_integral = 1.0;

  if (total_integral>0.0) {
    return integral;
  } else return 0;

}

// //---------------------------------------------------------------------------
Int_t RooRazor2DBinPdf::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
  if (matchArgs(allVars, analVars, th1x)) return 1;
  return 0;
}

// //---------------------------------------------------------------------------
Double_t RooRazor2DBinPdf::analyticalIntegral(Int_t code, const char* rangeName) const{

   Double_t th1xMin = th1x.min(rangeName); Double_t th1xMax = th1x.max(rangeName);
   Int_t iBinMin = (Int_t) th1xMin; Int_t iBinMax = (Int_t) th1xMax;

   if(B <= 0. || N <= 0. || X0 >= xMin || Y0 >= yMin) return 1.;

   Double_t integral = 0.0;
   Double_t total_integral =  1.0;

   //cout <<  "iBinMin = " << iBinMin << ",iBinMax = " << iBinMax << endl;
   Int_t nBins =  xBins*yBins;

   if (code==1 && iBinMin==0 && iBinMax>=nBins) {
     integral = -Gfun(xMin,yMax)-Gfun(xMax,yMin)+Gfun(xMax,yMax)+Gfun(xMin,yCut)+Gfun(xCut,yMin)-Gfun(xCut,yCut);
   }

   else if(code==1) {
      total_integral = Gfun(xMin,yMin)-Gfun(xMin,yMax)-Gfun(xMax,yMin)+Gfun(xMax,yMax);

      for (Int_t iBin=iBinMin; iBin<iBinMax; iBin++){
         // Int_t zBin = iBin % zBins;
         // Int_t yBin = ( (iBin - zBin)/(zBins) ) % (yBins);
         // Int_t xBin =  (iBin - zBin - yBin*zBins ) / (zBins*yBins);

         Int_t yBin = iBin % yBins;
         Int_t xBin = ( (iBin - yBin)/(yBins) ) % (xBins);

         if(iBin < 0 || iBin >= nBins) {
            integral += 0.0;
         }
         else {
   	     Double_t xLow = xArray[xBin];
   	     Double_t xHigh = xArray[xBin+1];
   	     Double_t yLow = yArray[yBin];
   	     Double_t yHigh = yArray[yBin+1];
   	     if(xLow < xCut && yLow < yCut) integral += 0.0;
            else integral += Gfun(xLow,yLow)-Gfun(xLow,yHigh)-Gfun(xHigh,yLow)+Gfun(xHigh,yHigh);
         }
      }
   } else {
     cout << "WARNING IN RooRazor2DBinPdf: integration code is not correct" << endl;
     cout << "                           what are you integrating on?" << endl;
     return 1.0;
   }

   if (total_integral>0.0) {
     return integral;
   } else return 1.0;
}
// //---------------------------------------------------------------------------

