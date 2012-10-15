/*
 * PDF used in the 35 pb^-1 V+jets analysis for W->enu and W->munu
 * Imported from previous CVS location here:
 * http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/mpierini/MLFit/
 */

#ifndef __ROO_VECBOSBTAGPDF_H__
#define __ROO_VECBOSBTAGPDF_H__

#include "RooAbsPdf.h"
#include "RooRealProxy.h"

class RooRealVar;
class RooAbsReal;

class VecbosBtagPdf : public RooAbsPdf {
public:
  VecbosBtagPdf(const char *name, const char *title, RooAbsReal& _m,
		RooAbsReal& _n, RooAbsReal& _n_b, RooAbsReal& _e_b,
                RooAbsReal& _e_nob) ;
  
  VecbosBtagPdf(const VecbosBtagPdf& other, const char* name = 0);
  virtual TObject* clone(const char* newname) const { 
    return new VecbosBtagPdf(*this,newname); }

  inline virtual ~VecbosBtagPdf() { }
  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const ;
  Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const ;

protected:

  RooRealProxy m;
  RooRealProxy n;
  RooRealProxy n_b;
  RooRealProxy e_b;
  RooRealProxy e_nob;

  Double_t evaluate() const;

private:
  
  ClassDef(VecbosBtagPdf,0)
};

#endif
