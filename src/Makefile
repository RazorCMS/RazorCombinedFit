include ../Makefile.inc

SHARED = libRazor.so
INCLUDELIST= RooRazor2DTail.h RooRazor2DSignal.h RooRazor3DSignal.h RooRazor3DBinSignal.h RooRazor2DTail_SYS.h RooRazorLShape.h RooRazor3DBinPdf.h RooRazor2DBinPdf.h RooBTagMult.h VecbosBtagPdf.h HypoTestInvTool.h StandardHypoTestInvDemo.h Linkdef.h

all: $(SHARED)

rootdict.cc: $(INCLUDELIST)
	$(ROOTSYS)/bin/rootcint -f $@ -c $(CINTINCLUDES) $^

$(SHARED): rootdict.o RooRazor2DTail.o RooRazor2DSignal.o RooRazor3DSignal.o RooRazor3DBinSignal.o RooRazor2DTail_SYS.o RooRazorLShape.o RooRazor3DBinPdf.o RooRazor2DBinPdf.o RooBTagMult.o VecbosBtagPdf.o HypoTestInvTool.o StandardHypoTestInvDemo.o
	$(LD) $(SOFLAGS) $(LDFLAGS) $(LIBS) -o $@ $^
	mv $(SHARED) ../lib

clean:
	@rm -f *.o
	@rm -f rootdict.*
	@rm -f $(SHARED)
	@rm -f ../lib/$(SHARED)
