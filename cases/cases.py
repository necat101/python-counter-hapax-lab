# Fixed synthetic text records resembling tiny ML training examples.
# No randomness, no downloaded corpora. All literals.
#
# Design goals:
# - some tokens appear once globally (true hapaxes)
# - some tokens appear 2-3x (vocabulary threshold boundary)
# - case variants: "Test" / "test" / "TEST"
# - punctuation variants: "word." / "word," / "word!"
# - apostrophes and underscores
#
# These are fake toy records only – not real reviews, not PII.

RECORDS = [
    # r01
    "fake_user_42 rated test_item_alpha great great great",
    # r02
    "demo_review_07 terrible terrible toy_product_beta",
    # r03
    "sample_input_99 Test test TEST example_token",
    # r04
    "fictional_doc_12 hello, hello world! world.",
    # r05
    "synthetic_record_03 rare_hapax_alpha unique_word_beta",
    # r06
    "toy_example_88 don't stop can't won't",
    # r07
    "example_note_21 under_score_token under_score_token normal",
    # r08
    "fake_order_55 alpha beta gamma alpha beta",
    # r09
    "demo_case_14 Apple apple APPLE fruit Fruit",
    # r10
    "sample_text_66 the the the quick brown fox",
    # r11
    "test_payload_11 hapax_one_only hapax_two_only",
    # r12
    "fictional_review_22 good good bad bad neutral",
    # r13
    "synthetic_entry_07 token_123 token_123 token_456",
    # r14
    "toy_sentence_31 foo bar foo_bar foo-bar",
    # r15
    "example_record_09 lorem ipsum lorem ipsum dolor",
    # r16
    "fake_comment_44 yes yes no maybe",
    # r17
    "demo_doc_19 cat dog cat dog bird",
    # r18
    "sample_log_22 error error warning info info info",
    # r19
    "test_input_05 single_use_token_xyz",
    # r20
    "fictional_note_77 repeat repeat repeat repeat once_only_qrs",
]

# Expected tokenization outputs for specific corner-case strings.
# Keys are (tokenizer_name, input_string), values are expected token lists.
# This makes the tokenization comparison explicit and auditable.

TOKENIZATION_EXPECTATIONS = {
    # re.findall(r"\w+", s)  – word chars only, case-sensitive
    ("word_regex", "Test test TEST"): ["Test", "test", "TEST"],
    ("word_regex", "hello, hello world! world."):
        ["hello", "hello", "world", "world"],
    ("word_regex", "don't stop can't won't"):
        ["don", "t", "stop", "can", "t", "won", "t"],
    ("word_regex", "foo bar foo_bar foo-bar"):
        ["foo", "bar", "foo_bar", "foo", "bar"],

    # str.split() – whitespace only, preserves punctuation
    ("naive_split", "Test test TEST"): ["Test", "test", "TEST"],
    ("naive_split", "hello, hello world! world."):
        ["hello,", "hello", "world!", "world."],
    ("naive_split", "don't stop can't won't"):
        ["don't", "stop", "can't", "won't"],
    ("naive_split", "foo bar foo_bar foo-bar"):
        ["foo", "bar", "foo_bar", "foo-bar"],

    # re.findall(r"\w+", s.lower()) – word chars, case-normalized
    ("word_regex_lower", "Test test TEST"): ["test", "test", "test"],
    ("word_regex_lower", "hello, hello world! world."):
        ["hello", "hello", "world", "world"],
    ("word_regex_lower", "don't stop can't won't"):
        ["don", "t", "stop", "can", "t", "won", "t"],
    ("word_regex_lower", "foo bar foo_bar foo-bar"):
        ["foo", "bar", "foo_bar", "foo", "bar"],

    # str.split(), then .lower() – whitespace, case-normalized, punctuation kept
    ("naive_split_lower", "Test test TEST"): ["test", "test", "test"],
    ("naive_split_lower", "hello, hello world! world."):
        ["hello,", "hello", "world!", "world."],
    ("naive_split_lower", "don't stop can't won't"):
        ["don't", "stop", "can't", "won't"],
    ("naive_split_lower", "foo bar foo_bar foo-bar"):
        ["foo", "bar", "foo_bar", "foo-bar"],
}

# Two fixed permutations of RECORDS, used to test vocabulary ordering stability.
# Same multiset of records, different presentation order.
# Counts and hapax membership must match; Counter insertion order may differ;
# deterministic (-freq, token) ordering must match.

RECORDS_PERMUTATION_A = RECORDS[:]  # original order

RECORDS_PERMUTATION_B = [
    RECORDS[19],  # r20
    RECORDS[10],  # r11
    RECORDS[2],   # r03
    RECORDS[15],  # r16
    RECORDS[7],   # r08
    RECORDS[0],   # r01
    RECORDS[13],  # r14
    RECORDS[5],   # r06
    RECORDS[17],  # r18
    RECORDS[9],   # r10
    RECORDS[3],   # r04
    RECORDS[12],  # r13
    RECORDS[18],  # r19
    RECORDS[6],   # r07
    RECORDS[14],  # r15
    RECORDS[1],   # r02
    RECORDS[11],  # r12
    RECORDS[8],   # r09
    RECORDS[4],   # r05
    RECORDS[16],  # r17
]
