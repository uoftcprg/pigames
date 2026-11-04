ENGINE_PATH=engines/go/
ENGINE=katago
MODEL_PATH=engines/go/kata1.bin.gz
CONFIG_PATH=engines/go/default_gtp.cfg
MAX_TIME=1
DELTA=0.01
GAMMA=1/4
OPENINGS_PATH=lib/fuego-code/book/book.dat
OPENINGS_LENGTH=16
SEED=42
MATCHES_COUNT=50

./examples/watermark/go/katago.py $ENGINE_PATH$ENGINE $MODEL_PATH $CONFIG_PATH $MAX_TIME $DELTA $GAMMA $OPENINGS_PATH $OPENINGS_LENGTH $SEED $MATCHES_COUNT > examples/watermark/data/go/$ENGINE.jsonl
