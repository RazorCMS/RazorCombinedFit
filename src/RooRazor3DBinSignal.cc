//---------------------------------------------------------------------------
#include "RooFit.h"
#include "Riostream.h"
#include <TMath.h>
#include <cassert>
#include <cmath>

#include "RooRazor3DBinSignal.h"
#include "RooRealVar.h"

ClassImp(RooRazor3DBinSignal)
//---------------------------------------------------------------------------
RooRazor3DBinSignal::RooRazor3DBinSignal(const char *name, const char *title,
				   RooAbsReal &_th1x,
				   TH3* _Hnominal, 
				   TH3* _Hjes, TH3* _Hpdf, TH3* _Hbtag, TH3* _Hisr,
				   RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag, RooAbsReal &_xIsr) : RooAbsPdf(name, title), 
  th1x("th1x", "th1x Observable", this, _th1x),
  xJes("xJes", "xJes", this, _xJes),
  xPdf("xPdf", "xPdf", this, _xPdf),
  xBtag("xBtag", "xBtag", this, _xBtag),
  xIsr("xIsr", "xIsr", this, _xIsr),
  Hnominal(_Hnominal),
  Hjes(_Hjes),
  Hpdf(_Hpdf),
  Hbtag(_Hbtag),
  Hisr(_Hisr),
  xBins(0),
  yBins(0),
  zBins(0)
{
  xBins = _Hnominal->GetXaxis()->GetNbins();
  yBins = _Hnominal->GetYaxis()->GetNbins();
  zBins = _Hnominal->GetZaxis()->GetNbins();
}
RooRazor3DBinSignal::RooRazor3DBinSignal(const RooRazor3DBinSignal& other, const char* name) :
   RooAbsPdf(other, name), 
   th1x("th1x", this, other.th1x), 
   xJes("xJes", this, other.xJes),
   xPdf("xPdf", this, other.xPdf),
   xBtag("xBtag", this, other.xBtag),
   xIsr("xIsr", this, other.xIsr),
   Hnominal(other.Hnominal),
   Hjes(other.Hjes),
   Hpdf(other.Hpdf),
   Hbtag(other.Hbtag),
   Hisr(other.Hisr),
   xBins(other.xBins),
   yBins(other.yBins),
   zBins(other.zBins)
{
}
Double_t RooRazor3DBinSignal::evaluate() const
{


  Int_t nBins = xBins*yBins*zBins;

  Int_t iBin = (Int_t) th1x;
  if(iBin < 0 || iBin >= nBins) {
    //cout << "in bin " << iBin << " which is outside of range" << endl;
    return 0.0;
  }

  
  Int_t zBin = iBin % zBins;
  Int_t yBin = ( (iBin - zBin)/(zBins) ) % (yBins);
  Int_t xBin =  (iBin - zBin - yBin*zBins ) / (zBins*yBins);

  double result = getBinIntegral3D(xBin,yBin,zBin);
  return result;
}

// //---------------------------------------------------------------------------
Int_t RooRazor3DBinSignal::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const{
  // integral on th1x bin dimension
  if (matchArgs(allVars, analVars, th1x)) return 1;
  // integrating nothing
  return 0;
}


// //---------------------------------------------------------------------------
Double_t RooRazor3DBinSignal::analyticalIntegral(Int_t code, const char* rangeName) const {
  const Double_t th1xMin = th1x.min(rangeName); const Double_t th1xMax = th1x.max(rangeName);
  Int_t iBinMin = (Int_t) th1xMin; Int_t iBinMax = (Int_t) th1xMax;

  if (code==1){
    // integral on all X Y and Z
    Double_t intPdf = 0.;

     for (Int_t iBin=iBinMin; iBin<iBinMax; iBin++){
       Int_t zBin = iBin % zBins;
       Int_t yBin = ( (iBin - zBin)/(zBins) ) % (yBins);
       Int_t xBin =  (iBin - zBin - yBin*zBins ) / (zBins*yBins);
       intPdf += getBinIntegral3D(xBin,yBin,zBin);
    }
    return  intPdf;
  }
  else {
    cout << "WARNING IN RooRazor3DBinSignal: integration code is not correct" << endl;
    cout << "                           what are you integrating on?" << endl;
    return 1.;
  }

}
// //---------------------------------------------------------------------------

