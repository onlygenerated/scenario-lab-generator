/**
 * ETL tips and tricks shown during loading screens.
 * Organized by skill tag — tips are filtered to match the user's selected focus skills.
 * Edit freely: add, remove, or reword any entry.
 */

export interface EtlTip {
  /** Skill tag this tip relates to, or 'GENERAL' for universal tips. */
  tag: string;
  text: string;
}

const ETL_TIPS: EtlTip[] = [
  // ── JOIN ──────────────────────────────────────────────────────────
  { tag: 'JOIN', text: 'INNER JOIN only keeps rows that match in both tables — unmatched rows silently disappear.' },
  { tag: 'JOIN', text: 'LEFT JOIN keeps every row from the left table, filling NULLs where there is no match on the right.' },
  { tag: 'JOIN', text: 'Joining on columns with NULLs? NULL = NULL is always false, so those rows won\'t match.' },
  { tag: 'JOIN', text: 'A one-to-many JOIN multiplies rows — if a key appears 3 times on the right, you get 3 output rows.' },
  { tag: 'JOIN', text: 'Always check your row count after a JOIN. If it went up unexpectedly, you may have duplicate keys.' },
  { tag: 'JOIN', text: 'CROSS JOIN produces every combination of rows — use it intentionally or not at all.' },
  { tag: 'JOIN', text: 'In pandas, pd.merge() defaults to INNER JOIN. Pass how="left" for a LEFT JOIN.' },
  { tag: 'JOIN', text: 'When joining tables with the same column name, pandas adds _x and _y suffixes. Use suffixes=() to control this.' },
  { tag: 'JOIN', text: 'A self-join (joining a table to itself) is great for comparing rows within the same dataset.' },
  { tag: 'JOIN', text: 'Multiple JOIN conditions (ON a.id = b.id AND a.date = b.date) can dramatically reduce output rows.' },
  { tag: 'JOIN', text: 'Validate your JOIN keys are the same data type — joining an INT to a VARCHAR may silently return zero rows.' },
  { tag: 'JOIN', text: 'FULL OUTER JOIN keeps all rows from both sides. It\'s rare in ETL but useful for reconciliation reports.' },

  // ── AGGREGATION ───────────────────────────────────────────────────
  { tag: 'AGGREGATION', text: 'GROUP BY produces one row per unique combination of grouped columns — count your groups to predict output size.' },
  { tag: 'AGGREGATION', text: 'COUNT(*) counts all rows including NULLs. COUNT(column) skips NULLs in that column.' },
  { tag: 'AGGREGATION', text: 'SUM and AVG ignore NULLs. If every value is NULL, the result is NULL — not zero.' },
  { tag: 'AGGREGATION', text: 'HAVING filters groups after aggregation. WHERE filters rows before. The order matters.' },
  { tag: 'AGGREGATION', text: 'In pandas, .groupby().agg() with a dict lets you apply different functions to different columns.' },
  { tag: 'AGGREGATION', text: 'Forgetting .reset_index() after a pandas groupby gives you a MultiIndex — usually not what you want.' },
  { tag: 'AGGREGATION', text: 'Use .nunique() in pandas to count distinct values within a group.' },
  { tag: 'AGGREGATION', text: 'AVG in SQL returns an integer if both inputs are integers. Cast to NUMERIC first for decimal precision.' },
  { tag: 'AGGREGATION', text: 'You can GROUP BY a computed expression (like DATE_TRUNC) without needing a subquery.' },
  { tag: 'AGGREGATION', text: 'String aggregation? Use STRING_AGG(column, \', \') in Postgres to combine values into one string.' },

  // ── WINDOW_FUNCTION ───────────────────────────────────────────────
  { tag: 'WINDOW_FUNCTION', text: 'Window functions compute across rows without collapsing them — you keep every row unlike GROUP BY.' },
  { tag: 'WINDOW_FUNCTION', text: 'ROW_NUMBER() assigns unique sequential numbers. RANK() leaves gaps after ties. DENSE_RANK() doesn\'t.' },
  { tag: 'WINDOW_FUNCTION', text: 'LAG(column, 1) looks at the previous row. LEAD(column, 1) looks at the next row. Great for comparisons.' },
  { tag: 'WINDOW_FUNCTION', text: 'PARTITION BY in a window function is like GROUP BY — it defines the "window" of rows to compute over.' },
  { tag: 'WINDOW_FUNCTION', text: 'SUM() OVER (ORDER BY date) gives you a running total — one of the most useful window patterns.' },
  { tag: 'WINDOW_FUNCTION', text: 'You can use multiple window functions in the same SELECT — each can have a different PARTITION BY.' },
  { tag: 'WINDOW_FUNCTION', text: 'Window functions execute after WHERE and GROUP BY but before ORDER BY and LIMIT.' },
  { tag: 'WINDOW_FUNCTION', text: 'NTILE(4) splits rows into quartiles. Useful for bucketing data into equal-sized groups.' },
  { tag: 'WINDOW_FUNCTION', text: 'In pandas, .expanding() gives cumulative window calculations. .rolling(n) gives a sliding window of size n.' },
  { tag: 'WINDOW_FUNCTION', text: 'FIRST_VALUE and LAST_VALUE grab the first/last value in a window — handy for "most recent" lookups.' },

  // ── PIVOT ─────────────────────────────────────────────────────────
  { tag: 'PIVOT', text: 'Pivoting turns row values into column headers — it reshapes long/narrow data into wide format.' },
  { tag: 'PIVOT', text: 'In pandas, .pivot_table() handles duplicate values with an aggfunc. Plain .pivot() will error on duplicates.' },
  { tag: 'PIVOT', text: 'Unpivoting (melt) is the reverse: wide columns become rows. Use pd.melt() in pandas.' },
  { tag: 'PIVOT', text: 'After pivoting, column names may be messy. Flatten a MultiIndex with df.columns = [col[1] for col in df.columns].' },
  { tag: 'PIVOT', text: 'CROSSTAB in Postgres is a pivot function — you\'ll need the tablefunc extension enabled.' },
  { tag: 'PIVOT', text: 'Pivoting often introduces NULLs where combinations don\'t exist. Use fill_value=0 in pandas to replace them.' },
  { tag: 'PIVOT', text: 'Pivot tables are great for summary reports but terrible for further joins — unpivot before joining.' },
  { tag: 'PIVOT', text: 'In pandas, pivot_table(index=, columns=, values=, aggfunc=) is the four-argument pattern to memorize.' },
  { tag: 'PIVOT', text: 'When pivoting time-series data, dates usually become the column headers and metrics become the values.' },
  { tag: 'PIVOT', text: 'Dynamic pivots (unknown column values) are hard in SQL but trivial in pandas — just call .pivot_table().' },

  // ── CLEANING ──────────────────────────────────────────────────────
  { tag: 'CLEANING', text: 'Always check for NULLs early: df.isnull().sum() gives you a per-column count instantly.' },
  { tag: 'CLEANING', text: '.strip() removes leading and trailing whitespace — invisible spaces are a top cause of failed joins.' },
  { tag: 'CLEANING', text: 'Standardize casing before comparisons: .str.lower() prevents "New York" != "new york" mismatches.' },
  { tag: 'CLEANING', text: 'Use .replace() or .map() for value standardization — e.g., mapping "NY", "N.Y.", "New York" to one value.' },
  { tag: 'CLEANING', text: 'Check for negative values where they shouldn\'t exist (prices, quantities) — a quick .describe() reveals this.' },
  { tag: 'CLEANING', text: 'COALESCE(a, b, c) in SQL returns the first non-NULL value. In pandas, use .fillna() or .combine_first().' },
  { tag: 'CLEANING', text: 'Empty strings and NULLs are different things. Replace empty strings with NaN first for consistent handling.' },
  { tag: 'CLEANING', text: 'Outlier detection tip: values beyond 3 standard deviations from the mean are worth investigating.' },
  { tag: 'CLEANING', text: '.value_counts() is your best friend for spotting typos, unexpected categories, and data skew.' },
  { tag: 'CLEANING', text: 'Validate column data types after loading — pandas sometimes infers object when you expect int or datetime.' },

  // ── DATE_HANDLING ─────────────────────────────────────────────────
  { tag: 'DATE_HANDLING', text: 'pd.to_datetime() handles most date formats automatically — avoid specifying format unless you need to.' },
  { tag: 'DATE_HANDLING', text: 'Extract date parts with .dt.year, .dt.month, .dt.day, .dt.dayofweek — no string parsing needed.' },
  { tag: 'DATE_HANDLING', text: 'DATE_TRUNC(\'month\', timestamp) in Postgres rounds down to the first of the month — great for monthly grouping.' },
  { tag: 'DATE_HANDLING', text: 'Subtracting two dates in pandas gives a Timedelta. Use .dt.days to get an integer day count.' },
  { tag: 'DATE_HANDLING', text: 'Time zones matter: a TIMESTAMP WITHOUT TIME ZONE and TIMESTAMP WITH TIME ZONE can\'t be compared directly in Postgres.' },
  { tag: 'DATE_HANDLING', text: 'Use pd.Timestamp.now() for the current time in pandas. In SQL, NOW() or CURRENT_TIMESTAMP does the same.' },
  { tag: 'DATE_HANDLING', text: 'EXTRACT(DOW FROM date) in Postgres returns 0 for Sunday, 6 for Saturday. Python\'s .weekday() returns 0 for Monday.' },
  { tag: 'DATE_HANDLING', text: 'Date arithmetic in Postgres: date + INTERVAL \'7 days\' adds a week. In pandas: date + pd.Timedelta(days=7).' },
  { tag: 'DATE_HANDLING', text: 'Watch out for dates stored as strings — they sort lexicographically, so "9/1/2024" comes after "10/1/2024".' },
  { tag: 'DATE_HANDLING', text: 'pd.date_range() generates sequences of dates — useful for creating calendar dimension tables.' },

  // ── DEDUPLICATION ─────────────────────────────────────────────────
  { tag: 'DEDUPLICATION', text: 'df.duplicated() shows which rows are duplicates. Pass subset=[cols] to check specific columns only.' },
  { tag: 'DEDUPLICATION', text: 'df.drop_duplicates(keep="last") keeps the most recent entry when duplicates exist.' },
  { tag: 'DEDUPLICATION', text: 'In SQL, use ROW_NUMBER() OVER (PARTITION BY key ORDER BY date DESC) and keep only row_number = 1.' },
  { tag: 'DEDUPLICATION', text: 'Always decide your dedup strategy first: keep first? keep last? keep the one with the most data?' },
  { tag: 'DEDUPLICATION', text: 'Check df.shape before and after dedup — the difference tells you exactly how many duplicates existed.' },
  { tag: 'DEDUPLICATION', text: 'DISTINCT in SQL removes exact duplicate rows. For partial matching, you need GROUP BY or window functions.' },
  { tag: 'DEDUPLICATION', text: 'Near-duplicates (same entity, slightly different data) are harder — consider fuzzy matching or grouping rules.' },
  { tag: 'DEDUPLICATION', text: 'Deduplication order matters in your pipeline: dedup before aggregation to avoid inflated counts.' },
  { tag: 'DEDUPLICATION', text: 'In Postgres, SELECT DISTINCT ON (column) ORDER BY column, date DESC keeps the latest row per key.' },
  { tag: 'DEDUPLICATION', text: 'Source systems often send the same record multiple times. Always assume duplicates exist until proven otherwise.' },

  // ── TYPE_CASTING ──────────────────────────────────────────────────
  { tag: 'TYPE_CASTING', text: 'In Postgres, use CAST(value AS INTEGER) or the shorthand value::INTEGER to convert types.' },
  { tag: 'TYPE_CASTING', text: 'pd.to_numeric(col, errors="coerce") converts to numbers and turns unparseable values into NaN instead of crashing.' },
  { tag: 'TYPE_CASTING', text: 'Boolean columns from CSV files often load as strings. Map {"true": True, "false": False} explicitly.' },
  { tag: 'TYPE_CASTING', text: 'Casting a FLOAT to INTEGER truncates in Postgres (rounds toward zero). Use ROUND() first if you want normal rounding.' },
  { tag: 'TYPE_CASTING', text: '.astype("int") in pandas will fail if there are NULLs. Use .astype("Int64") (capital I) for nullable integers.' },
  { tag: 'TYPE_CASTING', text: 'Currency strings like "$1,234.56" need .str.replace() to remove $ and commas before converting to float.' },
  { tag: 'TYPE_CASTING', text: 'VARCHAR to DATE casting in Postgres is strict — make sure your format matches or use TO_DATE(text, format).' },
  { tag: 'TYPE_CASTING', text: 'JSON fields in Postgres: use ->> to extract as text, -> to extract as JSON. They return different types.' },
  { tag: 'TYPE_CASTING', text: 'df.dtypes shows every column\'s type at a glance — always check this right after loading data.' },
  { tag: 'TYPE_CASTING', text: 'When writing to SQL with .to_sql(), pandas infers SQL types. Pass dtype={} to override for precision.' },

  // ── NORMALIZATION ───────────────────────────────────────────────────
  { tag: 'NORMALIZATION', text: '1NF means every column holds atomic values — no comma-separated lists or nested structures in a single cell.' },
  { tag: 'NORMALIZATION', text: '2NF removes partial dependencies: every non-key column must depend on the entire primary key, not just part of it.' },
  { tag: 'NORMALIZATION', text: '3NF removes transitive dependencies: non-key columns should depend on the key, the whole key, and nothing but the key.' },
  { tag: 'NORMALIZATION', text: 'Denormalized data is faster to read but harder to update. Normalized data is the opposite. Choose based on your use case.' },
  { tag: 'NORMALIZATION', text: 'A repeating group (e.g., item1, item2, item3 columns) is a 1NF violation — split them into separate rows.' },

  // ── PRIMARY_KEY ────────────────────────────────────────────────────
  { tag: 'PRIMARY_KEY', text: 'A primary key uniquely identifies each row. It must be NOT NULL and unique — PostgreSQL enforces both automatically.' },
  { tag: 'PRIMARY_KEY', text: 'SERIAL creates an auto-incrementing integer PK. Use it for surrogate keys when no natural key is obvious.' },
  { tag: 'PRIMARY_KEY', text: 'Composite primary keys (two+ columns) are valid but make JOINs harder. Prefer a surrogate key unless the combination is truly the identity.' },
  { tag: 'PRIMARY_KEY', text: 'Natural keys (email, SSN) can change over time. Surrogate keys (auto-increment IDs) are stable and join-friendly.' },

  // ── FOREIGN_KEY ────────────────────────────────────────────────────
  { tag: 'FOREIGN_KEY', text: 'A foreign key references another table\'s primary key — it enforces referential integrity so orphan rows can\'t exist.' },
  { tag: 'FOREIGN_KEY', text: 'REFERENCES parent_table(id) — the parent table and column must exist before you can add the FK constraint.' },
  { tag: 'FOREIGN_KEY', text: 'ON DELETE CASCADE automatically removes child rows when the parent is deleted. Use it intentionally.' },
  { tag: 'FOREIGN_KEY', text: 'Insert into parent tables first, then child tables. Foreign keys enforce this order.' },

  // ── STAR_SCHEMA ────────────────────────────────────────────────────
  { tag: 'STAR_SCHEMA', text: 'A star schema has one fact table (metrics/events) surrounded by dimension tables (who, what, where, when).' },
  { tag: 'STAR_SCHEMA', text: 'Fact tables store measurable events (sales, clicks). Dimension tables describe context (customer, product, date).' },
  { tag: 'STAR_SCHEMA', text: 'Dimension tables are typically small and wide. Fact tables are tall and narrow. Design accordingly.' },

  // ── SURROGATE_KEY ──────────────────────────────────────────────────
  { tag: 'SURROGATE_KEY', text: 'A surrogate key is a system-generated identifier (like SERIAL) with no business meaning — stable and efficient for joins.' },
  { tag: 'SURROGATE_KEY', text: 'When migrating data into a table with SERIAL PK, omit the PK column from INSERT — PostgreSQL auto-generates it.' },

  // ── CONSTRAINT_DESIGN ──────────────────────────────────────────────
  { tag: 'CONSTRAINT_DESIGN', text: 'NOT NULL prevents missing values. Add it to any column that must always have data — names, dates, foreign keys.' },
  { tag: 'CONSTRAINT_DESIGN', text: 'UNIQUE ensures no two rows share the same value in a column. Email addresses and usernames are classic examples.' },
  { tag: 'CONSTRAINT_DESIGN', text: 'CHECK constraints enforce business rules at the database level — e.g., CHECK (price > 0) prevents negative prices.' },
  { tag: 'CONSTRAINT_DESIGN', text: 'Constraints are your safety net. Even if the app validates data, the database should too — defense in depth.' },

  // ── INDEXING ───────────────────────────────────────────────────────
  { tag: 'INDEXING', text: 'An index speeds up SELECT queries but slows down INSERT/UPDATE. Add indexes on columns you frequently filter or join on.' },
  { tag: 'INDEXING', text: 'PostgreSQL automatically creates an index on PRIMARY KEY and UNIQUE columns — you don\'t need to add one manually.' },
  { tag: 'INDEXING', text: 'CREATE INDEX idx_name ON table(column) — name your indexes clearly so you can identify them later.' },

  // ── SCD (Slowly Changing Dimensions) ───────────────────────────────
  { tag: 'SCD', text: 'Type 1 SCD: overwrite the old value. Simple but you lose history.' },
  { tag: 'SCD', text: 'Type 2 SCD: add a new row with effective dates (valid_from, valid_to). Preserves full history but grows the table.' },
  { tag: 'SCD', text: 'Type 2 SCDs need a surrogate key — the natural key repeats across versions, so it can\'t be the PK alone.' },

  // ── GENERAL ───────────────────────────────────────────────────────
  { tag: 'GENERAL', text: 'ETL stands for Extract, Transform, Load — read data, reshape it, write it somewhere useful.' },
  { tag: 'GENERAL', text: 'Always check df.shape and df.head() after each step — catching issues early saves debugging later.' },
  { tag: 'GENERAL', text: 'Idempotent pipelines (same input = same output) are easier to debug, rerun, and trust.' },
  { tag: 'GENERAL', text: 'Use if_exists="replace" during development for easy reruns. Switch to "append" for production incremental loads.' },
  { tag: 'GENERAL', text: 'Read source data once and reuse the DataFrame — don\'t hit the database repeatedly for the same table.' },
  { tag: 'GENERAL', text: 'Name your DataFrames clearly: raw_orders, cleaned_orders, final_orders — your future self will thank you.' },
  { tag: 'GENERAL', text: 'Print intermediate row counts between steps. A sudden drop or spike tells you exactly where things went wrong.' },
  { tag: 'GENERAL', text: 'pd.read_sql_table() reads a whole table. pd.read_sql_query() lets you push filtering to the database.' },
  { tag: 'GENERAL', text: 'Small data? pandas is fine. Millions of rows? Consider pushing transformations into SQL for better performance.' },
  { tag: 'GENERAL', text: 'The best pipeline is the one you can explain to a teammate in under a minute.' },
];

export default ETL_TIPS;
