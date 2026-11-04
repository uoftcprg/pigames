ENGINE_PATH=engines/chess/
ENGINE=Ethereal
MULTI_PV=3
TIME=1
DELTA=0.1
GAMMA=1/4
OPENINGS_PATH=lib/books/8moves_v3.pgn.zip
SEED=42
MATCHES_COUNT=50

./examples/watermark/chess/chess_.py $ENGINE_PATH$ENGINE $MULTI_PV $TIME $DELTA $GAMMA $OPENINGS_PATH $SEED $MATCHES_COUNT > examples/watermark/data/chess/$ENGINE.jsonl
