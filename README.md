# Titanic Passenger Survival Analysis — Portfolio Practice Project

**By:** Muhammad K. — Data Analyst in progress, Madinah, Saudi Arabia
**GitHub:** https://github.com/km038805-ui
**Skills used:** Excel, Google Sheets, Python, Pandas, Data Cleaning, Data Analysis

> Portfolio practice project. This is **not client work and not work for any employer**.
> The data is the public Kaggle Titanic dataset, analysed as practice.

## Data source
- **Kaggle dataset:** Titanic — Machine Learning from Disaster — https://www.kaggle.com/competitions/titanic
- **File:** `titanic.csv` — 891 passengers, 12 columns.
- **Download mirror used (no Kaggle login needed):** https://github.com/datasciencedojo/datasets (titanic.csv)
- **Licence / use:** public Kaggle competition data, for learning and analysis.

## What I cleaned
- `Cabin` was missing for **687 of 891 passengers (77%)**, so that column was dropped — it cannot be used fairly.
- `Age` was missing for **177 passengers**; the missing ages were filled with the median age only for the age-group chart, and the original missing values are still visible in the cleaned file.
- Added `AgeGroup` (0-12, 13-18, 19-35, 36-60, 60+).

## Key findings (real numbers from the data)
- Overall survival: **342 of 891 passengers survived — 38.38%**.
- Survival by sex: female **74.2%**, male **18.89%**.
- Survival by class: 1st class **62.96%**, 2nd class **47.28%**, 3rd class **24.24%**.
- Survival by age group: children 0-12 **57.97%**, 60+ only **22.73%**.
- Survival by port: Cherbourg **55.36%**, Queenstown **38.96%**, Southampton **33.7%**.
- Average fare: survived **$48.40**, died **$22.12**.
- Average age: survived **28.34 years**, died **30.63 years**.

## Files
- `titanic_cleaned.csv` / `.xlsx` — cleaned data + Excel summaries
- `analysis.py` — Python/Pandas cleaning and analysis
- `charts/` — survival by sex, by class, by age group
- `findings.json` — all numbers above, computed by the script

## What this shows
Class, sex and age mattered most for survival — women, children and 1st-class passengers survived far more often. This is a classic beginner analysis, and it is labelled as practice, not as work for any shipping company.

> The cleaned Excel workbook (.xlsx) and chart images are in the local portfolio / CV, not in this repo, because this upload contains text files only.
