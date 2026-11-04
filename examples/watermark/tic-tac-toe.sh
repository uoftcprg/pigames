DELTA=0.1
GAMMA=1/4
OPENINGS_COUNT=4
SEED=42
MATCHES_COUNT=50

./examples/watermark/tic-tac-toe.py $DELTA $GAMMA $OPENINGS_COUNT $SEED $MATCHES_COUNT > examples/watermark/data/tic-tac-toe.jsonl
