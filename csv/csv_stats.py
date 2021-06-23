####### PACKAGES
import pandas as pd
import sys
import numpy as np

"""
 A module to perform some analysis on dataframes and csv files
"""


def do_csv_stat(fname=None,**kwargs):
    """
        Reads a csv into a dataframe to perform the analysis
        cf do_dataframe_stats
    """

    if fname is None:
        raise ValueError("Incorrect input : please provide filename")

    try:
        df = pd.read_csv(fname, index_col=0)
    except:
        raise ValueError("Enable to open file %s" %fname)

    return do_dataframe_stats(dataframe=df, **kwargs)


def identity(x):
    return x


def do_dataframe_stats(dataframe=None,cat=None,obs=None,filters=None,measures=None):
    """
        Reads a dataframe and averages observables (obs) for several categories (cat).
            obs and cat are lists of column names
            filters is a dictionary of filters functions
            measures is a dict of function dictionaries

        a list of cases is established according to the unique (filtered) values in categories
        for each case, a measure is computed
            by default mean and stddev, but other operations can be specified in measures

        filters is a dictionary { catergory_i : function, ...}
        measures is a dict of dicts :
            {observable_i : {measure_1 : function, measure_2 : function, ... measure_k : function } , ... }
        outputs a dataframe
    """

    df = dataframe
    if df is None:
        raise ValueError("Incorrect input : please provide a dataframe")
    if cat is None and obs is None:
        raise ValueError("Incorrect input : please provide categories and/or observables")

    if obs is None:
        obs = [ col for col in df.columns if col not in cat]

    if cat is None:
        cat = [ col for col in df.columns if col not in obs]

    # By default, filter for each category is identity
    filtre = {}
    for sel in cat:
        filtre[sel] = identity
    if filters is not None:
        filtre.update(filters)

    # By default, returns mean and std dev of observable
    mesure = {}
    for av in obs:
        mesure[av] = {"%s_mean"%av : np.mean, "%s_std"%av: np.std }
    if measures is not None:
        mesure.update(measures)

    # Here we identify all unique combination of categories
    cats = [np.sort(np.unique(filtre[sel](df[sel].to_numpy()))) for sel in cat]
    combis, n_combis = make_combinations(cats)

    chosen = None
    frames = []
    # for each unique combination
    for i in range(n_combis):
        comb = combis[:,i]
        dict = {}
        for j,name in enumerate(cat):
            val = comb[j]
            dict[name] = val
            if j==0:
                chosen = ( df[name] == val )
            else:
                chosen = (chosen & (df[name] == val) )
        # we have identified the lines corresponding to the specific unique combination of categories
        subdf = df.loc[chosen]

        # Now we perform the operation on this sub-dataframe
        for col in obs:
            try:
                values = subdf[col].to_numpy()
                mes = mesure[col]
                for key in mes.keys():
                    dict[key] = mes[key](values)
            except:
                pass
        # We add it to a temporary store of dataframes
        frames.append(pd.DataFrame(dict,index=[i]))

    # Now we concatenate the list of dataframes
    assembled = pd.concat(frames)

    return assembled


def make_combinations(cats):
    ncat = len(cats)
    lens = [len(cat) for cat in cats]
    n_s = np.product(lens)
    combis = np.ndarray((ncat, n_s))
    set = np.zeros((ncat, 1), dtype=int)
    i = 0
    while i < n_s:
        combis[:, i] = np.array([cats[i][int(s)] for i, s in enumerate(set[:, 0])])
        # updating
        i += 1
        if i < n_s:
            set = update_set(set, lens)
    return combis, n_s


def update_set(set, lens):
    found = False
    d=-1
    while not found:
        d+=1
        if set[d, 0] < (lens[d] - 1):
            set[d] += 1
            found = True
            for dd in range(d):
                set[dd] = 0
    return set


if __name__ == "__main__":
    """
    $ csv_stats.py FILE.CSV [-cat NAME_1 [NAME_2 ... NAME_N]] [-obs OBS_1 [OBS_2 ... OBS_M]] [-out FILE_OUT.CSV]
    Computes averages of certain observables in a csv file according to certain categories
        Categories are chosen from the CSV column names specified by NAME_1, NAME_2, ..., NAME_N
        Observables are chosen from the CSV column name specified by OBS_1, OBS_2, ..., OBS_M
    categories and/or observables should be specified but not neither
    """

    args = sys.argv[1:]
    fname = args[0]

    cat = None
    obs = None

    # mode is 0 for unset, 1 for cat, 2 for obs, 3 for out
    mode = 0

    outname = "stats.csv"
    for arg in args[1:]:
        if arg.startswith("-cat"):
            cat = []
            mode = 1
        elif arg.startswith("-obs"):
            obs = []
            mode = 2
        elif arg.startswith("-out"):
            mode = 3
        else:
            if mode == 1:
                cat.append(arg)
            elif mode == 2:
                obs. append(arg)
            elif mode == 3:
                outname = arg

    assembled = do_csv_stat(fname=fname,cat=cat,obs=obs)
    assembled.to_csv(outname)

    



