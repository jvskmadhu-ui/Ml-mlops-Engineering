# MLOps Batch Job

## Local Run

python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log

## Web App

python app.py

Open browser to http://localhost:5000 and click "Run Job" to execute the batch job and view results.

## Docker

docker build -t mlops-task .
docker run --rm mlops-task

## Example metrics.json

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4989,
  "latency_ms": 64,
  "seed": 42,
  "status": "success"
}
```