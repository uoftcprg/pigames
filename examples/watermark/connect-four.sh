DELTA=0.1
GAMMA=1/4
OPENINGS_COUNT=8
SEED=42
MATCHES_COUNT=50

./examples/watermark/connect-four.py $DELTA $GAMMA $OPENINGS_COUNT $SEED $MATCHES_COUNT > examples/watermark/data/connect-four.jsonl
