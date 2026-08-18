# Horse AI Predictor

Project purpose
- An open-source system to predict horse-racing outcomes using historical race data and provide betting analysis.

MVP 0.1 scope
- Create project scaffolding and configuration.
- Provide pipeline placeholders for data, features, modeling, betting logic, and evaluation.
- Add a minimal pytest test to confirm package import.

Predictions
- The system will eventually predict Win and Top-3 probabilities for horses in a race.

Betting recommendations
- Betting recommendations will be produced by comparing model probability estimates with market odds to identify potential edges.

Data & validation
- All predictions must use only information available before the race (no future leakage).
- Chronological / walk-forward validation will be used to prevent data leakage.

Legal & risk
- The system must never guarantee profit. Outputs are probabilistic estimates intended for research and educational purposes only.

Notes
- Python 3.12 is the target runtime for development and CI.
- Only free and open-source libraries are used for MVP 0.1.

Canonical Data Model
- One row represents one horse in one race, uniquely identified by race_id + horse_id.
- Pre-race features are the model inputs and must reflect only information known before the race starts.
- Post-race results are outcomes and targets; they are stored for evaluation and training labels, not as model inputs.
- Chronological data is required so historical form and validation are built in time order.
- Future information must never be used to predict a past race.

Data Ingestion Architecture
Raw source data
  ↓
Source Loader
  ↓
Normalizer
  ↓
Canonical Schema
  ↓
Validation
  ↓
Processed Dataset

- Raw source files enter through a loader that understands a specific source format.
- The normalizer standardizes column names, whitespace, missing values, dates, and numeric fields without inventing data.
- The canonical schema defines the one-horse-in-one-race structure expected by the rest of the system.
- Validation enforces required columns, primary-key uniqueness, sane value ranges, and leakage protection.
- Source-specific ingestion adapters will be added later for real racing data providers and export formats.
