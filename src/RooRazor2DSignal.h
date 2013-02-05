//---------------------------------------------------------------------------
#ifndef ROO_Razor2DSignal
#define ROO_Razor2DSignal
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooWorkspace.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "TMath.h"
#include <TH2.h>
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"

//---------------------------------------------------------------------------
class RooRazor2DSignal : public RooAbsPdf
{
public:
   RooRazor2DSignal(){};
   RooRazor2DSignal(const char *name, const char *title,
		  RooAbsReal &_x, RooAbsReal &_y,
		  const RooWorkspace& ws,
		  const char* _nominal, const char* _jes, const char* _pdf, const char* _btag,
		  RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag);

   RooRazor2DSignal(const RooRazor2DSignal& other, const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooRazor2DSignal(*this, newname);
   }
   inline virtual ~RooRazor2DSignal(){
   }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

   RooRealProxy X;        // dependent variable
   RooRealProxy Y;        // dependent variable
   RooRealProxy xJes;   // xJes
   RooRealProxy xPdf;   // xPdf
   RooRealProxy xBtag;   // xBtag

   TH2* Hnominal;
   TH2* Hjes;
   TH2* Hpdf;
   TH2* Hbtag;

   int iBinX;
   int iBinY;

   Double_t evaluate() const;

   Double_t getBinIntegral2D(const double xmin, const double xmax, 
			     const double ymin, const double ymax,
			     int xBin, int yBin, int code) const{
     
     double nom, jes, pdf, btag;
     double dx, dy, area;
     Double_t binInt;
    
     int xBinMin, xBinMax;
     int yBinMin, yBinMax;

     if (code==1 || code==2){ // integrate x
       xBinMin = Hnominal->GetXaxis()->FindBin(xmin);
       xBinMax = Hnominal->GetXaxis()->FindBin(xmax);
     

       if (xBin==xBinMin && xBinMin==xBinMax) dx = xmax - xmin;
       else if (xBin==xBinMin) dx = Hnominal->GetXaxis()->GetBinUpEdge(xBin) - xmin;
       else if (xBin==xBinMax) dx = xmax - Hnominal->GetXaxis()->GetBinLowEdge(xBin);
       else {
	 dx = Hnominal->GetXaxis()->GetBinWidth(xBin);
       }
       
     } else{ // don't integrate x
       dx = 1.;
     }
     
     if (code==1 || code==3){ // integrate y
       yBinMin = Hnominal->GetYaxis()->FindBin(ymin);
       yBinMax = Hnominal->GetYaxis()->FindBin(ymax);
     
       if (yBin==yBinMin && yBinMin==yBinMax) dy = ymax - ymin;
       else if (yBin==yBinMin) dy = Hnominal->GetYaxis()->GetBinUpEdge(yBin) - ymin;
       else if (yBin==yBinMax) dy = ymax - Hnominal->GetYaxis()->GetBinLowEdge(yBin);
       else {
	 dy = Hnominal->GetYaxis()->GetBinWidth(yBin);
       }

     } else{ // don't integrate y
       dy = 1.; 
     }
     
     area = dx*dy;
     
     double DX = Hnominal->GetXaxis()->GetBinWidth(xBin);
     double DY = Hnominal->GetYaxis()->GetBinWidth(yBin);

     double totalarea  =  DX*DY;

     nom = Hnominal->GetBinContent(xBin, yBin);
     jes = pow(1.0 + Hjes->GetBinContent(xBin, yBin), xJes);
     pdf = pow(1.0 + Hpdf->GetBinContent(xBin, yBin), xPdf);
     btag = pow(1.0 + Hbtag->GetBinContent(xBin, yBin), xBtag);

     binInt =  nom * jes * pdf * btag * area / totalarea;
     return binInt;
   }
   

private:
  ClassDef(RooRazor2DSignal,1) // Razor2DSignal function
};
//---------------------------------------------------------------------------
#endif
