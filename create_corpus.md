Use this command:
cat *.jsonl | shuf | split -l $(($(wc -l <(cat *.jsonl) | awk '{print int($1/257)}'))) -a 3 -d corpus/train_ && for f in corpus/train_*; do mv "$f" "$f.jsonl"; done && mv corpus/train_$(printf "%03d" $(ls corpus | grep -Eo '[0-9]+' | sort -nr | head -n1)).jsonl corpus/validation.jsonl
