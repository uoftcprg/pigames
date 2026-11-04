ENGINE_PATH=engines/go/
ENGINE=gnugo
DELTA=0.1
GAMMA=1/4
OPENINGS_PATH=lib/fuego-code/book/book.dat
OPENINGS_LENGTH=16
SEED=42
MATCHES_COUNT=50

./examples/watermark/go/gnugo.py $ENGINE_PATH$ENGINE $DELTA $GAMMA $OPENINGS_PATH $OPENINGS_LENGTH $SEED $MATCHES_COUNT > examples/watermark/data/go/$ENGINE.jsonl
