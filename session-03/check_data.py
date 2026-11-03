"""Check a Ternus data file (.xpd) against the design described in Auxiliary.txt.

Usage (from the session-03 folder, with the class Python environment):
    python check_data.py                  # checks the newest file in data/
    python check_data.py data/FILE.xpd    # checks a specific file

It checks that the file is complete and consistent: number of rows, trials per
condition and ISI, response coding, block order and trial numbering. It cannot
prove that what appeared on screen matched what was saved, because the file
only holds what the program wrote down.

The expected numbers come from config.py, so a short test run (fewer trials per
ISI in config.py) is checked against its own design.
"""
import csv
import glob
import os
import sys
from collections import Counter

from expyriment.misc import constants

import config

CONDITIONS = ("DOTS", "SHAPES")

EXPECTED_COLUMNS = ["subject_id", "condition", "trial", "isi_ms", "frame_ms",
                    "response", "group_response", "key", "rt_ms"]

# Written out here on purpose, separately from Ternus.py, so that this check
# does not simply repeat whatever the experiment does.
# raw key code -> (response, group_response) as saved in the file
EXPECTED_CODING = {
    str(constants.K_LEFT): ("element", "0"),
    str(constants.K_RIGHT): ("group", "1"),
}


def read_xpd(path):
    """Return the column names and the data rows (as dictionaries) of an .xpd file."""
    with open(path, newline="") as file:
        lines = [line for line in file if not line.startswith("#")]
    reader = csv.DictReader(lines)
    return reader.fieldnames, list(reader)


def check_columns(fieldnames, rows):
    if fieldnames == EXPECTED_COLUMNS:
        return []
    return [f"columns are {fieldnames}, expected {EXPECTED_COLUMNS}"]


def check_row_count(fieldnames, rows):
    expected = len(CONDITIONS) * len(config.ISI_VALUES_MS) * config.TRIALS_PER_ISI
    if len(rows) == expected:
        return []
    return [f"{len(rows)} rows, expected {expected}"]


def check_trials_per_condition_and_isi(fieldnames, rows):
    problems = []
    counts = Counter((row["condition"], row["isi_ms"]) for row in rows)
    expected_cells = {(c, str(isi)) for c in CONDITIONS for isi in config.ISI_VALUES_MS}
    for condition, isi in sorted(expected_cells):
        found = counts[(condition, isi)]
        if found != config.TRIALS_PER_ISI:
            problems.append(f"{condition} at ISI {isi}: {found} rows, expected {config.TRIALS_PER_ISI}")
    for condition, isi in sorted(set(counts) - expected_cells):
        problems.append(f"unexpected combination: condition {condition!r}, ISI {isi!r}")
    return problems


def check_block_order(fieldnames, rows):
    """Odd participant numbers do DOTS first, even numbers SHAPES first, one unbroken block each."""
    subject = int(rows[0]["subject_id"])
    expected_first = "DOTS" if subject % 2 == 1 else "SHAPES"
    expected = [expected_first] + [c for c in CONDITIONS if c != expected_first]
    blocks = []
    for row in rows:
        if not blocks or blocks[-1] != row["condition"]:
            blocks.append(row["condition"])
    if blocks == expected:
        return []
    return [f"participant {subject}: blocks appear as {blocks}, expected {expected}"]


def check_trial_numbers(fieldnames, rows):
    found = [row["trial"] for row in rows]
    expected = [str(number) for number in range(1, len(rows) + 1)]
    if found == expected:
        return []
    return [f"trial column is {found[:8]}..., expected 1, 2, 3, ... in order"]


def check_frame_duration(fieldnames, rows):
    bad = [row["trial"] for row in rows if row["frame_ms"] != str(config.IMAGE_DURATION_MS)]
    if not bad:
        return []
    return [f"frame_ms differs from config.IMAGE_DURATION_MS ({config.IMAGE_DURATION_MS}) on trials {bad[:8]}"]


def check_response_coding(fieldnames, rows):
    """LEFT must be saved as element/0 and RIGHT as group/1."""
    problems = []
    for row in rows:
        coding = EXPECTED_CODING.get(row["key"])
        if coding is None:
            problems.append(f"trial {row['trial']}: key {row['key']!r} is neither LEFT nor RIGHT")
        elif (row["response"], row["group_response"]) != coding:
            problems.append(f"trial {row['trial']}: key {row['key']} saved as "
                            f"{row['response']}/{row['group_response']}, expected {coding[0]}/{coding[1]}")
    return problems


def check_reaction_times(fieldnames, rows):
    bad = [row["trial"] for row in rows if not (row["rt_ms"].isdigit() and int(row["rt_ms"]) > 0)]
    if not bad:
        return []
    return [f"missing or invalid rt_ms on trials {bad[:8]}"]


def check_single_participant(fieldnames, rows):
    ids = sorted({row["subject_id"] for row in rows})
    if len(ids) == 1:
        return []
    return [f"rows from several participants: {ids}"]


CHECKS = [
    ("columns are the expected ones", check_columns),
    ("number of rows matches the design", check_row_count),
    ("trials per condition and ISI", check_trials_per_condition_and_isi),
    ("one participant", check_single_participant),
    ("block order follows the participant number", check_block_order),
    ("trial numbers are 1, 2, 3, ... in order", check_trial_numbers),
    ("frame_ms matches config.py", check_frame_duration),
    ("LEFT = element/0, RIGHT = group/1", check_response_coding),
    ("reaction times are present", check_reaction_times),
]


def run_checks(fieldnames, rows):
    """Run all checks and return a list of (description, problems)."""
    if not rows:
        return [("file contains data rows", ["no data rows found"])]
    return [(description, check(fieldnames, rows)) for description, check in CHECKS]


def main(argv):
    if len(argv) > 1:
        path = argv[1]
    else:
        files = glob.glob(os.path.join("data", "*.xpd"))
        if not files:
            print("No .xpd files found in data/. Pass a file name as an argument.")
            return 2
        path = max(files, key=os.path.getmtime)
    print(f"Checking {path}")

    fieldnames, rows = read_xpd(path)
    results = run_checks(fieldnames, rows)
    for description, problems in results:
        print(f"{'PASS' if not problems else 'FAIL'}  {description}")
        for problem in problems[:5]:
            print(f"        - {problem}")
        if len(problems) > 5:
            print(f"        - ... and {len(problems) - 5} more")

    failed = sum(1 for _, problems in results if problems)
    print("All checks passed." if failed == 0 else f"{failed} check(s) failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
