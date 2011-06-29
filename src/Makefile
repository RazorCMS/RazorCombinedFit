include ../Makefile.inc

SHARED = libRazor.so
INCLUDELIST= OneDFitFromYi.h RooAtLeast.h RooSameAs.h RooTwoSideGaussianWithAnExponentialTail.h RooTwoSideGaussianWithTwoExponentialTails.h RooRazor2DTail.h Linkdef.h

all: $(SHARED) FitMRDistribution

rootdict.cc: $(INCLUDELIST)
	$(ROOTSYS)/bin/rootcint -f $@ -c $(CINTINCLUDES) $^ 

$(SHARED): rootdict.o OneDFitFromYi.o RooAtLeast.o RooSameAs.o RooTwoSideGaussianWithAnExponentialTail.o RooTwoSideGaussianWithTwoExponentialTails.o RooRazor2DTail.o
	$(LD) $(SOFLAGS) $(LDFLAGS) $(LIBS) -o $@ $^
	mv $(SHARED) ../lib

FitMRDistribution:FitMRDistribution_Cleaned.o $(SHARED)
	$(LD) $(LDFLAGS) $(LIBS) ../lib/$(SHARED) -o $@ $<

clean:
	@rm -f *.o
	@rm -f rootdict.*
	@rm -f $(SHARED) FitMRDistribution
	@rm -f ../lib/$(SHARED)
