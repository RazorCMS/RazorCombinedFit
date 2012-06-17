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

    kfactors_one = [(200,6.28), (400,7.09), (600,8.44), (800,10.13), (1000,12.09), (1200,14.33) ]
    kfactors_pdf = [(200,6.35), (400,7.57), (600,9.45), (800,11.74), (1000,14.37), (1200,17.37) ]

    kfactors_two = [(175,6.26),(200,6.31),(225,6.37),(250,6.45),(275,6.55),(300,6.66),(325,6.78),(350,6.92),(375,7.06),(400,7.21),(425,7.37),(450,7.53),(475,7.70),(500,7.88),(525,8.07),(550,8.26),(575,8.46),(600,8.66),(625,8.86),(650,9.08),(675,9.29),(700,9.51),(725,9.74),(750,9.97),(775,10.21),(800,10.44),(825,10.69),(850,10.94),(875,11.19),(900,11.44),(925,11.71),(950,11.97),(975,12.24),(1000,12.51)]
    kfactors_half = [(175,6.23),(200,6.25),(225,6.29),(250,6.35),(275,6.43),(300,6.51),(325,6.61),(350,6.72),(375,6.83),(400,6.96),(425,7.09),(450,7.23),(475,7.38),(500,7.53),(525,7.69),(550,7.86),(575,8.03),(600,8.21),(625,8.39),(650,8.57),(675,8.76),(700,8.96),(725,9.16),(750,9.36),(775,9.57),(800,9.78),(825,9.99),(850,10.21),(875,10.44),(900,10.67),(925,10.90),(950,11.13),(975,11.37),(1000,11.62)]

    crossSec = rt.TFile.Open('SMS_XSECS.root')
    stop = crossSec.Get('stop_xsec')
    stop_unc = crossSec.Get('stop_xsec_unc')
    
    gluino = crossSec.Get('gluino_xsec')
    gluino_unc = crossSec.Get('gluino_xsec_unc')
    
    def fillUpAndDown(central, uncert):
        up = central.Clone('%s_up' % central.GetName())
        dw = central.Clone('%s_down' % central.GetName())
        
        up.Reset()
        dw.Reset()
        
        for i in xrange(1,central.GetNbinsX()+1):
            c = central.GetBinContent(i)
            u = uncert.GetBinContent(i)/100.
            
            up.SetBinContent(i, c*(1+u))
            dw.SetBinContent(i, c*(1-u))
        
        return up, dw

    stop_up, stop_down = fillUpAndDown(stop, stop_unc)
    gluino_up, gluino_down = fillUpAndDown(gluino, gluino_unc)

    tprime = rt.TH1D('tprime_xsec','tprime',83,175.,1200.)
    tprime_unc = tprime.Clone('tprime_xsec_unc')
    
    tprime_half = tprime.Clone('tprime_up')
    tprime_two = tprime.Clone('tprime_down')

    kfactors = []
    for line in file('kfactor_table_7TeV.txt'):
        line = line.replace('\n','')
        if line:
            tokens = map(float,[t for t in line.split(' ') if t])
            
            mass = tokens[0]
            xsec = tokens[1]
            kfac = tokens[2]

            susyNLO = getBinContent1D(stop, mass)
            susyNLOUnc = getBinContent1D(stop_unc, mass)/100.
            
            kfac_half = calcWeightedMean(kfactors_half,mass)
            kfac_two = calcWeightedMean(kfactors_two,mass)
            kfacUnc = max( abs(kfac - kfac_half), abs(kfac - kfac_two) )/kfac
            #print kfac, kfac_half, kfac_two, kfacUnc, susyNLOUnc, rt.TMath.Sqrt(kfacUnc**2 + susyNLOUnc**2)
            
            
            susyNLO_UP = getBinContent1D(stop_up, mass)
            susyNLO_DOWN = getBinContent1D(stop_down, mass)

            tprime.Fill(mass,kfac*susyNLO)
            tprime_half.Fill(mass,kfac_half*susyNLO_DOWN)
            tprime_two.Fill(mass,kfac_two*susyNLO_UP)
            tprime_unc.Fill(mass,100.*rt.TMath.Sqrt(kfacUnc**2 + susyNLOUnc**2))

            #kfactors.append( (mass, kfac) )
    
    #calcWeightedMean(kfactors,500)
    tprime_up, tprime_down = fillUpAndDown(tprime, tprime_unc)
    

    #susyNLO = getBinContent1D(stop, mass)
    #setBinContent1D(tprime,mass,susyNLO*kfac)

    output = rt.TFile.Open('tprime.root','recreate')
    #tprime
    tprime.Write()
    tprime_unc.Write()
    tprime_up.Write()
    tprime_down.Write()
    #stop
    stop.Write()
    stop_unc.Write()
    stop_down.Write()
    stop_up.Write()
    #gluino
    gluino.Write()
    gluino_unc.Write()
    gluino_down.Write()
    gluino_up.Write()
    output.Close()
