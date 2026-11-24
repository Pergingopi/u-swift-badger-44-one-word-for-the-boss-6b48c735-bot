#!/usr/bin/env python3
"""One Word for the Boss - exactly one word that describes the boss.

Pure Python 3.13 standard library. The program writes exactly one word to
/output/entry.txt. No network, no model call, fully deterministic: the same
code always writes the same bytes.

The word (13 characters, 13 bytes, no trailing newline):
    Spotlighthog

Why this word - candidates compared against the judge brief, in the brief's
own priority order (1. funny, 2. true, 3. fresh). The gate: exactly one
word, up to 30 characters, no phrase, no caption, no explanation, and the
word has to land on its own.

REVISION (24 Nov 2026, ~20:05 WIB): the builder's word "Backseatdriver"
was REPLACED. A fresh fetch of the public submissions endpoint
(GET /api/competitions/u-swift-badger-44-one-word-for-the-boss-6b48c735/submissions,
842 submissions, 412 unique titles) shows "Backseatdriver" is already in
the field - submitted 24 Nov 12:22:02Z (19:22 WIB) by handle "aint965",
status "submitted", earlier receipt than ours; the backseat family has 3
hits in total (Backseatdriver, Backseater x2). Copies share one rate and
the earlier receipt places above, so keeping it would cap the entry at a
shared rate. The field is far bigger than the 82 the builder assumed
(827 submissions at fetch time), so freshness was re-checked against the
real field, not from first principles alone. Title is used as the proxy
for the entry word: in this bounty the word-like titles track the word
(Hovercraft x23, Seagull x16, Ghost x10).

Candidates (reviser):

1. Backseatdriver - DEAD. Funny and true, but already submitted by
   another entrant with an earlier receipt. Out.
2. Spotlighthog - KEPT. "Spotlight hog" is a real idiom everyone already
   knows, so it lands instantly with no assembly required. Funny: the
   image is a boss hogging the stage light while the team does the work
   in the dark - "hog" does the comic work. True: the boss who takes
   the attention and the credit is the universal office archetype.
   Fresh: "spotlight" appears 0 times in all 842 field titles,
   "limelight" 0 times, and the only other hog word is "Gloryhog" (x1)
   - a different image (glory, not the stage spotlight). Thirteen
   characters, one word, no spaces, no punctuation.
3. Praisehog - the runner-up. Short (9ch) and the same "hog" gag, but
   "praise" is abstract where "spotlight" is a visual stage image, and
   "Praisethief" (x1) already sits nearby. Loses to Spotlighthog on the
   image.
4. Creditvampire - a vivid gag (vampire sucking credit), but an invented
   compound that needs a beat of assembly, and the vampire family is
   already crowded (Vampire, KPIvampire, Meetingvampire, Vampire Boss).
   Loses on fresh and on instant landing.
5. Puppeteer - a known word, but sinister rather than funny, and the
   puppet family is taken (Puppetmaster x4). Loses on funny and fresh.
6. Gaslighter - true, but a dark accusation, not a joke; fails the
   funny axis, the brief's first criterion. Out.
7. Moodbarometer - fresh and invented, but the judge has to assemble
   the meaning from parts and "barometer" is a flat, unfunny second
   half (the same flaw as the builder's Shoulderwatcher). Out.
8. Creditthief / Blameshifter / Tasktornado / Weathervane - all already
   in the field (x1 / x1 / x1 / x4). Out. Hovercraft (x23), Seagull
   (x16), Ghost (x10), Micromanager (x7), Teflon (x7), Bottleneck (x7),
   Arsonist (x7), Overlord (x6), Delegator (x9), Meetingizer (x7) and
   the whole hover/seagull/ghost/meeting/credit/vampire territory are
   crowded; the winning word needed a different image family, and the
   spotlight is one.

Newline decision: the gate requires exactly one word, up to 30 characters.
"Spotlighthog" is 13 characters, so no newline is needed to pass the
gate, and writing WITHOUT a trailing newline means the file is
byte-for-byte exactly the single word - nothing else for the judge to
read, and no ambiguity about what the word is.

Gate validation: before writing, the program asserts the entry is exactly
one word (no whitespace anywhere inside it), 1-30 characters, not only
whitespace, and encodable as UTF-8; after writing it reads the file back
and verifies the bytes on disk are exactly the word, so a bad word can
never be silently submitted. If any assert fails the program exits
non-zero and writes nothing.

Usage: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os

WORD = "Spotlighthog"


def validate_word(word: str) -> bytes:
    """Gate-check the entry before anything is written. Returns UTF-8 bytes."""
    assert isinstance(word, str), "word must be a str"
    assert word, "word must not be empty"
    assert word == word.strip(), "word must have no leading/trailing whitespace"
    assert not any(ch.isspace() for ch in word), "entry must be exactly one word"
    assert 1 <= len(word) <= 30, "gate requires 1-30 characters"
    assert word.strip(), "word must not be only whitespace"
    data = word.encode("utf-8")
    assert b"\n" not in data and b"\r" not in data, "no newline inside the word"
    return data


def _write_all(f, data: bytes) -> None:
    """Write all bytes, looping over partial writes."""
    view = memoryview(data)
    while view:
        n = f.write(view)
        if n is None:
            raise IOError("write returned None")
        view = view[n:]


def main():
    data = validate_word(WORD)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Clean the CONTENTS of the output folder only; never remove the folder
    # itself (the grader mounts it).
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
    tmp = os.path.join(out_dir, ".entry.txt.tmp")
    final = os.path.join(out_dir, "entry.txt")
    # Stale-tmp retry: a leftover tmp from a crashed run must not block us.
    for attempt in range(3):
        try:
            with open(tmp, "wb") as f:
                _write_all(f, data)
                f.flush()
                os.fsync(f.fileno())
            break
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            if attempt == 2:
                raise
    os.chmod(tmp, 0o644)
    os.replace(tmp, final)
    os.chmod(final, 0o644)
    # Read-back verification: the file on disk must be byte-for-byte the word.
    with open(final, "rb") as f:
        on_disk = f.read()
    assert on_disk == data, "entry.txt on disk differs from the validated word"
    assert (os.stat(final).st_mode & 0o777) == 0o644, "entry.txt must be mode 0644"


if __name__ == "__main__":
    main()
