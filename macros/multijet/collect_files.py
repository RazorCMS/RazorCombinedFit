import eostools
import os.path

if __name__ == '__main__':

    topdir = "/store/cmst3/user/wreece/Razor2011/MultiJetAnalysis/scratch0/T2tt"
    root_files = eostools.ls(topdir)
    print root_files

    import pickle
    pickle.dump(root_files,file('root_files.pkl','wb'))
