"""Real portfolio analysis for Muhammad K.
4 public Kaggle datasets, downloaded as raw CSVs (see raw/ folder).
Each project: clean -> analyse -> charts -> cleaned CSV + Excel workbook.
Run: python3 analyse_all.py
All numbers in the READMEs come from this script's output (findings.json).
"""
import json, os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.expanduser("~/workspace/goals/remote-halal-income-through-quick-data-skills/files/projects")
RAW = os.path.join(BASE, "raw")
plt.rcParams.update({"figure.dpi": 120, "font.size": 10})

def bar(series, title, xlabel, ylabel, path, color="#2563eb", rot=30):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    series.plot(kind="bar", ax=ax, color=color)
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=rot)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)

def save_excel(df, summaries, path):
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        df.head(1000).to_excel(w, sheet_name="Cleaned_Data", index=False)
        for name, s in summaries.items():
            s.to_excel(w, sheet_name=name[:31])

# ---------------------------------------------------------------- 1. Supermarket
def supermarket():
    p = os.path.join(BASE, "01-supermarket-sales")
    df = pd.read_csv(os.path.join(RAW, "supermarket_sales.csv"))
    raw_rows = len(df)
    df.columns = [c.strip().lower().replace(" ", "_").replace("%", "pct") for c in df.columns]
    # cleaning
    dup = int(df.duplicated(subset=["invoice_id"]).sum())
    df = df.drop_duplicates(subset=["invoice_id"])
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    missing = int(df.isna().sum().sum())
    f = {
        "raw_rows": raw_rows, "cleaned_rows": len(df), "duplicate_invoice_ids_removed": dup,
        "missing_values_after_cleaning": missing,
        "total_sales_usd": round(float(df["total"].sum()), 2),
        "total_gross_income_usd": round(float(df["gross_income"].sum()), 2),
        "avg_rating": round(float(df["rating"].mean()), 2),
        "avg_transaction_usd": round(float(df["total"].mean()), 2),
        "sales_by_branch": df.groupby("branch")["total"].sum().round(2).to_dict(),
        "sales_by_product_line": df.groupby("product_line")["total"].sum().round(2).sort_values(ascending=False).to_dict(),
        "sales_by_payment": df.groupby("payment")["total"].sum().round(2).to_dict(),
        "sales_by_customer_type": df.groupby("customer_type")["total"].sum().round(2).to_dict(),
        "top_product_line": df.groupby("product_line")["total"].sum().idxmax(),
        "best_branch": df.groupby("branch")["total"].sum().idxmax(),
        "monthly_sales": df.groupby("month")["total"].sum().round(2).to_dict(),
    }
    bar(df.groupby("product_line")["total"].sum().sort_values(ascending=False),
        "Total sales by product line", "Product line", "Total sales (USD)",
        os.path.join(p, "charts", "sales_by_product_line.png"))
    bar(df.groupby("branch")["total"].sum(), "Total sales by branch (city)",
        "Branch", "Total sales (USD)", os.path.join(p, "charts", "sales_by_branch.png"), rot=0)
    bar(df.groupby("payment")["total"].sum(), "Total sales by payment method",
        "Payment", "Total sales (USD)", os.path.join(p, "charts", "sales_by_payment.png"), rot=0)
    df.to_csv(os.path.join(p, "supermarket_sales_cleaned.csv"), index=False)
    save_excel(df, {"By_Product_Line": df.groupby("product_line")["total"].agg(["sum", "count"]),
                    "By_Branch": df.groupby("branch")["total"].agg(["sum", "count"]),
                    "Monthly": df.groupby("month")["total"].sum().to_frame()},
               os.path.join(p, "supermarket_sales_cleaned.xlsx"))
    json.dump(f, open(os.path.join(p, "findings.json"), "w"), indent=2)
    print("SUPERMARKET", f)

# ---------------------------------------------------------------- 2. Superstore
def superstore():
    p = os.path.join(BASE, "02-superstore-sales")
    df = pd.read_csv(os.path.join(RAW, "superstore.csv"), encoding="latin-1")
    raw_rows = len(df)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    dup_id = int(df.duplicated(subset=["row_id"]).sum())
    df = df.drop_duplicates(subset=["row_id"])
    missing_postal_before = int(df["postal_code"].isna().sum())
    # Postal Code is not needed for sales/profit analysis; keep rows, mark unknown
    df["postal_code"] = df["postal_code"].fillna("Unknown")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")
    df["year"] = df["order_date"].dt.year
    df["profit_margin_pct"] = (df["profit"] / df["sales"] * 100).round(2)
    loss = df[df["profit"] < 0]
    f = {
        "raw_rows": raw_rows, "cleaned_rows": len(df),
        "duplicate_row_ids_removed": dup_id,
        "missing_postal_codes_marked_unknown": missing_postal_before,
        "date_range": [str(df["order_date"].min().date()), str(df["order_date"].max().date())],
        "total_sales_usd": round(float(df["sales"].sum()), 2),
        "total_profit_usd": round(float(df["profit"].sum()), 2),
        "overall_profit_margin_pct": round(float(df["profit"].sum() / df["sales"].sum() * 100), 2),
        "total_orders": int(df["order_id"].nunique()),
        "sales_by_category": df.groupby("category")["sales"].sum().round(2).to_dict(),
        "profit_by_category": df.groupby("category")["profit"].sum().round(2).to_dict(),
        "sales_by_region": df.groupby("region")["sales"].sum().round(2).to_dict(),
        "profit_by_region": df.groupby("region")["profit"].sum().round(2).to_dict(),
        "sales_by_year": {str(k): round(float(v), 2) for k, v in df.groupby("year")["sales"].sum().items()},
        "loss_making_orders_pct": round(float(len(loss) / len(df) * 100), 2),
        "loss_making_rows": int(len(loss)),
        "worst_subcategory_by_profit": df.groupby("sub-category")["profit"].sum().sort_values().head(3).round(2).to_dict(),
        "best_subcategory_by_profit": df.groupby("sub-category")["profit"].sum().sort_values(ascending=False).head(3).round(2).to_dict(),
        "avg_discount_pct": round(float(df["discount"].mean() * 100), 2),
    }
    bar(df.groupby("category")["sales"].sum(), "Total sales by category", "Category", "Sales (USD)",
        os.path.join(p, "charts", "sales_by_category.png"), rot=0)
    bar(df.groupby("region")["profit"].sum(), "Total profit by region", "Region", "Profit (USD)",
        os.path.join(p, "charts", "profit_by_region.png"), rot=0)
    bar(df.groupby("year")["sales"].sum(), "Total sales by year", "Year", "Sales (USD)",
        os.path.join(p, "charts", "sales_by_year.png"), rot=0)
    df.to_csv(os.path.join(p, "superstore_sales_cleaned.csv"), index=False)
    save_excel(df, {"By_Category": df.groupby("category")[["sales", "profit"]].sum(),
                    "By_Region": df.groupby("region")[["sales", "profit"]].sum(),
                    "By_Year": df.groupby("year")[["sales", "profit"]].sum()},
               os.path.join(p, "superstore_sales_cleaned.xlsx"))
    json.dump(f, open(os.path.join(p, "findings.json"), "w"), indent=2)
    print("SUPERSTORE", f)

# ---------------------------------------------------------------- 3. HR attrition
def hr():
    p = os.path.join(BASE, "03-hr-employee-attrition")
    df = pd.read_csv(os.path.join(RAW, "hr_attrition.csv"))
    raw_rows = len(df)
    # cleaning: drop constant / ID columns that carry no analysis value
    df = df.drop(columns=[c for c in ["EmployeeCount", "Over18", "StandardHours"] if c in df.columns])
    dup = int(df.duplicated().sum())
    df = df.drop_duplicates()
    f = {
        "raw_rows": raw_rows, "cleaned_rows": len(df), "duplicate_rows_removed": dup,
        "missing_values": int(df.isna().sum().sum()),
        "attrition_yes": int((df["Attrition"] == "Yes").sum()),
        "attrition_rate_pct": round(float((df["Attrition"] == "Yes").mean() * 100), 2),
        "attrition_by_department_pct": df.groupby("Department")["Attrition"].apply(lambda s: round(float((s == "Yes").mean() * 100), 2)).to_dict(),
        "attrition_by_overtime_pct": df.groupby("OverTime")["Attrition"].apply(lambda s: round(float((s == "Yes").mean() * 100), 2)).to_dict(),
        "attrition_by_job_role_pct": df.groupby("JobRole")["Attrition"].apply(lambda s: round(float((s == "Yes").mean() * 100), 2)).sort_values(ascending=False).to_dict(),
        "attrition_by_job_satisfaction_pct": df.groupby("JobSatisfaction")["Attrition"].apply(lambda s: round(float((s == "Yes").mean() * 100), 2)).to_dict(),
        "avg_monthly_income_left": round(float(df[df["Attrition"] == "Yes"]["MonthlyIncome"].mean()), 2),
        "avg_monthly_income_stayed": round(float(df[df["Attrition"] == "No"]["MonthlyIncome"].mean()), 2),
        "avg_years_at_company_left": round(float(df[df["Attrition"] == "Yes"]["YearsAtCompany"].mean()), 2),
        "avg_years_at_company_stayed": round(float(df[df["Attrition"] == "No"]["YearsAtCompany"].mean()), 2),
        "avg_age": round(float(df["Age"].mean()), 2),
    }
    bar(df.groupby("Department")["Attrition"].apply(lambda s: (s == "Yes").mean() * 100),
        "Attrition rate (%) by department", "Department", "Attrition rate (%)",
        os.path.join(p, "charts", "attrition_by_department.png"), color="#dc2626", rot=0)
    bar(df.groupby("OverTime")["Attrition"].apply(lambda s: (s == "Yes").mean() * 100),
        "Attrition rate (%) by overtime", "Overtime", "Attrition rate (%)",
        os.path.join(p, "charts", "attrition_by_overtime.png"), color="#dc2626", rot=0)
    bar(df.groupby("JobSatisfaction")["Attrition"].apply(lambda s: (s == "Yes").mean() * 100),
        "Attrition rate (%) by job satisfaction (1=low, 4=high)", "Job satisfaction", "Attrition rate (%)",
        os.path.join(p, "charts", "attrition_by_satisfaction.png"), color="#dc2626", rot=0)
    df.to_csv(os.path.join(p, "hr_attrition_cleaned.csv"), index=False)
    save_excel(df, {"By_Department": df.groupby("Department")["Attrition"].apply(lambda s: (s == "Yes").mean() * 100).to_frame("attrition_pct"),
                    "By_JobRole": df.groupby("JobRole")["Attrition"].apply(lambda s: (s == "Yes").mean() * 100).to_frame("attrition_pct")},
               os.path.join(p, "hr_attrition_cleaned.xlsx"))
    json.dump(f, open(os.path.join(p, "findings.json"), "w"), indent=2)
    print("HR", f)

# ---------------------------------------------------------------- 4. Titanic
def titanic():
    p = os.path.join(BASE, "04-titanic-survival")
    df = pd.read_csv(os.path.join(RAW, "titanic.csv"))
    raw_rows = len(df)
    missing_age = int(df["Age"].isna().sum())
    missing_cabin = int(df["Cabin"].isna().sum())
    # cleaning: Cabin is 77% missing, so it is dropped for analysis (noted in README).
    # Age is filled with the median only for age-group analysis; the raw column is kept
    # in the cleaned file with missing values still visible.
    df["Age_filled"] = df["Age"].fillna(df["Age"].median())
    df["AgeGroup"] = pd.cut(df["Age_filled"], bins=[0, 12, 18, 35, 60, 100],
                            labels=["0-12", "13-18", "19-35", "36-60", "60+"])
    df = df.drop(columns=["Cabin"])
    f = {
        "raw_rows": raw_rows, "cleaned_rows": len(df),
        "missing_age": missing_age, "missing_cabin_dropped_column": missing_cabin,
        "overall_survival_rate_pct": round(float(df["Survived"].mean() * 100), 2),
        "survived_count": int(df["Survived"].sum()),
        "survival_by_sex_pct": df.groupby("Sex")["Survived"].mean().mul(100).round(2).to_dict(),
        "survival_by_class_pct": df.groupby("Pclass")["Survived"].mean().mul(100).round(2).to_dict(),
        "survival_by_age_group_pct": df.groupby("AgeGroup", observed=True)["Survived"].mean().mul(100).round(2).to_dict(),
        "survival_by_embarked_pct": df.groupby("Embarked")["Survived"].mean().mul(100).round(2).to_dict(),
        "avg_fare_survived": round(float(df[df["Survived"] == 1]["Fare"].mean()), 2),
        "avg_fare_died": round(float(df[df["Survived"] == 0]["Fare"].mean()), 2),
        "avg_age_survived": round(float(df[df["Survived"] == 1]["Age"].mean()), 2),
        "avg_age_died": round(float(df[df["Survived"] == 0]["Age"].mean()), 2),
    }
    bar(df.groupby("Sex")["Survived"].mean().mul(100), "Survival rate (%) by sex", "Sex", "Survived (%)",
        os.path.join(p, "charts", "survival_by_sex.png"), color="#059669", rot=0)
    bar(df.groupby("Pclass")["Survived"].mean().mul(100), "Survival rate (%) by passenger class", "Class", "Survived (%)",
        os.path.join(p, "charts", "survival_by_class.png"), color="#059669", rot=0)
    bar(df.groupby("AgeGroup", observed=True)["Survived"].mean().mul(100), "Survival rate (%) by age group", "Age group", "Survived (%)",
        os.path.join(p, "charts", "survival_by_age_group.png"), color="#059669", rot=0)
    df.to_csv(os.path.join(p, "titanic_cleaned.csv"), index=False)
    save_excel(df, {"By_Sex": df.groupby("Sex")["Survived"].mean().mul(100).to_frame("survival_pct"),
                    "By_Class": df.groupby("Pclass")["Survived"].mean().mul(100).to_frame("survival_pct")},
               os.path.join(p, "titanic_cleaned.xlsx"))
    json.dump(f, open(os.path.join(p, "findings.json"), "w"), indent=2)
    print("TITANIC", f)

if __name__ == "__main__":
    supermarket(); superstore(); hr(); titanic()
    print("DONE")
