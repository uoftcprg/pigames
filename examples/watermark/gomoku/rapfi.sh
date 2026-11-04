ENGINE_PATH=engines/gomoku/
ENGINE=rapfi
COUNT=3
TIMEOUT_TURN=1000
DELTA=0.1
GAMMA=1/4
OPENINGS_PATH=lib/gomocup-results/gomocup2026results/*.txt
SEED=42
MATCHES_COUNT=50

./examples/watermark/gomoku/rapfi.py ${ENGINE_PATH}pbrain-$ENGINE $COUNT $TIMEOUT_TURN $DELTA $GAMMA "$OPENINGS_PATH" $SEED $MATCHES_COUNT > examples/watermark/data/gomoku/$ENGINE.jsonl
