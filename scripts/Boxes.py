class BJetBoxLS(object):
    """The BJet search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'BJetLS'
        self.dumper = dumper
    def __call__(self, tree):
        return tree.nJet >= 6 and tree.metFilter and tree.hadBoxFilter and tree.hadTriggerFilter and tree.nCSVM > 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 0 and tree.nElectronTight == 0 and not tree.isolatedTrack10Filter and tree.nMuonLoose == 0 and tree.nElectronLoose == 0 and self.dumper.bdt() < -0.1 

class BJetBoxHS(object):
    """The BJet search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'BJetHS'
        self.dumper = dumper
    def __call__(self, tree):
        return tree.nJet >= 6 and tree.metFilter and tree.hadBoxFilter and tree.hadTriggerFilter and tree.nCSVM > 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 0 and tree.nElectronTight == 0 and not tree.isolatedTrack10Filter and tree.nMuonLoose == 0 and tree.nElectronLoose == 0 and self.dumper.bdt() >= -0.1 

class CR6JBVetoBoxLS(object):
    """The CR6JBVeto search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'CR6JBVetoLS'
        self.dumper = dumper
    def __call__(self, tree):
        return tree.nJet >= 6 and tree.metFilter and tree.hadBoxFilter and tree.hadTriggerFilter and tree.nCSVL == 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 0 and tree.nElectronTight == 0 and not tree.isolatedTrack10Filter and tree.nMuonLoose == 0 and tree.nElectronLoose == 0 and self.dumper.bdt() < -0.1 

class CR6JBVetoBoxHS(object):
    """The CR6JBVeto search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'CR6JBVetoHS'
        self.dumper = dumper
    def __call__(self, tree):
        return tree.nJet >= 6 and tree.metFilter and tree.hadBoxFilter and tree.hadTriggerFilter and tree.nCSVL == 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 0 and tree.nElectronTight == 0 and not tree.isolatedTrack10Filter and tree.nMuonLoose == 0 and tree.nElectronLoose == 0 and self.dumper.bdt() >= -0.1 

class CR6JSingleLeptonBVetoLS(object):
    """The CR6JSingleLeptonBJet search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'CR6JSingleLeptonBVetoLS'
        self.dumper = dumper
    def __call__(self, tree):
        nLoose = tree.nMuonLoose + tree.nElectronLoose
        return tree.nJet >= 6  and tree.metFilter and tree.hadBoxFilter and tree.hadTriggerFilter and tree.nCSVL == 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 0 and tree.nElectronTight == 0 and nLoose > 0 and self.dumper.bdt() < -0.1 

class CR6JSingleLeptonBVetoHS(object):
    """The BJet search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'CR6JSingleLeptonBVetoHS'
        self.dumper = dumper
    def __call__(self, tree):
        nLoose = tree.nMuonLoose + tree.nElectronLoose
        return tree.nJet >= 6 and tree.metFilter and tree.hadBoxFilter and tree.hadTriggerFilter and tree.nCSVL == 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 0 and tree.nElectronTight == 0 and nLoose > 0 and self.dumper.bdt() >= -0.1 

class MuBox(object):
    """The Mu search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'Mu'
        self.dumper = dumper
    def __call__(self, tree):
        return tree.nJetNoLeptons >= 4 and tree.metFilter and tree.muBoxFilter and tree.muTriggerFilter and tree.nCSVM > 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 1 and tree.nElectronTight == 0 and tree.nMuonLoose == 1 and tree.nElectronLoose == 0

class CRMuBVetoBox(object):
    """The Mu search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'CRMuBVeto'
        self.dumper = dumper
    def __call__(self, tree):
        return tree.nJetNoLeptons >= 4 and tree.metFilter and tree.muBoxFilter and tree.muTriggerFilter and tree.nCSVL == 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 1 and tree.nElectronTight == 0 and tree.nMuonLoose == 1 and tree.nElectronLoose == 0            

class EleBox(object):
    """The Ele search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'Ele'
        self.dumper = dumper
    def __call__(self, tree):
        return tree.nJetNoLeptons >= 4 and tree.metFilter and tree.eleBoxFilter and tree.eleTriggerFilter and tree.nCSVM > 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 0 and tree.nElectronTight == 1 and tree.nMuonLoose == 0 and tree.nElectronLoose == 1

class CREleBVetoBox(object):
    """The Ele search box used in the analysis"""
    def __init__(self, dumper):
        self.name = 'CREleBVeto'
        self.dumper = dumper
    def __call__(self, tree):
        return tree.nJetNoLeptons >= 4 and tree.metFilter and tree.eleBoxFilter and tree.eleTriggerFilter and tree.nCSVL == 0 and tree.MR >= 350 and tree.RSQ >= 0.03 and\
            tree.nMuonTight == 0 and tree.nElectronTight == 1 and tree.nMuonLoose == 0 and tree.nElectronLoose == 1


class BJet:
    def __init__(self, pt, eta, btagv, partonFlavour):
        self.pt = pt
        self.eta = eta
        self.btagv = btagv
        self.partonFlavour = partonFlavour

