"""Matouqin model generator"""
import pyomo.environ as pe      # more robust than using import *


'''
class Model:    # keep or not
    def __init__(self, verb=True):
        self.verb = verb        # output verbosity
        self.mc = mc      # define persistent elements if desired for running the model with modified params
'''


def mk_model():      # p: model parameters prepared in the Params class
    m = pe.AbstractModel('Matouqin v. 0.1')   # instance of the concrete model
    # print(f'Generating AbstractModel model for parameters (version: {p.ver}')

    # print(f'Dictionary of prepared parameters contains  {len(p.cat)} items.')

    # print(f'xx = {p.xx}')
    '''
    @m.Constraint(m.C)
    def xLink(mx, ii):  # link the corresponding m1 and mc_core variables
        return mx.x[ii] == p.eff.get('el2h') * mx.y[ii]
    # def link_rule(m, i):  # traditional (without decorations) constraint using a rule, just for illustration
    #     return m.x[i] == m.m1_cr_vars[i]
    # m.xLink = pe.Constraint(m.C, rule=link_rule)

    # AF and m1_vars defined above
    m.caf = pe.Var(m.C)    # CAF value
    m.cafMin = pe.Var()     # min of CAFs

    @m.Constraint(m.C)
    def cafMinD(mx, ii):
        return mx.cafMin <= mx.caf[ii]

    @m.Objective(sense=pe.maximize)
    def obj(mx):
        return mx.cafMin

    if self.verb:
        m.pprint()
    '''

    # sets
    # noinspection SpellCheckingInspection
    m.Se = pe.Set()     # set of rlectrolyzer
    m.Sh = pe.Set()     # set of hydrogen tanks
    m.Sc = pe.Set()     # set of fuel cell
    m.S = pe.Set()    # a composed set of storage devices
    m.nHrs = pe.Param(domain=pe.PositiveIntegers, default=10)       # the number of hours (time periods) in a year
    m.nHrs_ = pe.Param(initialize=(m.nHrs_value - 1))     # index of the last time periods (hour)
    m.T = pe.RangeSet(0, m.nHrs_)       # set of time periods (hour)

    # define variables needed for demonstrating decorators
    # decision variables
    m.Num = pe.Var(m.S, within=pe.NonNegativeIntegers)      # number of units of s-th storage device
    m.supply = pe.Var(within=pe.NonNegativeReals)       # energy committed to be provided in each hour, [MWh]

    # control variables
    m.dOut = pe.Var(m.T, within=pe.NonNegativeReals)        # electricity directly meet the commitment, [MWh]
    m.sIn = pe.Var(m.T, within=pe.NonNegativeReals)     # electricity inflow redirected to storage, [MWh]
    m.ePrs = pe.Var(m.T, within=pe.NonNegativeReals)        # electricity used to make high pressure, [MWh]
    m.sOut = pe.Var(m.T, within=pe.NonNegativeReals)        # electricity from storage to meet commitment, [MWh]
    m.eIn = pe.Var(m.Se, m.T, within=pe.NonNegativeReals)       # electricity inflow to each electrolyzer,[MWh].
    m.eSurplus = pe.Var(m.T, within=pe.NonNegativeReals)        # the loss of electricity while overproduction.
    m.eBought = pe.Var(m.T, within=pe.NonNegativeReals)     # amount of electricity bought on the market
    m.hIn = pe.Var(m.Sh, m.T, within=pe.NonNegativeReals)       # hydrogen inflow to each hydrogen tank, [kg]
    m.hOut = pe.Var(m.Sh, m.T, within=pe.NonNegativeReals)      # hydrogen outflow from each hydrogen tank, [kg]
    m.hVol = pe.Var(m.Sh, m.T, within=pe.NonNegativeReals)      # amount of hydrogen stored in s-th device
    m.hInc = pe.Var(m.Sc, m.T, within=pe.NonNegativeReals)      # hydrogen inflow to each fuel cell, [kg]
    m.cOut = pe.Var(m.Sc, m.T, within=pe.NonNegativeReals)      # electricity outflow from each fuel cell, [MWh]

    # Outcome variables
    m.revenue = pe.Var(within=pe.Reals)     # the annual revenue of the system
    m.income = pe.Var(within=pe.Reals)      # the annual income from satisfying the commitment
    m.invCost = pe.Var(within=pe.Reals)     # the annualized investment cost of the storage system
    m.balCost = pe.Var(within=pe.Reals)     # the cost of management of electricity surplus and shortage
    m.OMC = pe.Var(within=pe.Reals)     # the operation and maintenance costs

    # Auxiliary variables
    m.sCap = pe.Var(m.S, within=pe.NonNegativeReals)        # total capacity of ，总容量 s-th type of storage devices
    m.hMin = pe.Var(m.Sh, within=pe.NonNegativeReals)       # the lowest hydrogen needed in s-th type of tank
    m.mxIn = pe.Var(m.S, within=pe.NonNegativeReals)        # the maximum hydrogen inflow of s-th tank (per hour)
    m.mxOut = pe.Var(m.S, within=pe.NonNegativeReals)       # the maximum hydrogen outflow of s-th tank (per hour)
    m.h2T = pe.Var(m.T, within=pe.NonNegativeReals)     # total amount of hydrogen produced by all electrolyzer
    m.h2C = pe.Var(m.T, within=pe.NonNegativeReals)     # total amount of hydrogen from hydrogen tanks to fuel cells

    # parameters
    m.inflow = pe.Param(m.T, domain=pe.NonNegativeReals)     # amount of electricity incoming to the site
    m.mxCap = pe.Param(m.S, domain=pe.NonNegativeReals)     # unit storage capacity of each storage device
    m.hMxIns = pe.Param(m.Sh, domain=pe.NonNegativeReals)       # maximum hydrogen incoming to the tank [kg]
    m.hMxOut = pe.Param(m.Sh, domain=pe.NonNegativeReals)       # maximum hydrogen outflow from the tank [kg]
    m.hmi = pe.Param(m.Sh, domain=pe.NonNegativeReals)      # minimum hydrogen needed in hydrogen tank [kg]
    m.eh2 = pe.Param(m.Sh, domain=pe.NonNegativeReals)      # converting electricity to hydrogen, [kg/MWh]
    m.eph2 = pe.Param(m.Sh, domain=pe.NonNegativeReals)     # making high pressure, [MWh/kg]
    m.h2Res = pe.Param(m.Sh, domain=pe.NonNegativeReals)        # hydrogen retention rate, unit in percentage
    m.h2e = pe.Param(m.Se, domain=pe.NonNegativeReals)      # converting hydrogen to electricity [MWh/kg]
    m.Hrs = pe.Param(domain=pe.NonNegativeIntegers)     # the number of hours in a year
    m.ann = pe.Param(m.S, domain=pe.NonNegativeReals)       # annualization factor
    m.ePrice = pe.Param(domain=pe.NonNegativeReals)     # purchase price of buying electricity, [million RMB/MWh]
    m.overCost = pe.Param(domain=pe.NonNegativeReals)       # unit price of electricity surplus, [million RMB]
    m.sInv = pe.Param(m.S, domain=pe.NonNegativeReals)      # per unit investment cost of storage, [million RMB]
    m.Omc = pe.Param(m.S, domain=pe.NonNegativeReals)       # per unit operation cost of storage, [million RMB]

    # relations defining energy flows
    @m.Constraint(m.T)      # energy inflow is divided into four energy flows
    def inflow_blc(mx, t):
        return mx.inflow[t] == mx.dOut[t] + mx.sIn[t] + mx.Prs[t] + mx.Surplus[t]

    @m.Constraint(m.T)      # total electricity used to store hydrogen equal to the sum of inflows to electrolyzers
    def sin_blc(mx, t):
        return mx.sIn[t] == sum(mx.eIn[s, t] for s in mx.Se)

    @m.Constraint(m.Se, m.T)        # Inflows to all electrolyzers are constrained by the sum of their capacities
    def ein_upper(mx, s, t):
        return mx.eIn[s, t] <= mx.sCap[s]

    @m.Constraint(m.T)      # The amount of hydrogen produced by all electrolyzers
    def h2t_blc1(mx, t):
        return mx.h2T[t] == sum(mx.eh2[s] * mx.eIn[s, t] for s in mx.Se)

    @m.Constraint(m.T)      # Produced hydrogen is split between tanks
    def h2t_blc2(mx, t):
        return mx.h2T[t] == sum(mx.hIn[s, t] for s in mx.Sh)

    @m.Constraint(m.T)      # The amount of electricity used for pressure control of all hydrogen tanks
    def ePrs_blc(mx, t):
        return mx.ePrs[t] == sum(mx.eph2[s] * mx.hIn[s, t] for s in mx.Sh)

    @m.Constraint(m.Sh, m.T)        # Amount of hydrogen in each tank type
    def hVol_bal(mx, s, t):
        return mx.hVol[s, t] == mx.h2Res[s] * mx.hVol[s, (t-1)] + mx.hIn[s, t] - mx.hOut[s, t]

    @m.Constraint(m.Sh, m.T)        # Amount of hydrogen in tanks of each type
    def hVol_bon(mx, s, t):
        return mx.hMin[s] <= mx.hVol[s, t] <= mx.sCap[s]

    @m.Constraint(m.Sh, m.T)        # Maximum flow to each type of tank
    def hIn_upper(mx, s, t):
        return mx.hIn[s, t] <= mx.mxIn[s]

    @m.Constraint(m.Sh, m.T)        # Maximum flow from each type of tank to fuel cells
    def hOut_upper(mx, s, t):
        return mx.hOut[s, t] <= mx.mxOut[s]

    @m.Constraint(m.T)      # Hydrogen flow from tanks to all fuel cells
    def h2C_blc1(mx, t):
        return mx.h2C[t] == sum(mx.hOut[s, t] for s in mx.Sh)

    @m.Constraint(m.T)      # Hydrogen flow from tanks is split between fuel cells
    def h2C_blc2(mx, t):
        return mx.h2C[t] == sum(mx.hInc[s, t] for s in mx.Sc)

    @m.Constraint(m.T)      # The committed supply is composed of three parts
    def supply_blc(mx, t):
        return mx.supply == mx.dOut[t] + mx.sOut[t] + mx.eBought[t]

    @m.Constraint(m.T)      # electricity outflow from the storage is defined by the sum of outflows from fuel cells
    def sOut_blc(mx, t):
        return mx.sOut[t] == sum(mx.cOut[s, t] for s in mx.Sc)

    @m.Constraint(m.Sc, m.T)        # The electricity from fuel cells
    def cOut_blc(mx, s, t):
        return mx.cOut[s, t] == mx.h2e[s] * mx.hInc[s, t]

    @m.Constraint(m.Sc, m.T)        # The electricity outflow from the fuel cell
    def eOut_upper(mx, s, t):
        return mx.cOut[s, t] <= mx.sCap[s]

    # relations defining outcome variables
    @m.Constraint()     # Income from supplying
    def incomeC(mx):
        return mx.income == mx.ePrice * mx.nHrs * mx.supply

    @m.Constraint()     # Annualized investment cost of the storage system
    def invCostC(mx):
        return mx.invCost == sum(mx.ann[s] * mx.sInv[s] * mx.sNum[s] for s in mx.S)

    @m.Constraint()     # Operation and maintenance cost of the storage system
    def OMCC(mx):
        return mx.OMC == sum(mx.sOmc[s] * mx.sNum[s] for s in mx.S)

    @m.Constraint()     # Cost of balancing surplus and deficit
    def balCostC(mx):
        return (mx.balCost == mx.overCost * m.Hrs * sum(m.eSurplus[t] for t in mx.T) +
                mx.eBprice * mx.Hrs * sum(m.eBought[t] for t in mx.T))

    @m.Objective(sense=pe.maximize)     # Revenue (used as a Goal-Function/Objective in single-criterion analysis)
    def obj(mx):
        return mx.revenue == mx.income - mx.invCost - mx.OMC - mx.balCost

    print('mk_sms(): finished')
    # m.pprint(）
    return m
