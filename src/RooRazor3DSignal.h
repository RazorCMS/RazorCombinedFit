//---------------------------------------------------------------------------
#ifndef ROO_Razor3DSignal
#define ROO_Razor3DSignal
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooWorkspace.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "TMath.h"
#include <TH3.h>
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"

//---------------------------------------------------------------------------
class RooRazor3DSignal : public RooAbsPdf
{
public:
   RooRazor3DSignal(){};
   RooRazor3DSignal(const char *name, const char *title,
		    RooAbsReal &_x, RooAbsReal &_y, RooAbsReal &_z, 
		    const RooWorkspace& ws,
		    const char* _nominal, const char* _jes, const char* _pdf, const char* _btag, const char* _isr,
		    RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag, RooAbsReal &_xIsr);

   RooRazor3DSignal(const RooRazor3DSignal& other, const char* name) ;
   TObject* clone(const char* newname) const {
	   TNamed* result = new RooRazor3DSignal(*this, newname);
	   return result;
   }
   virtual ~RooRazor3DSignal() { 
   }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

   RooRealProxy X;        // dependent variable
   RooRealProxy Y;        // dependent variable
   RooRealProxy Z;        // dependent variable
   RooRealProxy xJes;   // xJes
   RooRealProxy xPdf;   // xPdf
   RooRealProxy xBtag;   // xBtag
   RooRealProxy xIsr;   // xIsr

   TH3* Hnominal;
   TH3* Hjes;
   TH3* Hpdf;
   TH3* Hbtag;
   TH3* Hisr;

   int iBinX;
   int iBinY;
   int iBinZ;

   Double_t evaluate() const;
   Double_t getBinIntegral3D(const double xmin, const double xmax, 
			     const double ymin, const double ymax,
			     const double zmin, const double zmax,
			     int xBin, int yBin, int zBin, int code) const{
     
     double dx, dy, dz, volume;
     Double_t binInt;
    
     int xBinMin, xBinMax;
     int yBinMin, yBinMax;
     int zBinMin, zBinMax;

     if (code==1 || code==2 || code==4 || code==5){ // integrate x
       xBinMin = Hnominal->GetXaxis()->FindBin(xmin);
       xBinMax = Hnominal->GetXaxis()->FindBin(xmax);
     
       if (xBinMin > xBin || xBinMax < xBin) return 0;

       if (xBin==xBinMin && xBinMin==xBinMax) dx = xmax - xmin;
       else if (xBin==xBinMin) dx = Hnominal->GetXaxis()->GetBinUpEdge(xBin) - xmin;
       else if (xBin==xBinMax) dx = xmax - Hnominal->GetXaxis()->GetBinLowEdge(xBin);
       else {
	 dx = Hnominal->GetXaxis()->GetBinWidth(xBin);
       }
       
     } else{ // don't integrate x
       dx = 1.;
     }
     
     if (code==1 || code==2 || code==3 || code==6){ // integrate y
       yBinMin = Hnominal->GetYaxis()->FindBin(ymin);
       yBinMax = Hnominal->GetYaxis()->FindBin(ymax);
     
       if (yBinMin > yBin || yBinMax < yBin) return 0;

       if (yBin==yBinMin && yBinMin==yBinMax) dy = ymax - ymin;
       else if (yBin==yBinMin) dy = Hnominal->GetYaxis()->GetBinUpEdge(yBin) - ymin;
       else if (yBin==yBinMax) dy = ymax - Hnominal->GetYaxis()->GetBinLowEdge(yBin);
       else {
	 dy = Hnominal->GetYaxis()->GetBinWidth(yBin);
       }

     } else{ // don't integrate y
       dy = 1.; 
     }

     if (code==1 || code==3 || code==4 || code==7){ // integrate z
       zBinMin = Hnominal->GetZaxis()->FindBin(zmin);
       zBinMax = Hnominal->GetZaxis()->FindBin(zmax);
       
       if (zBinMin > zBin || zBinMax < zBin) return 0;

       if (zBin==zBinMin && zBinMin==zBinMax) dz = zmax - zmin;
       else if (zBin==zBinMin) dz = Hnominal->GetZaxis()->GetBinUpEdge(zBin) - zmin;
       else if (zBin==zBinMax) dz = zmax - Hnominal->GetZaxis()->GetBinLowEdge(zBin);
       else {
	 dz = Hnominal->GetZaxis()->GetBinWidth(zBin);
       }
     } else{ // don't integrate z
       dz = 1.;
     }
     
     volume = dx*dy*dz;
     
     double DX = Hnominal->GetXaxis()->GetBinWidth(xBin);
     double DY = Hnominal->GetYaxis()->GetBinWidth(yBin);
     double DZ = Hnominal->GetZaxis()->GetBinWidth(zBin);
     double totalvolume  =  DX*DY*DZ;

     double jesVal = Hjes->GetBinContent(xBin, yBin, zBin);
     double pdfVal = Hpdf->GetBinContent(xBin, yBin, zBin);
     double btagVal = Hbtag->GetBinContent(xBin, yBin, zBin);
     double isrVal = Hisr->GetBinContent(xBin, yBin, zBin);

     double nomVal = Hnominal->GetBinContent(xBin, yBin, zBin);

     double rhoJes = pow(1.0 + fabs(jesVal),xJes*TMath::Sign(1.,jesVal));
     double rhoPdf = pow(1.0 + fabs(pdfVal),xPdf*TMath::Sign(1.,pdfVal));
     double rhoBtag = pow(1.0 + fabs(btagVal),xBtag*TMath::Sign(1.,btagVal));
     double rhoIsr = pow(1.0 + fabs(isrVal),xIsr*TMath::Sign(1.,isrVal));

     binInt =  nomVal * rhoJes * rhoPdf * rhoBtag * rhoIsr * volume / totalvolume;  
     return binInt >= 0. ? binInt : 0;
   }
   
private:
  ClassDef(RooRazor3DSignal,1) // Razor3DSignal function
};
//---------------------------------------------------------------------------
#endif
