"""Script to combine data cards from two boxes"""
import sys
import os.path

if __name__ == '__main__':
    MODEL = sys.argv[1]
    DIR_HS = sys.argv[2]
    DIR_LS = sys.argv[3]

    if len(sys.argv) > 4:
        DIR_ELE = sys.argv[4]

    temp = DIR_HS.split('_')

    if MODEL == 'T1tttt':
        mass_range = range(400, 1425, 25)
    elif MODEL == 'T2tt':
        mass_range = range(150, 800, 25)

    if len(sys.argv) > 4:
        os.system('mkdir -p combine_files_%s_ELEHAD_%s_%s'
                  % (MODEL, temp[-2], temp[-1]))

        for mass in mass_range:
            FILE_LS = (DIR_LS + '/razor_combine_BJetLS_%s_%s.0_25.0.txt'
                       % (MODEL, mass))
            FILE_HS = (DIR_HS + '/razor_combine_BJetHS_%s_%s.0_25.0.txt'
                       % (MODEL, mass))
            FILE_ELE = (DIR_ELE + '/razor_combine_Ele_%s_%s.0_25.0.txt'
                        % (MODEL, mass))
            print FILE_LS, FILE_HS, FILE_ELE

            if os.path.isfile(FILE_LS) and os.path.isfile(FILE_HS)\
                    and os.path.isfile(FILE_ELE):
                os.system('combineCards.py %s %s %s > data_card_ELEHAD_%s.txt'
                          % (FILE_LS, FILE_HS, FILE_ELE, mass))
                os.system('combine -M Asymptotic data_card_ELEHAD_%s.txt '
                          '-n ELEHAD_%s_%s_25' % (mass, MODEL, mass))
                os.system('mv data_card_ELEHAD_%s.txt '
                          'combine_files_%s_ELEHAD_%s_%s/' %
                          (mass, MODEL, temp[-2], temp[-1]))
                os.system('mv higgsCombine* combine_files_%s_ELEHAD_%s_%s/' %
                          (MODEL, temp[-2], temp[-1]))
                os.system('rm roostats*')

    else:
        os.system('mkdir -p combine_files_%s_HAD_%s_%s'
                  % (MODEL, temp[-2], temp[-1]))

        for mass in mass_range:
            FILE_LS = (DIR_LS + '/razor_combine_BJetLS_%s_%s.0_25.0.txt'
                       % (MODEL, mass))
            FILE_HS = (DIR_HS + '/razor_combine_BJetHS_%s_%s.0_25.0.txt'
                       % (MODEL, mass))
            print FILE_LS, FILE_HS

            if os.path.isfile(FILE_LS) and os.path.isfile(FILE_HS):
                os.system('combineCards.py %s %s > data_card_HAD_%s.txt' %
                          (FILE_LS, FILE_HS, mass))
                os.system('combine -M Asymptotic data_card_HAD_%s.txt '
                          '-n HAD_%s_%s_25' % (mass, MODEL, mass))
                os.system('mv data_card_HAD_%s.txt '
                          'combine_files_%s_HAD_%s_%s/' %
                          (mass, MODEL, temp[-2], temp[-1]))
                os.system('mv higgsCombine* combine_files_%s_HAD_%s_%s/' %
                          (MODEL, temp[-2], temp[-1]))
                os.system('rm roostats*')
