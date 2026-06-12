---
title: tds-csv — User Guide
author: Your Name
date: 2026-05-10
---

# tds-csv

**tds-csv** is a tiny CLI for quickly exploring CSV files. Built for the
*Tools in Data Science* course at IIT Madras, May 2026.

## Installation

```bash
uvx tds-csv-YOURNAME --help
```

## Usage

1. Show the top 10 rows
```
tds-csv sample.csv
```

2. Sort by a specific columns:
```
tds-csv sample.csv --by population --top 5
```

## How it works:

The tool:

- Reads the CSV with ```pandas.read_csv```.
- Sorts by the chosen column (defaulting to the first column).
- Takes the top N rows.
- Renders them with rich as a ```Unicode``` table.

## Architecture

The formula for text-to-digital transformation is:
```
output = Render(SortBy_col(Read(csv))[:N])
```

## License

MIT - see the [License](../LICENSE) file