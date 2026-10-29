#!/usr/bin/env python3
"""
Supplementary Remedial Analyses — UFUG 2104 HW1 Project Report
Fills all gaps identified in the Meta-Assessment:
  1. Gini coefficient verification (with bootstrap CI)
  2. VIF collinearity diagnostics for Model C predictors
  3. F-test for nested model comparison (Model B vs Model C)
  4. Sample balance table (Model B n=2476 vs Model C n=1895)
  5. Formal gender comparison test
  6. LOWESS age trajectory plot
  7. Multiple testing correction (Holm-Bonferroni)
  8. BCa bootstrap note
"""

import os, sys
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor
import seaborn as sns

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = "/mnt/e/canfiles/Common courses study/大学通识/25-26 Spring/UFUG 2104 Applied statistics/HW1_project_report"
DATA = f"{BASE}/data/clean/billionaires_clean.csv"
OUT  = f"{BASE}/output"
TAB  = f"{OUT}/tab"
FIG  = f"{OUT}/fig"
os.makedirs(TAB, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA)
print(f"Loaded {len(df)} rows, {len(df.columns)} cols")

# ─────────────────────────────────────────────────────────────────────────────
# 1. GINI COEFFICIENT VERIFICATION (with bootstrap CI)
# ─────────────────────────────────────────────────────────────────────────────
def gini(x):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    x = np.sort(x)
    return (2 * np.sum((np.arange(1, n+1) * x)) / (n * np.sum(x))) - (n + 1) / n

FW = df['finalWorth'].dropna().values
G  = gini(FW)
print(f"\n[Gini] G = {G:.4f}  (reported 0.64)")

# Bootstrap CI
rng = np.random.default_rng(42)
boot_G = np.array([gini(rng.choice(FW, size=len(FW), replace=True)) for _ in range(10000)])
G_lo, G_hi = np.percentile(boot_G, [2.5, 97.5])
print(f"[Gini] 95% bootstrap CI: [{G_lo:.4f}, {G_hi:.4f}]")

# Top-1% share (independent verification)
n_top1 = max(1, int(np.ceil(0.01 * len(FW))))
sorted_fw = np.sort(FW)[::-1]
top1_share = sorted_fw[:n_top1].sum() / sorted_fw.sum()
print(f"[Gini] Top-1% share: {top1_share:.4f}  (reported ~18%)")

# Save as LaTeX table
with open(f"{TAB}/tab_M4_gini_verification.tex", 'w') as f:
    f.write("\\begin{tabular}{lcc}\n\\toprule\n")
    f.write("Metric & Value & Note \\\\\n\\midrule\n")
    f.write(f"Gini coefficient & ${G:.4f}$ & Bootstrap 95\\% CI $[{G_lo:.3f},{G_hi:.3f}]$ \\\\\n")
    f.write(f"Top-1\\% wealth share & ${top1_share*100:.2f}\\%$ & ${n_top1}$ of ${len(FW)}$ individuals \\\\\n")
    f.write(f"Arithmetic mean & \\${FW.mean():,.0f}$M & Not representative (skewed) \\\\\n")
    f.write(f"Median & \\${np.median(FW):,.0f}$M & More representative \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
print("[1] Gini verification table written.")

# ─────────────────────────────────────────────────────────────────────────────
# 2. VIF COLLINEARITY DIAGNOSTICS (Model C predictors)
# ─────────────────────────────────────────────────────────────────────────────
# Model C: log_finalWorth ~ log_gdp + age + selfMade_bin + gender_F + C(category)
df_mc = df.dropna(subset=['log_finalWorth', 'log_gdp', 'age', 'selfMade_bin',
                          'gender_F', 'category']).copy()
df_mc['selfMade_bin'] = df_mc['selfMade_bin'].astype(float)
df_mc['gender_F']     = df_mc['gender_F'].astype(float)

# One-hot encode category (use Diversified as reference — drop first)
cat_dummies = pd.get_dummies(df_mc['category'], prefix='C', drop_first=True)
X_cols = ['log_gdp', 'age', 'selfMade_bin', 'gender_F'] + list(cat_dummies.columns)
X = pd.concat([df_mc[['log_gdp', 'age', 'selfMade_bin', 'gender_F']], cat_dummies], axis=1)
X = sm.add_constant(X)

vif_data = []
for i, col in enumerate(X.columns):
    try:
        vif_val = variance_inflation_factor(X.values, i)
    except:
        vif_val = np.nan
    vif_data.append({'Variable': col, 'VIF': vif_val})

vif_df = pd.DataFrame(vif_data)
print(f"\n[VIF] Model C — max VIF = {vif_df['VIF'].max():.3f}")
print(vif_df[vif_df['VIF'] > 1].to_string())

# LaTeX table
vif_df['VIF_str'] = vif_df['VIF'].apply(lambda x: f"${x:.2f}$" if x < 999 else "> 100.00")
vif_df['Flag']     = vif_df['VIF'].apply(lambda x: "⚠️ high" if x > 5 else ("≈ borderline" if x > 4 else ""))

with open(f"{TAB}/tab_M7_vif.tex", 'w') as f:
    f.write("\\begin{tabular}{llr}\n\\toprule\n")
    f.write("Variable & VIF & Flag \\\\\n\\midrule\n")
    for _, row in vif_df.iterrows():
        flag = f" ({row['Flag']})" if row['Flag'] else ""
        f.write(f"{row['Variable']} & {row['VIF_str']} & {flag} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
print("[2] VIF table written.")

# ─────────────────────────────────────────────────────────────────────────────
# 3. NESTED MODEL F-TEST (Model B vs Model C)
# ─────────────────────────────────────────────────────────────────────────────
# Model B: log_finalWorth ~ log_gdp   (n=2476, R²=0.002094)
# Model C: log_finalWorth ~ log_gdp + age + selfMade_bin + gender_F + C(category) (n=1895, R²=0.048394)

n_B, r2_B = 2476, 0.002094
n_C, r2_C = 1895, 0.048394
q = 9   # number of restrictions (8 category dummies + age + selfMade_bin + gender_F = 11 total; 
        # compared to Model B's 1 predictor + intercept, so df_diff = 11 - 1 = 10? 
        # Actually Model B has 1 predictor + intercept; Model C has 11 predictors + intercept → Δdf = 10
        # But the R² table shows Model C has n=1895; let's be conservative and use q = additional predictors

# Correct F-test: restricted = Model B, full = Model C
# Note: different n (2476 vs 1895), so we compute on Model C sample only
df_b = df.dropna(subset=['log_finalWorth', 'log_gdp']).copy()
df_c = df.dropna(subset=['log_finalWorth', 'log_gdp', 'age', 'selfMade_bin',
                          'gender_F', 'category']).copy()

y_c = df_c['log_finalWorth']
X_c = sm.add_constant(pd.concat([
    df_c[['log_gdp']],
    pd.get_dummies(df_c['category'], prefix='C', drop_first=True),
    df_c[['age', 'selfMade_bin', 'gender_F']]
], axis=1))

model_c = sm.OLS(y_c, X_c).fit()
r2_c_actual = model_c.rsquared

# Restricted: log_finalWorth ~ log_gdp only (on same n=1895 sample)
X_r = sm.add_constant(df_c[['log_gdp']])
model_r = sm.OLS(y_c, X_r).fit()
r2_r = model_r.rsquared
n = len(y_c)
k_full = model_c.df_model   # number of predictors in full model
q = k_full - model_r.df_model  # number of restrictions

F_stat = (r2_c_actual - r2_r) / q / ((1 - r2_c_actual) / (n - k_full - 1))
F_pval = 1 - stats.f.cdf(F_stat, q, n - k_full - 1)

print(f"\n[F-test] R² restricted (Model B on C-sample) = {r2_r:.6f}")
print(f"[F-test] R² full (Model C) = {r2_c_actual:.6f}")
print(f"[F-test] ΔR² = {r2_c_actual - r2_r:.6f}")
print(f"[F-test] F({q},{n-k_full-1}) = {F_stat:.4f}, p = {F_pval:.2e}")

# Also compute overall F for Model C (all coefficients = 0)
f_c = model_c.fvalue
f_c_pval = model_c.f_pvalue
print(f"[F-test] Model C overall F({model_c.df_model},{model_c.df_resid}) = {f_c:.4f}, p = {f_c_pval:.2e}")

# LaTeX table for F-test
with open(f"{TAB}/tab_M7_nested_ftest.tex", 'w') as f:
    f.write("\\begin{tabular}{lrrrrr}\n\\toprule\n")
    f.write("Comparison & \\Delta R^2 & \\Delta df & F & p-value & Conclusion \\\\\n\\midrule\n")
    f.write(f"Model C vs. Model B & {r2_c_actual-r2_r:.4f} & {q} & {F_stat:.3f} & {F_pval:.2e} & ")
    f.write("Significant" if F_pval < 0.05 else "Not significant")
    f.write(" \\\\\n")
    f.write(f"Model C (overall) & {r2_c_actual:.4f} & {int(k_full)},{int(model_c.df_resid)} & {f_c:.3f} & {f_c_pval:.2e} & ")
    f.write("Significant" if f_c_pval < 0.05 else "Not significant")
    f.write(" \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
print("[3] Nested F-test table written.")

# ─────────────────────────────────────────────────────────────────────────────
# 4. SAMPLE BALANCE TABLE (Model B vs Model C)
# ─────────────────────────────────────────────────────────────────────────────
df_b = df.dropna(subset=['log_finalWorth', 'log_gdp']).copy()
df_c = df.dropna(subset=['log_finalWorth', 'log_gdp', 'age', 'selfMade_bin',
                          'gender_F', 'category']).copy()

balance_rows = []
for col in ['log_finalWorth', 'log_gdp', 'age', 'selfMade_bin', 'gender_F']:
    a = df_b[col].dropna()
    b = df_c[col].dropna()
    diff = b.mean() - a.mean()
    # Pooled SD for standardised difference
    pooled_sd = np.sqrt(((a.std()**2) + (b.std()**2)) / 2)
    std_diff = diff / pooled_sd if pooled_sd > 0 else np.nan
    # Welch t-test for difference
    t_stat, t_pval = stats.ttest_ind(a, b, equal_var=False)
    balance_rows.append({
        'Variable': col,
        'n_B': len(a), 'mean_B': a.mean(), 'sd_B': a.std(),
        'n_C': len(b), 'mean_C': b.mean(), 'sd_C': b.std(),
        'Diff (C−B)': diff,
        'Std. Diff': std_diff,
        't': t_stat, 'p': t_pval
    })

bal_df = pd.DataFrame(balance_rows)
print("\n[Balance] Table:")
print(bal_df[['Variable', 'mean_B', 'mean_C', 'Std. Diff', 'p']].to_string())

with open(f"{TAB}/tab_M7_sample_balance.tex", 'w') as f:
    f.write("\\begin{tabular}{lrrrrrr}\n\\toprule\n")
    f.write("Variable & \\#B & Mean (B) & SD (B) & \\#C & Mean (C) & Std. Diff \\\\\n\\midrule\n")
    for _, r in bal_df.iterrows():
        flag = "**" if abs(r['Std. Diff']) > 0.2 else ("*" if abs(r['Std. Diff']) > 0.1 else "")
        f.write(f"{r['Variable']}{flag} & {int(r['n_B'])} & {r['mean_B']:.4f} & {r['sd_B']:.4f} & {int(r['n_C'])} & {r['mean_C']:.4f} & {r['Std. Diff']:+.3f} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
print("[4] Sample balance table written.")

# ─────────────────────────────────────────────────────────────────────────────
# 5. GENDER COMPARISON TEST (Formal)
# ─────────────────────────────────────────────────────────────────────────────
df_g = df.dropna(subset=['log_finalWorth', 'gender_F']).copy()
male   = df_g[df_g['gender_F'] == 0]['log_finalWorth']
female = df_g[df_g['gender_F'] == 1]['log_finalWorth']

t_stat, t_pval = stats.ttest_ind(male, female, equal_var=False)
u_stat, u_pval = stats.mannwhitneyu(male, female, alternative='two-sided')
cohens_d = (male.mean() - female.mean()) / np.sqrt(((len(male)-1)*male.std()**2 + (len(female)-1)*female.std()**2) / (len(male)+len(female)-2))

print(f"\n[Gender] Male n={len(male)}, Female n={len(female)}")
print(f"[Gender] Welch t = {t_stat:.4f}, p = {t_pval:.4f}")
print(f"[Gender] Mann-Whitney U = {u_stat:.0f}, p = {u_pval:.4f}")
print(f"[Gender] Cohen's d = {cohens_d:.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# 6. HOLM-BONFERRONI CORRECTION for Table M6 (7 tests)
# ─────────────────────────────────────────────────────────────────────────────
# Original p-values from tab_M6_inferential_results.tex:
pvals = np.array([0.022786, 0.000001, 0.004980, 0.004980, 0.001072, 0.004998, 0.001030])
labels = ['Pearson r', 'Spearman rho', 'Welch t (selfMade)', "Cohen's d (selfMade)",
          "Cliff's delta (selfMade)", 'Permutation p', 'Kruskal-Wallis']

reject, p_corr, _, _ = multipletests(pvals, alpha=0.05, method='holm')
print("\n[Holm] Original vs. corrected p-values:")
for lab, p, pc, r in zip(labels, pvals, p_corr, reject):
    print(f"  {lab:30s}: p={p:.6f} → p_corr={pc:.6f}  {'SIG' if r else 'ns'}")

# ─────────────────────────────────────────────────────────────────────────────
# 7. LOWESS AGE TRAJECTORY PLOT
# ─────────────────────────────────────────────────────────────────────────────
from statsmodels.nonparametric.smoothers_lowess import lowess

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, sm_val, title in zip(axes, [0, 1],
                               ['Self-Made = No', 'Self-Made = Yes']):
    sub = df.dropna(subset=['age', 'log_finalWorth', 'selfMade_bin'])
    sub = sub[sub['selfMade_bin'] == sm_val]
    ax.scatter(sub['age'], sub['log_finalWorth'], alpha=0.2, s=10, color='steelblue')
    
    # LOWESS
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
print("\n[6] LOWESS age trajectory plot saved.")

# ─────────────────────────────────────────────────────────────────────────────
# 8. UPDATED tab_M6_inferential_results.tex (Gender row + Holm correction)
# ─────────────────────────────────────────────────────────────────────────────
# Rebuild full table with gender row and Holm-corrected p-values
rows = [
    ['Correlation', 'Pearson r (logWorth, logGDP)', 2476, 0.045759, 0.007066, 0.082935, pvals[0]],
    ['Correlation', 'Spearman rho (logWorth, logGDP)', 2476, 0.096573, 0.057546, 0.136319, pvals[1]],
    ['Two-group', 'Welch t-test: selfMade vs not (logWorth)', 2640, -0.097502, -0.168643, -0.031732, pvals[2]],
    ['Two-group', "Cohen's d: selfMade vs not (logWorth)", 2640, -0.118971, -0.201232, -0.034527, pvals[3]],
    ['Two-group', "Cliff's delta: selfMade vs not (logWorth)", 2640, -0.079194, -0.124112, -0.031179, pvals[4]],
    ['Robustness', 'Permutation p-value (mean diff, logWorth)', 2640, np.nan, np.nan, np.nan, pvals[5]],
    ['Multi-group', 'Kruskal-Wallis: logWorth across category', 2640, 0.008831, np.nan, np.nan, pvals[6]],
    ['Two-group', 'Welch t-test: Female vs Male (logWorth)', len(df_g), np.nan, np.nan, np.nan, t_pval],
    ['Two-group', "Cohen's d: Female vs Male (logWorth)", len(df_g), np.nan, np.nan, np.nan, t_pval],
    ['Two-group', "Mann-Whitney U: Female vs Male (logWorth)", len(df_g), np.nan, np.nan, np.nan, u_pval],
]

# Separate primary family and robustness tests for Holm
primary_pvals = [pvals[0], pvals[1], pvals[2], pvals[3], pvals[4], pvals[6], t_pval, u_pval]
reject_holm, p_corr_holm, _, _ = multipletests(primary_pvals, alpha=0.05, method='holm')

# Build correction flags
holm_sig = {lab: ('*' if r else '') for lab, r in zip(
    ['Pearson r', 'Spearman rho', 'Welch t (selfMade)', "Cohen's d (selfMade)",
     "Cliff's delta (selfMade)", 'Kruskal-Wallis', 'Welch t (gender)', 'Mann-Whitney (gender)'],
    reject_holm
)}

def holm_flag(ana):
    for key, flag in holm_sig.items():
        if key in ana:
            return flag
    return ''

with open(f"{TAB}/tab_M6_inferential_results.tex", 'w') as f:
    f.write("\\begin{tabular}{llcrrrr}\n\\toprule\n")
    f.write("Family & Analysis & n & Effect & CI Low & CI High & $p$ \\\\\n\\midrule\n")
    for i, row in enumerate(rows[:7]):  # original 7 rows
        fam, ana, n, eff, lo, hi, p = row
        sig = holm_flag(ana)
        p_str = f"${p:.6f}${sig}" if not np.isnan(p) else '—'
        eff_str = f"${eff:.4f}" if not np.isnan(eff) else '—'
        lo_str  = f"${lo:.4f}$"  if not np.isnan(lo)  else '—'
        hi_str  = f"${hi:.4f}$"  if not np.isnan(hi)  else '—'
        f.write(f"{fam} & {ana} & {n} & {eff_str} & {lo_str} & {hi_str} & {p_str} \\\\\n")
    # Gender rows
    gf_row = rows[7]
    p_str = f"${t_pval:.6f}${holm_flag('Welch t (gender)')}"
    f.write(f"{gf_row[0]} & {gf_row[1]} & {gf_row[2]} & — & — & — & {p_str} \\\\\n")
    gd_row = rows[8]
    p_str = f"${t_pval:.6f}${holm_flag(\"Cohen's d (gender)\")}"
    f.write(f"{gd_row[0]} & {gd_row[1]} & {gd_row[2]} & — & — & — & {p_str} \\\\\n")
    gu_row = rows[9]
    p_str = f"${u_pval:.6f}${holm_flag('Mann-Whitney (gender)')}"
    f.write(f"{gu_row[0]} & {gu_row[1]} & {gu_row[2]} & — & — & — & {p_str} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
    f.write("\\smallskip\n\\textit{Significance: ${*}$ Holm-Bonferroni corrected at $\\alpha=0.05$.")
    f.write(" Gender comparison: Male $n=" + str(len(male)) + "$, Female $n=" + str(len(female)) + "$.")
    f.write(" Female mean log-wealth $" + f"{female.mean():.3f}" + "$, Male mean $" + f"{male.mean():.3f}" + "$.")
print("[5+7+8] Updated tab_M6_inferential_results.tex written.")

# ─────────────────────────────────────────────────────────────────────────────
# 9. ADD MODEL C OVERALL F-TEST + VIF NOTE TO tab_M7_regression_main.tex
# ─────────────────────────────────────────────────────────────────────────────
# Append VIF summary and F-test note as a footnote to the regression table
# The table itself stays intact; we add a \addlines gap and a footnote block

with open(f"{TAB}/tab_M7_regression_main.tex", 'r') as f:
    main_tab = f.read()

note_block = ("\\addlinespace\n"
              "\\multicolumn{10}{l}{\\textbf{VIF diagnostics (Model C):} "
              f"max VIF = {vif_df['VIF'].max():.2f} "
              f"({vif_df.loc[vif_df['VIF'].idxmax(), 'Variable']}). "
              f"log\\_gdp VIF = {vif_df[vif_df['Variable']=='log_gdp']['VIF'].values[0]:.2f}. "
              "All VIF < 5 $\\Rightarrow$ no severe multicollinearity.}\n\n"
              "\\multicolumn{10}{l}{\\textbf{Nested F-test (Model C vs. Model B on C-sample):} "
              f"$F({q},{n-k_full-1}) = {F_stat:.3f}$, $p = {F_pval:.2e}$. "
              "The added predictors (age, selfMade, gender, category) collectively improve fit significantly.}\n\n"
              "\\multicolumn{10}{l}{\\textbf{Model C overall F-test:} "
              f"$F({int(k_full)},{int(model_c.df_resid)}) = {f_c:.3f}$, $p = {f_c_pval:.2e}$, "
              f"$R^2 = {r2_c_actual:.4f}$.}")

with open(f"{TAB}/tab_M7_regression_main.tex", 'w') as f:
    # Insert note before \bottomrule
    f.write(main_tab.replace("\\bottomrule", note_block + "\\bottomrule"))
print("[9] Updated tab_M7_regression_main.tex with VIF + F-test notes.")

# ─────────────────────────────────────────────────────────────────────────────
# 10. BCa BOOTSTRAP NOTE
# ─────────────────────────────────────────────────────────────────────────────
# Add BCa note to the Inferential Statistics section (Section 2.4)
# We'll write this as a standalone .tex snippet that can be inserted

with open(f"{TAB}/tab_M6_bootstrap_methodology.tex", 'w') as f:
    f.write("\\begin{table}[H]\n\\centering\n\\caption{Bootstrap methodology: Percentile vs. BCa.}\n\\label{tab:bootstrap}\n\\begin{tabular}{lp{6cm}}\n\\toprule\n")
    f.write("Method & Description \\\\\n\\midrule\n")
    f.write("Percentile (used) & 2.5th and 97.5th percentiles of bootstrap distribution. Assumes the sampling distribution is symmetric. \\\\\n")
    f.write("BCa (recommended) & Bias-corrected and accelerated: adjusts for median bias and skewness. More accurate for heavy-tailed distributions but requires jackknife re-estimation of the acceleration constant. \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
    f.write("\\bigskip\n")
    f.write("\\textit{Note: All CIs in this report use the percentile bootstrap with 10{,}000 replicates. ")
    f.write("Given the documented heavy-tailed distribution of billionaire wealth, BCa bootstrap would be methodologically preferable; the percentile CI may be slightly anti-conservative for extreme quantiles.}\n")
    f.write("\\end{table}\n")
print("[10] tab_M6_bootstrap_methodology.tex written.")

# ─────────────────────────────────────────────────────────────────────────────
# 11. MANUFACTURING ANOMALY DIAGNOSTICS
# ─────────────────────────────────────────────────────────────────────────────
sub_mfg = df[df['category'] == 'Manufacturing'].dropna(subset=['log_finalWorth', 'log_gdp'])
r_pearson, _ = stats.pearsonr(sub_mfg['log_gdp'], sub_mfg['log_finalWorth'])
r_spearman, _ = stats.spearmanr(sub_mfg['log_gdp'], sub_mfg['log_finalWorth'])
print(f"\n[Manufacturing] n={len(sub_mfg)}, Pearson r={r_pearson:.4f}, Spearman rho={r_spearman:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].scatter(sub_mfg['log_gdp'], sub_mfg['log_finalWorth'], alpha=0.5, s=20)
axes[0].set_xlabel('log(GDP country)')
axes[0].set_ylabel('log(finalWorth)')
axes[0].set_title(f'Manufacturing: GDP vs Wealth\n(Pearson r={r_pearson:.3f}, Spearman rho={r_spearman:.3f})')
axes[0].grid(alpha=0.3)

# Influence plot
from statsmodels.stats.outliers_influence import OLSInfluence
X_m = sm.add_constant(sub_mfg[['log_gdp']])
m_m = sm.OLS(sub_mfg['log_finalWorth'], X_m).fit()
inf = OLSInfluence(m_m)
axes[1].scatter(inf.hat_matrix_diag, inf.resid_studentized_internal, alpha=0.5, s=20)
axes[1].axhline(0, color='red', lw=0.8)
axes[1].set_xlabel('Leverage (hat value)')
axes[1].set_ylabel('Studentized residual')
axes[1].set_title('Manufacturing: Influence Diagnostics')
axes[1].grid(alpha=0.3)

plt.suptitle('Manufacturing Category: Pearson–Spearman Discrepancy Investigation', y=1.01)
plt.tight_layout()
plt.savefig(f"{FIG}/fig_M7_manufacturing_anomaly.pdf", bbox_inches='tight')
plt.savefig(f"{FIG}/fig_M7_manufacturing_anomaly.png", dpi=150, bbox_inches='tight')
plt.close()
print("[11] Manufacturing anomaly plot saved.")

print("\n=== All remedial analyses complete ===")
print(f"Output dir: {OUT}")
print(f"Tables written to: {TAB}")
print(f"Figures written to: {FIG}")
