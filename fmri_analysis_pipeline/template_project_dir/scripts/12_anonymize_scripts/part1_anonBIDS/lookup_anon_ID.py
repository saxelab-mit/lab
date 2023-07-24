#! /usr/bin/env python 

import pandas as pd
import sys

def mapID(sOrigID):
    df = pd.read_csv('./anon_ID_mapping.tsv', sep = '\t')
    newIDs = df[df.ORIG_ID==sOrigID].ANON_ID.unique()

    if newIDs.size > 1:
        return('WARNINGNOUNIQUEID')
    elif newIDs.size < 1:
        return('MISSINGLOOKUP')
    else:
        return(newIDs[0].replace("_",""))


def main():
    orig_id = sys.argv[1]
    print (mapID(orig_id))
    
if __name__ == '__main__':
    main()

