# Dataset

The supplied assignment dataset is stored locally at `data/raw/Unemployment in India.csv`.

The project expects columns for region, date, estimated unemployment rate (%), and area. It also uses estimated employed and labour participation rate (%) if present.

The original CSV is never modified. The loader trims whitespace, removes completely empty rows and exact duplicate records, parses dates, validates unemployment percentages in the 0–100 range, and reports its cleaning decisions.

The dataset is excluded from Git by default. Verify the source license before redistributing it.
