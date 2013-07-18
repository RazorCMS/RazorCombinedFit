include ../Makefile.inc

SHARED = libRazor.so
INCLUDELIST= MLMixedSample.h OneDFitFromYi.h RooAtLeast.h RooSameAs.h RooTwoSideGaussianWithAnExponentialTail.h RooTwoSideGaussianWithTwoExponentialTails.h RooTwoSideGaussianWithThreeExponentialTails.h RooTwoSideGaussianWithOneExponentialTailAndOneInverseN.h RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential.h RooRazor2DTail.h RooRazor2DSignal.h RooRazor3DSignal.h RooRazor2DTurnOn.h RooRazor2DTail_SYS.h RooRazor2DTailBNN_SYS.h RooTwoBin.h RooRazorLShape.h RooDalglish.h RooBTagMult.h VecbosBtagPdf.h HypoTestInvTool.h StandardHypoTestInvDemo.h Linkdef.h

all: $(SHARED) FitMRDistribution

rootdict.cc: $(INCLUDELIST)
	$(ROOTSYS)/bin/rootcint -f $@ -c $(CINTINCLUDES) $^ 

$(SHARED): rootdict.o MLMixedSample.o OneDFitFromYi.o RooAtLeast.o RooSameAs.o RooTwoSideGaussianWithAnExponentialTail.o RooTwoSideGaussianWithTwoExponentialTails.o RooTwoSideGaussianWithThreeExponentialTails.o RooTwoSideGaussianWithOneExponentialTailAndOneInverseN.o RooTwoSideGaussianWithOneExponentialTailAndOneXDependentExponential.o RooRazor2DTail.o RooRazor2DSignal.o RooRazor3DSignal.o RooRazor2DTurnOn.o RooRazor2DTail_SYS.o RooRazor2DTailBNN_SYS.o RooTwoBin.o RooRazorLShape.o RooDalglish.o RooBTagMult.o VecbosBtagPdf.o HypoTestInvTool.o StandardHypoTestInvDemo.o SingleMu_2012_HLT_j1ptg200_100K.o
	$(LD) $(SOFLAGS) $(LDFLAGS) $(LIBS) -o $@ $^
	mv $(SHARED) ../lib

FitMRDistribution:FitMRDistribution_Cleaned.o $(SHARED)
	$(LD) $(LDFLAGS) $(LIBS) ../lib/$(SHARED) -o $@ $<

clean:
	@rm -f *.o
	@rm -f rootdict.*
	@rm -f $(SHARED) FitMRDistribution
	@rm -f ../lib/$(SHARED)
