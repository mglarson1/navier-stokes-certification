"""Rebuild revised figures from the six exact certificate records.

Run from the manuscript root: python3 figures/make_certificate_figures.py
The older diagnostic crossing data are kept separate from certified data.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import csv
import hashlib
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FILES = ["976_T0p5.json", "976_T0p6.json", "976_T0p8.json",
         "Newton_T0p5_A1.json", "Newton_T1p2.json", "Newton_T2_variational.json"]
JOBS = ["1646", "1673", "4110", "4106", "4109", "4639"]
ROWS = []
for name, job in zip(FILES, JOBS):
    path = ROOT / "evidence" / name
    data = json.loads(path.read_text())
    if "values_exact" in data:
        v = {k: F(x) for k, x in data["values_exact"].items()}
    else:
        v = {k: F(data[k]) for k in ["T", "beta", "gamma"]}
        for target, key in {
            "rho_upper": "rho_upper_exact", "A_gamma_upper": "A_gamma_upper_exact",
            "K_upper": "K_upper_exact", "linear_upper": "linear_error_upper_exact",
            "nonlinear_upper": "nonlinear_error_upper_exact",
            "radius_upper": "corrected_radius_upper_exact", "centre": "corrected_centre_exact",
            "eps_D": "reference_evaluation_error_upper_exact",
            "eps_eta": "eta_evaluation_error_upper_exact",
        }.items():
            v[target] = F(data[key])
        v["s_sqrtW_upper"] = v["linear_upper"] * v["beta"] / v["rho_upper"] / v["A_gamma_upper"]
        v["J_lower"] = v["centre"] - v["radius_upper"]
        v["J_upper"] = v["centre"] + v["radius_upper"]
    assert v["linear_upper"] == v["rho_upper"] / v["beta"] * v["s_sqrtW_upper"] * v["A_gamma_upper"]
    assert v["nonlinear_upper"] == v["K_upper"] * v["rho_upper"] ** 2
    assert v["radius_upper"] == v["linear_upper"] + v["nonlinear_upper"] + v["eps_D"] + v["eps_eta"]
    ROWS.append(dict(file=name, reference="976" if name.startswith("976") else "Newton",
                     closure_job=job, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     values_exact={k: str(x) for k, x in v.items()}))

(HERE / "data" / "certificate_budgets_T2_exact.json").write_text(
    json.dumps(ROWS, indent=2) + "\n")

plt.rcParams.update({
    "font.family": "DejaVu Serif", "mathtext.fontset": "cm",
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": .65, "axes.axisbelow": True,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "pdf.fonttype": 42, "savefig.bbox": "tight",
    "savefig.pad_inches": .06,
})
BLUE, ORANGE, GREEN, GREY = "#29679c", "#ca7040", "#20785d", "#565656"

def vals(row):
    return {k: F(v) for k, v in row["values_exact"].items()}

def up_label(value, digits=3):
    scale = 10 ** digits
    n = -((-value.numerator * scale) // value.denominator)
    return f"{n // scale}.{n % scale:0{digits}d}"

def radius_figure():
    fig, ax = plt.subplots(figsize=(6.25, 2.9))
    for i, row in enumerate(ROWS):
        v, y = vals(row), len(ROWS) - i - 1
        lin, non = float(v["linear_upper"] * 10**5), float(v["nonlinear_upper"] * 10**5)
        rad = float(v["radius_upper"] * 10**5)
        ax.barh(y, lin, .53, color=BLUE, label="linear term" if i == 0 else None)
        ax.barh(y, non, .53, left=lin, color=ORANGE, label="nonlinear remainder" if i == 0 else None)
        ax.text(rad + .10, y, up_label(v["radius_upper"] * 10**5), va="center", fontsize=8)
    labels = [("Candidate 976" if r["reference"] == "976" else "Newton") +
              r", $T=" + str(F(r["values_exact"]["T"])) + "$" for r in ROWS]
    ax.set_yticks(range(len(ROWS)-1, -1, -1), labels)
    ax.set_xlim(0, 10.25)
    ax.axvline(10, linestyle=(0, (4, 3)), lw=.8, color=GREY)
    ax.text(9.88, 5.47, "tolerance", ha="right", color=GREY, fontsize=8)
    ax.set_xlabel(r"Complete certified radius ($10^{-5}$)")
    ax.grid(axis="x", color="#e3e3e3", linewidth=.5)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1.18), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(HERE / "radius_anatomy.pdf")
    fig.savefig(HERE / "radius_anatomy.png", dpi=180)
    plt.close(fig)

def horizon_figure():
    with (HERE / "data" / "HORIZON_TABLE.csv").open() as f:
        diagnostics = list(csv.DictReader(f))
    fig, ax = plt.subplots(figsize=(6.1, 3.55))
    for ref, color, marker in [("976", ORANGE, "s"), ("Newton", BLUE, "o")]:
        certs = [(float(vals(r)["T"]), float(vals(r)["radius_upper"]), str(vals(r)["gamma"]))
                 for r in ROWS if r["reference"] == ref and F(r["values_exact"]["beta"]) == 1]
        diag = [(float(F(r["T_exact"])), float(r["model_linear_continuous_nonlinear"]))
                for r in diagnostics if r["field"] == ref]
        curve = sorted([(t, radius) for t, radius, g in certs if g in ("337/64", "673/128")] + diag)
        ax.plot(*zip(*curve), color=color, linewidth=1, alpha=.9)
        ax.plot(*zip(*diag), linestyle="none", marker=marker, markersize=5.5,
                markerfacecolor="white", markeredgecolor=color)
        ax.plot([x[0] for x in certs], [x[1] for x in certs], linestyle="none",
                marker=marker, markersize=6, color=color)
    new = vals(ROWS[-1])
    ax.scatter([2], [float(new["radius_upper"])], marker="D", s=49,
               color=GREEN, zorder=5)
    ax.annotate("Variational certificate\n" + r"$T=2,\ \beta=1/2,\ \gamma=2.7$",
                xy=(2, float(new["radius_upper"])), xytext=(1.62, 1.65e-5),
                fontsize=8, color=GREEN, ha="left",
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=.7))
    ax.axhline(1e-4, linestyle=(0, (4, 3)), lw=.8, color=GREY)
    ax.text(1.63, 1.12e-4, r"Tolerance $10^{-4}$", fontsize=8, color=GREY)
    ax.set_yscale("log")
    ax.set_xlim(.4, 2.3)
    ax.set_ylim(4e-6, 8e-4)
    ax.set_xlabel(r"Window length $T$")
    ax.set_ylabel("Radius of the drag enclosure")
    ax.grid(axis="y", color="#e3e3e3", linewidth=.5)
    handles = [
        Line2D([], [], color=ORANGE, marker="s", label=r"976, pointwise ($\beta=1$)", lw=1),
        Line2D([], [], color=BLUE, marker="o", label=r"Newton, pointwise ($\beta=1$)", lw=1),
        Line2D([], [], color=GREY, marker="o", markerfacecolor="white",
               linestyle="none", label="Open markers: diagnostic forecasts"),
        Line2D([], [], color=GREY, marker="o", linestyle="none", label="Filled markers: certified windows"),
    ]
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=7.7)
    fig.tight_layout()
    fig.savefig(HERE / "horizon_radius.pdf")
    fig.savefig(HERE / "horizon_radius.png", dpi=180)
    plt.close(fig)

if __name__ == "__main__":
    radius_figure()
    horizon_figure()
    print("Rebuilt two figures from six exact certificate records.")
