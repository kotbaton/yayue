"""
Handling of the CAF-PWL
"""


# noinspection PySingleQuotedDocstring
class PWL:  # representation of caf(x) for i-th criterion
    def __init__(self, mc, i, verb=-1):
        # todo: implement assumptions:
        #   actually we need only A (use U, if not provided) and R (use N, if not provided)
        #   remove/ignore A, if too close to U, ditto for R
        #   handle (report as error?, ignore iter?) close A & R
        #   ditto steep and flat slopes
        self.mc = mc    # CtrMca object
        self.cr = mc.cr[i]  # cr: specs of a criterion
        self.cr_name = self.cr.name
        self.is_act = self.cr.is_active
        self.is_fx = self.cr.is_fixed
        self.is_max = self.cr.mult == 1  # 1 for max-crit, -1 for min.
        self.is_asp = self.cr.asp is not None   # Asp. defined?
        self.is_res = self.cr.res is not None   # Res. defined?
        self.is_nadir = self.cr.nadir is not None   # Nadir defined?
        self.verb = verb
        self.asp_val = self.cr.utopia
        self.res_val = self.cr.nadir
        self.up_seg = False   # if True, then generate up-PWL segment
        self.lo_seg = False   # if True, then generate lo-PWL segment
        # self.vert_x = []    # x-values of vertices
        # self.vert_y = []    # y-values of vertices
        self.chk_ok = self.chk_param()

    # noinspection PyUnreachableCode
    def chk_param(self):
        if self.verb < 0:
            self.verb = self.mc.verb

        if 0 < self.verb > 1:
            # todo: cannot format None; either tolerate not formatted or modify to differentiate formatting of elements
            #   f"U = {self.cr.utopia:.2e}, A = {self.cr.asp:.2e}, R = {self.cr.res:.2e}, "
            #   f"N = {self.cr.nadir:.2e}.")
            print(f"\n----\nPWL crit '{self.cr_name}': act/fix = {self.is_act}/{self.is_fx}, is_max = {self.is_max}, "
                  f"U = {self.cr.utopia}, A = {self.cr.asp}, R = {self.cr.res}, N = {self.cr.nadir}.")

        # at least two (out of U, A, R, N) are needed
        assert self.cr.utopia is not None, f'PWL ctor: utopia of criterion "{self.cr_name}" is undefined.'
        assert self.is_res or self.is_nadir, f'Criterion {self.cr_name}: neither reservation nor nadir defined.'

        if self.is_nadir:
            maxVal = max(abs(self.cr.utopia), (abs(self.cr.nadir)))  # value used as basis for min-differences
        else:
            maxVal = max(abs(self.cr.utopia), (abs(self.cr.res)))  # value used as basis for min-differences
        minDiff = self.mc.minDiff * maxVal
        # check if U (set in ctor) can be replaced by the provided A
        if self.is_asp:
            if abs(self.cr.utopia - self.cr.asp) > minDiff:
                assert self.cr.isBetter(self.cr.utopia, self.cr.asp), f'crit {self.cr_name} (is_max {self.is_max}): '
                f' A {self.cr.asp:.2e} is worse than U {self.cr.utopia:.2e}.'
                self.asp_val = self.cr.asp
                self.up_seg = True
            else:
                if self.verb > 1:
                    print(f'crit {self.cr_name}: ignoring A {self.cr.asp:.2e} as too close to U {self.cr.utopia:.2e}. '
                          f'U used as A.')
                self.is_asp = False     # ignore A, too close to U

        # check if N (set in ctor) can be replaced by the provided R
        if self.is_res and self.is_nadir:
            if abs(self.cr.nadir - self.cr.res) > minDiff:
                assert self.cr.isBetter(self.cr.res, self.cr.nadir), f'crit {self.cr_name} (is_max {self.is_max}): '
                f' R {self.cr.res:.2e} is worse than N {self.cr.nadir:.2e}.'
                self.res_val = self.cr.res
                self.lo_seg = True
            else:
                if self.verb > 1:
                    print(f'crit {self.cr_name}: ignoring R {self.cr.res:.2e} as too close to N {self.cr.nadir:.2e}. '
                          f'N used as R.')
                self.is_res = False     # ignore R, too close to N

        # check, if the selected A/R (replaced, if required, by U/N) sufficiently differ
        if abs(self.asp_val - self.res_val) < minDiff:
            print(f'crit {self.cr_name}: the provided A/R pair ({self.asp_val:.2e}, {self.res_val:.2e}) is too close '
                  f'to define a PWL.')
            return False

        return True

        '''
        assert self.cr.isBetter(self.cr.utopia, self.cr.res), f'R {self.cr.res} must be worse than U {self.cr.utopia}.'
        assert self.cr.isBetter(self.cr.utopia, self.cr.nadir), f'N {self.cr.nadir} must be worse than U ' \
            f'{self.cr.utopia}.'
        assert self.cr.isBetter(self.cr.asp, self.cr.res), f'R {self.cr.res} must be worse than A {self.cr.asp}.'
        assert self.cr.isBetter(self.cr.asp, self.cr.nadir), f'N {self.cr.nadir} must be worse than A {self.cr.asp}.'
        assert self.cr.isBetter(self.cr.res, self.cr.nadir), f'N {self.cr.nadir} must be worse than R {self.cr.res}.'
        # the below relations introduced due to both numerical and methodological reasons
        assert self.mc.diffOK(i, self.cr.utopia, self.cr.nadir), f'utopia {self.cr.utopia:.2e} and nadir ' \
            f'{self.cr.nadir:.2e} closer than {minDiff:.1e}. Criterion "{self.cr.name}" unsuitable for MCA.'
        if self.is_asp and not self.mc.diffOK(i, self.cr.utopia, self.cr.asp):
            self.is_asp = False
            if self.verb > 2:
                print(f'\tA {self.cr.asp} ignored: it is too close to U {self.cr.utopia}.')
        if self.is_res and self.is_nadir and not self.mc.diffOK(i, self.cr.nadir, self.cr.res):
            self.is_res = False
            if self.verb > 2:
                print(f'\tR {self.cr.res} ignored: it is too close to N {self.cr.nadir}.')

        self.set_vert()  # define coordinates of the vertices

    # todo: simplify vertices (actually only two are needed!)
    def set_vert(self):  # define coordinates of the vertices
        self.vert_x.append(self.cr.utopia)
        self.vert_y.append(self.mc.cafAsp)     # the value shall be replaced/ignored, if is_asp == True
        # points defining "too close" (in terms of x) vertices are removed in the ctor
        if self.is_asp:
            self.vert_x.append(self.cr.asp)
            self.vert_y.append(self.mc.cafAsp)
        if self.is_res:
            self.vert_x.append(self.cr.res)
            self.vert_y.append(0)
        if self.is_nadir:
            self.vert_x.append(self.cr.nadir)
            self.vert_y.append(0)   # the value shall be later replaced or ignored, if is_res == True
        if self.verb > 2:
            print(f"PWL of crit. '{self.cr.name}' has {len(self.vert_x)} vertices: x = {self.vert_x}, "
                  f"y = {self.vert_y}")
        '''

    def segments(self):
        # start with the middle segment defined by the pair (self.asp_val, self.res_val) set in chk_param()
        '''
        if self.is_asp:
            x1 = self.vert_x[1]     # utopia not defining mid-segm, if A defined
            y1 = self.vert_y[1]
            x2 = self.vert_x[2]     # second mid-segment point is either R or Nadir (if R not defined)
            y2 = self.vert_y[2]
        else:
            x1 = self.vert_x[0]     # utopia defines mid-segment, if A is not defined
            y1 = self.vert_y[0]
            x2 = self.vert_x[1]     # second mid-segment point is either R or Nadir (if R not defined)
            y2 = self.vert_y[1]
        '''
        # print(f'mid_slope for crit. "{self.cr_name}": is_asp {self.is_asp}, x1 = {x1:.2e}, x2 = {x2:.2e}')
        ab = []     # list of (a, b, sc) parameters of segments, each defining line: y = ax + b, and core-var scaling
        x1 = self.asp_val   # serves as A
        x2 = self.res_val   # serves as R
        y1 = self.mc.cafAsp  # y(A)
        y2 = 0.  # y(R) = 0.
        y_delta = y1 - y2
        if self.mc.scVar:   # PWL based on scaled core-model var defining the criterion
            var_sc = y_delta / abs(x1 - x2)      # scaling coef. of the core-model var defining the criterion
            x1 *= var_sc
            x2 *= var_sc
            # mid_slope = 1.    # the calculated below should be close to 1,
            # mid_slope = self.cr.mult * y_delta / (var_sc * x_delta)     # negative for min.-criterion
        else:       # PWL based on NOT scaled core-model var
            var_sc = 1.

        x_delta = x1 - x2
        mid_slope = y_delta / x_delta
        # todo: define sensible values of mmin/max_slope
        min_slope = 1.e-8
        max_slope = 1.e6
        if abs(mid_slope) < min_slope or abs(mid_slope) > max_slope:
            print(f'\nNumerical problem in defining mid_slope for crit. "{self.cr_name}": is_asp {self.is_asp}, '
                  f'is_res {self.is_res},\n\tx1 = {x1:.3e}, x2 = {x2:.3e}, y1 = {y1:.2e}, y2 = {y2:.2e}')
            print(f'slope {mid_slope:.2e}, min_slope {min_slope:.2e}, max_slope {max_slope:.2e}.')
            print('PWL not generated.')
            # mid_slope = 100.    # rather give-up than attempt to redefine the slope
            return None, None

        # see: Bronsztejn p. 245
        b = y1 - mid_slope * x1     # alternatively: b = y2 - slope * x2
        ab.append([mid_slope, b])   # mid-segment is first in the list of segment specs.
        if self.verb > 2:
            print(f'Middle PWL segment is defined by: ({x1:.2e}, {y1:.2e}) and ({x2:.2e}, {y2:.2e}).')
            print(f'params of the mid-segment line y = ax + b: a = {mid_slope:.2e}, b = {b:.2e}, var_sc = {var_sc:2e}.')

        # assert len(self.vert_x) == 2, f'Processing PWL having {len(self.vert_x)} vertices not implemented yet.'
        # segments above A (if A defined) and below R (if R defined and not used for mid-segment):
        # defined using: one point and slope; the latter more flat or steep than mid-segment slope, for
        # segments above A and below R, respectively.

        if self.is_asp:  # generate segment above Asp
            up_slope = mid_slope / self.mc.slopeR    # flatter than mid_slop
            up_b = y1 - up_slope * x1  # defined as above but by A point
            ab.append([up_slope, up_b])  # up-segment is second (if generated) in the list of segment specs.
            if self.verb > 2:
                print(f'params of up-segment line y = ax + b: a = {up_slope:.2e}, b = {b:.2e}, var_sc = {var_sc:.2e}.')
        else:
            if self.verb > 2:
                print(f'upper segment of PWL not generated.')

        if self.is_res:  # generate segment below Res
            lo_slope = mid_slope * self.mc.slopeR    # steeper than mid_slop
            lo_b = y2 - lo_slope * x2  # defined as above but by R point
            ab.append([lo_slope, lo_b])  # lo-segment is next (either third or second) in the list of segment specs.
            if self.verb > 2:
                print(f'params of lo-segment line y = ax + b: a = {lo_slope:.2e}, b = {b:.2e}, var_sc = {var_sc:.2e}.')
        else:
            if self.verb > 2:
                print(f'lower segment of PWL not generated.')

        return var_sc, ab

        # noinspection PyUnreachableCode
        '''
        # alternative/complementary approaches by use of the pe PWL
        # not used but kept for possible future exploration/use
        
        # see the 6.6.1 p.28 for (cryptic) description of parameters of pe.Piecewise()
        # p = pe.Piecewise(...)

        import pyomo.core as pcore
        (code, slopes) = pcore.kernel.piecewise_library.util.characterize_function(pwl_x, pwl_y)
        # https://pyomo.readthedocs.io/en/stable/library_reference/kernel/piecewise/util.html
        # codes: 1: affine, 2: convex 3: concave 4: step 5: other
        print(f'\n{code=}, {slopes=}')

        import pyomo.kernel as pmo  # more robust than using import *
        # (code, slopes) = pmo.characterize_function(pwl_x, pwl_y)  # does not work
        # (code, slopes) = pmo.piecewise.characterize_function(pwl_x, pwl_y)  # does not work
        # (code, slopes) = pmo.characterize_function(pwl_x, pwl_y)  # neither pmo. nor pe. works

        # pmo.piecewise requires pmo vars?
        # x = pmo.Var(bounds=(0., 1000.))
        # x = pmo.Var(bounds=(None, None))
        # m.x = pmo.variable()
        # m.y = pmo.variable()
        m.y = pe.Var()
        m.goal = pe.Objective(expr=m.y, sense=pe.maximize)
        m.goal.activate()  # objective of m1 block is deactivated
        m.p = pmo.piecewise(pwl_x, pwl_y, input=m1_var, output=m.y, repn='cc', bound='eq',
                            require_bounded_input_variable=False)   # does not work
        print(f'{m.p = }, {type(m.p)}')
        # m.p.display()     # not supported
        # m.p.pprint()     # not supported
        # m.p.validate()    # validation fails: it considers m_var to be unbounded

        '''
