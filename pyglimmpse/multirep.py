import warnings

import numpy as np

from pyglimmpse.constants import Constants
from pyglimmpse.finv import finv
from pyglimmpse.probf import probf
from pyglimmpse.glmmpcl import glmmpcl

def _hlt(rank_C, rank_U, rank_X, total_N, eval_HINVE, df2Method):
    """
    shell function for hotelling lawley traces.
    :param rank_C:
    :param rank_U:
    :param rank_X:
    :param total_N:
    :param eval_HINVE:
    :return:
    """
    min_rank_C_U = min(rank_C, rank_U)
    df1 = rank_C * rank_U
    df2 = df2Method()

    if df2 <= 0 or np.isnan(eval_HINVE[0]):
        power = float('nan')
        warnings.warn('PowerWarn15: Power is missing because because the noncentrality could not be computed.')
    else:

    power, fmethod = _multi_power(Scalar.alpha, df1, df2, omega)
    power_l, power_u, fmethod_l, fmethod_u, noncen_l, noncen_u = glmmpcl(Scalar.alpha, df1, total_N, df2,
                                                                         CL.cl_type, CL.n_est, CL.rank_est,
                                                                         CL.alpha_cl, CL.alpha_cu, Scalar.tolerance,
                                                                         power, omega)
    return {'lower': power_l, 'power': power, 'upper': power_u}


def hltOneMomentNullApproximator(rank_C, rank_U, rank_X, total_N, eval_HINVE ):
    """
    This function calculates power for Hotelling-Lawley trace
    based on the Pillai F approximation. HLT is the "population value"
    Hotelling Lawley trace. F1 and DF2 are the hypothesis and
    error degrees of freedom, OMEGA is the non-centrality parameter, and
    FCRIT is the critical value from the F distribution.

    :param rank_C: rank of C matrix
    :param rank_U: rank of U matrix
    :param rank_X: rank of X matrix
    :param total_N: total N
    :param eval_HINVE: eigenvalues for H*INV(E)
    :param mmethod: multirep method
    :return: power, power for Hotelling-Lawley trace & CL if requested
    """
    # MMETHOD default= [4,2,2]
    # MultiHLT  Choices for Hotelling-Lawley Trace
    #       = 1  Pillai (1954, 55) 1 moment null approx


    df2Method = oneMomentDf2(rank_U, rank_X, total_N)

    # df2 need to > 0 and eigenvalues not missing
    if df2 <= 0 or np.isnan(eval_HINVE[0]):
        power = float('nan')
        warnings.warn('PowerWarn15: Power is missing because because the noncentrality could not be computed.')
    else:
        hlt, omega = calcHltOmega(eval_HINVE, rank_X, total_N)

        power, fmethod = _multi_power(Scalar.alpha, df1, df2, omega)

    power_l, power_u, fmethod_l, fmethod_u, noncen_l, noncen_u = glmmpcl(Scalar.alpha, df1, total_N, df2, CL.cl_type, CL.n_est, CL.rank_est,
                                                                         CL.alpha_cl, CL.alpha_cu, Scalar.tolerance, power, omega)

    return {'lower': power_l, 'power': power, 'upper': power_u}


def calcHltOmega(eval_HINVE, rank_X, total_N):
    if min_rank_C_U == 1:
        hlt = eval_HINVE * (total_N - rank_X) / total_N
        omega = (total_N * min_rank_C_U) * (hlt / min_rank_C_U)
    else:
        hlt = eval_HINVE
        omega = df2 * (hlt / min_rank_C_U)
    return hlt, omega


def oneMomentDf2(rank_U, rank_X, total_N):
    df2 = min_rank_C_U * (total_N - rank_X - rank_U - 1) + 2
    return df2


def hltTwoMomentNullApproximator(rank_C, rank_U, rank_X, total_N, eval_HINVE ):
    """
    This function calculates power for Hotelling-Lawley trace
    based on the Pillai F approximation. HLT is the "population value"
    Hotelling Lawley trace. F1 and DF2 are the hypothesis and
    error degrees of freedom, OMEGA is the non-centrality parameter, and
    FCRIT is the critical value from the F distribution.

    :param rank_C: rank of C matrix
    :param rank_U: rank of U matrix
    :param rank_X: rank of X matrix
    :param total_N: total N
    :param eval_HINVE: eigenvalues for H*INV(E)
    :param mmethod: multirep method
    :return: power, power for Hotelling-Lawley trace & CL if requested
    """
    min_rank_C_U = min(rank_C, rank_U)
    df1 = rank_C * rank_U

    # MMETHOD default= [4,2,2]
    # MultiHLT  Choices for Hotelling-Lawley Trace
    #       = 2  McKeon (1974) two moment null approx
    nu_df2 = (total_N - rank_X)*(total_N - rank_X) - (total_N - rank_X)*(2*rank_U + 3) + rank_U*(rank_U + 3)
    de_df2 = (total_N - rank_X)*(rank_C + rank_U + 1) - (rank_C + 2*rank_U + rank_U*rank_U - 1)
    df2 = 4 + (rank_C*rank_U + 2) * (nu_df2/de_df2)

    # df2 need to > 0 and eigenvalues not missing
    if df2 <= 0 or np.isnan(eval_HINVE[0]):
        power = float('nan')
        warnings.warn('PowerWarn15: Power is missing because because the noncentrality could not be computed.')
    else:
        if min_rank_C_U == 1:
            hlt = eval_HINVE * (total_N - rank_X) / total_N
            omega = (total_N * min_rank_C_U) * (hlt / min_rank_C_U)
        else:
            hlt = eval_HINVE
            omega = df2 * (hlt / min_rank_C_U)

        power, fmethod = multi_power(Scalar.alpha, df1, df2, omega)

    power_l, power_u, fmethod_l, fmethod_u, noncen_l, noncen_u = glmmpcl(Scalar.alpha, df1, total_N, df2, CL.cl_type, CL.n_est, CL.rank_est,
                                                                         CL.alpha_cl, CL.alpha_cu, Scalar.tolerance, power, omega)

    return {'lower': power_l, 'power': power, 'upper': power_u}

def hltOneMomentNullApproximatorObrienShee(rank_C, rank_U, rank_X, total_N, eval_HINVE ):
    """
    This function calculates power for Hotelling-Lawley trace
    based on the Pillai F approximation. HLT is the "population value"
    Hotelling Lawley trace. F1 and DF2 are the hypothesis and
    error degrees of freedom, OMEGA is the non-centrality parameter, and
    FCRIT is the critical value from the F distribution.

    :param rank_C: rank of C matrix
    :param rank_U: rank of U matrix
    :param rank_X: rank of X matrix
    :param total_N: total N
    :param eval_HINVE: eigenvalues for H*INV(E)
    :param mmethod: multirep method
    :return: power, power for Hotelling-Lawley trace & CL if requested
    """
    min_rank_C_U = min(rank_C, rank_U)
    df1 = rank_C * rank_U

    # MMETHOD default= [4,2,2]
    # MultiHLT  Choices for Hotelling-Lawley Trace
    #       = 3  Pillai (1959) one moment null approx+ OS noncen mult
    df2 = min_rank_C_U * (total_N - rank_X - rank_U - 1) + 2

    # df2 need to > 0 and eigenvalues not missing
    if df2 <= 0 or np.isnan(eval_HINVE[0]):
        power = float('nan')
        warnings.warn('PowerWarn15: Power is missing because because the noncentrality could not be computed.')
    else:
        hlt = eval_HINVE * (total_N - rank_X) / total_N
        omega = (total_N * min_rank_C_U) * (hlt / min_rank_C_U)

        power, fmethod = multi_power(Scalar.alpha, df1, df2, omega)

    power_l, power_u, fmethod_l, fmethod_u, noncen_l, noncen_u = glmmpcl(Scalar.alpha, df1, total_N, df2, CL.cl_type, CL.n_est, CL.rank_est,
                                                                         CL.alpha_cl, CL.alpha_cu, Scalar.tolerance, power, omega)

    return {'lower': power_l, 'power': power, 'upper': power_u}

def hltTwoMomentNullApproximatorObrienShee(rank_C, rank_U, rank_X, total_N, eval_HINVE ):
    """
    This function calculates power for Hotelling-Lawley trace
    based on the Pillai F approximation. HLT is the "population value"
    Hotelling Lawley trace. F1 and DF2 are the hypothesis and
    error degrees of freedom, OMEGA is the non-centrality parameter, and
    FCRIT is the critical value from the F distribution.

    :param rank_C: rank of C matrix
    :param rank_U: rank of U matrix
    :param rank_X: rank of X matrix
    :param total_N: total N
    :param eval_HINVE: eigenvalues for H*INV(E)
    :param mmethod: multirep method
    :return: power, power for Hotelling-Lawley trace & CL if requested
    """
    min_rank_C_U = min(rank_C, rank_U)
    df1 = rank_C * rank_U

    # MMETHOD default= [4,2,2]
    # MultiHLT  Choices for Hotelling-Lawley Trace
    #       = 4  McKeon (1974) two moment null approx+ OS noncen mult
    nu_df2 = (total_N - rank_X)*(total_N - rank_X) - (total_N - rank_X)*(2*rank_U + 3) + rank_U*(rank_U + 3)
    de_df2 = (total_N - rank_X)*(rank_C + rank_U + 1) - (rank_C + 2*rank_U + rank_U*rank_U - 1)
    df2 = 4 + (rank_C*rank_U + 2) * (nu_df2/de_df2)

    # df2 need to > 0 and eigenvalues not missing
    if df2 <= 0 or np.isnan(eval_HINVE[0]):
        power = float('nan')
        warnings.warn('PowerWarn15: Power is missing because because the noncentrality could not be computed.')
    else:
        hlt = eval_HINVE * (total_N - rank_X) / total_N
        omega = (total_N * min_rank_C_U) * (hlt / min_rank_C_U)

        power, fmethod = multi_power(Scalar.alpha, df1, df2, omega)

    power_l, power_u, fmethod_l, fmethod_u, noncen_l, noncen_u = glmmpcl(Scalar.alpha, df1, total_N, df2, CL.cl_type, CL.n_est, CL.rank_est,
                                                                         CL.alpha_cl, CL.alpha_cu, Scalar.tolerance, power, omega)

    return {'lower': power_l, 'power': power, 'upper': power_u}


def pbt(rank_C, rank_U, rank_X, total_N, eval_HINVE ):
    """
    This function calculates power for Pillai-Bartlett trace based on the
    F approx. method.  V is the "population value" of PBT,
    DF1 and DF2 are the hypothesis and error degrees of freedom,
    OMEGA is the noncentrality parameter, and FCRIT is the
    critical value from the F distribution.

    :param rank_C: rank of C matrix
    :param rank_U: rank of U matrix
    :param rank_X: rank of X matrix
    :param total_N: total N
    :param eval_HINVE: eigenvalues for H*INV(E)
    :param MultiPBT: multirep method
    :return: power, power for Pillai-Bartlett trace & CL if requested
    """

    # MMETHOD[1]  Choices for Pillai-Bartlett Trace
    #   = 1  Pillai (1954, 55) one moment null approx
    #   = 2  Muller (1998) two moment null approx
    #   = 3  Pillai (1959) one moment null approx + OS noncen mult
    #   = 4  Muller (1998) two moment null approx + OS noncen mult
    if MultiPBT == Constants.MULTI_PBT_PILLAI or MultiPBT == Constants.MULTI_PBT_PILLAI_OS:
        df1 = rank_C * rank_U
        df2 = min(rank_C, rank_U) * (total_N - rank_X + min(rank_C, rank_U) - rank_U)

    elif MultiPBT == Constants.MULTI_PBT_MULLER or MultiPBT == Constants.MULTI_PBT_MULLER_OS:
        mu1 = rank_C * rank_U / (total_N - rank_X + rank_C)
        factor1 = (total_N - rank_X + rank_C -rank_U) / (total_N - rank_X + rank_C - 1)
        factor2 = (total_N - rank_X) / (total_N - rank_X + rank_C + 2)
        variance = 2 * rank_C * rank_U * factor1 * factor2 / (total_N - rank_X + rank_C)**2
        mu2 = variance + mu1**2
        m1 = mu1 / min(rank_C, rank_U)
        m2 = mu2 / (min(rank_C, rank_U) * min(rank_C, rank_U))
        denom = m2 - m1 * m1
        df1 = 2 * m1 * (m1 - m2) / denom
        df2 = 2 * (m1 - m2) * (1 - m1) /denom

    if df2 <= 0 or np.isnan(eval_HINVE[0]):
        power = float('nan')
        warnings.warn('PowerWarn15: Power is missing because because the noncentrality could not be computed.')
    else:
        if (MultiPBT == Constants.MULTI_PBT_PILLAI_OS or MultiPBT == Constants.MULTI_PBT_MULLER_OS)\
                or min(rank_U, rank_C) == 1:
            evalt = eval_HINVE * (total_N - rank_X) / total_N
        else:
            evalt = eval_HINVE

        v = sum(evalt / (np.ones((min(rank_C, rank_U), 1)) + evalt))

        if (min(rank_C, rank_U) - v) <= Scalar.tolerance:
            power = float('nan')
        else:
            if (MultiPBT == Constants.MULTI_PBT_PILLAI_OS or MultiPBT == Constants.MULTI_PBT_MULLER_OS)\
                    or min(rank_U, rank_C) == 1:
                omega = total_N * min(rank_C, rank_U) * v / (min(rank_C, rank_U) - v)
            else:
                omega = df2 * v / (min(rank_C, rank_U) - v)

            power, fmethod = multi_power(Scalar.alpha, df1, df2, omega)

    power_l, power_u, fmethod_l, fmethod_u, noncen_l, noncen_u = glmmpcl(Scalar.alpha, df1, total_N, df2, CL.cl_type, CL.n_est,
                                                                         CL.rank_est,
                                                                         CL.alpha_cl, CL.alpha_cu, Scalar.tolerance, power, omega)

    return {'lower': power_l, 'power': power, 'upper': power_u}


def wlk(rank_C, rank_U, rank_X, total_N, eval_HINVE ):
    """
    This function calculates power for Wilk's Lambda based on
    the F approx. method.  W is the "population value" of Wilks` Lambda,
    DF1 and DF2 are the hypothesis and error degrees of freedom, OMEGA
    is the noncentrality parameter, and FCRIT is the critical value
    from the F distribution. RM, RS, R1, and TEMP are intermediate
    variables.

    :param rank_C: rank of C matrix
    :param rank_U: rank of U matrix
    :param rank_X: rank of X matrix
    :param total_N: total N
    :param eval_HINVE: eigenvalues for H*INV(E)
    :param MultiWLK: multirep method
    :return: power, power for Hotelling-Lawley trace & CL if requested
    """
    min_rank_C_U = min(rank_C, rank_U)
    df1 = rank_C * rank_U

    # MMETHOD default= [4,2,2]
    # MMETHOD[2] Choices for Wilks' Lambda
    #       = 1  Rao (1951) two moment null approx
    #       = 2  Rao (1951) two moment null approx
    #       = 3  Rao (1951) two moment null approx + OS Obrien Shee noncen mult
    #       = 4  Rao (1951) two moment null approx + OS noncen mult
    if np.isnan(eval_HINVE[0]):
        w = float('nan')
        warnings.warn('PowerWarn15: Power is missing because because the noncentrality could not be computed.')
    else:
        if MultiWLK == Constants.MULTI_WLK_RAO or MultiWLK == Constants.MULTI_WLK_RAO_OS or min_rank_C_U == 1:
            w = np.exp(np.sum(-np.log(np.ones((min_rank_C_U, 1)) + eval_HINVE * (total_N - rank_X)/total_N)))
        else:
            w = np.exp(np.sum(-np.log(np.ones((min_rank_C_U, 1)) + eval_HINVE)))

    if min_rank_C_U == 1:
        df2 = total_N - rank_X -rank_U + 1
        rs = 1
        tempw = w
    else:
        rm = total_N - rank_X - (rank_U - rank_C + 1)/2
        rs = np.sqrt(rank_C*rank_C*rank_U*rank_U - 4) / (rank_C*rank_C + rank_U*rank_U - 5)
        r1 = (rank_U - rank_C - 2)/4
        if np.isnan(w):
            tempw = float('nan')
        else:
            tempw = np.power(w, 1/rs)
        df2 = (rm * rs) - 2 * r1

    if np.isnan(tempw):
        omega = float('nan')
    else:
        if MultiWLK == Constants.MULTI_WLK_RAO or MultiWLK == Constants.MULTI_WLK_RAO_OS or min_rank_C_U == 1:
            omega = (total_N * rs) * (1 - tempw) /tempw
        else:
            omega = df2 * (1 - tempw) / tempw

    if df2 <= 0 or np.isnan(w) or np.isnan(omega):
        power = float('nan')
        warnings.warn('PowerWarn15: Power is missing because because the noncentrality could not be computed.')
    else:
        power, fmethod = multi_power(Scalar.alpha, df1, df2, omega)

    power_l, power_u, fmethod_l, fmethod_u, noncen_l, noncen_u = glmmpcl(Scalar.alpha, df1, total_N, df2, CL.cl_type, CL.n_est,
                                                                         CL.rank_est,
                                                                         CL.alpha_cl, CL.alpha_cu, Scalar.tolerance, power, omega)

    return {'lower': power_l, 'power': power, 'upper': power_u}


def special(rank_C, rank_U, rank_X, total_N, eval_HINVE ):
    """
    This function performs two disparate tasks. For B=1 (UNIVARIATE
    TEST), the powers are calculated more efficiently. For A=1 (SPECIAL
    MULTIVARIATE CASE), exact multivariate powers are calculated.
    Powers for the univariate tests require separate treatment.
    DF1 & DF2 are the hypothesis and error degrees of freedom,
    OMEGA is the noncentrality parameter, and FCRIT is the critical
    value from the F distribution.

    :param rank_C: rank of C matrix
    :param rank_U: rank of U matrix
    :param rank_X: rank of X matrix
    :param total_N: total N
    :param eval_HINVE: eigenvalues for H*INV(E)
    :return: power, power for Hotelling-Lawley trace & CL if requested
    """
    df1 = rank_C * rank_U
    df2 = total_N - rank_X - rank_U + 1

    if df2 <= 0 or np.isnan(eval_HINVE[0]):
        power = float('nan')
        warnings.warn('PowerWarn15: Power is missing because because the noncentrality could not be computed.')
    else:
        omega = eval_HINVE[0] * (total_N - rank_X)
        power, fmethod = multi_power(Scalar.alpha, df1, df2, omega)

    power_l, power_u, fmethod_l, fmethod_u, noncen_l, noncen_u = glmmpcl(Scalar.alpha, df1, total_N, df2, CL.cl_type, CL.n_est,
                                                                         CL.rank_est,
                                                                         CL.alpha_cl, CL.alpha_cu, Scalar.tolerance, power, omega)

    return {'lower': power_l, 'power': power, 'upper': power_u}


def _multi_power(alpha, df1, df2, omega):
    """ The common part for these four multirep methods
        Computing power
        :rtype: object"""
    fcrit = finv(1 - alpha, df1, df2)
    prob, fmethod = probf(fcrit, df1, df2, omega)
    if fmethod == Constants.FMETHOD_NORMAL_LR and prob == 1:
        power = alpha
    else:
        power = 1 - prob
    power = float(power)
    return power, fmethod
