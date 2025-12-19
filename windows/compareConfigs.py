# copyright Mark McIntyre, 2025-

# script to compare two RMS config files 

import sys
from configparser import ConfigParser


def compareSection(cfg1, cfg2, sectionName):
    for rec in cfg1[sectionName]:
        if rec not in cfg2[sectionName]:
            print(f'{rec} missing from [{sectionName}] in right file')
        else:
            val1 = cfg1[sectionName][rec]
            val2 = cfg2[sectionName][rec]
            if val1 != val2:
                print(f'{rec} in [{sectionName}] differs - {val1} vs {val2}')
    
    for rec in cfg2[sectionName]:
        if rec not in cfg1[sectionName]:
            print(f'{rec} missing from [{sectionName}] in left file')
    return 


if __name__ == '__main__':
    src = sys.argv[1]
    targ = sys.argv[2]
    cfg1 = ConfigParser()
    cfg1.read(src)
    cfg2 = ConfigParser()
    cfg2.read(targ)
    for sec in cfg1.sections():
        if sec not in cfg2:        
            print(f'section [{sec}] missing from {targ}')
        compareSection(cfg1, cfg2, sec)
