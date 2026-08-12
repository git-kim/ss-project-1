import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
import statsmodels.formula.api as smf

def estimate_dispersion_alpha(poisson_result) -> float:
    """
    Estimates the negative binomial alpha with the standard auxiliary
    regression: ((y - mu)^2 - y) / mu = alpha * mu.
    """
    y = poisson_result.model.endog
    mu = poisson_result.mu
    aux = ((y - mu) ** 2 - y) / mu
    return float(sm.OLS(aux, mu).fit().params[0])

def fit_negative_binomial(formula: str, data: pd.DataFrame)\
    -> tuple[object, float]:
    """
    Returns:
        (fitted negative binomial GLM result, estimated alpha)
    """
    poisson_result = smf.glm(formula, data=data,
                             family=sm.families.Poisson()).fit()
    alpha = estimate_dispersion_alpha(poisson_result)

    negative_binomial_result = smf.glm(
        formula, data=data,
        family=sm.families.NegativeBinomial(alpha=alpha)).fit()

    return negative_binomial_result, alpha

def get_irr_with_ci(result, covariates: dict, temperatures,
                    reference_temperature: float)\
    -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Incidence rate ratio against the reference temperature, computed as a
    contrast of design matrix rows so that the covariance between the two
    predictions is taken into account.

    Returns:
        (irr, lower bound, upper bound)
    """
    design_info = result.model.data.design_info

    grid = pd.DataFrame([
        {**covariates, "평균기온": temperature}
        for temperature in [*temperatures, reference_temperature]
        ])

    matrix = np.asarray(patsy.build_design_matrices([design_info], grid)[0])
    reference_row = matrix[-1]

    effects = []

    for row in matrix[:-1]:
        test = result.t_test(row - reference_row)
        lower, upper = test.conf_int()[0]
        effects.append((test.effect[0], lower, upper))

    return tuple(np.exp(np.asarray(effects)).T)
