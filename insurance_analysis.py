"""
Insurance Distribution Growth Analytics
---------------------------------------
Channel performance, partner segmentation and white-space analysis on the
Kaggle "Health Insurance Cross Sell Prediction" dataset (train.csv).

Run:
    python insurance_analysis.py            # full analysis
    python insurance_analysis.py --model    # also fits the optional lead-scoring model

Needs: data/train.csv  (download from Kaggle and place it in the data/ folder)

Outputs (all in outputs/):
    sql_<name>.csv        result of every query in sql/queries.sql
    channel_tiers.csv     channel segmentation  -> Power BI page 2
    region_whitespace.csv white-space sizing    -> Power BI page 3
    charts/*.png          quick charts for the README
    findings.txt          your real numbers for resume bullets and the strategy note

Note: the dataset has anonymised region and channel codes and no currency.
"Channels" here stand in for partners such as agents and brokers.
"""

import argparse
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "train.csv"
DB_FILE = ROOT / "data" / "insurance.db"
SQL_FILE = ROOT / "sql" / "queries.sql"
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"

MIN_CHANNEL_LEADS = 500    # ignore tiny channels when tiering
MIN_REGION_LEADS = 1000    # ignore tiny regions when setting the benchmark
BENCHMARK_QUANTILE = 0.75  # "top quartile" conversion benchmark

REQUIRED = {"id", "gender", "age", "driving_license", "region_code",
            "previously_insured", "vehicle_age", "vehicle_damage",
            "annual_premium", "policy_sales_channel", "vintage", "response"}


# ----------------------------------------------------------------------------
# 1. Load and clean
# ----------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise SystemExit(f"Put the Kaggle file at {DATA_FILE} and run again.")
    df = pd.read_csv(DATA_FILE)
    df.columns = df.columns.str.lower()
    missing = REQUIRED - set(df.columns)
    if missing:
        raise SystemExit(f"train.csv is missing columns: {sorted(missing)}")

    before = len(df)
    df = df.drop_duplicates(subset="id")
    print(f"Loaded {before:,} rows, kept {len(df):,} after removing duplicate ids; "
          f"missing values: {int(df[list(REQUIRED)].isna().sum().sum())}")

    df["region_code"] = df["region_code"].astype(int)
    df["policy_sales_channel"] = df["policy_sales_channel"].astype(int)
    df["age_band"] = pd.cut(
        df["age"], bins=[17, 25, 35, 45, 55, 65, 120],
        labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]).astype(str)
    return df


def to_sqlite(df: pd.DataFrame) -> sqlite3.Connection:
    DB_FILE.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    df.to_sql("leads", conn, if_exists="replace", index=False)
    return conn


# ----------------------------------------------------------------------------
# 2. SQL conversion analysis
# ----------------------------------------------------------------------------
def read_queries() -> dict:
    queries, name, buf = {}, None, []
    for line in SQL_FILE.read_text().splitlines():
        if line.startswith("-- name:"):
            if name:
                queries[name] = "\n".join(buf).strip()
            name, buf = line.split(":", 1)[1].strip(), []
        elif name:
            buf.append(line)
    if name:
        queries[name] = "\n".join(buf).strip()
    return queries


def run_sql(conn) -> dict:
    results = {}
    for name, sql in read_queries().items():
        res = pd.read_sql(sql, conn)
        res.to_csv(OUT / f"sql_{name}.csv", index=False)
        results[name] = res
        if name not in ("by_region", "by_channel"):
            print(f"\n--- {name} ---\n{res.to_string(index=False)}")
    return results


# ----------------------------------------------------------------------------
# 3. Channel (partner) tiering
# ----------------------------------------------------------------------------
def tier_channels(by_channel: pd.DataFrame) -> pd.DataFrame:
    ch = by_channel[by_channel["leads"] >= MIN_CHANNEL_LEADS].copy()
    ch["conv_rate"] = ch["conversions"] / ch["leads"]
    ch["premium_won"] = ch["conversions"] * ch["avg_premium"]

    vol_cut, rate_cut = ch["leads"].median(), ch["conv_rate"].median()

    def tier(r):
        high_vol, high_rate = r.leads >= vol_cut, r.conv_rate >= rate_cut
        if high_vol and high_rate:
            return "Star"
        if high_rate:
            return "Scale-up"
        if high_vol:
            return "Fix"
        return "Review"

    ch["tier"] = ch.apply(tier, axis=1)
    ch["suggested_action"] = ch["tier"].map({
        "Star": "Protect and retain: priority support, recognition",
        "Scale-up": "Route more leads and widen territory",
        "Fix": "Coaching and incentive redesign to lift conversion",
        "Review": "Reassess viability; consider deprioritising"})
    ch.sort_values("premium_won", ascending=False).to_csv(
        OUT / "channel_tiers.csv", index=False)
    return ch


# ----------------------------------------------------------------------------
# 4. White-space sizing
# ----------------------------------------------------------------------------
def size_whitespace(by_region: pd.DataFrame):
    rg = by_region.copy()
    rg["conv_rate"] = rg["conversions"] / rg["leads"]
    benchmark = rg.loc[rg["leads"] >= MIN_REGION_LEADS, "conv_rate"].quantile(
        BENCHMARK_QUANTILE)

    gap = (benchmark - rg["conv_rate"]).clip(lower=0)
    rg["extra_conversions"] = gap * rg["leads"]
    rg["premium_uplift_full"] = rg["extra_conversions"] * rg["avg_premium"]
    rg["premium_uplift_half"] = rg["premium_uplift_full"] / 2   # conservative case
    rg = rg.sort_values("premium_uplift_full", ascending=False)
    rg.to_csv(OUT / "region_whitespace.csv", index=False)
    return rg, benchmark


# ----------------------------------------------------------------------------
# 5. Optional lead-scoring model
# ----------------------------------------------------------------------------
def lead_model(df: pd.DataFrame) -> dict:
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import train_test_split

    X = pd.get_dummies(
        df[["gender", "age", "driving_license", "previously_insured",
            "vehicle_age", "vehicle_damage", "annual_premium", "vintage"]],
        drop_first=True)
    X = X.astype(float)
    X["annual_premium"] = np.log1p(X["annual_premium"])
    X = (X - X.mean()) / X.std().replace(0, 1)   # standardise; guard constant columns
    y = df["response"]

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_tr, y_tr)
    scores = model.predict_proba(X_te)[:, 1]

    top = y_te.loc[pd.Series(scores, index=y_te.index).nlargest(len(y_te) // 10).index]
    return {"auc": roc_auc_score(y_te, scores),
            "top_decile_rate": top.mean(),
            "base_rate": y_te.mean()}


# ----------------------------------------------------------------------------
# 6. Charts
# ----------------------------------------------------------------------------
def make_charts(res: dict, ch: pd.DataFrame, rg: pd.DataFrame):
    CHARTS.mkdir(parents=True, exist_ok=True)

    a = res["by_age_band"]
    plt.figure(figsize=(7, 4))
    plt.bar(a["age_band"], a["conv_pct"], color="#4C78A8")
    plt.title("Conversion rate by age band"); plt.ylabel("Conversion %")
    plt.tight_layout(); plt.savefig(CHARTS / "conversion_by_age_band.png", dpi=150); plt.close()

    colors = {"Star": "#2E7D32", "Scale-up": "#1976D2", "Fix": "#F57C00", "Review": "#9E9E9E"}
    plt.figure(figsize=(7, 5))
    for t, g in ch.groupby("tier"):
        plt.scatter(g["leads"], g["conv_rate"] * 100, label=t, color=colors[t], alpha=0.8)
    plt.xscale("log"); plt.xlabel("Leads (log scale)"); plt.ylabel("Conversion %")
    plt.title("Channel tiers: volume vs conversion"); plt.legend()
    plt.tight_layout(); plt.savefig(CHARTS / "channel_tiers.png", dpi=150); plt.close()

    top = rg.head(10).iloc[::-1]
    plt.figure(figsize=(7, 4.5))
    plt.barh(top["region_code"].astype(str), top["premium_uplift_full"], color="#4C78A8")
    plt.title("Top 10 regions by estimated premium uplift")
    plt.xlabel("Estimated additional premium (dataset currency units)"); plt.ylabel("Region code")
    plt.tight_layout(); plt.savefig(CHARTS / "whitespace_top10.png", dpi=150); plt.close()


# ----------------------------------------------------------------------------
# 7. Findings (your real numbers)
# ----------------------------------------------------------------------------
def write_findings(res, ch, rg, benchmark, model_out):
    o = res["overall"].iloc[0]
    lines = ["KEY FINDINGS (use these real numbers in your resume and strategy note)", ""]
    lines.append(f"Leads: {int(o.leads):,} | Conversions: {int(o.conversions):,} | "
                 f"Overall conversion: {o.conv_pct}% | Avg premium: {int(o.avg_premium):,}")

    lines += ["", "Segment extremes (groups with 1,000+ leads):"]
    for key in ["age_band", "previously_insured", "vehicle_damage", "vehicle_age", "gender"]:
        t = res[f"by_{key}"]
        t = t[t["leads"] >= 1000].sort_values("conv_pct")
        if len(t) >= 2:
            lines.append(f"- {key}: highest {t[key].iloc[-1]} at {t['conv_pct'].iloc[-1]}%, "
                         f"lowest {t[key].iloc[0]} at {t['conv_pct'].iloc[0]}%")

    lines += ["", f"Channels analysed (>= {MIN_CHANNEL_LEADS} leads): {len(ch)}"]
    lines.append("Tier counts: " + ", ".join(f"{k}={v}" for k, v in ch["tier"].value_counts().items()))
    fix = ch[ch["tier"] == "Fix"]
    if len(fix):
        share = fix["leads"].sum() / ch["leads"].sum() * 100
        lines.append(f"'Fix' channels hold {share:.1f}% of leads in analysed channels but convert below the median")

    below = rg[(rg["leads"] >= MIN_REGION_LEADS) & (rg["premium_uplift_full"] > 0)]
    lines += ["", f"Regions analysed: {len(rg)} | Top-quartile benchmark conversion: {benchmark*100:.2f}%",
              f"Regions (1,000+ leads) below benchmark: {len(below)}",
              f"Estimated uplift if all reach benchmark: {rg['premium_uplift_full'].sum():,.0f}",
              f"Conservative (close half the gap): {rg['premium_uplift_half'].sum():,.0f}",
              "Top 3 regions by uplift: " + ", ".join(
                  f"{int(r.region_code)} ({r.premium_uplift_full:,.0f})" for r in rg.head(3).itertuples())]

    if model_out:
        lines += ["", f"Lead-scoring model AUC: {model_out['auc']:.3f}",
                  f"Top-decile conversion {model_out['top_decile_rate']*100:.1f}% vs "
                  f"base {model_out['base_rate']*100:.1f}% "
                  f"({model_out['top_decile_rate']/model_out['base_rate']:.1f}x lift)"]

    text = "\n".join(lines)
    (OUT / "findings.txt").write_text(text)
    print("\n" + "=" * 70 + "\n" + text)


# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action="store_true", help="fit optional lead-scoring model")
    args = parser.parse_args()

    OUT.mkdir(exist_ok=True)
    df = load_data()
    conn = to_sqlite(df)
    res = run_sql(conn)
    ch = tier_channels(res["by_channel"])
    rg, benchmark = size_whitespace(res["by_region"])
    model_out = lead_model(df) if args.model else None
    make_charts(res, ch, rg)
    write_findings(res, ch, rg, benchmark, model_out)
    print(f"\nDone. Files saved in {OUT}")


if __name__ == "__main__":
    main()
