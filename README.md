# Tools in Data Science Course

This repository contains files for Tools in Data Science course done as part of IITM BS degree in Data Science.

## Overview of files

### 1. `fastapi_sentiment.py`

- Developed a FastAPI-based batch sentiment analysis API.
- Implemented POST /sentiment endpoint accepting multiple sentences in a single request.
- Added Pydantic request validation for structured JSON input.
- Built a rule-based sentiment classifier with positive and negative keyword matching.
- Handled common negation phrases such as "not good" and "not bad".
- Returned sentiment labels (happy, sad, neutral) while preserving input order.
- Enabled CORS support for cross-origin API access.

### 2. `fastapi_web_framework.py`

- Developed a FastAPI service for serving student records from a [CSV dataset](q-fastapi.csv).
- Implemented GET /api endpoint to return all student data in JSON format.
- Added support for filtering results using repeated class query parameters.
- Preserved original CSV ordering in API responses.
- Used Python's csv.DictReader for structured data ingestion.
- Configured CORS middleware to allow requests from any origin.

### 3. `image_compression.py`

- Implemented a 5×5 image reconstruction pipeline using provided tile-mapping specification.
- Rearranged image tiles programmatically using PIL image cropping and pasting operations.
- Applied luminance-based grayscale conversion using coefficients 0.2126, 0.7152, and 0.0722.
- Processed image pixel data using NumPy for precise grayscale calculations.
- Generated a lossless grayscale output image suitable for automated verification.
- Experimented with alternate tile-mapping directions and grayscale rounding strategies to satisfy strict pixel-level grading requirements.
- [Given Image](jigsaw.webp) | [Reconstructed Image](answer.png)

### 4. `project`

A serverless FastAPI endpoint deployed on Vercel that processes telemetry data and returns latency and uptime metrics for requested regions.

- Accepts POST requests with a JSON payload containing a list of regions and a latency threshold.
- Computes:
  - Average latency (avg_latency)
  - 95th percentile latency (p95_latency)
  - Average uptime (avg_uptime)
  - Threshold breach count (breaches)
  - Supports multiple regions in a single request.
  - Configured with CORS support for cross-origin access.
  - Deployed as a Python serverless function using FastAPI and Vercel.

### 5. `.github/workflows/tds.yml`

- Developed a GitHub Actions workflow for automated repository validation.
- Implemented manual workflow execution using the workflow_dispatch trigger.
- Configured a job to run on a GitHub-hosted Ubuntu environment.
- Added a custom workflow step containing the required IITM email identifier.
- Verified successful workflow execution through the GitHub Actions dashboard.
- Integrated workflow automation into the existing Git repository structure.
- Applied CI/CD concepts using GitHub Actions and YAML-based workflow definitions.\_

### 6. `variance.py`

- Computed the sample variance of manufacturing measurements from a production dataset to evaluate process stability and quality consistency.
- Reads measurement data from JSON.
- Calculates sample variance using Bessel's correction (N−1 denominator).
- Produces statistically correct variance estimates for quality control analysis.
- Supports manufacturing process monitoring and anomaly detection.

### 7. `unicode.py`

- Processed multiple datasets stored in different text encodings (CP-1252, UTF-8, and UTF-16) and performed cross-file data analysis.
- Automatically detects and reads files with different encodings.
- Handles Unicode character normalization and encoding differences.
- Extracts symbol-value pairs from CSV and TSV files.
- Filters records matching specified Unicode symbols.
- Aggregates and computes the final sum across all datasets.
- Demonstrates robust handling of international text data.
