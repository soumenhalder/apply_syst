#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Soumen Halder

blue = "\033[1;34m"
end = "\033[0m"
red = "\033[1;31m"
import numpy as np
import root_pandas as pad
import pandas as pd
import glob
from tabulate import tabulate
import time

var1min = 'p_min' 
var1max = 'p_max'
var2min = 'cos_min'
var2max = 'cos_max'
var1_Ntuple = 'K_p' 
var2_Ntuple = 'K_costheta'
ignore= ['variable']

def bin_id(var1,var2, BIN1, BIN2,source = False,):
    """Returns the bin_id of a 2D histogram,

    Parameters:
    p (array)    : bin edge of first variable (take from systematics table)
    c (array)    : bin edge of second variable (take from systematics table)
    source (bool): systematics table (True) or ntuple of events (False by default)?

    Returns:
    binID [int, int]: returns bin id of these two variables

    """
    
    if source:
        # right = False by default but still its needed to show here, as because we are choosing lower 
        # bin to determine the bin_id of systematics table 
        d2 = np.digitize([var2 ], BIN2, right= False).tolist()[0]
        d1 = np.digitize([var1 ], BIN1, right= False).tolist()[0]
    else:
        # right = False is not necessary here for normal events. Because its very unlikely to 
        # fall momentum or polar angle at the edge of the bin and hence its kept undecided.
        d2 = np.digitize([var2 ], BIN2).tolist()[0]
        d1 = np.digitize([var1 ], BIN1).tolist()[0]

    return [d1,d2]

def systematics_table():
    """
    Return the systematics table in question
    """
    # Put the systematics table in this function,
    # For this particlular case there are two tables, for + and - ly charged particle, so I merged them.
    X1 = pd.read_csv('systematics_table/Rdtmc_keff_m_B0-6_all.log',dtype='str')
    X2 = pd.read_csv('systematics_table/Rdtmc_keff_p_B0-6_all.log',dtype='str')
    X = pd.concat([X1,X2])
    X = X.drop(ignore,axis=1).astype(float)
    
    # NOTE Step 1
    # find bins
    BIN1 = np.sort(np.unique(X[[var1min, var1max]].values))
    BIN2 = np.sort(np.unique(X[[var2min, var2max]].values))
    print('The bins are: ', BIN1, ' and \n ', BIN2)

    # NOTE Step 2.0
    X[['v1_binid','v2_binid']] = X.apply(lambda Z:bin_id(Z[var1min],Z[var2min], BIN1, BIN2, True ),axis=1,
                                       result_type="expand")
    return X, BIN1, BIN2

def analysis_ntuple(BIN1, BIN2):
    df = pad.read_root('ntuple.root',key='tree')
    # NOTE Step 2.1
    df[['v1_binid_k1','v2_binid_k1']] = df.apply(lambda Z:bin_id(Z[var1_Ntuple],Z[var2_Ntuple],  BIN1, BIN2)  ,axis=1, result_type="expand")
    return df.copy()

def test(syst,ntup, final):
    if ntup.shape[0] != final.shape[0]: 
        col = [ '__experiment__','__run__','__event__',var1_Ntuple ,var2_Ntuple]
        outoftable = pd.concat([ntup[col],final[col],final[col]]).drop_duplicates(keep=False)
        print(red,'There are %s candidates which are out of scope to assign weights which %s percent of total candidates'%(outoftable.shape[0],100*outoftable.shape[0]/ntup.shape[0]), end)
        print(tabulate(outoftable[col], headers = 'keys', tablefmt = 'psql'))
    
    ff = final[(final[var2_Ntuple] < final[var2max]) | (final[var2_Ntuple] > final[var2min])]
    a = pd.concat([final,ff,ff]).drop_duplicates(keep=False).shape[0]
    ff = final[(final[var1_Ntuple] < final[var1max]) | (final[var1_Ntuple] > final[var1min])]
    b = pd.concat([final,ff,ff]).drop_duplicates(keep=False).shape[0]
    if (a+b) != 0:
        print(red,"There are some issue, %s candidates having improper merging"%(a+b),end )

    List1 = list(syst['v1_binid'].value_counts())
    a = List1.count(List1[0]) == len(List1)
    List2 = list(syst['v2_binid'].value_counts())
    b = List2.count(List2[0]) == len(List2)
    if  (not a)  or  (not b) :
        print(red,'There are some issue with binning the systematics table. Two or more bins seems to come to a single one.', end)
        if not a:
            print(red,'p bins seems to be affected.',end)
        if not b:
            print(red,'c bins seems to be affected.',end)

if __name__ == "__main__":
    stime = time.time()

    # load systematics table
    syst, BIN1, BIN2 = systematics_table()

    # load analysis ntuple
    ntup = analysis_ntuple(BIN1, BIN2)

    #NOTE Step 3
    # Other than var1,var2 charge is also a binary factor of merging
    final = ntup.merge(syst,left_on=['v1_binid_k1','v2_binid_k1','K_charge'] ,right_on=['v1_binid','v2_binid','charge'])
    
    # Some cross checks
    test(syst, ntup,final)

    # Converting to root file
    outputfile = 'merged.root'
    final.to_root(outputfile,key='tree')
    print(blue,'\n\n\n\nYour final ntuple created in form of root file and saved as %s. Have a look'%(outputfile),end)
    print(tabulate(final.head(10), headers = 'keys', tablefmt = 'psql'))
    print('time taken: %s'%(time.time()-stime))
