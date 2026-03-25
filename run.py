import argparse
import yaml
import pandas as pd
import numpy as np
import logging
import json
import time
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--log-file', required=True)
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(filename=args.log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Job started")

    start_time = time.time()

    config = {}
    try:
        # Load config
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        required = ['seed', 'window', 'version']
        for r in required:
            if r not in config:
                raise ValueError(f"Missing config field: {r}")
        seed = config['seed']
        window = config['window']
        version = config['version']
        logging.info(f"Config loaded: seed={seed}, window={window}, version={version}")
        np.random.seed(seed)

        # Load data
        df = pd.read_csv(args.input)
        if df.empty:
            raise ValueError("Empty input file")
        if 'close' not in df.columns:
            raise ValueError("Missing 'close' column")
        rows_loaded = len(df)
        logging.info(f"Rows loaded: {rows_loaded}")

        # Compute rolling mean
        df['rolling_mean'] = df['close'].rolling(window=window).mean()
        logging.info("Rolling mean computed")

        # Generate signal
        df['signal'] = (df['close'] > df['rolling_mean']).astype(int)
        # For NaN in rolling_mean, signal is NaN, so drop for mean
        signal_rate = df['signal'].dropna().mean()
        logging.info("Signal generated")

        # Metrics
        rows_processed = len(df)
        latency_ms = int((time.time() - start_time) * 1000)
        metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }
        logging.info(f"Metrics: {metrics}")
        logging.info("Job completed successfully")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        version = config.get('version', 'unknown') if config else 'unknown'
        metrics = {
            "version": version,
            "status": "error",
            "error_message": str(e)
        }

    # Write metrics
    with open(args.output, 'w') as f:
        json.dump(metrics, f, indent=2)

    # Print to stdout
    print(json.dumps(metrics, indent=2))

    # Exit code
    if metrics.get('status') == 'error':
        sys.exit(1)

if __name__ == '__main__':
    main()