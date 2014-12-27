"""Script to combine data cards from two boxes"""
import sys
import os.path

if __name__ == '__main__':
    MODEL = sys.argv[1]
    DIR_HS = sys.argv[2]
    DIR_LS = sys.argv[3]

    temp = DIR_HS.split('_')

    if MODEL == 'T1tttt':
        mass_range = range(400, 1425, 25)
    elif MODEL == 'T2tt':
        mass_range = range(150, 800, 25)

    os.system('mkdir -p Tests/combine_files_%s_BJetHS_%s_%s'
              % (MODEL, temp[-2], temp[-1]))

    for mass in mass_range:
        FILE_LS = (DIR_LS + '/razor_combine_BJetHS_%s_%s.0_25.0.txt'
                   % (MODEL, mass))
        FILE_HS = (DIR_HS + '/razor_combine_BJetHS_%s_%s.0_25.0.txt'
                   % (MODEL, mass))
        print FILE_LS, FILE_HS

        if os.path.isfile(FILE_LS) and os.path.isfile(FILE_HS):
            os.system('combineCards.py %s %s > data_card_BJetHS_%s.txt' %
                      (FILE_LS, FILE_HS, mass))
            os.system('combine -M Asymptotic data_card_BJetHS_%s.txt '
                      '-n BJetHS_%s_%s_25' % (mass, MODEL, mass))
            os.system('mv data_card_BJetHS_%s.txt '
                      'Tests/combine_files_%s_BJetHS_%s_%s/' %
                      (mass, MODEL, temp[-2], temp[-1]))
            os.system('mv higgsCombine* Tests/combine_files_%s_BJetHS_%s_%s/' %
                      (MODEL, temp[-2], temp[-1]))
            os.system('rm roostats*')
