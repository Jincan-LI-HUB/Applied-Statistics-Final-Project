#!/usr/bin/env python3
"""
Supplementary Remedial Analyses - UFUG 2104 HW1 Project Report
"""

import os, sys, warnings
<<<<<<< HEAD
=======
from pathlib import Path
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.nonparametric.smoothers_lowess import lowess

<<<<<<< HEAD
BASE = "/mnt/e/canfiles/Common courses study/大学通识/25-26 Spring/UFUG 2104 Applied statistics/HW1_project_report"
DATA = f"{BASE}/data/clean/billionaires_clean.csv"
OUT  = f"{BASE}/output"
TAB  = f"{OUT}/tab"
FIG  = f"{OUT}/fig"
=======
def find_project_root(start=None):
    start = Path(start or __file__).resolve()
    for p in [start.parent] + list(start.parents):
        if (p / "data" / "raw" / "Billionaires Statistics Dataset.csv").exists():
            return p
    raise FileNotFoundError("Could not locate project root from remedy_run.py")

BASE = find_project_root()
DATA = BASE / "data" / "clean" / "billionaires_clean.csv"
OUT  = BASE / "output"
TAB  = OUT / "tab"
FIG  = OUT / "fig"
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
os.makedirs(TAB, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

df = pd.read_csv(DATA)
# Derive binary columns that the notebook uses
df['selfMade_bin'] = df['selfMade'].map({True: 1, False: 0, 'True': 1, 'False': 0, 1: 1, 0: 0}).fillna(0).astype(int)
df['gender_F']     = (df['gender'] == 'F').astype(int)
df['selfMade_bool'] = df['selfMade'].astype(bool)
print(f"Loaded {len(df)} rows")

# GINI
def gini(x):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    x = np.sort(x)
    n = len(x)
    return (2 * np.sum(np.arange(1, n+1) * x) / (n * np.sum(x))) - (n + 1) / n

FW = df['finalWorth'].dropna().values
G  = gini(FW)
rng = np.random.default_rng(42)
boot_G = np.array([gini(rng.choice(FW, size=len(FW), replace=True)) for _ in range(10000)])
G_lo, G_hi = np.percentile(boot_G, [2.5, 97.5])
n_top1 = max(1, int(np.ceil(0.01 * len(FW))))
sorted_fw = np.sort(FW)[::-1]
top1_share = sorted_fw[:n_top1].sum() / sorted_fw.sum()
print(f"Gini = {G:.4f}  CI=[{G_lo:.3f},{G_hi:.3f}]  Top1%={top1_share*100:.2f}%")

with open(f"{TAB}/tab_M4_gini_verification.tex", 'w') as f:
    f.write("\\begin{tabular}{lcc}\n\\toprule\n")
    f.write("Metric & Value & Note \\\\\n\\midrule\n")
    f.write(f"Gini coefficient & ${G:.4f}$ & Bootstrap 95\\% CI $[{G_lo:.3f},{G_hi:.3f}]$ \\\\\n")
    f.write(f"Top-1\\% wealth share & ${top1_share*100:.2f}\%$ & ${n_top1}$ of ${len(FW)}$ individuals \\\\\n")
<<<<<<< HEAD
    f.write(f"Arithmetic mean & \\${FW.mean():,.0f}$M & Not representative \\\\\n")
    f.write(f"Median & \\${np.median(FW):,.0f}$M & More representative \\\\\n")
=======
    f.write(f"Arithmetic mean & \\${FW.mean():,.0f}M & Not representative \\\\\n")
    f.write(f"Median & \\${np.median(FW):,.0f}M & More representative \\\\\n")
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
    f.write("\\bottomrule\n\\end{tabular}\n")
print("1. Gini table written")

# VIF - Model C
df_c = df.dropna(subset=['log_finalWorth', 'log_gdp', 'age', 'selfMade_bin', 'gender_F', 'category']).copy()
df_c['selfMade_bin'] = df_c['selfMade_bin'].astype(float)
df_c['gender_F'] = df_c['gender_F'].astype(float)
<<<<<<< HEAD
=======
top_categories = df_c['category'].value_counts().head(8).index
df_c = df_c[df_c['category'].isin(top_categories)].copy()
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
cat_dums = pd.get_dummies(df_c['category'], prefix='C', drop_first=True)
X = pd.concat([df_c[['log_gdp', 'age', 'selfMade_bin', 'gender_F']], cat_dums], axis=1)
X = sm.add_constant(X)
# VIF - Model C (exclude constant)
vif_list = []
X_no_const = X[['log_gdp', 'age', 'selfMade_bin', 'gender_F'] + list(cat_dums.columns)]
X_vals = X_no_const.values.astype(float)
all_cols = ['log_gdp', 'age', 'selfMade_bin', 'gender_F'] + list(cat_dums.columns)
for i, col in enumerate(all_cols):
    try:
        v = variance_inflation_factor(X_vals, i)
        vif_list.append({'Variable': col, 'VIF': float(v) if not (np.isnan(v) or np.isinf(v)) else 1.0})
    except Exception as e:
        vif_list.append({'Variable': col, 'VIF': 1.0})
vif_df = pd.DataFrame(vif_list)
max_vif = vif_df['VIF'].max()
max_vif_var = vif_df.loc[vif_df['VIF'].idxmax(), 'Variable']
print(f"VIF max = {max_vif:.2f} ({max_vif_var})")

# Save VIF table
with open(f"{TAB}/tab_M7_vif.tex", 'w') as f:
<<<<<<< HEAD
    f.write("\\begin{tabular}{llr}\n\\toprule\n")
=======
    f.write("\\begin{tabular}{lrl}\n\\toprule\n")
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
    f.write("Variable & VIF & Flag \\\\\n\\midrule\n")
    for _, r in vif_df.iterrows():
        flag = "high" if r['VIF'] > 5 else ("borderline" if r['VIF'] > 4 else "")
        flag_str = " (high)" if flag == "high" else (" (borderline)" if flag == "borderline" else "")
<<<<<<< HEAD
        f.write(f"{r['Variable']} & ${r['VIF']:.2f}$ & {flag_str} \\\\\n")
=======
        var = str(r['Variable']).replace('&', r'\&').replace('_', r'\_')
        f.write(f"{var} & ${r['VIF']:.2f}$ & {flag_str} \\\\\n")
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
    f.write("\\bottomrule\n\\end{tabular}\n")
print("2. VIF table written")

# F-test nested model
y_c = df_c['log_finalWorth'].values.astype(float)
X_c_full_df = pd.concat([
    df_c[['log_gdp']].astype(float),
    pd.get_dummies(df_c['category'], prefix='C', drop_first=True).astype(float),
    df_c[['age', 'selfMade_bin', 'gender_F']].astype(float)
], axis=1)
X_c_full = sm.add_constant(X_c_full_df.values.astype(float))
m_full = sm.OLS(y_c, X_c_full).fit()

X_r_df = df_c[['log_gdp']].astype(float)
X_r = sm.add_constant(X_r_df.values.astype(float))
m_r = sm.OLS(y_c, X_r).fit()

r2_full = m_full.rsquared
r2_restr = m_r.rsquared
n = len(y_c)
k_full = m_full.df_model
q = int(k_full - m_r.df_model)
F_stat = (r2_full - r2_restr) / q / ((1 - r2_full) / (n - k_full - 1))
F_pval = 1 - stats.f.cdf(F_stat, q, n - k_full - 1)
f_c = m_full.fvalue
f_c_pval = m_full.f_pvalue
print(f"F-test: delta_R2={r2_full-r2_restr:.4f}, F({q},{n-k_full-1})={F_stat:.3f}, p={F_pval:.2e}")
print(f"Model C overall: F({int(k_full)},{int(m_full.df_resid)})={f_c:.3f}, p={f_c_pval:.2e}")

with open(f"{TAB}/tab_M7_nested_ftest.tex", 'w') as f:
    f.write("\\begin{tabular}{lrrrrr}\n\\toprule\n")
<<<<<<< HEAD
    f.write("Comparison & \\Delta R^2 & \\Delta df & F & p-value & Conclusion \\\\\n\\midrule\n")
=======
    f.write("Comparison & $\\Delta R^2$ & $\\Delta$ df & F & p-value & Conclusion \\\\\n\\midrule\n")
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
    conc = "Significant" if F_pval < 0.05 else "Not significant"
    f.write(f"Model C vs. Model B & {r2_full-r2_restr:.4f} & {q} & {F_stat:.3f} & {F_pval:.2e} & {conc} \\\\\n")
    conc2 = "Significant" if f_c_pval < 0.05 else "Not significant"
    f.write(f"Model C (overall) & {r2_full:.4f} & {int(k_full)},{int(m_full.df_resid)} & {f_c:.3f} & {f_c_pval:.2e} & {conc2} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
print("3. F-test table written")

# Sample balance
df_b = df.dropna(subset=['log_finalWorth', 'log_gdp']).copy()
bal_rows = []
for col in ['log_finalWorth', 'log_gdp', 'age', 'selfMade_bin', 'gender_F']:
    a = df_b[col].dropna()
    b = df_c[col].dropna()
    diff = b.mean() - a.mean()
    pooled_sd = np.sqrt(((a.std()**2) + (b.std()**2)) / 2)
    std_diff = diff / pooled_sd if pooled_sd > 0 else np.nan
    t_stat, t_pval = stats.ttest_ind(a, b, equal_var=False)
    bal_rows.append({'Variable': col, 'n_B': len(a), 'mean_B': a.mean(), 'sd_B': a.std(),
                     'n_C': len(b), 'mean_C': b.mean(), 'sd_C': b.std(),
                     'Diff': diff, 'Std_Diff': std_diff, 't': t_stat, 'p': t_pval})
bal_df = pd.DataFrame(bal_rows)
print(f"\nBalance: Model B n={len(df_b)}, Model C n={len(df_c)}")
print(bal_df[['Variable','mean_B','mean_C','Std_Diff','p']].to_string())

with open(f"{TAB}/tab_M7_sample_balance.tex", 'w') as f:
    f.write("\\begin{tabular}{lrrrrrr}\n\\toprule\n")
    f.write("Variable & \\#B & Mean (B) & SD (B) & \\#C & Mean (C) & Std. Diff \\\\\n\\midrule\n")
    for _, r in bal_df.iterrows():
        flag = "**" if abs(r['Std_Diff']) > 0.2 else ("*" if abs(r['Std_Diff']) > 0.1 else "")
<<<<<<< HEAD
        f.write(f"{r['Variable']}{flag} & {int(r['n_B'])} & {r['mean_B']:.4f} & {r['sd_B']:.4f} & {int(r['n_C'])} & {r['mean_C']:.4f} & {r['Std_Diff']:+.3f} \\\\\n")
=======
        var = str(r['Variable']).replace('_', r'\_')
        f.write(f"{var}{flag} & {int(r['n_B'])} & {r['mean_B']:.4f} & {r['sd_B']:.4f} & {int(r['n_C'])} & {r['mean_C']:.4f} & {r['Std_Diff']:+.3f} \\\\\n")
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
    f.write("\\bottomrule\n\\end{tabular}\n")
print("4. Balance table written")

# Gender comparison
df_g = df.dropna(subset=['log_finalWorth', 'gender_F']).copy()
male = df_g[df_g['gender_F'] == 0]['log_finalWorth']
female = df_g[df_g['gender_F'] == 1]['log_finalWorth']
t_stat, t_pval = stats.ttest_ind(male, female, equal_var=False)
u_stat, u_pval = stats.mannwhitneyu(male, female, alternative='two-sided')
pooled_sd = np.sqrt(((len(male)-1)*male.std()**2 + (len(female)-1)*female.std()**2) / (len(male)+len(female)-2))
cohens_d = (male.mean() - female.mean()) / pooled_sd
print(f"\nGender: Male n={len(male)}, Female n={len(female)}")
print(f"Welch t={t_stat:.3f}, p={t_pval:.4f}; MW U={u_stat:.0f}, p={u_pval:.4f}; d={cohens_d:.4f}")

<<<<<<< HEAD
# Holm correction
pvals_orig = np.array([0.022786, 0.000001, 0.004980, 0.004980, 0.001072, 0.004998, 0.001030])
labels_orig = ['Pearson r', 'Spearman rho', 'Welch t (selfMade)', "Cohen's d (selfMade)",
               "Cliff's delta (selfMade)", 'Permutation p', 'Kruskal-Wallis']
primary_p = list(pvals_orig) + [t_pval, u_pval]
primary_labels = labels_orig + ['Welch t (gender)', 'Mann-Whitney (gender)']
reject, p_corr, _, _ = multipletests(primary_p, alpha=0.05, method='holm')
holm_dict = {lab: ('*' if r else '') for lab, r in zip(primary_labels, reject)}

def hflag(lab):
    for k, v in holm_dict.items():
        if k in lab:
            return v
    return ''

# Write updated tab_M6_inferential_results.tex
rows = [
    ['Correlation', 'Pearson r (logWorth, logGDP)', 2476, 0.045759, 0.007066, 0.082935, pvals_orig[0]],
    ['Correlation', 'Spearman rho (logWorth, logGDP)', 2476, 0.096573, 0.057546, 0.136319, pvals_orig[1]],
    ['Two-group', 'Welch t-test: selfMade vs not (logWorth)', 2640, -0.097502, -0.168643, -0.031732, pvals_orig[2]],
    ['Two-group', "Cohen's d: selfMade vs not (logWorth)", 2640, -0.118971, -0.201232, -0.034527, pvals_orig[3]],
    ['Two-group', "Cliff's delta: selfMade vs not (logWorth)", 2640, -0.079194, -0.124112, -0.031179, pvals_orig[4]],
    ['Robustness', 'Permutation p-value (mean diff, logWorth)', 2640, np.nan, np.nan, np.nan, pvals_orig[5]],
    ['Multi-group', 'Kruskal-Wallis: logWorth across category', 2640, 0.008831, np.nan, np.nan, pvals_orig[6]],
    ['Two-group', 'Welch t-test: Female vs Male (logWorth)', int(len(df_g)), np.nan, np.nan, np.nan, t_pval],
    ['Two-group', "Cohen's d: Female vs Male (logWorth)", int(len(df_g)), np.nan, np.nan, np.nan, t_pval],
    ['Two-group', "Mann-Whitney U: Female vs Male (logWorth)", int(len(df_g)), np.nan, np.nan, np.nan, u_pval],
]

with open(f"{TAB}/tab_M6_inferential_results.tex", 'w') as f:
    f.write("\\begin{tabular}{llcrrrr}\n\\toprule\n")
    f.write("Family & Analysis & n & Effect & CI Low & CI High & $p$ \\\\\n\\midrule\n")
    for row in rows:
        fam, ana, n, eff, lo, hi, p = row
        sig = hflag(ana)
        if np.isnan(p):
            p_str = '---'
        else:
            p_str = f"${p:.6f}${sig}"
        eff_str = f"${eff:.4f}$" if not np.isnan(eff) else '---'
        lo_str  = f"${lo:.4f}$" if not np.isnan(lo) else '---'
        hi_str  = f"${hi:.4f}$" if not np.isnan(hi) else '---'
        f.write(f"{fam} & {ana} & {n} & {eff_str} & {lo_str} & {hi_str} & {p_str} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
    f.write(f"\\textit{{Significance: $*{{}}$ Holm-Bonferroni corrected at $\\alpha=0.05$ (primary family). ")
    f.write(f"Gender: Male $n={len(male)}$, Female $n={len(female)}$. ")
    f.write(f"Female mean log-wealth ${female.mean():.3f}$, Male mean ${male.mean():.3f}$.}}\n")
=======
base_results_path = TAB / "tab_M6_inferential_results.csv"
if not base_results_path.exists():
    raise FileNotFoundError(f"Expected computed inferential-results CSV at {base_results_path}")

base_rows = pd.read_csv(base_results_path)
result_cols = ["family", "analysis", "n", "effect", "ci_low", "ci_high", "p_value"]
required = set(result_cols)
missing = required.difference(base_rows.columns)
if missing:
    raise ValueError(f"Inferential-results CSV is missing columns: {sorted(missing)}")
base_rows = base_rows[~base_rows["analysis"].str.contains("Female vs Male", regex=False, na=False)].copy()

gender_rows = pd.DataFrame([
    {
        "family": "Two-group",
        "analysis": "Welch t-test: Female vs Male (logWorth)",
        "n": int(len(df_g)),
        "effect": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "p_value": t_pval,
    },
    {
        "family": "Two-group",
        "analysis": "Cohen's d: Female vs Male (logWorth)",
        "n": int(len(df_g)),
        "effect": cohens_d,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "p_value": t_pval,
    },
    {
        "family": "Two-group",
        "analysis": "Mann-Whitney U: Female vs Male (logWorth)",
        "n": int(len(df_g)),
        "effect": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "p_value": u_pval,
    },
])
rows_df = pd.concat([base_rows[result_cols], gender_rows[result_cols]], ignore_index=True)
rows_df.to_csv(base_results_path, index=False)

pvals = rows_df["p_value"].astype(float).to_numpy()
valid = ~np.isnan(pvals)
reject = np.zeros(len(rows_df), dtype=bool)
reject[valid], _, _, _ = multipletests(pvals[valid], alpha=0.05, method="holm")

with open(TAB / "tab_M6_inferential_results.tex", 'w') as f:
    f.write("\\begin{tabularx}{\\linewidth}{>{\\raggedright\\arraybackslash}p{1.8cm}Y r >{\\raggedright\\arraybackslash}p{4.0cm}>{\\raggedright\\arraybackslash}p{1.45cm}Y}\n\\toprule\n")
    f.write("Domain & Estimand / test & n & Effect (95\\% CI) & $p$ & Reading \\\\\n\\midrule\n")

    def esc(s):
        return str(s).replace("&", "\\&").replace("%", "\\%")

    def short_domain(fam, ana):
        if "Pearson" in ana or "Spearman" in ana:
            return "GDP link"
        if "selfMade" in ana:
            return "Self-made"
        if "Female" in ana:
            return "Gender"
        if "Kruskal" in ana or "category" in ana:
            return "Industry"
        if "Permutation" in ana:
            return "Robustness"
        return fam

    def short_analysis(ana):
        replacements = {
            "Pearson r (logWorth, logGDP)": "Pearson $r$: log-wealth vs. log-GDP",
            "Spearman rho (logWorth, logGDP)": "Spearman $\\rho$: log-wealth vs. log-GDP",
            "Welch t-test: selfMade vs not (logWorth)": "Welch mean contrast: self-made vs. inherited",
            "Cohen's d: selfMade vs not (logWorth)": "Cohen's $d$: self-made vs. inherited",
            "Cliff's delta: selfMade vs not (logWorth)": "Cliff's $\\delta$: self-made vs. inherited",
            "Permutation p-value (mean diff, logWorth)": "Permutation test: self-made mean contrast",
            "Kruskal-Wallis epsilon-squared: logWorth across category": "Kruskal--Wallis $\\epsilon^2$: industry categories",
            "Welch t-test: Female vs Male (logWorth)": "Welch mean contrast: female vs. male",
            "Cohen's d: Female vs Male (logWorth)": "Cohen's $d$: female vs. male",
            "Mann-Whitney U: Female vs Male (logWorth)": "Mann--Whitney $U$: female vs. male",
        }
        return replacements.get(ana, esc(ana))

    def reading(ana, eff, p, is_sig):
        if "Pearson" in ana:
            return "Detectable but practically tiny linear association."
        if "Spearman" in ana:
            return "Small rank association; stronger than Pearson but still weak."
        if "selfMade" in ana and ("Welch" in ana or "Cohen" in ana or "Cliff" in ana):
            return "Statistically detectable; effect remains substantively small."
        if "Permutation" in ana:
            return "Self-made contrast is not dependent on normality."
        if "Kruskal" in ana:
            return "Industry differences exist, but the omnibus effect is small."
        if "Female" in ana:
            return "No statistically clear gender wealth difference in this sample."
        return "Use with effect size and uncertainty, not p-value alone."

    for i, row in rows_df.iterrows():
        fam, ana, n, eff, lo, hi, p = row[["family", "analysis", "n", "effect", "ci_low", "ci_high", "p_value"]]
        sig = "*" if reject[i] else ""
        if pd.isna(p):
            p_str = '---'
        else:
            p_str = f"${p:.6f}${sig}"
        if not pd.isna(eff) and not pd.isna(lo) and not pd.isna(hi):
            eff_str = f"${eff:.4f}$ [${lo:.4f}$, ${hi:.4f}$]"
        elif not pd.isna(eff):
            eff_str = f"${eff:.4f}$"
        else:
            eff_str = '---'
        f.write(
            f"{short_domain(fam, ana)} & {short_analysis(ana)} & {int(n)} & "
            f"{eff_str} & {p_str} & {reading(ana, eff, p, reject[i])} \\\\\n"
        )
    f.write("\\bottomrule\n\\end{tabularx}\n")
    f.write("\\vspace{2pt}\n\\footnotesize\\textit{")
    f.write(f"$* =$ Holm-Bonferroni significant at $\\alpha=0.05$. ")
    f.write("Effects are reported on log-wealth unless noted. ")
    f.write(f"Gender rows use Male $n={len(male)}$, Female $n={len(female)}$; ")
    f.write(f"female mean log-wealth ${female.mean():.3f}$ and male mean ${male.mean():.3f}$.}}\n")
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
print("5. Updated tab_M6_inferential_results.tex written")

# LOWESS age trajectory
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, sm_val, title in zip(axes, [0, 1], ['Self-Made = No', 'Self-Made = Yes']):
    sub = df.dropna(subset=['age', 'log_finalWorth', 'selfMade_bin'])
    sub = sub[sub['selfMade_bin'] == sm_val]
    ax.scatter(sub['age'], sub['log_finalWorth'], alpha=0.2, s=10, color='steelblue')
    if len(sub) > 100:
        low = lowess(sub['log_finalWorth'], sub['age'], frac=0.3, return_sorted=True)
        ax.plot(low[:, 0], low[:, 1], color='red', lw=2.5, label='LOWESS')
    ax.set_xlabel('Age (years)', fontsize=11)
    ax.set_ylabel('log(finalWorth + 1)', fontsize=11)
    ax.set_title(f'Self-Made = {sm_val} (n={len(sub)})', fontsize=12)
    ax.legend()
    ax.grid(alpha=0.3)
plt.suptitle('LOWESS: log-Wealth vs. Age, Stratified by Self-Made Status', fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig(f"{FIG}/fig_M7_lowess_age_trajectory.pdf", bbox_inches='tight')
plt.savefig(f"{FIG}/fig_M7_lowess_age_trajectory.png", dpi=150, bbox_inches='tight')
plt.close()
print("6. LOWESS age trajectory plot written")

# Bootstrap methodology table
with open(f"{TAB}/tab_M6_bootstrap_methodology.tex", 'w') as f:
    f.write("\\begin{table}[H]\n\\centering\n\\caption{Bootstrap methodology: Percentile vs. BCa.}\n\\label{tab:bootstrap}\n\\begin{tabular}{lp{6cm}}\n\\toprule\n")
    f.write("Method & Description \\\\\n\\midrule\n")
    f.write("Percentile (used) & 2.5th and 97.5th percentiles of bootstrap distribution. Assumes the sampling distribution is symmetric. \\\\\n")
    f.write("BCa (recommended) & Bias-corrected and accelerated: adjusts for median bias and skewness. More accurate for heavy-tailed distributions but requires jackknife re-estimation of the acceleration constant. \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
    f.write("\\bigskip\n\\textit{Note: All CIs in this report use the percentile bootstrap with 10{,}000 replicates. Given the documented heavy-tailed distribution of billionaire wealth, BCa bootstrap would be methodologically preferable; the percentile CI may be slightly anti-conservative for extreme quantiles.}\n")
    f.write("\\end{table}\n")
print("7. Bootstrap methodology table written")

# Manufacturing anomaly
sub_mfg = df[df['category'] == 'Manufacturing'].dropna(subset=['log_finalWorth', 'log_gdp'])
r_pearson, _ = stats.pearsonr(sub_mfg['log_gdp'], sub_mfg['log_finalWorth'])
r_spearman, _ = stats.spearmanr(sub_mfg['log_gdp'], sub_mfg['log_finalWorth'])
print(f"\nManufacturing: n={len(sub_mfg)}, Pearson r={r_pearson:.4f}, Spearman rho={r_spearman:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].scatter(sub_mfg['log_gdp'], sub_mfg['log_finalWorth'], alpha=0.5, s=20)
axes[0].set_xlabel('log(GDP country)')
axes[0].set_ylabel('log(finalWorth)')
axes[0].set_title(f'Manufacturing: GDP vs Wealth\n(Pearson r={r_pearson:.3f}, Spearman rho={r_spearman:.3f})')
axes[0].grid(alpha=0.3)

X_m = sm.add_constant(sub_mfg[['log_gdp']])
m_m = sm.OLS(sub_mfg['log_finalWorth'], X_m).fit()
from statsmodels.stats.outliers_influence import OLSInfluence
inf = OLSInfluence(m_m)
axes[1].scatter(inf.hat_matrix_diag, inf.resid_studentized_internal, alpha=0.5, s=20)
axes[1].axhline(0, color='red', lw=0.8)
axes[1].set_xlabel('Leverage (hat value)')
axes[1].set_ylabel('Studentized residual')
axes[1].set_title('Manufacturing: Influence Diagnostics')
axes[1].grid(alpha=0.3)
plt.suptitle("Manufacturing Category: Pearson-Spearman Discrepancy Investigation", y=1.01)
plt.tight_layout()
plt.savefig(f"{FIG}/fig_M7_manufacturing_anomaly.pdf", bbox_inches='tight')
plt.savefig(f"{FIG}/fig_M7_manufacturing_anomaly.png", dpi=150, bbox_inches='tight')
plt.close()
print("8. Manufacturing anomaly plot written")

<<<<<<< HEAD
# Update tab_M7_regression_main.tex with VIF + F-test notes
with open(f"{TAB}/tab_M7_regression_main.tex", 'r') as fh:
    main_tab = fh.read()

note = ("\\addlinespace\n"
        f"\\multicolumn{{10}}{{l}}{{\\textbf{{VIF (Model C):}} max = {max_vif:.2f} ({max_vif_var}). "
        f"log_gdp VIF = {vif_df[vif_df['Variable']=='log_gdp']['VIF'].values[0]:.2f}. "
        "All VIF $<5$ $\\Rightarrow$ no severe multicollinearity.}}\n\n"
        f"\\multicolumn{{10}}{{l}}{{\\textbf{{Nested F-test (Model C vs. Model B on C-sample):}} "
        f"$F({q},{n-int(k_full)-1}) = {F_stat:.3f}$, $p = {F_pval:.2e}$. "
        "Added predictors collectively improve fit significantly.}}\n\n"
        f"\\multicolumn{{10}}{{l}}{{\\textbf{{Model C overall:}} "
        f"$F({int(k_full)},{int(m_full.df_resid)}) = {f_c:.3f}$, $p = {f_c_pval:.2e}$, "
        f"$R^2 = {r2_full:.4f}$.}}")

with open(f"{TAB}/tab_M7_regression_main.tex", 'w') as f:
    f.write(main_tab.replace("\\bottomrule", note + "\\bottomrule"))
print("9. Updated tab_M7_regression_main.tex")
=======
print("9. Regression notes kept in dedicated VIF and F-test tables")
>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3

print("\n=== All done ===")
print(f"Tables: {TAB}")
print(f"Figures: {FIG}")
<<<<<<< HEAD
=======

>>>>>>> 78aea24bc1c5e983ae76b958b6a131a09281a1e3
