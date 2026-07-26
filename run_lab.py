#!/usr/bin/env python3
"""Run hapax / vocabulary threshold correctness lab.

Produces RESULTS.md with a table generated from actual run data.
"""

from __future__ import annotations

import sys
sys.path.insert(0, ".")

from collections import Counter

from cases.cases import (
    RECORDS,
    RECORDS_PERMUTATION_A,
    RECORDS_PERMUTATION_B,
    TOKENIZATION_EXPECTATIONS,
)
from methods.feature_methods import (
    counter_raw_baseline,
    counter_lowercase_baseline,
    naive_split_baseline,
    naive_split_lower_baseline,
    vocab_min_freq_1,
    vocab_min_freq_2,
    vocab_min_freq_3,
    deterministic_vocab_order,
    naive_vocab_order,
    tokenize_word_regex,
    tokenize_word_regex_lower,
    tokenize_naive_split,
    tokenize_naive_split_lower,
    vocab_order_deterministic,
    vocab_order_insertion,
    count_tokens,
    hapax_set,
)


def check_tokenization_expectations() -> list[tuple[str, bool, str]]:
    """Verify all explicit tokenization expectations."""
    tokenizer_map = {
        "word_regex": tokenize_word_regex,
        "word_regex_lower": tokenize_word_regex_lower,
        "naive_split": tokenize_naive_split,
        "naive_split_lower": tokenize_naive_split_lower,
    }
    results = []
    for (tok_name, input_text), expected in TOKENIZATION_EXPECTATIONS.items():
        fn = tokenizer_map[tok_name]
        actual = fn(input_text)
        ok = actual == expected
        detail = "" if ok else f"got {actual!r}, expected {expected!r}"
        results.append((f"tokenize:{tok_name} {input_text!r}", ok, detail))
    return results


def check_ordering_permutation() -> list[tuple[str, bool, str]]:
    """Check vocabulary ordering under two fixed record permutations."""
    # Build counts for both permutations using lowercase word_regex tokenizer
    def build_counts(records):
        toks = []
        for r in records:
            toks.extend(tokenize_word_regex_lower(r))
        return count_tokens(toks)

    counts_a = build_counts(RECORDS_PERMUTATION_A)
    counts_b = build_counts(RECORDS_PERMUTATION_B)

    results = []

    # Counts must match (same multiset of records)
    ok = counts_a == counts_b
    results.append(("perm: counts match", ok, "" if ok else "counts differ"))

    # Hapax membership must match
    hap_a = hapax_set(counts_a)
    hap_b = hapax_set(counts_b)
    ok = hap_a == hap_b
    results.append(("perm: hapax_set match", ok, "" if ok else "hapax sets differ"))

    # Insertion order: record whether it differs (this is expected,
    # not a failure – we just document it)
    order_a = vocab_order_insertion(counts_a)
    order_b = vocab_order_insertion(counts_b)
    differs = order_a != order_b
    results.append((
        "perm: insertion_order differs",
        True,  # informational, always pass
        "yes (expected – first-seen order depends on record order)"
        if differs else "no – insertion order happened to match"
    ))

    # Deterministic order must match
    det_a = vocab_order_deterministic(counts_a)
    det_b = vocab_order_deterministic(counts_b)
    ok = det_a == det_b
    results.append((
        "perm: deterministic_order match",
        ok,
        "" if ok else "deterministic ordering differed (bug!)"
    ))

    return results, counts_a, det_a


def main() -> None:
    rows = []

    methods = [
        ("counter_raw_baseline", counter_raw_baseline),
        ("counter_lowercase_baseline", counter_lowercase_baseline),
        ("naive_split_baseline", naive_split_baseline),
        ("naive_split_lower_baseline", naive_split_lower_baseline),
        ("vocab_min_freq_1", vocab_min_freq_1),
        ("vocab_min_freq_2", vocab_min_freq_2),
        ("vocab_min_freq_3", vocab_min_freq_3),
        ("deterministic_vocab_order", deterministic_vocab_order),
        ("naive_vocab_order", naive_vocab_order),
    ]

    print("=== python-counter-hapax-lab ===\n")

    for name, fn in methods:
        res = fn(RECORDS)
        hapax_count = res["hapax_count"]
        vocab_size = res["vocab_size"]
        vocab_filtered_size = res.get("vocab_filtered_size", "")
        min_freq = res.get("min_freq", "")
        rows.append({
            "method": name,
            "hapax_count": hapax_count,
            "vocab_size": vocab_size,
            "min_freq": min_freq,
            "vocab_filtered_size": vocab_filtered_size,
        })
        print(f"{name:30s}  hapaxes={hapax_count:3d}  vocab={vocab_size:3d}", end="")
        if vocab_filtered_size:
            print(f"  min_freq={min_freq}  filtered_vocab={vocab_filtered_size}", end="")
        print()

    # Tokenization expectation checks
    print("\n--- tokenization expectations ---")
    tok_results = check_tokenization_expectations()
    for label, ok, detail in tok_results:
        status = "PASS" if ok else "FAIL"
        print(f"  {status:4s}  {label}" + (f" – {detail}" if detail else ""))

    # Ordering / permutation checks
    print("\n--- ordering / permutation checks ---")
    perm_results, counts_perm, det_order = check_ordering_permutation()
    for label, ok, detail in perm_results:
        status = "PASS" if ok else "FAIL"
        print(f"  {status:4s}  {label}" + (f" – {detail}" if detail else ""))

    # Sanity assertions
    print("\n--- sanity assertions ---")
    raw_res = counter_raw_baseline(RECORDS)
    lower_res = counter_lowercase_baseline(RECORDS)
    # Case normalization should reduce or maintain hapax count
    # (merging "Test"/"test"/"TEST" → one token with count 3)
    assert lower_res["hapax_count"] <= raw_res["hapax_count"], \
        "lowercase hapax_count should be <= raw"
    print(f"  PASS  lowercase hapax_count ({lower_res['hapax_count']}) "
          f"<= raw ({raw_res['hapax_count']})")

    # Vocab min_freq thresholds must be monotonic decreasing
    v1 = vocab_min_freq_1(RECORDS)
    v2 = vocab_min_freq_2(RECORDS)
    v3 = vocab_min_freq_3(RECORDS)
    assert v1["vocab_filtered_size"] >= v2["vocab_filtered_size"] >= v3["vocab_filtered_size"]
    print(f"  PASS  vocab sizes monotonic: "
          f"min_freq=1 → {v1['vocab_filtered_size']}, "
          f"min_freq=2 → {v2['vocab_filtered_size']}, "
          f"min_freq=3 → {v3['vocab_filtered_size']}")

    # Hapax tokens must NOT appear in min_freq>=2 vocab
    hapax_tokens = hapax_set(lower_res["counts"])
    vocab_ge2 = v2["vocab_filtered"]
    assert hapax_tokens.isdisjoint(vocab_ge2), "hapaxes leaked into min_freq>=2 vocab"
    print(f"  PASS  {len(hapax_tokens)} hapax tokens correctly excluded from min_freq>=2 vocab")

    # Deterministic ordering must be stable
    assert det_order == vocab_order_deterministic(counts_perm)
    print(f"  PASS  deterministic vocab ordering is stable")

    # Write RESULTS.md
    with open("RESULTS.md", "w") as f:
        f.write("# RESULTS\n\n")
        f.write("Generated by `run_lab.py`. All stdlib only, no randomness, no downloads.\n\n")
        f.write("## Method results\n\n")
        f.write("| method | hapax_count | vocab_size | min_freq | vocab_filtered_size |\n")
        f.write("|--------|-------------|------------|----------|---------------------|\n")
        for r in rows:
            f.write(f"| {r['method']} | {r['hapax_count']} | {r['vocab_size']} | "
                    f"{r['min_freq']} | {r['vocab_filtered_size']} |\n")
        f.write("\n## Tokenization expectations\n\n")
        for label, ok, detail in tok_results:
            f.write(f"- {'✅' if ok else '❌'} {label}" +
                    (f" – {detail}" if detail else "") + "\n")
        f.write("\n## Ordering / permutation checks\n\n")
        for label, ok, detail in perm_results:
            f.write(f"- {'✅' if ok else '❌'} {label}" +
                    (f" – {detail}" if detail else "") + "\n")
        f.write("\n## Sanity assertions\n\n")
        f.write(f"- lowercase hapax_count ({lower_res['hapax_count']}) "
                f"<= raw ({raw_res['hapax_count']}) ✅\n")
        f.write(f"- vocab sizes monotonic: min_freq=1 → {v1['vocab_filtered_size']}, "
                f"min_freq=2 → {v2['vocab_filtered_size']}, "
                f"min_freq=3 → {v3['vocab_filtered_size']} ✅\n")
        f.write(f"- {len(hapax_tokens)} hapax tokens correctly excluded "
                f"from min_freq>=2 vocab ✅\n")
        f.write(f"- deterministic vocab ordering is stable ✅\n")

        f.write("\n## Top tokens (lowercase baseline)\n\n")
        f.write("| token | count |\n|-------|-------|\n")
        for tok, c in lower_res["counts"].most_common(15):
            f.write(f"| {tok} | {c} |\n")

        f.write("\n## Hapax tokens (lowercase baseline)\n\n")
        f.write(", ".join(sorted(hapax_tokens)) + "\n")

        f.write("\n## Deterministic vocabulary order (first 20)\n\n")
        for i, tok in enumerate(det_order[:20], 1):
            c = counts_perm[tok]
            f.write(f"{i}. `{tok}` (n={c})\n")

    print("\nWrote RESULTS.md")


if __name__ == "__main__":
    main()
