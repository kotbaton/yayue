# See PyCharm help at https://www.jetbrains.com/help/pycharm/
#   noinspection PyUnresolvedReferences
#   infty = float('inf')

""" Main function of the MCMA: prepare the core model, define the work-space. """

# todo: check consistency of using scaled and not-scaled entities
# todo: add/print info:
#   on values of scaling coeffs.
#   A/R undefined for Pareto set corners (virtual solutions, i.e., no values of model variables)
#   size of cubes in scaled coordinates, values of A/R in native (model-vars) scales

# import sys		# needed for sys.exit()
# import os
# from os import R_OK, access
# from os.path import isfile
# import pandas as pd
# import pickle     # pickle does not process relations defined with decorations (without decorations processed ok)
# import dill  # stores and retrieves pyomo models into/from binary file
from datetime import datetime as dt
# from datetime import timedelta as td

from driver import *  # driver (run the analysis set-up and iterations)
from cfg import *  # configuration (dir/file location, parameter values, etc

# import from remote dir does no work
# sys.path.append('/Users/marek/Documents/GitHub/yayue/models/pipa/pipa0')
# sys.path.append('../pipa/pipa0')
# from sms import mk_sms as pipa_sms  # pipa, initial versions
# from inst import instance as pipa_ins  # ditto
# the below imports work, if files are in the same dir, the above needs to be explored/modified
# from sms import mk_sms as pipa_sms  # pipa, initial versions
# from inst import instance as pipa_ins  # ditto
# from t3sms import mk_sms as sms3  # tiny, testing model
# from t3inst import mk_inst as ins3  # ditto
# from t4conc import mk_conc as conc4  # tiny testing model, developed as concrete (without abstract)
# from tspipa import sbPipa as sbPipa  # sand-box tiny Pipa testing model, developed as concrete (without abstract)
# from tsjg1 import jg1 as jg1  # sand-box tiny jg1 model


# noinspection SpellCheckingInspection
if __name__ == '__main__':
    tstart = dt.now()
    # print('Started at:', str(tstart))

    # todo: enable the cli option for _usr specs
    # process the run configuration options and configure the working space
    ana_def = './Data/ana_dir.yml'    # yaml file defining the analysis directory
    config = Config(ana_def)    # process yaml config. file
    cfg = config.data   # dict with config. options

    # optional standard output redirection
    default_stdout = sys.stdout
    fn_name = cfg.get('fn_out')  # file-name for redirected stdout
    if fn_name is None:
        redir_stdo = False  # no redirection of stdout to a file
        fn_out = None
        f_out = None
    else:
        redir_stdo = True  # optional redirection of stdout to the stdOut file
        fn_out = f'{cfg.get("resDir")}{fn_name}'  # path to the file for redirected stdout
        # assert not os.path.exists(fn_out), f'Rename/remove the already used file: {fn_out}'
        print(f'Stdout redirected to: "{fn_out}".')
        f_out = open(fn_out, 'w')
        sys.stdout = f_out

    driver(cfg)  # driver and all classes get all needed info from the cfg dict

    tend = dt.now()
    print('\nStarted at: ', str(tstart))
    print('Finished at:', str(tend))
    time_diff = tend - tstart
    print(f'Wall-clock execution time: {time_diff.seconds} sec.')

    if redir_stdo:  # close the redirected output
        f_out.close()
        sys.stdout = default_stdout
        print(f'\nRedirected stdout stored in {fn_out}. Now writing to the console.')
        print('\nStarted at: ', str(tstart))
        print('Finished at:', str(tend))
        print(f'Wall-clock execution time: {time_diff.seconds} sec.')
