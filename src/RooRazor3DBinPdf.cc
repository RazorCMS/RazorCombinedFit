//---------------------------------------------------------------------------
#include "RooFit.h"

#include "Riostream.h"
#include <TMath.h>
#include <cassert>
#include <cmath>
#include <math.h>

#include "RooRazor3DBinPdf.h"
#include "RooRealVar.h"

ClassImp(RooRazor3DBinPdf)
//---------------------------------------------------------------------------
RooRazor3DBinPdf::RooRazor3DBinPdf(const char *name, const char *title,
				   RooAbsReal& _th1x,  
				   RooAbsReal& _x0, RooAbsReal& _y0, 
				   RooAbsReal& _b, RooAbsReal& _n,
				   RooAbsReal& _xCut, RooAbsReal& _yCut, RooAbsReal& _zCut,
				   TH3* _Hnominal) : RooAbsPdf(name, title), 
  th1x("th1x", "th1x Observable", this, _th1x),
  X0("X0", "X Offset", this, _x0),
  Y0("Y0", "Y Offset", this, _y0),
  B("B", "B Shape parameter", this, _b),
  N("N", "N Shape parameter", this, _n),
  xCut("xCut", "X Cut parameter",this, _xCut),
  yCut("yCut", "Y Cut parameter",this, _yCut),
  zCut("zCut", "Z Cut parameter",this, _zCut),
  Hnominal(_Hnominal),
  xBins(0),
  yBins(0),
  zBins(0),
  xMax(0),
  yMax(0),
  zMax(0),
  xMin(0),
  yMin(0),
  zMin(0)
{
  xBins = Hnominal->GetXaxis()->GetNbins();
  yBins = Hnominal->GetYaxis()->GetNbins();
  zBins = Hnominal->GetZaxis()->GetNbins();
  xMin = Hnominal->GetXaxis()->GetBinLowEdge(1);
  yMin = Hnominal->GetYaxis()->GetBinLowEdge(1);
  zMin = Hnominal->GetZaxis()->GetBinLowEdge(1);
  xMax = Hnominal->GetXaxis()->GetBinUpEdge(xBins);
  yMax = Hnominal->GetYaxis()->GetBinUpEdge(yBins);
  zMax = Hnominal->GetZaxis()->GetBinUpEdge(zBins);
}
//---------------------------------------------------------------------------
RooRazor3DBinPdf::RooRazor3DBinPdf(const RooRazor3DBinPdf& other, const char* name) :
   RooAbsPdf(other, name), 
   th1x("th1x", this, other.th1x),  
   X0("X0", this, other.X0),
   Y0("Y0", this, other.Y0),
   B("B", this, other.B),
   N("N", this, other.N),
   xCut("xCut", this, other.xCut),
   yCut("yCut", this, other.yCut),
   zCut("zCut", this, other.zCut),
   Hnominal(other.Hnominal),
   xBins(other.xBins),
   yBins(other.yBins),
   zBins(other.zBins),
   xMax(other.xMax),
   yMax(other.yMax),
   zMax(other.zMax),
   xMin(other.xMin),
   yMin(other.yMin),
   zMin(other.zMin)
{
}
//---------------------------------------------------------------------------
Double_t RooRazor3DBinPdf::evaluate() const
{
  Double_t integral = 0.0;
  Double_t total_integral = 1.0;
  Double_t bin_width = 1.0;


  if(B <= 0. || N <= 0. || X0 >= xMin || Y0 >= yMin) return 0.0;

  Int_t nBins = xBins*yBins*zBins;

  Int_t iBin = (Int_t) th1x;
  if(iBin < 0 || iBin >= nBins) {
    //cout << "in bin " << iBin << " which is outside of range" << endl;
    return 0.0;
  }

  
  Int_t zBin = iBin % zBins;
  Int_t yBin = ( (iBin - zBin)/(zBins) ) % (yBins);
  Int_t xBin =  (iBin - zBin - yBin*zBins ) / (zBins*yBins);

  //cout << "in bin " << iBin << " which is in range" << endl;
  //cout << "(" << xBin+1 << "," << yBin+1 << "," << zBin+1 << ")" << endl;

  Double_t zLow = Hnominal->GetZaxis()->GetBinLowEdge(zBin+1);
  Double_t zHigh = Hnominal->GetZaxis()->GetBinUpEdge(zBin+1);
  if (zCut >= zLow and zCut < zHigh){
    Double_t xLow = Hnominal->GetXaxis()->GetBinLowEdge(xBin+1);
    Double_t xHigh = Hnominal->GetXaxis()->GetBinUpEdge(xBin+1);
    Double_t yLow = Hnominal->GetYaxis()->GetBinLowEdge(yBin+1);
    Double_t yHigh = Hnominal->GetYaxis()->GetBinUpEdge(yBin+1);

    
    if(xLow < xCut && yLow < yCut) {
      return 0.0;
    }

    integral = Gfun(xLow,yLow)-Gfun(xLow,yHigh)-Gfun(xHigh,yLow)+Gfun(xHigh,yHigh);
    total_integral = Gfun(xMin,yMin)-Gfun(xMin,yMax)-Gfun(xMax,yMin)+Gfun(xMax,yMax);
    //total_integral = 1.0;
    bin_width = (yHigh-yLow)*(xHigh-xLow)*(zHigh-zLow);
  }

  if (total_integral>0.0) {
    return integral;
  } else return 0;

}

// //---------------------------------------------------------------------------
Int_t RooRazor3DBinPdf::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
  if (matchArgs(allVars, analVars, th1x)) return 1;
  return 0;
}

// //---------------------------------------------------------------------------
Double_t RooRazor3DBinPdf::analyticalIntegral(Int_t code, const char* rangeName) const{

   Double_t th1xMin = th1x.min(rangeName); Double_t th1xMax = th1x.max(rangeName);
   Int_t iBinMin = (Int_t) th1xMin; Int_t iBinMax = (Int_t) th1xMax;

   
   if(B <= 0. || N <= 0. || X0 >= xMin || Y0 >= yMin) return 1.;

   Double_t integral = 0.0;
   Double_t total_integral =  1.0;
   Double_t bin_width = 1.0;
   
   //cout <<  "iBinMin = " << iBinMin << ",iBinMax = " << iBinMax << endl;
   Int_t nBins =  xBins*yBins*zBins;

   if (code==1 && iBinMin==0 && iBinMax>=nBins){
     integral = -Gfun(xMin,yMax)-Gfun(xMax,yMin)+Gfun(xMax,yMax)+Gfun(xMin,yCut)+Gfun(xCut,yMin)-Gfun(xCut,yCut);
   }
   else if(code==1) { 
     total_integral = Gfun(xMin,yMin)-Gfun(xMin,yMax)-Gfun(xMax,yMin)+Gfun(xMax,yMax);
     for (Int_t iBin=iBinMin; iBin<iBinMax; iBin++){
       Int_t zBin = iBin % zBins;
       Int_t yBin = ( (iBin - zBin)/(zBins) ) % (yBins);
       Int_t xBin =  (iBin - zBin - yBin*zBins ) / (zBins*yBins);
 
       Double_t zLow = Hnominal->GetZaxis()->GetBinLowEdge(zBin+1);
       Double_t zHigh = Hnominal->GetZaxis()->GetBinUpEdge(zBin+1);

       if(iBin < 0 || iBin >= nBins) {
	 integral += 0.0;
       }
       else{
	 if (zCut >= zLow and zCut < zHigh){
	   Double_t xLow = Hnominal->GetXaxis()->GetBinLowEdge(xBin+1);
	   Double_t xHigh = Hnominal->GetXaxis()->GetBinUpEdge(xBin+1);
	   Double_t yLow = Hnominal->GetYaxis()->GetBinLowEdge(yBin+1);
	   Double_t yHigh = Hnominal->GetYaxis()->GetBinUpEdge(yBin+1);

	   bin_width = (yHigh-yLow)*(xHigh-xLow)*(zHigh-zLow);
	   if(xLow < xCut && yLow < yCut) integral += 0.0;
	   else integral += Gfun(xLow,yLow)-Gfun(xLow,yHigh)-Gfun(xHigh,yLow)+Gfun(xHigh,yHigh);
	 }
       }
     }
   } else {
     cout << "WARNING IN RooRazor3DBinPdf: integration code is not correct" << endl;
     cout << "                           what are you integrating on?" << endl;
     return 1.0;
   }

   if (total_integral>0.0) {
     
     return integral;
   } else return 1.0;
}
// //---------------------------------------------------------------------------

