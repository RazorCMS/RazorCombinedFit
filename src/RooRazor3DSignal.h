//---------------------------------------------------------------------------
#ifndef ROO_Razor3DSignal
#define ROO_Razor3DSignal
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooWorkspace.h"
#include "RooAbsReal.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "TMath.h"
#include <TH3D.h>
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"

//---------------------------------------------------------------------------
class RooRazor3DSignal : public RooAbsPdf
{
public:
   RooRazor3DSignal(){};
   RooRazor3DSignal(const char *name, const char *title,
		  RooAbsReal &_x, RooAbsReal &_y, RooAbsReal &_z, 
		  TH3D* _nominal, TH3D* _jes, TH3D* _pdf, TH3D* _btag,
		  RooAbsReal &_xJes, RooAbsReal &_xPdf, RooAbsReal &_xBtag);
   RooRazor3DSignal(const RooRazor3DSignal& other, const char* name=0) ;
   RooRazor3DSignal(const char *name, const char *title,
		  RooAbsReal &_x, RooAbsReal &_y, RooAbsReal &_z,
		  TH3D* _nominal, TH3D* _error,
		  RooAbsReal &_xError);
   TObject* clone(const char* newname) const {
	   TNamed* result = new RooRazor3DSignal(*this);
	   result->SetName(newname);
	   return result;
   }
   ~RooRazor3DSignal() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:

   RooRealProxy X;        // dependent variable
   RooRealProxy Y;        // dependent variable
   RooRealProxy Z;        // dependent variable
   RooRealProxy xJes;   // xJes
   RooRealProxy xPdf;   // xPdf
   RooRealProxy xBtag;   // xBtag

   TH3D* Hnominal;
   TH3D* Hjes;
   TH3D* Hpdf;
   TH3D* Hbtag;

   int iBinX;
   int iBinY;
   int iBinZ;

   Double_t evaluate() const;
   Bool_t importWorkspaceHook(RooWorkspace& ws);

   Double_t getBinIntegral3D(const double xmin, const double xmax, 
			     const double ymin, const double ymax,
			     const double zmin, const double zmax,
			     int xBin, int yBin, int zBin, int code) const{
     
     double nom, jes, pdf, btag;
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

     nom = Hnominal->GetBinContent(xBin, yBin, zBin);
     jes = pow(1.0 + Hjes->GetBinContent(xBin, yBin, zBin), xJes);
     pdf = pow(1.0 + Hpdf->GetBinContent(xBin, yBin, zBin), xPdf);
     btag = pow(1.0 + Hbtag->GetBinContent(xBin, yBin, zBin), xBtag);

     binInt =  nom * jes * pdf * btag * volume / totalvolume;
     return binInt;
   }
   
private:
  ClassDef(RooRazor3DSignal,1) // Razor3DSignal function
};
//---------------------------------------------------------------------------
#endif
