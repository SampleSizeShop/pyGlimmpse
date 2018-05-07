import warnings
import numpy as np

from pyglimmpse.constants import Constants
from pyglimmpse.model.epsilon import Epsilon
from pyglimmpse.model.power import Power
from pyglimmpse.probf import probf


def uncorrected(sigma_star: np.matrix, rank_U: float, total_N: float, rank_X: float) -> Power:
    pass


def geisser_greenhouse_muller_barton_1989(sigma_star: np.matrix, rank_U: float, total_N: float, rank_X: float) -> Power:
    """
    This function computes the approximate expected value of the Geisser-Greenhouse estimate using the approximator
    detailed in Muller and Barton 1989.

    Parameters
    ----------
    sigma_star: np.matrix
        The covariance matrix, :math:`\Sigma_*`,  defined as: :math:`\Sigma_* = U\'\Sigma U`
        This should be scaled in advance by multiplying :math:`\Sigma` by a constant SIGMASCALARTEMP
    rank_U: float
        rank of U () matrix
    total_N: float
        total N, the sample size
    rank_X: float
        rank of X matrix (design/essence)

    Returns
    -------
    power: Power
        power as calculated by the Chi-Muller test.
    """
    epsilon = _calc_epsilon(sigma_star, rank_U)
    f_i, f_ii = _gg_derivs_functions_eigenvalues(epsilon, rank_U)
    g_1 = _calc_g_1(epsilon, f_i, f_ii)
    expected_epsilon = epsilon.eps + g_1 / (total_N - rank_X)
    return expected_epsilon


def geisser_greenhouse_muller_edwards_simpson_taylor_2007(sigma_star: np.matrix, rank_U: float, total_N: float, rank_X: float) -> Power:
    """
    This function computes the approximate expected value of the Geisser-Greenhouse estimate using the approximator
    detailed in Muller, Edwards, Simpson and Taylor 2007.

    Parameters
    ----------
    sigma_star: np.matrix
        The covariance matrix, :math:`\Sigma_*`,  defined as: :math:`\Sigma_* = U\'\Sigma U`
        This should be scaled in advance by multiplying :math:`\Sigma` by a constant SIGMASCALARTEMP
    rank_U: float
        rank of U () matrix
    total_N: float
        total N, the sample size
    rank_X: float
        rank of X matrix (design/essence)

    Returns
    -------
    power: Power
        power as calculated by the Chi-Muller test.
    """
    epsilon = _calc_epsilon(sigma_star, rank_U)

    nu = total_N - rank_X
    expt1 = 2 * nu * epsilon.slam2 + nu ** 2 * epsilon.slam1
    expt2 = nu * (nu + 1) * epsilon.slam2 + nu * epsilon.nameME()

    # Define GG Approx E(.) for Method 1
    expected_epsilon = (1 / rank_U) * (expt1 / expt2)
    return expected_epsilon


def chi_muller_muller_barton_1989(sigma_star: np.matrix, rank_U: float, total_N: float, rank_X: float) -> Power:
    """
    This function computes the approximate expected value of the Huynh-Feldt estimate with the Chi-Muller results via
    the approximate expected value of the Huynh-Feldt estimate using the approximator detailed in
    Muller and Barton 1989.

    Parameters
    ----------
    sigma_star: np.matrix
        The covariance matrix, :math:`\Sigma_*`,  defined as: :math:`\Sigma_* = U\'\Sigma U`
        This should be scaled in advance by multiplying :math:`\Sigma` by a constant SIGMASCALARTEMP
    rank_U: float
        rank of U () matrix
    total_N: float
        total N, the sample size
    rank_X: float
        rank of X matrix (design/essence)

    Returns
    -------
    power: Power
        power as calculated by the Chi-Muller test.
    """
    expected_epsilon_hf = hyuhn_feldt_muller_barton_1989(
                    sigma_star=sigma_star,
                    rank_U=rank_U,
                    total_N=total_N,
                    rank_X=rank_X
    )

    expected_epsilon_cm = _calc_cm_expected_epsilon_estimator(expected_epsilon_hf, rank_X, total_N)

    return expected_epsilon_cm


def chi_muller_muller_edwards_simpson_taylor_2007(sigma_star: np.matrix, rank_U: float, total_N: float, rank_X: float) -> Power:
    """
    This function computes the approximate expected value of the Huynh-Feldt estimate with the Chi-Muller results via
    the approximate expected value of the Huynh-Feldt estimate using the approximator detailed in
    Muller, Edwards, Simpson and Taylor 2007.

    Parameters
    ----------
    sigma_star: np.matrix
        The covariance matrix, :math:`\Sigma_*`,  defined as: :math:`\Sigma_* = U\'\Sigma U`
        This should be scaled in advance by multiplying :math:`\Sigma` by a constant SIGMASCALARTEMP
    rank_U: float
        rank of U () matrix
    total_N: float
        total N, the sample size
    rank_X: float
        rank of X matrix (design/essence)

    Returns
    -------
    power: Power
        power as calculated by the Chi-Muller test.
    """
    expected_epsilon = hyuhn_feldt_muller_edwards_simpson_taylor_2007(
        sigma_star=sigma_star,
        rank_U=rank_U,
        total_N=total_N,
        rank_X=rank_X
    )

    expected_epsilon = _calc_cm_expected_epsilon_estimator(expected_epsilon, rank_X, total_N)

    return expected_epsilon

def hyuhn_feldt_muller_barton_1989(sigma_star: np.matrix, rank_U: float, total_N: float, rank_X: float) -> Power:
    """
    This function computes power via the approximate expected value of the Huynh-Feldt estimate using the
    approximator detailed in Muller and Barton 1989.

    Parameters
    ----------
    sigma_star: np.matrix
        The covariance matrix, :math:`\Sigma_*`,  defined as: :math:`\Sigma_* = U\'\Sigma U`
        This should be scaled in advance by multiplying :math:`\Sigma` by a constant SIGMASCALARTEMP
    rank_U: float
        rank of U () matrix
    total_N: float
        total N, the sample size
    rank_X: float
        rank of X matrix (design/essence)

    Returns
    -------
    power: Power
        power as calculated by the Huyhn-Feldt test.
    """
    epsilon = _calc_epsilon(sigma_star, rank_U)

    # Compute approximate expected value of Huynh-Feldt estimate
    bh_i, bh_ii, h1, h2 = _hf_derivs_functions_eigenvalues(rank_U, rank_X, total_N, epsilon)
    g_1 = _calc_g_1(epsilon, bh_i, bh_ii)
    # Define HF Approx E(.) for Method 0
    expected_epsilon = h1 / (rank_U * h2) + g_1 / (total_N - rank_X)

    return expected_epsilon


def hyuhn_feldt_muller_edwards_simpson_taylor_2007(sigma_star: np.matrix, rank_U: float, total_N: float, rank_X: float) -> Power:
    """
    This function computes power via the approximate expected value of the Huynh-Feldt estimate using the
    approximator detailed in Muller, Edwards, Simpson and Taylor 2007

    Parameters
    ----------
    sigma_star: np.matrix
        The covariance matrix, :math:`\Sigma_*`,  defined as: :math:`\Sigma_* = U\'\Sigma U`
        This should be scaled in advance by multiplying :math:`\Sigma` by a constant SIGMASCALARTEMP
    rank_U: float
        rank of U () matrix
    total_N: float
        total N, the sample size
    rank_X: float
        rank of X matrix (design/essence)

    Returns
    -------
    power: Power
        power as calculated by the Huyhn-Feldt test.
    """
    epsilon = _calc_epsilon(sigma_star, rank_U)
    # Computation of EXP(T1) and EXP(T2)
    nu = total_N - rank_X
    expt1 = 2 * nu * epsilon.slam2 + nu ** 2 * epsilon.slam1
    expt2 = nu * (nu + 1) * epsilon.slam2 + nu * epsilon.nameME()
    num01 = (1 / rank_U) * ((nu + 1) * expt1 - 2 * expt2)
    den01 = nu * expt2 - expt1
    expected_epsilon = num01 / den01
    return expected_epsilon


def box(sigma_star: np.matrix, rank_U: float, total_N: float, rank_X: float) -> Power:
    pass

def _calc_epsilon(sigma_star: np.matrix, rank_U: float) -> Epsilon:
    """
    This module produces matrices required for Geisser-Greenhouse,
    Huynh-Feldt or uncorrected repeated measures power calculations. It
    is the first step. Program uses approximations of expected values of
    epsilon estimates due to Muller (1985), based on theorem of Fujikoshi
    (1978). Program requires that U be orthonormal and orthogonal to a
    columns of 1's.

    Parameters
    ----------
    sigma_star: np.matrix
        The covariance matrix, :math:`\Sigma_*`,  defined as: :math:`\Sigma_* = U\'\Sigma U`
        This should be scaled in advance by multiplying :math:`\Sigma` by a constant SIGMASCALARTEMP
    rank_U: float
        rank of U matrix

    Returns
    -------
    epsilon
        :class:`.Epsilon` object containing the following
        d, number of distinct eigenvalues
        mtp, multiplicities of eigenvalues
        eps, epsilon calculated from U`*SIGMA*U
        deigval, first eigenvalue
        slam1, sum of eigenvalues squared
        slam2, sum of squared eigenvalues
        slam3, sum of eigenvalues
    """

    #todo is this true for ALL epsilon? If so build into the class and remove this method.
    if rank_U != np.shape(sigma_star)[0]:
        raise Exception("rank of U should equal to nrows of sigma_star")

    # Get eigenvalues of covariance matrix associated with E. This is NOT
    # the USUAL sigma. This cov matrix is that of (Y-YHAT)*U, not of (Y-YHAT).
    # The covariance matrix is normalized to minimize numerical problems
    epsilon = Epsilon(sigma_star, rank_U)
    return epsilon


def _calc_g_1(epsilon, f_i, f_ii):
    """
    This calculates :math:`g_1` as defined in Muller and Barton 1989

    .. math::
        g_1 = \sum_{i=1}^{d}f_ii\lambda_i^2m_i + \mathop{\sum \sum}_{i \\neq j} \dfrac {f_i\lambda_i \lambda_jm_im_j}{\lambda_i - \lambda_j}


    :math:`m_i, m_j` are the the multiplicities if the :math:`i^{th}, j^{th}` distinct eigenvalues.

    :math:`f_i` is :math:`\dfrac{\partial f}{\partial \lambda}` and :math:`f_{ii}` is :math:`\dfrac{\partial f^{(2)}}{\partial \lambda^{(2)}}`

    Parameters
    ----------
    epsilon: :class:`.Epsilon`
        The :class:`.Epsilon` object calculated for this test
    f_i: float
        the value of the first derivative of the function of the eigenvalues wrt :math:`\lambda`
    f_ii: float
        the value of the second derivative of the function of the eigenvalues wrt :math:`\lambda`

    Returns
    -------
    g_i: float
        the value of :math:`g_i` as defined above

    """

    t1 = np.multiply(np.multiply(f_ii, np.power(epsilon.deigval, 2)), epsilon.mtp)
    sum1 = np.sum(t1)
    if epsilon.d == 1:
        sum2 = 0
    else:
        t2 = np.multiply(np.multiply(f_i, epsilon.deigval), epsilon.mtp)
        t3 = np.multiply(epsilon.deigval, epsilon.mtp)
        tm1 = t2 * t3.T
        t4 = epsilon.deigval * np.full((1, epsilon.d), 1)
        tm2 = t4 - t4.T
        tm2inv = 1 / (tm2 + np.identity(d)) - np.identity(d)
        tm3 = np.multiply(tm1, tm2inv)
        sum2 = np.sum(tm3)
    g_1 = sum1 + sum2

    return g_1


def _hf_derivs_functions_eigenvalues(rank_U: float, rank_X: float, total_N: float, epsilon: Epsilon):
    """
    This function computes the derivatives of the functions of eigenvalues for the Huyhn_Feldt test. For HF, FNCT is epsilon tilde

    For Huyhn-Feldt:

    .. math::

        h(\lambda) = \dfrac{(Nb_\epsilon - 2)}{b(N - r -b_\epsilon)}  = \dfrac{h_1(\lambda)}{h_2(\lambda)b}

    with:

    .. math::
        h_1 = N(\Sigma\lambda_k)^2 - 2\Sigma\lambda_k^2

        h_2 = (N - r)\Sigma\lambda_k^2 - (\Sigma\lambda_k)^2

    In turn:

    .. math::
        \partial h_1 = 2N(\Sigma\lambda_k) - 4\lambda_i

        \partial h_2 = 2(N - r)\lambda_i - 2\Sigma\lambda_k

    and:

    .. math::

        \partial h_1^{(2)} = 2N - 4

        \partial h_2^{(2)} = 2(N - r) - 2

    The necessary derivatives are:

    .. math::

        bh_i = \dfrac{\partial h_1}{h_2} - \dfrac{h_1 \partial h_2}{h_2^2}

    and:

    .. math::

        bh_{ii} = \dfrac{\partial h_1^{(2)}}{h_2} -  \dfrac{ 2 \partial h_1\partial h_2}{h_2^2} + \dfrac{ 2h_1(\partial h_2)^2}{h_2^3} - \dfrac{h_1\partial h_2^{2}}{h_2^2}


    Parameters
    ----------
    rank_U: float
        rank of U matrix
    rank_X: float
        rank of X matrix
    total_N: float
        total N
    epsilon: :class:`.Epsilon`
        The :class:`.Epsilon` object calculated for this test

    Returns
    -------
    bh_i: float
        the value of the first derivative of the function of the eigenvalues wrt :math:`\lambda`
    bh_ii: float
        the value of the second derivative of the function of the eigenvalues wrt :math:`\lambda`
    h_1: float
        the value of h_1 as defined above
    h_2: float
        the value of h_2 as defined above

    """
    h1 = total_N * epsilon.slam1 - 2 * epsilon.slam2
    h2 = (total_N - rank_X) * epsilon.slam2 - epsilon.slam1
    derh1 = np.full((epsilon.d, 1), 2 * total_N * epsilon.slam3) - 4 * epsilon.deigval
    derh2 = 2 * (total_N - rank_X) * epsilon.deigval - np.full((epsilon.d, 1), 2 * np.sqrt(epsilon.slam1))
    bh_i = (derh1 - h1 * derh2 / h2) / (rank_U * h2)
    der2h1 = np.full((epsilon.d, 1), 2 * total_N - 4)
    der2h2 = np.full((epsilon.d, 1), 2 * (total_N - rank_X) - 2)
    bh_ii = (
           (np.multiply(-derh1, derh2) / h2 + der2h1 - np.multiply(derh1, derh2) / h2 + 2 * h1 * np.power(derh2, 2) / h2 ** 2 - h1 * der2h2 / h2)
           / (h2 * rank_U))
    return bh_i, bh_ii, h1, h2


def _gg_derivs_functions_eigenvalues(epsilon: Epsilon, rank_U: float):
    """
    This function computes the derivatives of the functions of eigenvalues for the Geisser-Greenhouse test.

    For Geisser-Greenhouse test :math:`f( \lambda) = \epsilon` so :math:`f_i` the first derivative, with respect to :math:`\lambda` is:

    .. math::

        f_i = \partial f = 2(\Sigma\lambda_k)(\Sigma\lambda_k^2)^{-1} - 2\lambda_i(\Sigma\lambda_k)^2(\Sigma\lambda_k^2)^{-2}b^{-1}

    and :math:`f_{ii}` the second derivative, with respect to :math:`\lambda` is:

    .. math::

        f_{ii} = \partial f^{(2)} = 2(\Sigma\lambda_k^2)^{-1}b^{-1} - 8\lambda_i(\Sigma\lambda_k)(\Sigma\lambda_k^2)^{-2}b^{-1} +  8\lambda_i^2(\Sigma\lambda_k)^2(\Sigma\lambda_k^2)^{-3}b^{-1} -2(\Sigma\lambda_k)^2(\Sigma\lambda_k^2)^{-2}b^{-1}

    Parameters
    ----------
    epsilon:class:`.Epsilon`
        The :class:`.Epsilon` object calculated for this test
    rank_U: float
        rank of U matrix

    Returns
    -------
    f_i: float
        the value of the first derivative of the function of the eigenvalues wrt :math:`\lambda`
    f_ii: float
        the value of the second derivative of the function of the eigenvalues wrt :math:`\lambda`

    """
    f_i = np.full((epsilon.d, 1), 1) * 2 * epsilon.slam3 / (epsilon.slam2 * rank_U) \
         - 2 * epsilon.deigval * epsilon.slam1 / (rank_U * epsilon.slam2 ** 2)
    c0 = 1 - epsilon.slam1 / epsilon.slam2
    c1 = -4 * epsilon.slam3 / epsilon.slam2
    c2 = 4 * epsilon.slam1 / epsilon.slam2 ** 2
    f_ii = 2 * (c0 * np.full((epsilon.d, 1), 1)
               + c1 * epsilon.deigval
               + c2 * np.power(epsilon.deigval, 2)) / (rank_U * epsilon.slam2)
    return f_i, f_ii


def _calc_cm_expected_epsilon_estimator(exeps, rank_X, total_N):
    """
    This function computes the approximate expected value of the Chi-Muller estimate.

    Parameters
    ----------
    exeps: float
        the expected value of the epsilon estimator calculated using the approximate expected value of
        the Huynh-Feldt estimate
    rank_X: float
        rank of X matrix
    total_N: float
        total N

    Return
    ------
    epsilon:class:`pyglimmpse.model.Epsilon`
        The :class:`.Epsilon` object calculated for this test
    """
    if total_N - rank_X == 1:
        uefactor = 1
    else:
        nu_e = total_N - rank_X
        nu_a = (nu_e - 1) + nu_e * (nu_e - 1) / 2
        uefactor = (nu_a - 2) * (nu_a - 4) / (nu_a ** 2)
    exeps = uefactor * exeps
    return exeps

def lastuni(rank_C, rank_U, total_N, rank_X,
            error_sum_square, hypo_sum_square, sigmastareval, sigmastarevec,
            exeps, eps, unirepmethod, Scalar, Option, CL, IP):
    """
    This function calculates power for univariate repeated measures power calculations.

    Parameters
    ----------
    rank_C: float
        rank of the C matrix
    rank_U: float
        rank of the U matrix
    total_N: float
        total number of observations
    rank_X:
        rank of the X matrix
    error_sum_square: float
        error sum of squares
    hypo_sum_square: float
        hypothesis sum of squares
    sigmastareval:
        eigenvalues  of SIGMASTAR=U`*SIGMA*U
    sigmastarevec:
        eigenvectors of SIGMASTAR=U`*SIGMA*U
    exeps: float
        expected value epsilon estimator
    eps:
        epsilon calculated from U`*SIGMA*U

    Returns
    -------
    power: Power
        power for the univariate test.
    """

    nue = total_N - rank_X

    if rank_U > nue and (Option.opt_calc_un or Option.opt_calc_gg or Option.opt_calc_box):
        warnings.warn('Power is missing, because Uncorrected, Geisser-Greenhouse and Box tests are '
                      'poorly behaved (super low power and test size) when B > N-R, i.e., HDLSS.')
        raise Exception("#TODO what kind of exception")

    if np.isnan(exeps) or nue <= 0:
        raise Exception("exeps is NaN or total_N  <= rank_X")

    undf1 = rank_C * rank_U
    undf2 = rank_U * nue

    # Create defaults - same for either SIGMA known or estimated
    sigstar = error_sum_square / nue
    q1 = np.trace(sigstar)
    q2 = np.trace(hypo_sum_square)
    q3 = q1 ** 2
    q4 = np.sum(np.power(sigstar, 2))
    q5 = np.trace(sigstar * hypo_sum_square)
    lambar = q1 / rank_U

    # Case 1
    # Enter loop to compute E1-E5 based on known SIGMA
    if (not CL.sigma_type) and (not IP.ip_plan):
        epsn_num = q3 + q1 * q2 * 2 / rank_C
        epsn_den = q4 + q5 * 2 / rank_C
        epsn = epsn_num / (rank_U * epsn_den)
        e_1_2 = exeps
        e_4 = eps
        if unirepmethod == Constants.UCDF_MULLER1989_APPROXIMATION:
            e_3_5 = eps
        else:
            e_3_5 = epsn

    # Case 2
    # Enter loop to compute E1-E5 based on estimated SIGMA
    if CL.sigma_type and (not IP.ip_plan):
        nu_est = CL.n_est - CL.rank_est
        if nu_est <= 1:
            raise Exception("ERROR 81: Too few estimation df in LASTUNI. df = N_EST - RANK_EST <= 1.")

        # For POWERCALC =6=HF, =7=CM, =8=GG critical values
        epstilde_r = ((nu_est + 1) * q3 - 2 * q4) / (rank_U * (nu_est * q4 - q3))
        epstilde_r_min = min(epstilde_r, 1)
        mult = np.power(nu_est, 2) + nu_est - 2

        epsnhat_num = q3 * nu_est * (nu_est + 1) + q1 * q2 * 2 * mult / rank_C - q4 * 2 * nu_est
        epsnhat_den = q4 * nu_est * nu_est + q5 * 2 * mult / rank_C - q3 * nu_est
        epsnhat = epsnhat_num / (rank_U * epsnhat_den)

        nua0 = (nu_est - 1) + nu_est * (nu_est - 1) / 2
        tau10 = nu_est * ((nu_est + 1) * q1 * q1 - 2 * q4) / (nu_est * nu_est + nu_est - 2)
        tau20 = nu_est * (nu_est * q4 - q1 * q1) / (nu_est * nu_est + nu_est - 2)

        epsda = tau10 * (nua0 - 2) * (nua0 - 4) / (rank_U * nua0 * nua0 * tau20)
        epsda = max(min(epsda, 1), 1 / rank_U)
        epsna = (1 + 2 * (q2 / rank_C) / q1) / (1 / epsda + 2 * rank_U * (q5 / rank_C) / (q1 * q1))
        omegaua = q2 * epsna * (rank_U / q1)

        # Set E_1_2 for all tests

        # for UN or Box critical values
        if Option.opt_calc_un or Option.opt_calc_box:
            e_1_2 = epsda

        # for HF crit val
        if Option.opt_calc_hf:
            if rank_U <= nue:
                e_1_2 = epstilde_r_min
            else:
                e_1_2 = epsda

        # for CM crit val
        if Option.opt_calc_cm:
            e_1_2 = epsda

        # for GG crit val
        if Option.opt_calc_gg:
            e_1_2 = eps

        # Set E_3_5 for all tests
        if unirepmethod == Constants.UCDF_MULLER1989_APPROXIMATION:
            e_3_5 = eps
        else:
            e_3_5 = epsnhat

        # Set E_4 for all tests
        if Option.opt_calc_cm:
            e_4 = epsda
        else:
            e_4 = eps

        # Compute DF for confidence limits for all tests
        cl1df = rank_U * nu_est * e_4 / e_3_5

    # case 3
    # Enter loop to compute E1-E5 when planning IP study
    if IP.ip_plan and (not CL.sigma_type):
        nu_ip = IP.n_ip - IP.rank_ip
        e_1_2 = exeps
        e_4 = eps

        if Option.opt_calc_hf or Option.opt_calc_cm or Option.opt_calc_gg:
            lambdap = np.concatenate((sigmastareval,
                                      np.power(sigmastareval, 2),
                                      np.power(sigmastareval, 3),
                                      np.power(sigmastareval, 4)), axis=1)
            sumlam = np.matrix(np.sum(lambdap, axis=0)).T
            kappa = np.multiply(np.multiply(np.matrix([[1], [2], [8], [48]]), nu_ip), sumlam)
            muprime2 = np.asscalar(kappa[1] + np.power(kappa[0], 2))
            meanq2 = np.asscalar(np.multiply(np.multiply(nu_ip, nu_ip + 1), sumlam[1]) + np.multiply(nu_ip, np.sum(
                sigmastareval * sigmastareval.T)))

            et1 = muprime2 / np.power(nu_ip, 2)
            et2 = meanq2 / np.power(nu_ip, 2)
            ae_epsn_up = et1 + 2 * q1 * q2
            ae_epsn_dn = rank_U * (et2 + 2 * q5)
            aex_epsn = ae_epsn_up / ae_epsn_dn
            e_3_5 = aex_epsn
        else:
            epsn_num = q3 + q1 * q2 * 2 / rank_C
            epsn_den = q4 + q5 * 2 / rank_C
            epsn = epsn_num / (rank_U * epsn_den)
            e_3_5 = epsn

    # Error checking
    if e_1_2 < 1 / rank_U:
        e_1_2 = 1 / rank_U
        warnings.warn('PowerWarn17: The approximate expected value of estimated epsilon was truncated up to 1/B.')
    if e_1_2 > 1:
        e_1_2 = 1
        warnings.warn('PowerWarn18: The approximate expected value of estimated epsilon was truncated down to 1.')

    # Obtain noncentrality and critical value for power point estimate
    omega = e_3_5 * q2 / lambar
    if Option.opt_calc_cm and CL.sigma_type and (not IP.ip_plan):
        omega = omegaua

    fcrit = finv(1 - Scalar.alpha, undf1 * e_1_2, undf2 * e_1_2)

    # Compute power point estimate
    # 1. Muller, Edwards & Taylor 2002 CDF exact, Davies' algorithm
    if unirepmethod == Constants.UCDF_EXACT_DAVIES or \
            unirepmethod == Constants.UCDF_EXACT_DAVIES_FAIL:
        df1 = float("nan")
        df2 = float("nan")
        fmethod = float("nan")
        qweight = np.concatenate((sigmastareval, -sigmastareval * fcrit * undf1 / undf2))
        qnuvec = np.concatenate((np.full((rank_U, 1), rank_C), np.full((rank_U, 1), total_N - rank_X)), axis=0)
        dgover = np.diag(1 / np.sqrt(np.squeeze(np.asarray(sigmastareval))))
        factori = sigmastarevec * dgover
        omegstar = factori.T * hypo_sum_square * factori
        qnoncen = np.concatenate((np.diag(omegstar), np.zeros((rank_U, 1))), axis=0)
        # TODO cdfpowr = qprob()
        cdfpowr = float("nan")
        if np.isnan(cdfpowr):
            warnings.warn('PowerWarn19: Power missing due to Davies" algorithm fail.')
        else:
            power = 1 - cdfpowr

    # 2. Muller, Edwards & Taylor 2002 and Muller Barton 1989 CDF approx
    # UCDFTEMP[]=4 reverts to UCDFTEMP[]=2 if exact CDF fails
    if (unirepmethod == Constants.UCDF_MULLER1989_APPROXIMATION or
                unirepmethod == Constants.UCDF_MULLER2004_APPROXIMATION) or \
            (unirepmethod == Constants.UCDF_EXACT_DAVIES_FAIL and np.isnan(power)):
        df1 = undf1 * e_3_5
        df2 = undf2 * e_4
        prob, fmethod = probf(fcrit, df1, df2, omega)
        if fmethod == Constants.FMETHOD_NORMAL_LR and prob == 1:
            power = Scalar.alpha
        else:
            power = 1 - prob

    # TODO: is this the same as glmmpcl???? looks like it is.
    if CL.cl_type == Constants.CLTYPE_DESIRED_KNOWN:
        if unirepmethod == Constants.UCDF_EXACT_DAVIES or \
                unirepmethod == Constants.UCDF_EXACT_DAVIES_FAIL:
            raise Exception("ERROR 82: Any use of Exact CDF is incompatible with computation of CL for power.")

        # Calculate lower bound for power
        if CL.alpha_cl <= Scalar.tolerance:
            prob_l = 1 - Scalar.alpha
            fmethod_l = Constants.FMETHOD_MISSING
            noncen_l = float('nan')
        else:
            chi_l = chi2.ppf(CL.alpha_cl, cl1df)
            noncen_l = omega * (chi_l / cl1df)
            prob_l, fmethod_l = probf(fcrit, df1, df2, noncen_l)

        if fmethod_l == Constants.FMETHOD_NORMAL_LR and prob_l == 1:
            power_l = Scalar.alpha
        else:
            power_l = 1 - prob_l

        # Calculate upper bound for power
        if CL.alpha_cu <= Scalar.tolerance:
            prob_u = 0
            fmethod_u = Constants.FMETHOD_MISSING
            noncen_u = float('nan')
        else:
            chi_u = chi2.ppf(1 - CL.alpha_cu, cl1df)
            noncen_u = omega * (chi_u / cl1df)
            prob_u, fmethod_u = probf(fcrit, df1, df2, noncen_u)

        if fmethod_u == Constants.FMETHOD_NORMAL_LR and prob_u == 1:
            power_u = Scalar.alpha
        else:
            power_u = 1 - prob_u

        power_l = float(power_l)
        power_u = float(power_u)
    else:
        power_l = None
        power_u = None

    power = float(power)

    return {'lower': power_l, 'power': power, 'upper': power_u}