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
