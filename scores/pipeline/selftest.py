"""Quick checks that the rules behave. Run:  python scores/pipeline/selftest.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from music21 import key, pitch  # noqa: E402

import annotate  # noqa: E402
import licenses  # noqa: E402

GOOD = {"composition_status": "public-domain-us", "derivatives_allowed": "yes",
        "edition_license": "CC-BY-SA 4.0", "verified_by": "A. Person", "source_format": "musicxml"}


def expect(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return cond


def main():
    ok = True
    ok &= expect(licenses.check_license("x", None)[0] is False, "L1 refuses a missing row")
    ok &= expect(licenses.check_license("x", GOOD)[0] is True, "a complete PD/CC row passes")
    for lic in ("CC-BY-ND", "CC BY-NC-ND 4.0", "cc-by-nd-3.0", "NoDerivatives"):
        ok &= expect(not licenses.check_license("x", {**GOOD, "edition_license": lic})[0], f"L4 refuses '{lic}'")
    ok &= expect(not licenses.check_license("x", {**GOOD, "derivatives_allowed": "no"})[0], "L3 refuses derivatives_allowed=no")
    ok &= expect(not licenses.check_license("x", {**GOOD, "composition_status": "unknown"})[0], "L2 refuses unknown status")
    ok &= expect(not licenses.check_license("x", {**GOOD, "verified_by": ""})[0], "L5 refuses empty verified_by")
    ok &= expect(licenses.check_license("x", {**GOOD, "edition_license": "CC-BY-NC"})[0], "NC alone is not ND")
    do = pitch.Pitch("G")
    got = [annotate.solfege_syllable(pitch.Pitch(n), do) for n in ("G4", "A4", "B4", "C5", "C#5", "D5", "F5", "F#5")]
    ok &= expect(got == ["do", "re", "mi", "fa", "fi", "sol", "te", "ti"], f"A3 solfege in G: {got}")
    minor = key.Key("a")
    ok &= expect(annotate.solfege_syllable(pitch.Pitch("A4"), minor.relative.tonic) == "la", "A3 minor tonic is la")
    ok &= expect(annotate._count_label(2.5) == (2, "&") and annotate._count_label(1.0) == (1, None), "A2 count labels")
    print("All checks passed." if ok else "Some checks FAILED.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
