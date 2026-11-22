"""Check a Stroop results file (CSV downloaded from the results screen).

Usage (from the stroop folder):
    python3 check_data.py                       # newest stroop_results*.csv in this folder or ~/Downloads
    python3 check_data.py path/to/file.csv      # a specific file

The expected numbers are NOT typed here. The number of repeats is read from
experiment.js (CONGRUENT_REPEATS and, if present, REPETITIONS), so changing
the design there changes what this script expects.

The colour names and keys ARE written out here on purpose, separately from
experiment.js, so the check does not simply repeat whatever the experiment does.

It checks the saved file only. It cannot prove that the right word and ink
appeared on screen.
"""
import csv
import glob
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_JS = os.path.join(HERE, "experiment.js")

EXPECTED_COLUMNS = ["trial_number", "word", "ink", "condition",
                    "correct_key", "response", "correct", "rt"]

# word shown -> ink class -> key. Written out separately from experiment.js.
COLOURS = [
    {"word": "RED",    "ink": "red",    "key": "r"},
    {"word": "GREEN",  "ink": "green",  "key": "g"},
    {"word": "BLUE",   "ink": "blue",   "key": "b"},
    {"word": "YELLOW", "ink": "yellow", "key": "y"},
]
KEY_FOR_INK = {c["ink"]: c["key"] for c in COLOURS}
INK_FOR_WORD_UPPER = {c["word"]: c["ink"] for c in COLOURS}


def read_constant(name, default=None):
    """Read `var NAME = 3;` from experiment.js and return 3."""
    with open(EXPERIMENT_JS, encoding="utf-8") as file:
        text = file.read()
    match = re.search(r"^\s*(?:var|let|const)\s+" + name + r"\s*=\s*(\d+)", text, re.MULTILINE)
    if match:
        return int(match.group(1))
    if default is not None:
        return default
    raise SystemExit(f"Could not find {name} in {EXPERIMENT_JS}")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return reader.fieldnames, list(reader)


def expected_design():
    """Return the numbers the design should produce, from experiment.js."""
    congruent_repeats = read_constant("CONGRUENT_REPEATS")
    repetitions = read_constant("REPETITIONS", default=1)
    n = len(COLOURS)
    return {
        "repetitions": repetitions,
        "congruent_repeats": congruent_repeats,
        "congruent": n * congruent_repeats * repetitions,
        "incongruent": n * (n - 1) * repetitions,
        "per_congruent_pair": congruent_repeats * repetitions,
        "per_incongruent_pair": repetitions,
        "per_ink": (congruent_repeats + (n - 1)) * repetitions,
    }


# Every check takes (fieldnames, rows, design) and returns a list of problems.

def check_columns(fieldnames, rows, design):
    if fieldnames == EXPECTED_COLUMNS:
        return []
    return [f"columns are {fieldnames}, expected {EXPECTED_COLUMNS}"]


def check_row_count(fieldnames, rows, design):
    expected = design["congruent"] + design["incongruent"]
    if len(rows) == expected:
        return []
    return [f"{len(rows)} rows, expected {expected}"]


def check_condition_counts(fieldnames, rows, design):
    counts = Counter(row["condition"] for row in rows)
    problems = []
    for condition in ("congruent", "incongruent"):
        if counts[condition] != design[condition]:
            problems.append(f"{condition}: {counts[condition]} trials, expected {design[condition]}")
    for other in sorted(set(counts) - {"congruent", "incongruent"}):
        problems.append(f"unknown condition label {other!r}")
    return problems


def check_condition_matches_word_and_ink(fieldnames, rows, design):
    problems = []
    for row in rows:
        word_ink = INK_FOR_WORD_UPPER.get(row["word"])
        if word_ink is None:
            problems.append(f"trial {row['trial_number']}: unknown word {row['word']!r}")
            continue
        expected = "congruent" if word_ink == row["ink"] else "incongruent"
        if row["condition"] != expected:
            problems.append(f"trial {row['trial_number']}: {row['word']} in {row['ink']} ink "
                            f"is labelled {row['condition']}, should be {expected}")
    return problems


def check_each_pair_count(fieldnames, rows, design):
    """Every word x ink combination must appear the right number of times."""
    counts = Counter((row["word"], row["ink"]) for row in rows)
    problems = []
    for word_colour in COLOURS:
        for ink_colour in COLOURS:
            pair = (word_colour["word"], ink_colour["ink"])
            congruent = word_colour["ink"] == ink_colour["ink"]
            expected = design["per_congruent_pair"] if congruent else design["per_incongruent_pair"]
            if counts[pair] != expected:
                problems.append(f"{pair[0]} in {pair[1]} ink: {counts[pair]} trials, expected {expected}")
    return problems


def check_ink_balance(fieldnames, rows, design):
    counts = Counter(row["ink"] for row in rows)
    return [f"ink {c['ink']}: {counts[c['ink']]} trials, expected {design['per_ink']}"
            for c in COLOURS if counts[c["ink"]] != design["per_ink"]]


def check_correct_key(fieldnames, rows, design):
    """correct_key must be the key of the INK colour (not of the word)."""
    problems = []
    for row in rows:
        expected = KEY_FOR_INK.get(row["ink"])
        if row["correct_key"] != expected:
            problems.append(f"trial {row['trial_number']}: ink {row['ink']} has correct_key "
                            f"{row['correct_key']!r}, expected {expected!r}")
    return problems


def check_responses_present_and_valid(fieldnames, rows, design):
    valid = set(KEY_FOR_INK.values())
    return [f"trial {row['trial_number']}: response {row['response']!r} is not one of {sorted(valid)}"
            for row in rows if row["response"].lower() not in valid]


def check_correct_column(fieldnames, rows, design):
    """correct must be true exactly when response equals correct_key."""
    problems = []
    for row in rows:
        should_be = row["response"].lower() == row["correct_key"].lower()
        saved = row["correct"].strip().lower()
        if saved not in ("true", "false"):
            problems.append(f"trial {row['trial_number']}: correct is {row['correct']!r}, not true/false")
        elif (saved == "true") != should_be:
            problems.append(f"trial {row['trial_number']}: response {row['response']!r}, "
                            f"correct_key {row['correct_key']!r}, but correct = {saved}")
    return problems


def check_trial_numbers(fieldnames, rows, design):
    found = [row["trial_number"] for row in rows]
    expected = [str(number) for number in range(1, len(rows) + 1)]
    if found == expected:
        return []
    return [f"trial_number column is {found[:8]}..., expected 1, 2, 3, ... in order"]


def check_reaction_times(fieldnames, rows, design):
    bad = []
    for row in rows:
        try:
            if float(row["rt"]) <= 0:
                bad.append(row["trial_number"])
        except ValueError:
            bad.append(row["trial_number"])
    return [f"missing or invalid rt on trials {bad[:8]}"] if bad else []


CHECKS = [
    ("columns are the expected ones", check_columns),
    ("number of rows matches the design", check_row_count),
    ("congruent / incongruent counts", check_condition_counts),
    ("condition label matches word and ink", check_condition_matches_word_and_ink),
    ("each word x ink pair appears the right number of times", check_each_pair_count),
    ("each ink appears equally often", check_ink_balance),
    ("correct_key matches the ink colour", check_correct_key),
    ("responses are present and valid keys", check_responses_present_and_valid),
    ("correct agrees with response and correct_key", check_correct_column),
    ("trial numbers are 1, 2, 3, ... in order", check_trial_numbers),
    ("reaction times are present", check_reaction_times),
]


def find_default_file():
    candidates = []
    for folder in (HERE, os.getcwd(), os.path.expanduser("~/Downloads")):
        candidates += glob.glob(os.path.join(folder, "stroop_results*.csv"))
    return max(candidates, key=os.path.getmtime) if candidates else None


def main(argv):
    path = argv[1] if len(argv) > 1 else find_default_file()
    if not path:
        print("No stroop_results*.csv found. Pass a file name as an argument.")
        return 2
    print(f"Checking {path}")

    design = expected_design()
    print(f"Design from experiment.js: CONGRUENT_REPEATS = {design['congruent_repeats']}, "
          f"REPETITIONS = {design['repetitions']} -> {design['congruent'] + design['incongruent']} trials expected")

    fieldnames, rows = read_csv(path)
    if not rows:
        print("FAIL  file contains no data rows")
        return 1

    column_problems = check_columns(fieldnames, rows, design)
    if column_problems:
        print("FAIL  columns are the expected ones")
        print(f"        - {column_problems[0]}")
        print("The other checks need these columns, so they were not run.")
        return 1

    failed = 0
    for description, check in CHECKS:
        problems = check(fieldnames, rows, design)
        print(f"{'PASS' if not problems else 'FAIL'}  {description}")
        for problem in problems[:5]:
            print(f"        - {problem}")
        if len(problems) > 5:
            print(f"        - ... and {len(problems) - 5} more")
        failed += bool(problems)

    print("All checks passed." if failed == 0 else f"{failed} check(s) failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
