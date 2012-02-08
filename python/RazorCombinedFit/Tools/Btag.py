#See https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagPOG#Recommendation_for_b_c_tagging_a

def getTCHEMScaleFactor(pt):
    """Return the data/MC scale factor from muon+jet events with the TCHEM tagger"""
    #see https://twiki.cern.ch/twiki/pub/CMS/BtagPOG/SFb-mujet_payload.txt
    if pt > 670: pt = 670
    if pt < 30: pt = 30
    return 0.932251*((1.+(0.00335634*pt))/(1.+(0.00305994*pt)))
    