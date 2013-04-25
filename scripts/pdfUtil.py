import ROOT as rt
import math


def GetPDFEnvelope(centers, errors):
    # Gives the combined central value and the envelope for the PDFs
    # Based on the PDF4LHC prescription: http://www.hep.ucl.ac.uk/pdf4lhc/PDF4LHCrecom.pdf
    # Takes as input the central values and errors for all PDF sets
    npdfs = len(centers)

    maxup = -100000.0
    minlow = 100000.0
    for i in range(npdfs):
        up = centers[i] + errors[i]
        low = centers[i] - errors[i]
        #print i, up, low
        if up > maxup:
            maxup = up
        if low < minlow:
            minlow = low

    center = 0.5*(maxup + minlow)
    error = 0.5*(maxup - minlow)

    #print maxup, minlow
    #print 'Total:', center, error, error/center, '\n'

    return center, error


def GetPDFCenErr(w, pdfset):

    # Gives the central value and the symmetric error for a given PDF
    # Takes as input the n-dim list of weights and the PDF set name

    nmembers = len(w)
    npairs = (nmembers-1)/2

    if pdfset == 'CTEQ':
        center = w[0]
        sum = 0
        for i in range(npairs):
            sum = sum + math.pow((w[2*i+1] - w[2*i+2]), 2)
        sum = math.sqrt(sum)
        error = sum / 2
        # convert the 95% into 68%
        error = error / 1.645
        #print 'CTEQ', center, err, error/center

    if pdfset == 'MRST':
        center = w[0]
        sum = 0
        for i in range(npairs):
            sum = sum + math.pow((w[2*i+1] - w[2*i+2]), 2)
        sum = math.sqrt(sum)
        error = sum / 2
        #print 'MRST', center, error, error/center

    if pdfset == 'NNPDF':
        center = w[0]
        sum = 0
        for i in range(1, nmembers):
            sum = sum + math.pow((w[i] - center), 2)
        sum = sum / float(nmembers)
        error = math.sqrt(sum)
        #print 'NNPDF', center, error, error/center, '\n'

    #print pdfset, center, error, error/center

    return center, error


