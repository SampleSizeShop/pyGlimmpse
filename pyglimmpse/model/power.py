from scipy import special
from scipy.stats import chi2

from pyglimmpse.constants import Constants
from pyglimmpse.finv import finv
from pyglimmpse.probf import probf


class Power:
    """
    Object representing power and associated metadata returned by power calculations.
    """
    def __init__(self):
        self.power = 0
        self.noncentrality_parameter = 0
        self.fmethod = "DEFAULT"
        self.lowerBound = Power()
        self.upperBound = Power()

    def glmmpcl(self,
                alphatest,
                dfh,   # df1
                n2,    # total_N ??? what is this
                dfe2,  # df2
                cl_type,
                n_est,
                rank_est,
                alpha_cl,
                alpha_cu,
                tolerance,
                power,
                omega):
        """
        This function computes confidence intervals for noncentrality and
        power for a General Linear Hypothesis (GLH  Ho:C*beta=theta0) test
        in the General Linear Univariate Model (GLUM: y=X*beta+e, HILE
        GAUSS), based on estimating the effect, error variance, or neither.
        Methods from Taylor and Muller (1995).

        :param f_a: = MSH/MSE, the F value observed if BETAhat=BETA and
                    Sigmahat=Sigma, under the alternative hypothesis, with:
                        MSH=Mean Square Hypothesis (effect variance)
                        MSE=Mean Square Error (error variance)
                    NOTE:
                        F_A = (N2/N1)*F_EST and
                        MSH = (N2/N1)*MSH_EST,
                        with "_EST" indicating value which was observed
                        in sample 1 (source of estimates)
        :param alphatest: Significance level for target GLUM test
        :param dfh: degrees of freedom for target GLH
        :param n2:
        :param dfe2: Error df for target hypothesis
        :param cl_type:  =1 if Sigma estimated and Beta known
                        =2 if Sigma estimated and Beta estimated
        :param n_est: (scalar) # of observations in analysis which yielded
                        BETA and SIGMA estimates
        :param rank_est: (scalar) design matrix rank in analysis which
                            yielded BETA and SIGMA estimates
        :param alpha_cl: Lower tail probability for confidence interval
        :param alpha_cu: Upper tail probability for confidence interval
        :param tolerance:
        :return:
            power_l, power confidence interval lower bound
            power_u, power confidence interval upper bound
            fmethod_l, Method used to calculate probability from F CDF
                        used in lower confidence limits power calculation
            fmethod_u, Method used to calculate probability from F CDF
                        used in lower confidence limits power calculation
            noncen_l, noncentrality confidence interval lower bound
            noncen_u, noncentrality confidence interval upper bound
            powerwarn, vector of power calculation warning counts
        """
        if self.cl_type == Constants.CLTYPE_DESIRED_KNOWN or self.cl_type == Constants.CLTYPE_DESIRED_ESTIMATE:
            if np.isnan(power):
                warnings.warn('Powerwarn16: Confidence limits are missing because power is missing.')
            else:
                f_a = omega/dfh
                dfe1, fcrit, noncen_e = self._calc_noncentrality(alphatest, dfe2, dfh, f_a, n_est, rank_est)

                self.lowerBound.noncentrality_parameter  = self._lowerbound_noncentrality(alpha_cl, cl_type, dfe1, dfh, f_a, noncen_e, tolerance)
                self.lowerBound.fmethod, self.lowerBound.power = self._lowerbound_power(alpha_cl, alphatest, dfe2, dfh, fcrit, self.lowerBound.noncentrality_parameter, tolerance)

                self.upperBound.noncentrality_parameter = self._upperbound_noncentrality(alpha_cu, cl_type, dfe1, dfh, f_a, noncen_e, tolerance)
                self.upperBound.fmethod, self.upperBound.power = self._upperbound_power(alpha_cu, alphatest, dfe2, dfh, fcrit, self.upperBound.noncentrality_parameter , tolerance)

                self._warn_conservative_ci(alpha_cl, cl_type, n2, n_est, self.lowerBound.noncentrality_parameter, self.upperBound.noncentrality_parameter)
        else:
            self.lowerBound = None
            self.upperBound = None
    def _warn_conservative_ci(self):
        """warning for conservative confidence interval"""
        if (self.cl_type == Constants.CLTYPE_DESIRED_KNOWN or
                    self.cl_type == Constants.CLTYPE_DESIRED_ESTIMATE) and self.n2 != self.n_est:
            if self.alpha_cl > 0 and self.noncen_l == 0:
                warnings.warn('PowerWarn5: The lower confidence limit on power is conservative.')
            if self.alpha_cl == 0 and self.noncen_u == 0:
                warnings.warn('PowerWarn10: The upper confidence limit on power is conservative.')

    def _calc_noncentrality(self):
        """Calculate noncentrality"""
        self.dfe1 = self.n_est - self.rank_est
        self.noncen_e = self.dfh * self.f_a
        self.fcrit = finv(1 - self.alphatest, self.dfh, self.dfe2)

    def _upperbound_noncentrality(self, alphatest, alpha_cu, cl_type, dfe1, dfe2, dfh, fcrit, f_a, noncen_e, tolerance):
        """Calculate upper bound for noncentrality"""
        x = 1 - alpha_cu
        y = alpha_cu
        # default values if alpha < tolerance
        noncentrality = float('Inf')
        prob = 0
        power = self._calc_bound(alphatest, alpha_cu, x, y, prob, noncentrality, cl_type, dfe1, dfe2, dfh, fcrit, f_a, noncen_e, tolerance)
        return power

    def _lowerbound_noncentrality(self, alphatest, alpha_cl, cl_type, dfe1, dfe2, dfh, fcrit, f_a, noncen_e, tolerance):
        """Calculate lower bound for noncentrality"""
        x = alpha_cl
        y = 1 - alpha_cl
        # default values if alpha < tolerance
        noncentrality = 0
        prob = 1 - alphatest
        power =  self._calc_bound(alphatest, alpha_cl, x, y, prob, noncentrality, cl_type, dfe1, dfe2, dfh, fcrit, f_a, noncen_e, tolerance)
        return power

    def _calc_bound(self, alphatest, alpha, x, y, prob, noncentrality, cl_type, dfe1, dfe2, dfh, fcrit, f_a, noncen_e, tolerance):
        """Calculate power bounds """
        fmethod = Constants.FMETHOD_MISSING
        if alpha > tolerance:
            if cl_type == Constants.CLTYPE_DESIRED_KNOWN:
                chi = chi2.ppf(x, dfe1)
                noncentrality = (chi / dfe1) * noncen_e
            elif cl_type == Constants.CLTYPE_DESIRED_ESTIMATE:
                bound = finv(y, dfh, dfe1)
                if f_a <= bound:
                    noncentrality = 0
                else:
                    noncentrality = special.ncfdtrinc(dfh, dfe1, y, f_a)
            prob, fmethod = probf(fcrit, dfh, dfe2, noncentrality)
        if fmethod == Constants.FMETHOD_NORMAL_LR and prob == 1:
            power_bound = alphatest
        else:
            power_bound = 1 - prob

        power = Power()
        power.power = power_bound
        power.fmethod = fmethod
        power.noncentrality_parameter = noncentrality
        return power