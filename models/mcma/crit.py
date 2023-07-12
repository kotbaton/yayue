# import sys      # needed from stdout
# import os
# import numpy as np


class Crit:     # definition and attributes of a single criterion
    # see: ~/src/mcma/mc_defs.h for the corresponding C++ classes
    """Attributes of particular criterion."""
    def __init__(self, cr_name, var_name, typ):
        # Specified at criterion declaration: crit. name, core-model var., min or max.
        self.name = cr_name
        self.var_name = var_name
        if typ == 'min':
            self.attr = 'minimized'
            self.mult = -1.  # multiplier (used for simplifying handling)
        elif typ == 'max':
            self.attr = 'maximized'
            self.mult = 1.
        else:
            raise Exception(f'Unknown criterion type "{typ}" for criterion "{cr_name}".')
        # the below values shall be defined/updated when available
        self.sc_var = -1.   # scaling of the var value (for defining the corresponding CAF); negative means undefined
        self.is_active = None
        self.utopia = None  # set only once
        self.nadir = None   # checked, and possibly updated, every iteration, see self.updNadir()
        self.asp = None     # aspiration value (not scaled)
        self.res = None     # reservation value (not scaled)
        self.val = None     # last computed value
        #
        print(f"Criterion: name = '{cr_name}', var_name = '{var_name}', {self.attr} created.")

    def setUtopia(self, val):   # to be called only once for each criterion
        assert self.utopia is None, f'utopia of crit {self.name} already set.'
        self.utopia = val
        print(f'utopia of crit "{self.name}" set to {val}.')

    def updNadir(self, stage, val):
        """Update nadir value, if val is a better approximation."""
        if self.nadir is None or stage == 0:    # set initial value
            self.nadir = val
            print(f'nadir of crit "{self.name}" set to {val} ({stage = }).')
            return
        shift = False
        eps = 1.e-6     # margin to avoid setting to the same value
        old_val = self.nadir

        # stage 2: first appr. of nadir, regularized selfish opt. for each crit. in a row
        # tigthen (move closer to U) "too bad" value from selfish opt. in stage 1
        if stage == 2:
            if self.mult == 1:  # max-crit, tight to larger values
                if old_val + eps < val:
                    shift = True    # move closer to U
            else:       # min-crit, tight to smaller values
                if old_val - eps > val:
                    shift = True     # move closer to U
        # in stages: 1, 3, and RFP: relax (move away from U) "too tight" values (from previous appr.)
        # in stage 1 (selfish opt.): just collect worst values of each criterion
        # in stage 3: 2nd stage on nadir appr.: apply AF with only one criterion active
        # in stages >= 4: RFP, AF defined by preferences (A, R, activity) set for each criterion
        else:
            if self.mult == 1:  # max-crit, relax to smaller values
                if old_val - eps > val:
                    shift = True     # move away from U
            else:       # min-crit, relax to the larger val
                if old_val + eps < val:
                    shift = True     # move away from U

        if shift:
            self.nadir = val    # set val as new nadir appr.
            no_yes = ''
        else:
            no_yes = 'not'

        print(f'nadir appr. of crit "{self.name}": {old_val} {no_yes} changed to {val} (in {stage=}).')
