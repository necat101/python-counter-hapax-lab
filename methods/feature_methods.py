"""Feature extraction / hapax counting methods.

All stdlib only: collections.Counter, re.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable


def tokenize_word_regex(text: str) -> list[str]:
    """re.findall(r"\\w+", text) – word chars only, case-sensitive."""
    return re.findall(r"\w+", text)


def tokenize_word_regex_lower(text: str) -> list[str]:
    """re.findall(r"\\w+", text.lower()) – word chars, case-normalized."""
    return re.findall(r"\w+", text.lower())


def tokenize_naive_split(text: str) -> list[str]:
    """str.split() – whitespace only, punctuation preserved, case-sensitive."""
    return text.split()


def tokenize_naive_split_lower(text: str) -> list[str]:
    """str.split() then .lower() – punctuation preserved, case-normalized."""
    return [t.lower() for t in text.split()]


def count_tokens(tokens: Iterable[str]) -> Counter:
    """Return a Counter for the given token iterable."""
    return Counter(tokens)


def hapax_set(counts: Counter) -> set[str]:
    """Return the set of tokens occurring exactly once."""
    return {tok for tok, c in counts.items() if c == 1}


def vocab_min_freq(counts: Counter, min_freq: int) -> set[str]:
    """Return vocabulary tokens with count >= min_freq."""
    return {tok for tok, c in counts.items() if c >= min_freq}


def vocab_order_insertion(counts: Counter) -> list[str]:
    """Vocabulary in Counter insertion order (first-seen order).

    This is deterministic for a fixed input order, but WILL change
    if records are presented in a different order – first-seen changes.
    Not suitable for a canonical vocabulary ordering.
    """
    return list(counts.keys())


def vocab_order_deterministic(counts: Counter) -> list[str]:
    """Vocabulary sorted by (-freq, token).

    Stable regardless of input presentation order.
    Canonical ordering for reproducible vocabularies.
    """
    return sorted(counts.keys(), key=lambda tok: (-counts[tok], tok))


# ----------------------------------------------------------------------
# Method wrappers – each takes a list of text records and returns a result dict.
# ----------------------------------------------------------------------


def _run_pipeline(records: list[str], tokenizer_fn) -> dict:
    tokens: list[str] = []
    for rec in records:
        tokens.extend(tokenizer_fn(rec))
    counts = count_tokens(tokens)
    hapaxes = hapax_set(counts)
    return {
        "tokens": tokens,
        "counts": counts,
        "hapax_set": hapaxes,
        "hapax_count": len(hapaxes),
        "vocab_size": len(counts),
    }


def counter_raw_baseline(records: list[str]) -> dict:
    """Counter with re.findall(r"\\w+"), case-sensitive."""
    return _run_pipeline(records, tokenize_word_regex)


def counter_lowercase_baseline(records: list[str]) -> dict:
    """Counter with re.findall(r"\\w+"), case-normalized."""
    return _run_pipeline(records, tokenize_word_regex_lower)


def naive_split_baseline(records: list[str]) -> dict:
    """Counter with str.split(), case-sensitive, punctuation kept.

    Footgun: punctuation creates spurious hapaxes, e.g. "word." vs "word".
    """
    return _run_pipeline(records, tokenize_naive_split)


def naive_split_lower_baseline(records: list[str]) -> dict:
    """Counter with str.split(), case-normalized, punctuation kept."""
    return _run_pipeline(records, tokenize_naive_split_lower)


def vocab_min_freq_1(records: list[str]) -> dict:
    """Vocabulary with min_freq=1 – hapax tokens ARE included."""
    res = counter_lowercase_baseline(records)
    res["min_freq"] = 1
    res["vocab_filtered"] = vocab_min_freq(res["counts"], 1)
    res["vocab_filtered_size"] = len(res["vocab_filtered"])
    return res


def vocab_min_freq_2(records: list[str]) -> dict:
    """Vocabulary with min_freq=2 – true hapaxes are DROPPED."""
    res = counter_lowercase_baseline(records)
    res["min_freq"] = 2
    res["vocab_filtered"] = vocab_min_freq(res["counts"], 2)
    res["vocab_filtered_size"] = len(res["vocab_filtered"])
    return res


def vocab_min_freq_3(records: list[str]) -> dict:
    """Vocabulary with min_freq=3 – more aggressive filtering."""
    res = counter_lowercase_baseline(records)
    res["min_freq"] = 3
    res["vocab_filtered"] = vocab_min_freq(res["counts"], 3)
    res["vocab_filtered_size"] = len(res["vocab_filtered"])
    return res


def deterministic_vocab_order(records: list[str]) -> dict:
    """Vocabulary ordered by (-freq, token) – canonical, input-order independent."""
    res = counter_lowercase_baseline(records)
    res["vocab_ordered"] = vocab_order_deterministic(res["counts"])
    return res


def naive_vocab_order(records: list[str]) -> dict:
    """Vocabulary in Counter insertion order (first-seen).

    Deterministic for fixed input order. The footgun: first-seen order
    changes when record order changes, so this is unsuitable for a
    canonical vocabulary ordering independent of input presentation.
    """
    res = counter_lowercase_baseline(records)
    res["vocab_ordered"] = vocab_order_insertion(res["counts"])
    return res
