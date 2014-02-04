//---------------------------------------------------------------------------
#ifndef ROO_Razor3DBinSignal
#define ROO_Razor3DBinSignal
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "TMath.h"
#include <TH3.h>
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"

//---------------------------------------------------------------------------
class RooRazor3DBinSignal : public RooAbsPdf
{
public:
   RooRazor3DBinSignal(){};
   RooRazor3DBinSignal(const char *name, const char *title,
		    RooAbsReal &_th1x, 
		    TH3* _Hnominal, 
		    TH3* _Hjes, TH3* _Hpdf, TH3* _Hbtag ,TH3* _Hisr,
		    RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag, RooAbsReal &_xIsr);

   RooRazor3DBinSignal(const RooRazor3DBinSignal& other, const char* name) ;
   TObject* clone(const char* newname) const {
	   TNamed* result = new RooRazor3DBinSignal(*this, newname);
	   return result;
   }
   virtual ~RooRazor3DBinSignal() { 
   }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

   RooRealProxy th1x;        // dependent variable
   RooRealProxy xJes;   // xJes
   RooRealProxy xPdf;   // xPdf
   RooRealProxy xBtag;   // xBtag
   RooRealProxy xIsr;   // xIsr
   TH3* Hnominal;
   TH3* Hjes;
   TH3* Hpdf;
   TH3* Hbtag;
   TH3* Hisr;
   Int_t xBins;        // X bins
   Int_t yBins;        // Y bins
   Int_t zBins;        // Z bins
   Double_t evaluate() const;
   Double_t getBinIntegral3D(int xBin, int yBin, int zBin) const{
     
     double dx, dy, dz, volume;
     Double_t binInt;

     dx = Hnominal->GetXaxis()->GetBinWidth(xBin+1);
     dy = Hnominal->GetYaxis()->GetBinWidth(yBin+1);
     dz = Hnominal->GetZaxis()->GetBinWidth(zBin+1);

     volume = dx*dy*dz;

     double jesVal = Hjes->GetBinContent(xBin+1, yBin+1, zBin+1);
     double pdfVal = Hpdf->GetBinContent(xBin+1, yBin+1, zBin+1);
     double btagVal = Hbtag->GetBinContent(xBin+1, yBin+1, zBin+1);
     double isrVal = Hisr->GetBinContent(xBin+1, yBin+1, zBin+1);

     double nomVal = Hnominal->GetBinContent(xBin+1, yBin+1, zBin+1);

     double rhoJes = pow(1.0 + fabs(jesVal),xJes*TMath::Sign(1.,jesVal));
     double rhoPdf = pow(1.0 + fabs(pdfVal),xPdf*TMath::Sign(1.,pdfVal));
     double rhoBtag = pow(1.0 + fabs(btagVal),xBtag*TMath::Sign(1.,btagVal));
     double rhoIsr = pow(1.0 + fabs(isrVal),xIsr*TMath::Sign(1.,isrVal));

     binInt =  nomVal * rhoJes * rhoPdf * rhoBtag * rhoIsr / volume ;  
     return binInt >= 0. ? binInt : 0;
   }
   
private:
  ClassDef(RooRazor3DBinSignal,1) // Razor3DBinSignal function
};
//---------------------------------------------------------------------------
#endif
