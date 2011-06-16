#ifndef LINKDEF_H_
#define LINKDEF_H_

#ifdef __CINT__
 
#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;
#pragma link C++ nestedclasses;

#pragma link C++ defined_in "RooAtLeast.h";
#pragma link C++ defined_in "RooSameAs.h";
#pragma link C++ defined_in "RooTwoSideGaussianWithAnExponentialTail.h";
#pragma link C++ defined_in "RooTwoSideGaussianWithTwoExponentialTails.h";

#endif

#endif /*LINKDEF_H_*/
