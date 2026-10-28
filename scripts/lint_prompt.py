#!/usr/bin/env python3
"""no-plastic prompt linter: scores an image prompt against the anti-plastic checklist.

Zero dependencies (Python 3.9+ stdlib). Two modes, auto-detected:

  generate  a text-to-image prompt. Scored on coverage of the eight brief fields
            (subject, composition, camera, light, palette, texture, era, negatives)
            minus penalties for the words that pull models toward the plastic look.
  edit      an instruction applied to an existing image. Scored on whether it names
            one change, locks identity and framing, forbids seams and halos, and
            limits scope to what was asked.

Usage:
  python3 scripts/lint_prompt.py prompt.txt [more.txt ...]
  echo "..." | python3 scripts/lint_prompt.py -
  python3 scripts/lint_prompt.py --json prompt.txt
  python3 scripts/lint_prompt.py --brief prompt.txt      # prints a brief skeleton to fill in
  python3 scripts/lint_prompt.py --strict --min-score 70 prompt.txt   # exit 1 when below

The checks are regular expressions over plain English. They cannot see the image;
they only tell you whether the prompt gives the model enough photographic facts and
whether it contains known trouble words. Always run a pilot image and look at it.
"""
import argparse
import json
import os
import re
import sys

__version__ = "0.1.0"

# --------------------------------------------------------------------------- helpers

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-/.]*")


def _rx(*alts):
    """Build one case-insensitive regex from a list of phrase patterns."""
    return re.compile(r"(?i)(?<![A-Za-z])(?:" + "|".join(alts) + r")(?![A-Za-z])")


NEGATED_RE = re.compile(r"(?i)\b(?:no|not|without|avoid|never|instead of|rather than)\s+(?:\w+[\s-]+){0,2}$")


def _find(rx, text, limit=4, skip_negated=False):
    """Return up to `limit` distinct matches (original casing, first occurrence order).

    With skip_negated, a match preceded by 'no', 'not', 'without', 'avoid' (within two words)
    is ignored: 'no retouched plastic look' is a negative, not a plastic trigger."""
    seen, out = set(), []
    for m in rx.finditer(text):
        if skip_negated and NEGATED_RE.search(text[max(0, m.start() - 40):m.start()]):
            continue
        key = m.group(0).lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(m.group(0))
        if len(out) >= limit:
            break
    return out


def word_count(text):
    return len(WORD_RE.findall(text))


NEG_SPLIT_RE = re.compile(r"(?i)(?<![A-Za-z])(?:negative(?: prompt)?|neg)\s*:\s*")
MJ_NO_RE = re.compile(r"(?i)--no\s+(.*?)(?=\s--\w|$)")
MJ_PARAM_RE = re.compile(r"\s--(?!no\b)[a-z]+(?:\s+[^\s-][^\s]*)*")


def split_negative(text):
    """Split a prompt into (positive, negative) parts.

    Understands a 'Negative:' line (SDXL / ComfyUI habit) and Midjourney's '--no a, b'.
    Other Midjourney parameters (--ar, --style, --s) are removed from the positive part."""
    neg_parts = []
    m = NEG_SPLIT_RE.search(text)
    if m:
        neg_parts.append(text[m.end():].strip())
        text = text[:m.start()]
    for mm in MJ_NO_RE.finditer(text):
        neg_parts.append(mm.group(1).strip())
    text = MJ_NO_RE.sub("", text)
    text = MJ_PARAM_RE.sub("", text)
    return text.strip(), "\n".join(p for p in neg_parts if p)


# --------------------------------------------------------------------------- generate mode

# Each category: id, label, weight, regex, advice shown when it is missing.
GEN_CATEGORIES = [
    ("subject", "subject", 15, _rx(
        r"(?:in|about) (?:his|her|their) (?:early |mid-?|late )?(?:twenties|thirties|forties|fifties|sixties|seventies)",
        r"\d{2}s\b", r"\d{2}[- ]year[- ]old", r"year-old",
        r"hair", r"beard", r"stubble", r"freckles", r"glasses", r"earrings?", r"nose stud",
        r"skin(?: tone)?", r"(?:dark|light|olive|brown|pale|deep brown|medium-brown) skin",
        r"coat", r"shirt", r"t-shirt", r"sweater", r"blazer", r"jacket", r"hoodie", r"scarf", r"dress",
        r"jeans", r"trousers", r"turtleneck", r"blouse", r"knit", r"linen", r"wool", r"denim", r"cotton",
        r"sports bra", r"leggings", r"apron", r"uniform",
        r"mug", r"teapot", r"sneaker", r"handbag", r"bottle", r"vase", r"plant", r"dog", r"cat",
        r"half[- ]smile", r"smile", r"neutral expression", r"expression", r"squint\w*", r"laugh\w*", r"eyes closed",
    ), "say who or what, with two or three physical facts (age range, hair, clothing, expression); 'a woman' gives the model nothing to hold on to"),
    ("composition", "composition", 10, _rx(
        r"head[- ]and[- ]shoulders", r"waist[- ]up", r"three[- ]quarter", r"full[- ]body", r"close[- ]up",
        r"centred", r"centered", r"off[- ]cent(?:re|er)", r"left third", r"right third", r"rule of thirds",
        r"upper two thirds", r"lower third", r"landscape frame", r"portrait frame", r"square frame",
        r"vertical frame", r"horizontal frame", r"wide shot", r"medium shot", r"eye level", r"low angle",
        r"high angle", r"overhead", r"top[- ]down", r"straight[- ]on", r"profile", r"from behind",
        r"walking away", r"in the frame", r"out of frame", r"empty space", r"negative space", r"framing",
    ), "state the framing (head and shoulders, waist-up, full-body) and where the subject sits in the frame"),
    ("camera", "camera / lens", 12, _rx(
        r"\d{2,3}\s?mm(?: equivalent)?", r"f/?\d(?:\.\d)?", r"\blens\b", r"aperture",
        r"shallow depth of field", r"depth of field", r"bokeh", r"phone (?:main )?camera", r"front[- ]camera",
        r"selfie", r"point[- ]and[- ]shoot", r"medium format", r"35\s?mm film", r"iso \d+",
        r"wide[- ]angle", r"telephoto", r"macro", r"shot on", r"tilt[- ]shift", r"flagship phone",
    ), "name the camera and lens so perspective and depth of field are decided: '50 mm at f/2', '85 mm at f/2.8', 'phone main camera, 24 mm equivalent'"),
    ("light", "light", 15, _rx(
        r"window light", r"golden[- ]hour", r"overcast", r"softbox", r"key light", r"rim light", r"rim[- ]lit",
        r"rimming", r"gentle fill", r"fill light", r"backlight", r"backlit", r"side[- ]light\w*", r"raking light",
        r"candlelight", r"lamp", r"open shade", r"hard light", r"dappled", r"on[- ]camera flash", r"flash",
        r"north light", r"sunrise", r"sunset", r"dusk", r"low sun", r"bounce", r"catchlights?",
        r"daylight", r"morning light", r"evening light", r"afternoon light", r"midday sun", r"from camera left",
        r"from camera right", r"from the left", r"from the right", r"light from", r"underexposed", r"overexposed",
        r"natural light", r"soft light", r"studio light", r"fluorescent", r"tungsten", r"neon",
    ), "describe the light as a photographer would: source, direction, quality ('large soft window light from camera left with a gentle fill')"),
    ("palette", "palette / grade", 8, _rx(
        r"palette", r"colou?r grade", r"muted", r"warm tones", r"cool tones", r"teal", r"amber", r"desaturated",
        r"kodachrome", r"portra", r"film stock", r"lifted blacks", r"creamy highlights", r"true[- ]to[- ]life colou?rs?",
        r"true colou?rs", r"neutral daylight", r"no colou?r cast", r"monochrome", r"black[- ]and[- ]white",
        r"saturated", r"pastel", r"earth tones", r"warm and faded", r"faded", r"contrast", r"filmic", r"colou?r cast",
    ), "give the grade one clause: 'gentle filmic grade, creamy highlights, slightly lifted blacks' or 'true-to-life colour, no cast'"),
    ("texture", "texture", 15, _rx(
        r"skin texture", r"pores", r"freckles", r"film grain", r"\bgrain\b", r"fine lines", r"stubble",
        r"flyaway", r"individual strands", r"strands", r"weave", r"wrinkles", r"sweat", r"imperfections",
        r"blemish\w*", r"peach fuzz", r"texture", r"fabric", r"creases", r"scratches", r"noise", r"halation",
        r"lived[- ]in", r"worn", r"weathered", r"dust", r"crumbs", r"speckles?", r"speckled", r"pits", r"uneven\w*",
        r"scuffs?", r"fingerprints", r"patina", r"brushstrokes", r"knit", r"pilling", r"scratched",
    ), "ask for texture explicitly: 'natural skin texture with visible pores', 'fine film grain', 'fabric weave'; models smooth by default"),
    ("era", "era / medium", 10, _rx(
        r"\b(?:19|20)\d0s\b", r"\b19\d\d\b", r"\bfilm\b", r"kodachrome", r"polaroid", r"disposable camera",
        r"editorial", r"catalogue", r"catalog", r"snapshot", r"phone photo", r"documentary", r"street photograph\w*",
        r"instant film", r"slide photo", r"beauty[- ]editorial", r"lifestyle photograph", r"studio portrait",
        r"product photograph", r"listing photo", r"holiday photo", r"family photo", r"candid",
        r"photograph", r"photo\b", r"selfie", r"headshot", r"portrait of", r"still life",
    ), "anchor the medium and era: 'editorial lifestyle photograph', 'honest phone photo', '1974 Kodachrome slide'; without it the model picks 'render'"),
    ("negatives", "anti-plastic negatives", 15, _rx(
        r"no (?:retouched )?plastic(?: look| skin)?", r"not over[- ]processed", r"no retouch\w*", r"unretouched",
        r"no filters?", r"natural skin", r"no smoothing", r"no plastic smoothing", r"untouched", r"no airbrush\w*",
        r"no halos", r"no (?:visible )?seams", r"no oversharpen\w*", r"no hdr", r"avoid \w+", r"rather than a staged",
        r"not a render", r"no cgi", r"no beauty filter", r"real (?:skin|photograph|photo)",
    ), "close with what to avoid, phrased as a photographer would: 'natural skin texture, no retouched plastic look, not over-processed'"),
]

# Flags: id, label, severity (2 = red, 1 = yellow), regex, advice.
GEN_FLAGS = [
    ("superlatives", "quality words", 2, _rx(
        r"masterpiece", r"best quality", r"ultra[- ]?realistic", r"hyper[- ]?realistic", r"hyper[- ]?detailed",
        r"highly detailed", r"extremely detailed", r"intricate details?", r"\b8k\b", r"\b4k\b", r"\b16k\b", r"\buhd\b",
        r"ultra hd", r"award[- ]winning", r"trending on artstation", r"artstation", r"octane render",
        r"unreal engine", r"ray[- ]traced", r"ray tracing", r"\bcgi\b", r"3d render", r"photorealistic", r"photo-realistic",
    ), "quality words add no photographic fact and pull toward the CGI look the model was praised for; replace with one camera sentence and one light sentence"),
    ("plastic_skin", "plastic-skin triggers", 2, _rx(
        r"flawless(?: skin)?", r"perfect skin", r"smooth skin", r"silky skin", r"porcelain skin", r"glowing skin",
        r"glass skin", r"airbrushed", r"retouched", r"dewy skin", r"poreless", r"symmetrical face", r"perfect symmetry",
        r"perfectly symmetrical", r"doll[- ]like", r"radiant skin", r"luminous skin", r"baby[- ]smooth",
    ), "these words are the plastic look; ask for the opposite: 'natural skin texture with visible pores, slight asymmetry, unretouched'"),
    ("vague_light", "vague light", 1, _rx(
        r"perfect lighting", r"even lighting", r"studio lighting", r"dramatic lighting", r"cinematic lighting",
        r"volumetric lighting", r"god rays", r"beautiful lighting", r"professional lighting", r"soft glow",
        r"lens flare", r"glowing",
    ), "'dramatic' or 'studio' says nothing about direction or size; name the source and where it sits"),
    ("vague_adjectives", "empty adjectives", 1, _rx(
        r"beautiful", r"pretty", r"attractive", r"handsome", r"gorgeous", r"stunning", r"breathtaking", r"cute",
        r"aesthetic", r"\bvibes?\b", r"\bepic\b", r"amazing", r"perfect", r"elegant", r"sexy",
    ), "an adjective the camera cannot execute; swap it for a visible fact (what the hair does, what the shirt is made of)"),
    ("boilerplate_negatives", "boilerplate negative list", 1, _rx(
        r"bad anatomy", r"extra fingers", r"extra limbs", r"deformed", r"mutated", r"\bugly\b", r"disfigured",
        r"low quality", r"worst quality", r"jpeg artifacts", r"watermark", r"signature", r"text, logo", r"bad hands",
        r"cropped", r"out of frame, ", r"poorly drawn",
    ), "SD1.5-era negative soup; Flux and Nano Banana ignore it and it spends your prompt budget. Keep only negatives that name a look you have actually seen"),
    ("render_words", "render vocabulary", 1, _rx(
        r"render\b", r"rendered", r"3d\b", r"blender", r"unity", r"digital art", r"concept art", r"illustration",
        r"anime", r"painting", r"artwork",
    ), "fine if you want an illustration; for a photo these words move the result off the photographic manifold"),
]

EDIT_VERB_RE = re.compile(
    r"(?i)^\s*(?:please\s+)?(?:change|remove|replace|turn (?:this|that|the|my|our|her|him|it)|restore|enhance|sharpen|unblur|upscale|"
    r"make (?:this|that|the|my|our|it|her|him)|add|swap|put|convert (?:this|that|the|my)|fix|erase|recolou?r|retouch|clean up|"
    r"straighten|extend|expand|crop|relight|colou?rize|repair|keep)\b"
)

EDIT_HINT_RE = _rx(r"this (?:photo|image|picture|selfie|portrait|photograph)", r"exactly as (?:they are|it is)",
                   r"do not change", r"keep (?:the|her|his|their|everything)")

# --------------------------------------------------------------------------- edit mode

EDIT_CATEGORIES = [
    ("change", "one named change", 15, EDIT_VERB_RE,
     "open with the verb and the single thing that changes: 'Remove the stranger ...', 'Change her hairstyle to ...'"),
    ("preserve", "identity lock", 25, _rx(
        r"keep (?:the |her |his |their )?(?:[\w' ,-]+?)(?:exactly as (?:they are|it is|she is|he is))",
        r"exactly as (?:they are|it is)", r"keep (?:her|his|their) (?:face|identity|features)",
        r"same person", r"preserve (?:the )?(?:identity|face|features)", r"identity exactly", r"unchanged",
    ), "list what must survive and say 'exactly as they are': face, skin tone, hair edges, expression, clothes, light"),
    ("framing", "framing lock", 20, _rx(
        r"do not change the framing", r"do not crop", r"same zoom", r"same (?:crop|framing|position)",
        r"not (?:crop|zoom in|recompose)", r"no recompos\w*", r"framing, crop, camera angle", r"full original frame",
    ), "lock the frame: 'Output the full original frame at the same zoom; do not crop, zoom in or recompose'"),
    ("seams", "no seams / halos", 15, _rx(
        r"no (?:smudges|seams|halos|visible seams)", r"repeated textures", r"nothing looks patched", r"no patch\w*",
        r"no (?:over)?sharpening halos", r"fill (?:the|that) (?:space|area|gap)", r"matching (?:sand|sea|sky|wall|floor|brick|table|lake|marble|background|texture)",
    ), "for removals say what fills the hole ('matching sand, sea and sky') and forbid 'smudges, repeated textures, halos or visible seams'"),
    ("realism", "realism clause", 15, _rx(
        r"untouched real photograph", r"real photograph", r"same photo taken with a (?:much )?better camera",
        r"not over[- ]processed", r"no plastic skin", r"natural skin texture", r"no plastic smoothing",
        r"look(?:s)? real", r"salon[- ]fresh", r"believable",
    ), "say the result must read as an untouched real photograph, natural and not over-processed, no plastic skin"),
    ("scope", "scope limit", 10, _rx(
        r"anything not mentioned", r"nothing else", r"only (?:the|that|this)", r"and everything else",
        r"everything else exactly", r"do not (?:add|alter|modify) anything",
    ), "close the door on side effects: 'Do not change ... or anything not mentioned'"),
]

EDIT_FLAGS = [
    ("regen_words", "generation words in an edit", 2, _rx(
        r"reimagine", r"completely new", r"different person", r"from scratch", r"new face", r"generate a",
        r"masterpiece", r"ultra[- ]?realistic", r"\b8k\b", r"\b4k\b", r"best quality", r"photorealistic",
    ), "an edit prompt that asks to reimagine will drift identity; describe only the delta"),
    ("plastic_skin", "plastic-skin triggers", 2, GEN_FLAGS[1][3],
     "smoothing words in an edit produce the waxy 'enhanced' look; ask for 'natural skin texture, no plastic smoothing'"),
    ("vague_adjectives", "empty adjectives", 1, GEN_FLAGS[3][3],
     "swap for a visible fact about the change"),
]


# --------------------------------------------------------------------------- scoring

def detect_mode(text):
    if EDIT_VERB_RE.search(text):
        return "edit"
    if EDIT_HINT_RE.search(text) and word_count(text) < 120:
        return "edit"
    return "generate"


def repeated_phrases(text, n=4):
    """3-word phrases that occur more than once (ignoring case and punctuation)."""
    words = [w.lower().strip(".,;:") for w in WORD_RE.findall(text)]
    seen, dupes = {}, []
    for i in range(len(words) - n + 1):
        g = " ".join(words[i:i + n])
        seen[g] = seen.get(g, 0) + 1
        if seen[g] == 2:
            dupes.append(g)
    return dupes[:3]


def tag_soup(text):
    """True when the prompt is mostly comma-separated fragments of 1-2 words."""
    parts = [p.strip() for p in re.split(r"[,\n]", text) if p.strip()]
    if len(parts) < 8:
        return False
    short = sum(1 for p in parts if word_count(p) <= 2)
    return short / len(parts) >= 0.6


def lint(text, mode="auto"):
    full = text.strip()
    text, negative = split_negative(full)
    if mode == "auto":
        mode = detect_mode(text)
    cats = GEN_CATEGORIES if mode == "generate" else EDIT_CATEGORIES
    flags = GEN_FLAGS if mode == "generate" else EDIT_FLAGS
    words = word_count(full)

    coverage, score = [], 0
    for cid, label, weight, rx, advice in cats:
        matches = _find(rx, text)
        if cid == "negatives" and negative:
            # an explicit negative prompt counts, but only if it names a look rather than boilerplate
            named = [w.strip() for w in re.split(r"[,\n]", negative) if w.strip()]
            matches = ["negative: " + ", ".join(named[:4])] + matches
        ok = bool(matches)
        if ok:
            score += weight
        coverage.append({"id": cid, "label": label, "weight": weight, "ok": ok,
                         "matches": matches[:4], "advice": None if ok else advice})

    hits = []
    for fid, label, sev, rx, advice in flags:
        # boilerplate negatives live in the negative part; every other flag is about the positive prompt
        scope = negative if fid == "boilerplate_negatives" else text
        matches = _find(rx, scope, skip_negated=True)
        if matches:
            penalty = min(len(matches), 3) * (8 if sev == 2 else 3)
            score -= penalty
            hits.append({"id": fid, "label": label, "severity": sev, "matches": matches,
                         "penalty": penalty, "advice": advice})

    # structural flags (both modes)
    if words < 15:
        score -= 10
        hits.append({"id": "too_short", "label": "too short", "severity": 2, "matches": ["%d words" % words],
                     "penalty": 10, "advice": "under 15 words the model fills every gap with its default look; a working brief is usually 40-120 words"})
    elif words > 180:
        score -= 5
        hits.append({"id": "too_long", "label": "long prompt", "severity": 1, "matches": ["%d words" % words],
                     "penalty": 5, "advice": "over ~180 words later clauses lose weight (SDXL's text encoder truncates at 77 tokens); move the least visual sentence out"})
    dupes = repeated_phrases(text)
    if dupes:
        score -= 3
        hits.append({"id": "repetition", "label": "repeated phrase", "severity": 1, "matches": dupes,
                     "penalty": 3, "advice": "said twice does not weigh twice; keep one"})
    if mode == "generate" and tag_soup(text):
        score -= 8
        hits.append({"id": "tag_soup", "label": "tag soup", "severity": 2, "matches": ["comma-separated fragments"],
                     "penalty": 8, "advice": "write sentences a photographer could act on; comma tags were an SD1.5 habit and read as 'render' to current models"})

    score = max(0, min(100, score))
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D" if score >= 30 else "F"
    return {"version": __version__, "mode": mode, "words": words, "score": score, "grade": grade,
            "coverage": coverage, "flags": hits}


# --------------------------------------------------------------------------- output

def _fmt_matches(ms):
    return ", ".join('"%s"' % m for m in ms)


def render_report(result, name):
    r = result
    lines = []
    lines.append("no-plastic lint  %s" % name)
    lines.append("mode: %-9s words: %-5d score: %d/100  (%s)" % (r["mode"], r["words"], r["score"], r["grade"]))
    lines.append("")
    lines.append("coverage")
    for c in r["coverage"]:
        if c["ok"]:
            lines.append("  [x] %-24s %s" % (c["label"], _fmt_matches(c["matches"])))
        else:
            lines.append("  [ ] %-24s %s" % (c["label"], c["advice"]))
    if r["flags"]:
        lines.append("")
        lines.append("flags")
        for f in r["flags"]:
            mark = "!!" if f["severity"] == 2 else "! "
            lines.append("  %s %-23s %s  (-%d)" % (mark, f["label"], _fmt_matches(f["matches"]), f["penalty"]))
            lines.append("     %s" % f["advice"])
    lines.append("")
    missing = [c["label"] for c in r["coverage"] if not c["ok"]]
    if r["score"] >= 85 and not missing:
        lines.append("next: run one pilot image and review it against references/checklist.md before any batch")
    elif missing:
        lines.append("next: add %s; then re-lint and pilot one image" % ", ".join(missing[:4]))
    else:
        lines.append("next: remove the flagged words, re-lint, then pilot one image")
    return "\n".join(lines) + "\n"


BRIEF_FIELDS = [
    ("subject", "Subject"), ("composition", "Composition"), ("camera", "Camera / lens"), ("light", "Light"),
    ("palette", "Palette / grade"), ("texture", "Texture"), ("era", "Era / medium"), ("negatives", "Negatives"),
]


def render_brief(result, text):
    """A brief skeleton: found phrases per field, '?' where the prompt is silent."""
    if result["mode"] != "generate":
        return "brief skeleton is for generate prompts; this one was detected as an edit instruction\n"
    by_id = {c["id"]: c for c in result["coverage"]}
    lines = ["# Photographic brief (fill every '?')", ""]
    for fid, label in BRIEF_FIELDS:
        c = by_id[fid]
        val = "; ".join(c["matches"]) if c["ok"] else "?  <- " + c["advice"]
        lines.append("%-16s %s" % (label + ":", val))
    lines.append("")
    lines.append("Rewrite as 3-5 sentences in this order: subject and action; framing; camera and light; palette, texture and era; negatives.")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- CLI

def read_input(path):
    if path == "-":
        return sys.stdin.read(), "stdin"
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read(), path


def main(argv=None):
    ap = argparse.ArgumentParser(prog="lint_prompt.py", description="Score an image prompt against the no-plastic checklist.")
    ap.add_argument("files", nargs="*", help="prompt text files ('-' for stdin); default: stdin")
    ap.add_argument("--mode", choices=["auto", "generate", "edit"], default="auto", help="force a mode (default: auto-detect)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--brief", action="store_true", help="print a brief skeleton with the found phrases and the gaps")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any prompt scores below --min-score")
    ap.add_argument("--min-score", type=int, default=70, help="threshold for --strict (default 70)")
    ap.add_argument("--version", action="version", version="no-plastic lint " + __version__)
    a = ap.parse_args(argv)

    files = a.files or ["-"]
    results, worst = [], 100
    for i, path in enumerate(files):
        try:
            text, name = read_input(path)
        except OSError as e:
            print("error: %s" % e, file=sys.stderr)
            return 2
        if not text.strip():
            print("error: %s is empty" % name, file=sys.stderr)
            return 2
        res = lint(text, a.mode)
        res["file"] = name
        results.append(res)
        worst = min(worst, res["score"])
        if a.json:
            continue
        if i:
            sys.stdout.write("\n")
        sys.stdout.write(render_brief(res, text) if a.brief else render_report(res, name))
    if a.json:
        out = results[0] if len(results) == 1 else results
        sys.stdout.write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    if a.strict and worst < a.min_score:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
