#!/usr/bin/env python

import ROOT as rt

def getBinContent1D(histo, x):
    
    xaxis = histo.GetXaxis()
    xbin = xaxis.FindBin(x)
    
    bin = histo.GetBin(xbin)
    return histo.GetBinContent(bin)

def setBinContent1D(histo, x, val):
    
    xaxis = histo.GetXaxis()
    xbin = xaxis.FindBin(x)
    
    bin = histo.GetBin(xbin)
    return histo.SetBinContent(bin, val)

def calcWeightedMean(kfactors, mass):

    wsum = 0
    sum = 0
    for i in xrange(len(kfactors)):
        try:
            w = 1./(1.*abs(mass - kfactors[i][0]))
        except ZeroDivisionError, e:
            #if there is an exact value, we don't extrapolate
            return kfactors[i][1]
        wsum += w
        sum += (w*kfactors[i][1])
    result = sum/(1.*wsum)
    return result

if __name__ == '__main__':

#    mass       *1/2 scale      *1 scale     *2 scale   CTEQ5L
#    200          6.25                 6.28           6.31           6.35
#    400          6.96                 7.09           7.21           7.57
#    600          8.21                 8.44           8.66           9.45
#    800          9.78                10.13         10.44         11.74
#    1000       11.62                12.09         12.51         14.37
#    1200       13.72                14.33         14.87         17.37

    kfactors_half = [(200,6.25), (400,6.96), (600,8.21), (800,9.78), (1000,11.62), (1200,13.72) ]
    kfactors_one = [(200,6.28), (400,7.09), (600,8.44), (800,10.13), (1000,12.09), (1200,14.33) ]
    kfactors_two = [(200,6.31), (400,7.21), (600,8.66), (800,10.44), (1000,12.51), (1200,14.87) ]
    kfactors_pdf = [(200,6.35), (400,7.57), (600,9.45), (800,11.74), (1000,14.37), (1200,17.37) ]

    crossSec = rt.TFile.Open('referenceXSecs.root')
    stop = crossSec.Get('stop')

    tprime = rt.TH1D('tprime','tprime',83,175.,1200.)
    tprimeMath = tprime.Clone('tprimeMath')
    tprime_half = tprime.Clone('tprime_half')
    tprime_two = tprime.Clone('tprime_two')
    tprime_pdf = tprime.Clone('tprime_pdf')

    kfactors = []
    for line in file('kfactor_table_7TeV.txt'):
        line = line.replace('\n','')
        if line:
            tokens = map(float,[t for t in line.split(' ') if t])
            
            mass = tokens[0]
            xsec = tokens[1]
            kfac = tokens[2]
            
            kfac_half = calcWeightedMean(kfactors_half,mass)
            kfac_one = calcWeightedMean(kfactors_one,mass)
            kfac_two = calcWeightedMean(kfactors_two,mass)
            kfac_pdf = calcWeightedMean(kfactors_pdf,mass)
            
            susyNLO = getBinContent1D(stop, mass)

            tprime.Fill(mass,kfac*susyNLO)
            tprime_half.Fill(mass,(kfac/kfac_one)*kfac_half*susyNLO)
            tprime_two.Fill(mass,(kfac/kfac_one)*kfac_two*susyNLO)
            tprime_pdf.Fill(mass,(kfac/kfac_one)*kfac_pdf*susyNLO)

            tprimeMath.Fill(mass,xsec*kfac)

            #kfactors.append( (mass, kfac) )
    
    #calcWeightedMean(kfactors,500)
    

    #susyNLO = getBinContent1D(stop, mass)
    #setBinContent1D(tprime,mass,susyNLO*kfac)

    output = rt.TFile.Open('tprime.root','recreate')
    tprime.Write()
    tprime_half.Write()
    tprime_two.Write()
    tprime_pdf.Write()
    tprimeMath.Write()
    stop.Write()
    output.Close()
