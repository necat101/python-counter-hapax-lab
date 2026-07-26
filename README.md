# python-counter-hapax-lab

Rare-token / hapax handling correctness lab for ML-adjacent text feature pipelines.

Inspired by [HN #15202895](https://news.ycombinator.com/item?id=15202895) – ["A First Exercise in Natural Language Processing with Python: Counting Hapaxes"](https://catswhisker.xyz/log/2017/9/7/a_first_excercise_in_natural_language_processing_with_python_counting_hapaxes/).

All code is **Python stdlib only** (`collections.Counter`, `re`). No NLTK, spaCy, third-party packages, randomness, downloaded corpora, model downloads, training, or timing benchmarks.

## What it tests

- **`collections.Counter`** for token frequency counting
- **Tokenization and case normalization change the hapax set** – `"Test"` / `"test"` / `"TEST"` merge with `.lower()`, punctuation (`"word."` vs `"word"`) creates spurious hapaxes with naive `str.split()`
- **Hapax tokens vs vocabulary threshold** – a token occurring once globally is a true hapax; a configurable `min_freq` vocabulary threshold (e.g. `count >= 2`) DROPS all hapax tokens from the feature vocabulary
- **Deterministic ordering for equally frequent tokens** – `sorted(counts, key=lambda tok: (-counts[tok], tok))` gives a canonical vocabulary order independent of input presentation. Counter insertion order (first-seen) changes when record order changes – unsuitable for canonical vocabularies

## Methods

| method | tokenizer | case | hapaxes | vocab |
|--------|-----------|------|---------|-------|
| `counter_raw_baseline` | `re.findall(r"\w+")` | sensitive | 55 | 77 |
| `counter_lowercase_baseline` | `re.findall(r"\w+")` | normalized | 47 | 72 |
| `naive_split_baseline` | `str.split()` | sensitive | 62 | 79 |
| `naive_split_lower_baseline` | `str.split()` | normalized | 54 | 74 |
| `vocab_min_freq_1` | word_regex_lower | normalized | 47 | 72 → 72 |
| `vocab_min_freq_2` | word_regex_lower | normalized | 47 | 72 → 25 |
| `vocab_min_freq_3` | word_regex_lower | normalized | 47 | 72 → 7 |
| `deterministic_vocab_order` | word_regex_lower | normalized | 47 | 72 |
| `naive_vocab_order` | word_regex_lower | normalized | 47 | 72 |

Case normalization merges case variants (`"Test"` / `"test"` / `"TEST"` → count 3, no longer hapax), reducing hapax count 55 → 47. Naive `str.split()` preserves punctuation, creating spurious hapaxes (`"word."` vs `"word"`), inflating hapax count to 62 / 79 vocab.

Vocabulary thresholding at `min_freq >= 2` drops all 47 true hapaxes, leaving 25 tokens. At `min_freq >= 3` only 7 tokens survive.

## Tokenization expectations

All tokenization outputs are explicitly recorded in `cases/cases.py` – no "correct" tokenizer is assumed universal:

| input | `word_regex` | `naive_split` | `word_regex_lower` | `naive_split_lower` |
|-------|-------------|---------------|--------------------|--------------------|
| `Test test TEST` | `["Test","test","TEST"]` | same | `["test","test","test"]` | same |
| `hello, hello world! world.` | `["hello","hello","world","world"]` | `["hello,","hello","world!","world."]` | same as word_regex | same as naive_split |
| `don't stop can't won't` | `["don","t","stop","can","t","won","t"]` | `["don't","stop","can't","won't"]` | same | same |
| `foo bar foo_bar foo-bar` | `["foo","bar","foo_bar","foo","bar"]` | `["foo","bar","foo_bar","foo-bar"]` | same | same |

## Vocabulary ordering

Two fixed permutations of the same 20 records are tested:

- **Counts and hapax membership:** identical across permutations ✅
- **Counter insertion order:** differs (first-seen order depends on record order) – this is the footgun, NOT suitable for canonical vocabularies
- **Deterministic `(-freq, token)` order:** identical across permutations ✅

## Running

```bash
python3 run_lab.py
python3 -m unittest tests.test_hapax -v
```

Produces `RESULTS.md` from actual run data.

## Scope

- Fixed synthetic text records only (20 toy "training examples" – fake user IDs, demo reviews, synthetic tokens). No real corpus, no PII.
- Demonstrates `collections.Counter`-based rare-token handling – does NOT validate an NLP model or production tokenizer.
- Python stdlib only. No NLTK, spaCy, third-party packages.
- No randomness, no downloaded datasets, no model training.

## License

MIT
