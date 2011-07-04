//---------------------------------------------------------------------------
#ifndef ROO_Dalglish
#define ROO_Dalglish
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "TMath.h"
//#include "Math/SpecFuncMathCore.h"
//#include "Math/SpecFuncMathMore.h"

//---------------------------------------------------------------------------
class RooDalglish : public RooAbsPdf
{
public:
   RooDalglish() {} ;
   RooDalglish(const char *name, const char *title,
				RooAbsReal &_x, RooAbsReal &_y, RooAbsReal &_xhat, RooAbsReal &_yhat, RooAbsReal &_b,
				RooAbsReal &_x0, RooAbsReal &_y0, RooAbsReal &_c, RooAbsReal &_s, RooAbsReal &_sigmaX, 
				RooAbsReal &_sigmaY, RooAbsReal &_xoff, RooAbsReal &_yoff);
   RooDalglish(const RooDalglish& other,
      const char* name = 0);
   virtual TObject* clone(const char* newname) const { return new RooDalglish(*this,newname); }
   inline virtual ~RooDalglish() { }

   
	Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars,const char* rangeName) const;
	Double_t analyticalIntegral(Int_t code, const char* rangeName) const;

protected:
	RooRealProxy X;        // dependent variable
	RooRealProxy Y;        // other dependent variable
	RooRealProxy Xhat;     // offset parameter for tail part 
	RooRealProxy Yhat;     // offset parameter for tail part
	RooRealProxy B;        // slope of tail part
	RooRealProxy X0;       // X 'scale';
	RooRealProxy Y0;       // Y 'scale';
	RooRealProxy C;        // xy iso contour value
	RooRealProxy S;        // strength of 'turn-off'
	RooRealProxy SigmaX;   // sigma of X gaussian 'turn-off'
	RooRealProxy SigmaY;   // sigma of Y gaussian 'turn-off'
	RooRealProxy XOFF;     // X dial for gaussian 'turn-off'
	RooRealProxy YOFF;     // Y dial for gaussian 'turn-off'
	

   Double_t evaluate() const;
private:
  ClassDef(RooDalglish,1) // Dalglish function
};
//---------------------------------------------------------------------------
#endif
