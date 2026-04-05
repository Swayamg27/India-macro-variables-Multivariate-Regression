# =============================================================================
#  Multivariate Regression Analysis — India Macroeconomic Variables (2015–2025)
#  Author  : [Your Name]
#  Method  : OLS (Ordinary Least Squares) via statsmodels
#  Data    : RBI DBIE | MOSPI | World Bank | IMF WEO | Ministry of Finance
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import warnings
warnings.filterwarnings("ignore")

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})

NAVY   = "#1C3557"
TEAL   = "#028090"
GOLD   = "#E8A838"
RED    = "#C0392B"
CREAM  = "#F5F5F0"
GREY   = "#7F8C8D"

# =============================================================================
# 1. LOAD DATA
# =============================================================================
df = pd.read_csv("india_macro_data.csv")
print("=" * 60)
print("  INDIA MACROECONOMIC DATASET (2015–2025)")
print("=" * 60)
print(df.to_string(index=False))

# =============================================================================
# 2. OLS REGRESSION
# =============================================================================
y = df["GDP_Growth"]
X_cols = ["CPI_Inflation", "Repo_Rate", "Investment_GDP",
          "Unemployment", "Govt_Debt_GDP", "Govt_Spending_GDP", "Fiscal_Deficit_GDP"]
X = sm.add_constant(df[X_cols])

model  = sm.OLS(y, X).fit()
fitted = model.fittedvalues
resid  = model.resid

print("\n" + "=" * 60)
print("  OLS REGRESSION RESULTS")
print("=" * 60)
print(model.summary())

# =============================================================================
# 3. VIF  (Multicollinearity Check)
# =============================================================================
vif_data = pd.DataFrame({
    "Variable": X_cols,
    "VIF": [variance_inflation_factor(X.values, i + 1) for i in range(len(X_cols))]
}).sort_values("VIF", ascending=False)
print("\n── Variance Inflation Factors (VIF) ──")
print(vif_data.to_string(index=False))

# =============================================================================
# 4. CHARTS
# =============================================================================
years = df["Year"].tolist()

# ── Fig 1 : Actual vs Fitted GDP ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5), facecolor=CREAM)
ax.set_facecolor(CREAM)
ax.plot(years, y,      color=NAVY, lw=2.5, marker="o", ms=7, label="Actual GDP Growth")
ax.plot(years, fitted, color=GOLD, lw=2,   marker="s", ms=6, ls="--", label="Model Fitted")
ax.axhline(0, color=GREY, lw=0.8, ls=":")
ax.fill_between(years, y, fitted, alpha=0.12, color=TEAL)
ax.annotate("COVID-19\nShock", xy=("2020-21", -5.8), xytext=("2019-20", -7.5),
            arrowprops=dict(arrowstyle="->", color=RED), color=RED, fontsize=9, fontweight="bold")
ax.set_title("Actual vs Model-Fitted GDP Growth — India (2015–2025)",
             fontsize=14, fontweight="bold", color=NAVY, pad=14)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("GDP Growth (%)", fontsize=11)
ax.tick_params(axis="x", rotation=45)
ax.legend(fontsize=10, framealpha=0)
ax.text(0.99, 0.97, f"R² = {model.rsquared:.3f}  |  Adj R² = {model.rsquared_adj:.3f}",
        transform=ax.transAxes, ha="right", va="top", fontsize=10,
        color=NAVY, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.7))
plt.tight_layout()
plt.savefig("chart1_actual_vs_fitted.png", bbox_inches="tight", facecolor=CREAM)
plt.close()
print("\n✅  Saved: chart1_actual_vs_fitted.png")

# ── Fig 2 : Regression Coefficients ─────────────────────────────────────────
coef_df = pd.DataFrame({
    "Variable": X_cols,
    "Coefficient": model.params[1:].values,
    "pvalue": model.pvalues[1:].values
}).sort_values("Coefficient")

colors = [TEAL if c > 0 else RED for c in coef_df["Coefficient"]]

fig, ax = plt.subplots(figsize=(9, 5), facecolor=CREAM)
ax.set_facecolor(CREAM)
bars = ax.barh(coef_df["Variable"], coef_df["Coefficient"], color=colors, height=0.55, edgecolor="white")
ax.axvline(0, color=NAVY, lw=1.2)
for bar, (_, row) in zip(bars, coef_df.iterrows()):
    sig = "***" if row.pvalue < 0.01 else ("**" if row.pvalue < 0.05 else ("*" if row.pvalue < 0.10 else ""))
    val = row.Coefficient
    offset = 0.03 if val >= 0 else -0.03
    ax.text(val + offset, bar.get_y() + bar.get_height() / 2,
            f"{val:+.2f} {sig}", va="center", fontsize=9,
            color=NAVY, fontweight="bold")
ax.set_title("OLS Regression Coefficients — Effect on GDP Growth (%)",
             fontsize=13, fontweight="bold", color=NAVY, pad=12)
ax.set_xlabel("β Coefficient (ceteris paribus)", fontsize=10)
ax.text(0.99, 0.02, "*** p<0.01  ** p<0.05  * p<0.10",
        transform=ax.transAxes, ha="right", fontsize=8.5, color=GREY)
plt.tight_layout()
plt.savefig("chart2_coefficients.png", bbox_inches="tight", facecolor=CREAM)
plt.close()
print("✅  Saved: chart2_coefficients.png")

# ── Fig 3 : Correlation Heatmap ───────────────────────────────────────────────
all_vars = ["GDP_Growth"] + X_cols
corr = df[all_vars].corr()
labels = ["GDP", "CPI", "Repo", "Invest", "Unemp", "GDebt", "GSpend", "FDef"]

fig, ax = plt.subplots(figsize=(8, 6.5), facecolor=CREAM)
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn",
            xticklabels=labels, yticklabels=labels,
            linewidths=0.5, linecolor="white",
            vmin=-1, vmax=1, ax=ax, square=True,
            cbar_kws={"shrink": 0.8})
ax.set_title("Correlation Matrix — India Macro Variables (2015–2025)",
             fontsize=13, fontweight="bold", color=NAVY, pad=12)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", rotation=0)
plt.tight_layout()
plt.savefig("chart3_correlation_heatmap.png", bbox_inches="tight", facecolor=CREAM)
plt.close()
print("✅  Saved: chart3_correlation_heatmap.png")

# ── Fig 4 : Macro Dashboard (2×2) ────────────────────────────────────────────
fig = plt.figure(figsize=(13, 9), facecolor=CREAM)
fig.suptitle("India Macroeconomic Dashboard (2015–2025)",
             fontsize=15, fontweight="bold", color=NAVY, y=0.98)
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32)

# Panel A — GDP
ax0 = fig.add_subplot(gs[0, 0])
ax0.set_facecolor(CREAM)
ax0.bar(years, df["GDP_Growth"],
        color=[RED if v < 0 else NAVY for v in df["GDP_Growth"]], width=0.55, edgecolor="white")
ax0.axhline(0, color=GREY, lw=0.8)
ax0.set_title("GDP Growth (%)", fontweight="bold", color=NAVY)
ax0.tick_params(axis="x", rotation=45, labelsize=7)

# Panel B — Monetary (CPI + Repo)
ax1 = fig.add_subplot(gs[0, 1])
ax1.set_facecolor(CREAM)
ax1.plot(years, df["CPI_Inflation"], color=RED,  lw=2, marker="o", ms=5, label="CPI Inflation")
ax1.plot(years, df["Repo_Rate"],     color=NAVY, lw=2, marker="s", ms=5, label="Repo Rate")
ax1.set_title("Monetary Variables (%)", fontweight="bold", color=NAVY)
ax1.legend(fontsize=8, framealpha=0)
ax1.tick_params(axis="x", rotation=45, labelsize=7)

# Panel C — Investment vs Unemployment
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_facecolor(CREAM)
ax2_twin = ax2.twinx()
ax2.bar(years, df["Investment_GDP"], color=TEAL, alpha=0.7, width=0.55, label="Investment % GDP")
ax2_twin.plot(years, df["Unemployment"], color=GOLD, lw=2, marker="D", ms=5, label="Unemployment %")
ax2.set_title("Investment & Unemployment", fontweight="bold", color=NAVY)
ax2.set_ylabel("Investment % GDP", fontsize=8, color=TEAL)
ax2_twin.set_ylabel("Unemployment %", fontsize=8, color=GOLD)
ax2.tick_params(axis="x", rotation=45, labelsize=7)

# Panel D — Fiscal Variables
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_facecolor(CREAM)
ax3.plot(years, df["Govt_Debt_GDP"],      color=NAVY, lw=2, marker="o", ms=5, label="Govt Debt % GDP")
ax3.plot(years, df["Fiscal_Deficit_GDP"], color=RED,  lw=2, marker="s", ms=5, label="Fiscal Deficit %")
ax3.plot(years, df["Govt_Spending_GDP"],  color=TEAL, lw=2, marker="^", ms=5, label="Govt Spending %")
ax3.set_title("Fiscal Variables (%)", fontweight="bold", color=NAVY)
ax3.legend(fontsize=7.5, framealpha=0)
ax3.tick_params(axis="x", rotation=45, labelsize=7)

for ax in [ax0, ax1, ax2, ax3]:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

plt.savefig("chart4_macro_dashboard.png", bbox_inches="tight", facecolor=CREAM)
plt.close()
print("✅  Saved: chart4_macro_dashboard.png")

# ── Fig 5 : Residuals Plot ────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), facecolor=CREAM)
fig.suptitle("OLS Diagnostic Plots", fontsize=13, fontweight="bold", color=NAVY)

# Residuals vs Fitted
axes[0].set_facecolor(CREAM)
axes[0].scatter(fitted, resid, color=NAVY, edgecolors="white", s=70, zorder=3)
axes[0].axhline(0, color=RED, lw=1.2, ls="--")
axes[0].set_xlabel("Fitted Values", fontsize=10)
axes[0].set_ylabel("Residuals", fontsize=10)
axes[0].set_title("Residuals vs Fitted", fontweight="bold", color=NAVY)
for i, yr in enumerate(years):
    axes[0].annotate(yr[:4], (fitted.iloc[i], resid.iloc[i]),
                     fontsize=7, color=GREY, textcoords="offset points", xytext=(4, 3))

# Normal Q-Q
sm.qqplot(resid, line="s", ax=axes[1], alpha=0.7,
          markerfacecolor=TEAL, markeredgecolor="white")
axes[1].set_facecolor(CREAM)
axes[1].set_title("Normal Q-Q Plot of Residuals", fontweight="bold", color=NAVY)
axes[1].get_lines()[0].set(color=TEAL, markersize=8)
axes[1].get_lines()[1].set(color=RED, lw=1.5)

for ax in axes:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig("chart5_diagnostics.png", bbox_inches="tight", facecolor=CREAM)
plt.close()
print("✅  Saved: chart5_diagnostics.png")

# =============================================================================
# 5. SUMMARY TABLE
# =============================================================================
print("\n" + "=" * 60)
print("  KEY RESULTS SUMMARY")
print("=" * 60)
summary = pd.DataFrame({
    "Variable":    X_cols,
    "β Coeff":     np.round(model.params[1:].values, 2),
    "Std Error":   np.round(model.bse[1:].values, 2),
    "t-stat":      np.round(model.tvalues[1:].values, 2),
    "p-value":     np.round(model.pvalues[1:].values, 3),
    "Sig":         ["***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else "(*)"))
                    for p in model.pvalues[1:]]
})
print(summary.to_string(index=False))
print(f"\nR²        = {model.rsquared:.4f}")
print(f"Adj R²    = {model.rsquared_adj:.4f}")
print(f"F-stat    = {model.fvalue:.2f}  (p = {model.f_pvalue:.4f})")
print(f"AIC       = {model.aic:.2f}")
print(f"BIC       = {model.bic:.2f}")
print("\nAll charts saved. Project ready for GitHub upload.")
