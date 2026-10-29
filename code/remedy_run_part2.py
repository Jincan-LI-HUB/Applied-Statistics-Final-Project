#!/usr/bin/env python3
"""
Part 2: K-fold CV + Quantile Regression + BCa Bootstrap for UFUG 2104 HW1
"""
import os, warnings
<<<<<<< HEAD
=======
from pathlib import Path
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.stats import norm as np_norm
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from sklearn.model_selection import KFold
<<<<<<< HEAD
DATA = "/mnt/e/canfiles/Common courses study/大学通识/25-26 Spring/UFUG 2104 Applied statistics/HW1_project_report/data/clean/billionaires_clean.csv"
TAB = "/mnt/e/canfiles/Common courses study/大学通识/25-26 Spring/UFUG 2104 Applied statistics/HW1_project_report/output/tab"
=======
def find_project_root(start=None):
    start = Path(start or __file__).resolve()
    for p in [start.parent] + list(start.parents):
        if (p / "data" / "raw" / "Billionaires Statistics Dataset.csv").exists():
            return p
    raise FileNotFoundError("Could not locate project root from remedy_run_part2.py")

BASE = find_project_root()
DATA = BASE / "data" / "clean" / "billionaires_clean.csv"
TAB = BASE / "output" / "tab"
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
os.makedirs(TAB, exist_ok=True)

print("Loading data...")
df = pd.read_csv(DATA)
df['selfMade_bin'] = df['selfMade'].map({True: 1, False: 0, 'True': 1, 'False': 0, 1: 1, 0: 0}).fillna(0).astype(int)
df['gender_F'] = (df['gender'] == 'F').astype(int)
df['log_finalWorth'] = np.log1p(df['finalWorth'])
df['log_gdp'] = np.log1p(df['gdp_country_num'])
df['category'] = df['category'].fillna('Unknown')
df_c = df.dropna(subset=['log_finalWorth', 'log_gdp', 'age', 'selfMade_bin', 'gender_F', 'category'])
<<<<<<< HEAD
=======
top_categories = df_c['category'].value_counts().head(8).index
df_c = df_c[df_c['category'].isin(top_categories)].copy()
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3

# ============================================================
# 1. K-FOLD CROSS-VALIDATION FOR MODEL C
# ============================================================
print("\n=== K-FOLD CROSS-VALIDATION (Model C) ===")

df_cv = df_c.dropna(subset=['log_finalWorth','log_gdp','age','selfMade_bin','gender_F','category']).copy()
cat_dums_cv = pd.get_dummies(df_cv['category'], prefix='C', drop_first=True)
X_cv = pd.concat([df_cv[['log_gdp','age','selfMade_bin','gender_F']].astype(float), cat_dums_cv.astype(float)], axis=1)
X_cv = sm.add_constant(X_cv)
y_cv = df_cv['log_finalWorth'].values.astype(float)

k = 10
kf = KFold(n_splits=k, shuffle=True, random_state=42)
r2_oos = []
r2_is = []

for fold_idx, (train_idx, test_idx) in enumerate(kf.split(X_cv)):
    X_tr, X_te = X_cv.iloc[train_idx], X_cv.iloc[test_idx]
    y_tr, y_te = y_cv[train_idx], y_cv[test_idx]
    model = sm.OLS(y_tr, X_tr).fit()
    r2_is.append(model.rsquared)
    y_pred = model.predict(X_te)
    ss_res = np.sum((y_te - y_pred)**2)
    ss_tot = np.sum((y_te - np.mean(y_te))**2)
    r2_oos.append(1 - ss_res/ss_tot if ss_tot > 0 else np.nan)

r2_is = np.array(r2_is)
r2_oos = np.array(r2_oos)
r2_is_mean = float(np.mean(r2_is))
r2_oos_mean = float(np.mean(r2_oos))
r2_oos_std = float(np.std(r2_oos))

print(f"In-sample R^2 (mean): {r2_is_mean:.4f}")
print(f"Out-of-sample R^2 (mean): {r2_oos_mean:.4f} +/- {r2_oos_std:.4f}")
print(f"Fold-level OOS R^2: {[round(x,4) for x in r2_oos]}")

cv_tab = (
    r"\begin{tabular}{lcc}"
    + r"\toprule "
    + r"Metric & Value \\ "
    + r"\midrule "
<<<<<<< HEAD
    + f"In-sample $R^2$ (10-fold mean) & {r2_is_mean:.4f} \\ "
    + f"Out-of-sample $R^2$ (10-fold mean) & {r2_oos_mean:.4f} \\ "
    + f"Out-of-sample $R^2$ SD & {r2_oos_std:.4f} \\ "
    + f"In-sample vs. OOS gap & {r2_is_mean - r2_oos_mean:.4f} \\ "
=======
    + f"In-sample $R^2$ (10-fold mean) & {r2_is_mean:.4f} \\\\ "
    + f"Out-of-sample $R^2$ (10-fold mean) & {r2_oos_mean:.4f} \\\\ "
    + f"Out-of-sample $R^2$ SD & {r2_oos_std:.4f} \\\\ "
    + f"In-sample vs. OOS gap & {r2_is_mean - r2_oos_mean:.4f} \\\\ "
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
    + r"\bottomrule "
    + r"\end{tabular}"
)
with open(f"{TAB}/tab_M7_kfold_cv.tex", 'w') as f:
    f.write(cv_tab)
print(f"K-fold CV table written.")

# ============================================================
# 2. QUANTILE REGRESSION
# ============================================================
print("\n=== QUANTILE REGRESSION ===")

<<<<<<< HEAD
df_qr = df[['log_finalWorth','log_gdp','age','selfMade_bin','gender_F','category']].dropna()
=======
df_qr = df_c[['log_finalWorth','log_gdp','age','selfMade_bin','gender_F','category']].dropna()
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
cat_qr = pd.get_dummies(df_qr['category'], prefix='C', drop_first=True)
X_qr = pd.concat([df_qr[['log_gdp','age','selfMade_bin','gender_F']].astype(float), cat_qr.astype(float)], axis=1)
X_qr = sm.add_constant(X_qr)
y_qr = df_qr['log_finalWorth'].values.astype(float)

tau_results = {}
for tau in [0.25, 0.5, 0.75, 0.9]:
    try:
        qr = QuantReg(y_qr, X_qr).fit(q=tau, vcov='robust', kernel='epa', bandwidth='hsheather')
        gdp_col = 'log_gdp'
        b = float(qr.params[gdp_col])
        p = float(qr.pvalues[gdp_col])
        tau_results[tau] = (b, p)
        print(f"  tau={tau}: log_gdp beta={b:.4f}, p={p:.4f}")
    except Exception as e:
        print(f"  tau={tau} failed: {e}")

# Build quantile regression table
tau_labels = ["tau=0.25", "tau=0.50", "tau=0.75", "tau=0.90"]
tau_betas = [f"${tau_results[t][0]:.4f}$" for t in [0.25, 0.5, 0.75, 0.9]]
tau_pvals = [f"${tau_results[t][1]:.3f}$" for t in [0.25, 0.5, 0.75, 0.9]]

qr_tab = (
    r"\begin{tabular}{lcccc} "
    + r"\toprule "
    + "& " + " & ".join(tau_labels) + r" \\ "
    + r"\midrule "
    + r"log\_gdp $\beta$ & " + " & ".join(tau_betas) + r" \\ "
    + r"P-value & " + " & ".join(tau_pvals) + r" \\ "
    + r"\bottomrule "
    + r"\end{tabular}"
)
with open(f"{TAB}/tab_M7_quantile_regression.tex", 'w') as f:
    f.write(qr_tab)
print(f"Quantile regression table written.")

# ============================================================
# 3. BCA BOOTSTRAP FOR GINI
# ============================================================
print("\n=== BCA BOOTSTRAP FOR GINI ===")

def gini_coefficient(x):
    x = np.sort(np.array(x, dtype=float))
    n = len(x)
    if n < 2:
        return np.nan
    idx = np.arange(1, n+1)
    return (2 * np.sum(idx * x) / (n * np.sum(x))) - (n + 1) / n

def bca_ci(data, stat_fn, B=5000, alpha=0.05):
    n = len(data)
    theta_hat = stat_fn(data)
    rng = np.random.default_rng(42)
    reps = np.array([stat_fn(rng.choice(data, size=n, replace=True)) for _ in range(B)])
    z0 = np_norm.ppf(np.mean(reps < theta_hat))
    jackknife = np.array([stat_fn(np.delete(data, i)) for i in range(n)])
    jk_mean = np.mean(jackknife)
    a_num = np.sum((jk_mean - jackknife)**3)
    a_den = 6 * (np.sum((jk_mean - jackknife)**2)**1.5)
    a = a_num / a_den if a_den != 0 else 0
    lo_p = max(0.0001, min(0.9999, np_norm.cdf(z0 + np_norm.ppf(alpha/2))))
    hi_p = max(0.0001, min(0.9999, np_norm.cdf(z0 + np_norm.ppf(1 - alpha/2))))
    ci_lo = np.percentile(reps, lo_p * 100)
    ci_hi = np.percentile(reps, hi_p * 100)
    return theta_hat, ci_lo, ci_hi, z0, a, reps

np.random.seed(42)
FW = df['finalWorth'].dropna().values.astype(float)
gini_pt, bca_lo, bca_hi, z0, accel, bca_reps = bca_ci(FW, gini_coefficient, B=5000)

pct_lo = float(np.percentile(bca_reps, 2.5))
pct_hi = float(np.percentile(bca_reps, 97.5))

print(f"Gini point estimate: {gini_pt:.4f}")
print(f"BCa 95% CI: [{bca_lo:.4f}, {bca_hi:.4f}]")
print(f"Percentile 95% CI: [{pct_lo:.4f}, {pct_hi:.4f}]")
print(f"Difference: lower {(bca_lo-pct_lo):.4f}, upper {(bca_hi-pct_hi):.4f}")
print(f"z0={z0:.4f}, accel={accel:.4f}")

bca_tab = (
    r"\begin{tabular}{lcc} "
    + r"\toprule "
    + r"Method & Point Estimate & 95\% CI \\ "
    + r"\midrule "
<<<<<<< HEAD
    + f"Percentile Bootstrap & ${gini_pt:.4f}$ & $[{pct_lo:.4f}, {pct_hi:.4f}]$ \\ "
    + f"BCa Bootstrap & ${gini_pt:.4f}$ & $[{bca_lo:.4f}, {bca_hi:.4f}]$ \\ "
    + f" Bias correction $z_0$ & \multicolumn{{2}}{{c}}{{{z0:.4f}}} \\ "
    + f" Acceleration $a$ & \multicolumn{{2}}{{c}}{{{accel:.4f}}} \\ "
=======
    + f"Percentile Bootstrap & ${gini_pt:.4f}$ & $[{pct_lo:.4f}, {pct_hi:.4f}]$ \\\\ "
    + f"BCa Bootstrap & ${gini_pt:.4f}$ & $[{bca_lo:.4f}, {bca_hi:.4f}]$ \\\\ "
    + f" Bias correction $z_0$ & \\multicolumn{{2}}{{c}}{{{z0:.4f}}} \\\\ "
    + f" Acceleration $a$ & \\multicolumn{{2}}{{c}}{{{accel:.4f}}} \\\\ "
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
    + r"\bottomrule "
    + r"\end{tabular}"
)
with open(f"{TAB}/tab_M4_bca_bootstrap.tex", 'w') as f:
    f.write(bca_tab)
print(f"BCa bootstrap table written.")

print("\n=== ALL PART 2 ANALYSES COMPLETE ===")
print(f"Files in {TAB}:")
for fn in sorted(os.listdir(TAB)):
    if fn.startswith('tab_M7_kfold') or fn.startswith('tab_M7_quantile') or fn.startswith('tab_M4_bca'):
        print(f"  {fn}")
<<<<<<< HEAD
=======

>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
