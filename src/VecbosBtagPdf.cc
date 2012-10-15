#include <iostream>
#include <math.h>

#include "VecbosBtagPdf.h"
#include "RooRealVar.h"
#include "RooRealConstant.h"

ClassImp(VecbosBtagPdf)

VecbosBtagPdf::VecbosBtagPdf(const char *name, const char *title,
			     RooAbsReal& _m, RooAbsReal& _n, 
			     RooAbsReal& _n_b, RooAbsReal& _e_b,
			     RooAbsReal& _e_nob)
  :
  RooAbsPdf(name, title),
  m("m", "Dependent", this, _m),
  n("n", "n", this, _n),
  n_b("n_b", "n_b", this, _n_b),
  e_b("e_b", "e_b", this, _e_b),
  e_nob("e_nob", "e_nob", this, _e_nob)
{
  //cout << "!!!!!!!!!!!!!!   INIT VECBOSPTAGPDF" << endl;
  //_n.Print("V");
  /*
  cout << "!!!!!!!!!!!!!!   INIT VECBOSPTAGPDF" << endl;
  cout << ((RooRealVar*)m.absArg()) << endl;;
  cout << ((RooRealVar*)n.absArg()) << endl;;
  cout << ((RooRealVar*)n_b.absArg()) << endl;;
  cout << ((RooRealVar*)e_b.absArg()) << endl;;
  cout << ((RooRealVar*)e_nob.absArg()) << endl;;
  */
}

VecbosBtagPdf::VecbosBtagPdf(const VecbosBtagPdf& other, const char* name) :
  RooAbsPdf(other, name), m("m", this, other.m), n("n", this, other.n),
  n_b("n_b", this, other.n_b), e_b("e_b", this, other.e_b), 
  e_nob("e_nob", this, other.e_nob)  
{
}

Double_t VecbosBtagPdf::evaluate() const 
{
  double n_nob = n - n_b;
  double bin0tags = pow(1.-e_nob, n_nob)*pow(1.-e_b,n_b);  
  double bin1tags =  
    n_nob*e_nob*pow(1.-e_nob, n_nob-1)*pow(1.-e_b,n_b) +
    pow(1.-e_nob, n_nob)*n_b*e_b*pow(1.-e_b, n_b-1);  
  double bin2tagsInc = 1. - bin0tags - bin1tags;
  double val = 0.;
  //cout << "m,n: " << m << " " << n << endl;
  //cout << "bin0,1,2: " << bin0tags <<", " << bin1tags << ", " << bin2tagsInc << ", " << endl;
  if(m>=0. && m <1.)      val = bin0tags;
  else if(m>=1. && m <2.) val = bin1tags;
  else if(m>=2 && m <3.) val = bin2tagsInc;
  //cout << "val: " << val << endl;

  return val;
}


Int_t VecbosBtagPdf::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const 
{
  if (matchArgs(allVars, analVars,m)) return 1;
  return 0;
}

Double_t VecbosBtagPdf::analyticalIntegral(Int_t code, const char* rangeName) const 
{
  assert(code==1) ;
  Double_t sum(1.0) ;
  return sum;    
}

