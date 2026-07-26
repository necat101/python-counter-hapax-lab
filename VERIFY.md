# VERIFY

Fresh-clone verification of [python-counter-hapax-lab](https://github.com/necat101/python-counter-hapax-lab).

```
$ git clone https://github.com/necat101/python-counter-hapax-lab.git python-counter-hapax-lab-verify
$ cd python-counter-hapax-lab-verify
$ git rev-parse HEAD
e124696e9fe043427cdc01c3290bb59fa51d64f2

$ python3 run_lab.py
=== python-counter-hapax-lab ===

counter_raw_baseline            hapaxes= 55  vocab= 77
counter_lowercase_baseline      hapaxes= 47  vocab= 72
naive_split_baseline            hapaxes= 62  vocab= 79
naive_split_lower_baseline      hapaxes= 54  vocab= 74
vocab_min_freq_1                hapaxes= 47  vocab= 72  min_freq=1  filtered_vocab=72
vocab_min_freq_2                hapaxes= 47  vocab= 72  min_freq=2  filtered_vocab=25
vocab_min_freq_3                hapaxes= 47  vocab= 72  min_freq=3  filtered_vocab=7
deterministic_vocab_order       hapaxes= 47  vocab= 72
naive_vocab_order               hapaxes= 47  vocab= 72

--- tokenization expectations ---
  PASS  tokenize:word_regex 'Test test TEST'
  PASS  tokenize:word_regex 'hello, hello world! world.'
  PASS  tokenize:word_regex "don't stop can't won't"
  PASS  tokenize:word_regex 'foo bar foo_bar foo-bar'
  PASS  tokenize:naive_split 'Test test TEST'
  PASS  tokenize:naive_split 'hello, hello world! world.'
  PASS  tokenize:naive_split "don't stop can't won't"
  PASS  tokenize:naive_split 'foo bar foo_bar foo-bar'
  PASS  tokenize:word_regex_lower 'Test test TEST'
  PASS  tokenize:word_regex_lower 'hello, hello world! world.'
  PASS  tokenize:word_regex_lower "don't stop can't won't"
  PASS  tokenize:word_regex_lower 'foo bar foo_bar foo-bar'
  PASS  tokenize:naive_split_lower 'Test test TEST'
  PASS  tokenize:naive_split_lower 'hello, hello world! world.'
  PASS  tokenize:naive_split_lower "don't stop can't won't"
  PASS  tokenize:naive_split_lower 'foo bar foo_bar foo-bar'

--- ordering / permutation checks ---
  PASS  perm: counts match
  PASS  perm: hapax_set match
  PASS  perm: insertion_order differs – yes (expected – first-seen order depends on record order)
  PASS  perm: deterministic_order match

--- sanity assertions ---
  PASS  lowercase hapax_count (47) <= raw (55)
  PASS  vocab sizes monotonic: min_freq=1 → 72, min_freq=2 → 25, min_freq=3 → 7
  PASS  47 hapax tokens correctly excluded from min_freq>=2 vocab
  PASS  deterministic vocab ordering is stable

Wrote RESULTS.md

$ python3 -m unittest tests.test_hapax -v
test_case_normalization_reduces_hapax_count ... ok
test_lowercase_counter_independently ... ok
test_naive_split_preserves_punctuation ... ok
test_counts_and_hapaxes_match_across_permutations ... ok
test_deterministic_order_stable_across_permutations ... ok
test_insertion_order_changes_with_record_order ... ok
test_all_expectations ... ok
test_hapaxes_excluded_from_min_freq_2 ... ok
test_min_freq_thresholds_independently ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.009s

OK
```

Verified commit: `e124696e9fe043427cdc01c3290bb59fa51d64f2`

All 9 unittest cases pass. All tokenization expectations pass. Ordering/permutation checks pass. Results match the committed `RESULTS.md`.
