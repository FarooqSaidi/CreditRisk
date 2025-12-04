"""
Bayesian Risk Models Implementation
Uses analytical approximations and conjugate priors for efficient real-time inference.
"""
import numpy as np
from scipy import stats
from scipy.optimize import minimize
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

@dataclass
class BayesianResult:
    mean: float
    lower_hdi: float
    upper_hdi: float
    distribution: str
    params: Dict[str, float]

class BayesianPDModel:
    """
    Bayesian Logistic Regression for Probability of Default (PD)
    Uses Laplace Approximation for posterior estimation.
    """
    def __init__(self):
        self.coef_mean = None
        self.coef_cov = None
        
    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))
        
    def fit(self, X: np.ndarray, y: np.ndarray, prior_precision: float = 1.0):
        """
        Fit using Laplace Approximation (finding MAP and Hessian)
        X: Feature matrix (n_samples, n_features)
        y: Target vector (n_samples,)
        """
        n_samples, n_features = X.shape
        
        # Negative Log Posterior
        def neg_log_posterior(w):
            # Prior: w ~ N(0, I/prior_precision)
            prior = 0.5 * prior_precision * np.sum(w**2)
            
            # Likelihood: Bernoulli
            logits = X @ w
            # Stable log-likelihood
            # log(p) = log(1 / (1 + exp(-logits))) = -log(1 + exp(-logits))
            # log(1-p) = -logits - log(1 + exp(-logits))
            # ll = y * log(p) + (1-y) * log(1-p)
            #    = y * (-log(1+exp(-logits))) + (1-y) * (-logits - log(1+exp(-logits)))
            #    = -y*logits + y*logits - logits - log(...) -> Wait, standard derivation:
            # ll = sum(y_i * log(p_i) + (1-y_i) * log(1-p_i))
            
            # Use logaddexp for stability
            log_p = -np.logaddexp(0, -logits)
            log_1_minus_p = -np.logaddexp(0, logits)
            
            ll = np.sum(y * log_p + (1 - y) * log_1_minus_p)
            
            return prior - ll

        # Find MAP estimate
        w0 = np.zeros(n_features)
        res = minimize(neg_log_posterior, w0, method='BFGS')
        self.coef_mean = res.x
        
        # Compute Hessian at MAP (Inverse Covariance)
        # H = X.T @ S @ X + prior_precision * I
        # where S = diag(p * (1-p))
        p = self.sigmoid(X @ self.coef_mean)
        S = np.diag(p * (1 - p))
        H = X.T @ S @ X + prior_precision * np.eye(n_features)
        
        try:
            self.coef_cov = np.linalg.inv(H)
        except np.linalg.LinAlgError:
            self.coef_cov = np.eye(n_features) * 1e-6

    def predict_proba(self, X: np.ndarray, n_samples: int = 1000) -> BayesianResult:
        """
        Predict PD with uncertainty using Monte Carlo sampling from posterior approximation
        """
        if self.coef_mean is None:
            # Default fallback if not fitted
            return BayesianResult(0.05, 0.01, 0.10, "Beta", {})
            
        # Sample weights from posterior N(mu, Sigma)
        w_samples = np.random.multivariate_normal(self.coef_mean, self.coef_cov, size=n_samples)
        
        # Calculate logits and probs for each sample
        logits = X @ w_samples.T
        probs = self.sigmoid(logits)
        
        # For a single instance X (1, n_features), probs is (1, n_samples)
        # Average over samples
        mean_pd = np.mean(probs)
        lower_hdi = np.percentile(probs, 2.5)
        upper_hdi = np.percentile(probs, 97.5)
        
        return BayesianResult(
            mean=float(mean_pd),
            lower_hdi=float(lower_hdi),
            upper_hdi=float(upper_hdi),
            distribution="Posterior Predictive",
            params={"n_samples": n_samples}
        )

class BayesianLGDModel:
    """
    Bayesian LGD Model using Conjugate Priors (Beta Distribution)
    LGD is modeled as Beta(alpha, beta).
    Prior: Beta(a0, b0)
    Likelihood: Binomial (conceptually) or direct Beta updates
    """
    def __init__(self, prior_alpha=2.0, prior_beta=2.0):
        self.alpha = prior_alpha
        self.beta = prior_beta
        
    def update(self, observed_lgds: np.ndarray):
        """
        Update posterior based on observed LGDs (0 to 1)
        Using Method of Moments approximation for Beta update or simple count if binary
        For continuous LGD [0,1], we can treat it as:
        alpha_new = alpha_old + sum(lgd) * phi
        beta_new = beta_old + sum(1-lgd) * phi
        where phi is a precision parameter.
        
        Simplification: Treat observations as 'successes' and 'failures' weighted
        """
        # Simple update: mean matching
        n = len(observed_lgds)
        if n == 0:
            return
            
        # Estimate alpha/beta from data using Method of Moments
        mean = np.mean(observed_lgds)
        var = np.var(observed_lgds)
        
        if var < 1e-6: var = 1e-6
        
        # Common estimation for Beta parameters
        phi = (mean * (1 - mean) / var) - 1
        if phi < 0: phi = 1.0 # Fallback
        
        alpha_data = mean * phi
        beta_data = (1 - mean) * phi
        
        # Bayesian Update (weighted average of prior and data)
        # This is a heuristic update for continuous data
        weight = n / (n + 10.0) # Weight of data increases with n
        
        self.alpha = self.alpha * (1 - weight) + alpha_data * weight * n
        self.beta = self.beta * (1 - weight) + beta_data * weight * n

    def predict(self) -> BayesianResult:
        mean_lgd = self.alpha / (self.alpha + self.beta)
        
        # HDI for Beta distribution
        lower_hdi = stats.beta.ppf(0.025, self.alpha, self.beta)
        upper_hdi = stats.beta.ppf(0.975, self.alpha, self.beta)
        
        return BayesianResult(
            mean=float(mean_lgd),
            lower_hdi=float(lower_hdi),
            upper_hdi=float(upper_hdi),
            distribution="Beta",
            params={"alpha": float(self.alpha), "beta": float(self.beta)}
        )

class BayesianHazardModel:
    """
    Bayesian Survival Analysis (Weibull)
    Estimates Time-to-Default
    """
    def __init__(self):
        self.shape = 1.0 # k
        self.scale = 1.0 # lambda
        
    def fit(self, durations, events):
        """
        Fit Weibull parameters using MLE (can be viewed as MAP with flat prior)
        durations: time elapsed
        events: 1 if default occurred, 0 if censored
        """
        # Use scipy.stats.weibull_min to fit
        # Only use uncensored data for simple fit, or custom likelihood for censored
        defaults = durations[events == 1]
        if len(defaults) < 2:
            return
            
        # Fit shape (c) and scale
        params = stats.weibull_min.fit(defaults, floc=0)
        self.shape = params[0]
        self.scale = params[2]
        
    def predict_survival(self, t: float) -> BayesianResult:
        """Predict survival probability at time t"""
        # Survival function S(t) = exp(-(t/scale)^shape)
        surv_prob = np.exp(-(t / self.scale) ** self.shape)
        
        # Approximate uncertainty (heuristic)
        std_dev = 0.05 # Placeholder for full Bayesian uncertainty
        
        return BayesianResult(
            mean=float(surv_prob),
            lower_hdi=max(0.0, float(surv_prob - 1.96 * std_dev)),
            upper_hdi=min(1.0, float(surv_prob + 1.96 * std_dev)),
            distribution="Weibull",
            params={"shape": float(self.shape), "scale": float(self.scale)}
        )
