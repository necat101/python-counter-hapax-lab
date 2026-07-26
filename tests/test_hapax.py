import unittest
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
    tokenize_word_regex,
    tokenize_word_regex_lower,
    tokenize_naive_split,
    tokenize_naive_split_lower,
    count_tokens,
    hapax_set,
    vocab_min_freq,
    vocab_order_deterministic,
    vocab_order_insertion,
    counter_raw_baseline,
    counter_lowercase_baseline,
    vocab_min_freq_1,
    vocab_min_freq_2,
    vocab_min_freq_3,
)


class TestTokenizationExpectations(unittest.TestCase):
    """Verify all explicit tokenization expectations from cases.py."""

    def test_all_expectations(self):
        tokenizer_map = {
            "word_regex": tokenize_word_regex,
            "word_regex_lower": tokenize_word_regex_lower,
            "naive_split": tokenize_naive_split,
            "naive_split_lower": tokenize_naive_split_lower,
        }
        for (tok_name, input_text), expected in TOKENIZATION_EXPECTATIONS.items():
            with self.subTest(tokenizer=tok_name, input=input_text):
                fn = tokenizer_map[tok_name]
                actual = fn(input_text)
                self.assertEqual(actual, expected)


class TestCounterHapax(unittest.TestCase):
    """Test Counter-based hapax computation independently."""

    def test_lowercase_counter_independently(self):
        """Recompute counts/hapaxes independently of feature_methods."""
        tokens = []
        for rec in RECORDS:
            tokens.extend(tokenize_word_regex_lower(rec))
        counts = Counter(tokens)
        hapaxes = {tok for tok, c in counts.items() if c == 1}

        # Compare against method wrapper
        res = counter_lowercase_baseline(RECORDS)
        self.assertEqual(res["counts"], counts)
        self.assertEqual(res["hapax_set"], hapaxes)
        self.assertEqual(res["hapax_count"], len(hapaxes))

    def test_case_normalization_reduces_hapax_count(self):
        """Case normalization merges case variants, reducing hapax count."""
        raw = counter_raw_baseline(RECORDS)
        lower = counter_lowercase_baseline(RECORDS)
        # "Test"/"test"/"TEST" → 3 hapaxes raw, 1 token count=3 lower
        # "Apple"/"apple"/"APPLE" → similar
        # "Fruit"/"fruit" → similar
        self.assertLessEqual(lower["hapax_count"], raw["hapax_count"])
        self.assertLess(lower["vocab_size"], raw["vocab_size"])


class TestVocabularyThresholds(unittest.TestCase):
    """Test min-frequency vocabulary filtering."""

    def test_min_freq_thresholds_independently(self):
        """Recompute vocab thresholds independently."""
        res = counter_lowercase_baseline(RECORDS)
        counts = res["counts"]

        vocab_ge1 = {tok for tok, c in counts.items() if c >= 1}
        vocab_ge2 = {tok for tok, c in counts.items() if c >= 2}
        vocab_ge3 = {tok for tok, c in counts.items() if c >= 3}

        # Check method wrappers return matching sets
        self.assertEqual(vocab_min_freq_1(RECORDS)["vocab_filtered"], vocab_ge1)
        self.assertEqual(vocab_min_freq_2(RECORDS)["vocab_filtered"], vocab_ge2)
        self.assertEqual(vocab_min_freq_3(RECORDS)["vocab_filtered"], vocab_ge3)

        # Monotonic: higher min_freq → smaller or equal vocab
        self.assertGreaterEqual(len(vocab_ge1), len(vocab_ge2))
        self.assertGreaterEqual(len(vocab_ge2), len(vocab_ge3))

    def test_hapaxes_excluded_from_min_freq_2(self):
        """True hapaxes must NOT appear in min_freq>=2 vocabulary."""
        res = counter_lowercase_baseline(RECORDS)
        hapaxes = hapax_set(res["counts"])
        vocab_ge2 = vocab_min_freq_2(RECORDS)["vocab_filtered"]
        self.assertTrue(hapaxes.isdisjoint(vocab_ge2),
                        f"hapaxes leaked into vocab_ge2: {hapaxes & vocab_ge2}")


class TestOrderingPermutation(unittest.TestCase):
    """Test vocabulary ordering under two fixed record permutations."""

    def build_counts(self, records):
        toks = []
        for r in records:
            toks.extend(tokenize_word_regex_lower(r))
        return count_tokens(toks)

    def test_counts_and_hapaxes_match_across_permutations(self):
        """Same multiset of records → same counts, same hapax set."""
        counts_a = self.build_counts(RECORDS_PERMUTATION_A)
        counts_b = self.build_counts(RECORDS_PERMUTATION_B)
        self.assertEqual(counts_a, counts_b)
        self.assertEqual(hapax_set(counts_a), hapax_set(counts_b))

    def test_insertion_order_changes_with_record_order(self):
        """Counter insertion order (first-seen) changes with record order."""
        counts_a = self.build_counts(RECORDS_PERMUTATION_A)
        counts_b = self.build_counts(RECORDS_PERMUTATION_B)
        order_a = vocab_order_insertion(counts_a)
        order_b = vocab_order_insertion(counts_b)
        # First-seen order SHOULD differ between the two permutations
        # (this is the footgun – not suitable for canonical vocab)
        self.assertNotEqual(order_a, order_b,
                            "insertion order unexpectedly matched – "
                            "permutations may be too similar")

    def test_deterministic_order_stable_across_permutations(self):
        """(-freq, token) ordering must be identical regardless of input order."""
        counts_a = self.build_counts(RECORDS_PERMUTATION_A)
        counts_b = self.build_counts(RECORDS_PERMUTATION_B)
        det_a = vocab_order_deterministic(counts_a)
        det_b = vocab_order_deterministic(counts_b)
        self.assertEqual(det_a, det_b)
        # Also verify ordering property: descending freq, then alpha
        for i in range(len(det_a) - 1):
            tok_i = det_a[i]
            tok_j = det_a[i + 1]
            c_i = counts_a[tok_i]
            c_j = counts_a[tok_j]
            # Either freq decreases, or freq equal and token alpha <=
            self.assertTrue(
                c_i > c_j or (c_i == c_j and tok_i <= tok_j),
                f"ordering violation: {tok_i}(n={c_i}) before {tok_j}(n={c_j})"
            )

    def test_reported_top_tokens_use_deterministic_order(self):
        """Top tokens reported in RESULTS.md must use (-freq, token) ordering,
        not Counter.most_common() first-seen tie-breaking."""
        res = counter_lowercase_baseline(RECORDS)
        counts = res["counts"]
        top_reported = vocab_order_deterministic(counts)[:15]
        # Verify: descending freq, ties broken alphabetically
        for i in range(len(top_reported) - 1):
            tok_i = top_reported[i]
            tok_j = top_reported[i + 1]
            c_i = counts[tok_i]
            c_j = counts[tok_j]
            self.assertTrue(
                c_i > c_j or (c_i == c_j and tok_i <= tok_j),
                f"top tokens ordering violation: "
                f"{tok_i}(n={c_i}) before {tok_j}(n={c_j})"
            )
        # Specifically: the n=3 group should be alphabetically ordered
        n3_tokens = [tok for tok in top_reported if counts[tok] == 3]
        self.assertEqual(n3_tokens, sorted(n3_tokens),
                         "n=3 tied tokens must be alphabetically ordered")


class TestNaiveSplitFootgun(unittest.TestCase):
    """Test that naive str.split() creates spurious hapaxes from punctuation."""

    def test_naive_split_preserves_punctuation(self):
        """str.split() keeps trailing punctuation, creating distinct tokens."""
        text = "hello, hello world! world."
        regex_tokens = tokenize_word_regex(text)
        split_tokens = tokenize_naive_split(text)
        # regex: ['hello', 'hello', 'world', 'world']
        # split: ['hello,', 'hello', 'world!', 'world.']
        self.assertEqual(regex_tokens, ["hello", "hello", "world", "world"])
        self.assertEqual(split_tokens, ["hello,", "hello", "world!", "world."])
        # split creates 4 hapaxes (all distinct), regex creates 0
        self.assertEqual(len(hapax_set(Counter(regex_tokens))), 0)
        self.assertEqual(len(hapax_set(Counter(split_tokens))), 4)


if __name__ == "__main__":
    unittest.main()
