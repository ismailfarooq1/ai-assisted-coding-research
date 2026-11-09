#!/usr/bin/env python3
"""Materialize researcher-defined task specifications and private evaluator controls."""
import json
from pathlib import Path
import difflib

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / 'sharedInputs/measuredStudy01'
BASE = ROOT / 'experiments/existingWorkflow/memos'

TASKS = [
    ('colorAlpha', 'color.ts', 'Add optional alpha to colorToHex. With alpha omitted or undefined keep the current six-digit RGB output. With alpha explicitly provided append two lowercase hex digits: clamp finite alpha to [0,1], round alpha*255; non-finite alpha defaults to 1. Explicit alpha=1 therefore appends ff. Preserve existing RGB clamping, rounding, missing-color behavior and call compatibility.', '''import { colorToHex } from "@/lib/color";
it("supports explicit alpha and preserves RGB behavior", () => {
  const convert = colorToHex as (value?: {red?: number; green?: number; blue?: number; alpha?: number}) => string | undefined;
  expect(convert({red: 1, green: 0.5, blue: 0, alpha: 0.5})).toBe("#ff800080");
  expect(convert({alpha: 0})).toBe("#00000000");
  expect(convert({alpha: 1})).toBe("#000000ff");
  for (const alpha of [Infinity, -Infinity, NaN, 2]) expect(convert({alpha})).toBe("#000000ff");
  expect(convert({alpha: -1})).toBe("#00000000");
  expect(convert({red: NaN, green: -1, blue: 2})).toBe("#0000ff");
  expect(convert({alpha: undefined})).toBe("#000000");
  expect(convert()).toBeUndefined();
});
'''),
    ('legacyReleaseTag', 'release-version.ts', 'Extend getReleaseTag to accept an already-prefixed lowercase legacy tag v0.x.y[-rc.K], returning it unchanged. Use the existing legacy numeric grammar (no leading zeroes except a single zero; positive rc number). Preserve bare legacy conversion and bare calendar releases. Continue rejecting prefixed calendar releases, uppercase V, double v, whitespace and malformed versions.', '''import { getReleaseTag } from "@/lib/release-version";
it("normalizes historical tags idempotently without broadening calendar syntax", () => {
  for (const value of ["v0.1.0", "v0.0.0", "v0.25.9-rc.2"]) expect(getReleaseTag(value)).toBe(value);
  expect(getReleaseTag("0.25.9-rc.2")).toBe("v0.25.9-rc.2");
  expect(getReleaseTag("26.09.0")).toBe("26.09.0");
  for (const value of ["v26.09.0", "vv0.1.0", "V0.1.0", " v0.1.0", "v0.1.0 ", "v0.01.0", "v0.1.00", "v0.1.0-rc.0", "v0.1.0-rc.01", "v1.2.3"]) expect(getReleaseTag(value)).toBeUndefined();
});
'''),
    ('unicodeSpaceTitles', 'space-display.ts', 'Make getDuplicateSpaceTitles compare titles using Unicode NFC normalization. Return all original spellings whose normalized group occurs at least twice, retaining first-occurrence order of original spellings. Do not trim or case-fold, do not mutate inputs, and keep other exports unchanged. Exact duplicates still count; an original spelling occurs at most once in the returned set.', '''import { getDuplicateSpaceTitles } from "@/lib/space-display";
it("groups NFC-equivalent titles and retains original spellings and order", () => {
  const input = Object.freeze([Object.freeze({title: "cafe\\u0301"}), Object.freeze({title: "x"}), Object.freeze({title: "café"}), Object.freeze({title: "x"})]);
  expect([...getDuplicateSpaceTitles(input)]).toEqual(["cafe\\u0301", "x", "café"]);
  expect([...getDuplicateSpaceTitles([{title:"A"},{title:"a"},{title:" A"}])]).toEqual([]);
  expect([...getDuplicateSpaceTitles([{title:"Product"},{title:"research"},{title:"Product"},{title:"product"}])]).toEqual(["Product"]);
  expect([...getDuplicateSpaceTitles([])]).toEqual([]);
  expect(input[0].title).toBe("cafe\\u0301");
});
'''),
    ('retryMetadata', 'error.ts', 'Harden only the client-side getRetryAfterSeconds metadata parser. Accept canonical positive base-10 safe-integer strings matching [1-9][0-9]* whose numeric value is <= Number.MAX_SAFE_INTEGER. Reject zero, signs, leading zeros, whitespace, fractions, exponents, junk and unsafe integers. Preserve RATE_LIMITED reason gating and existing error messages. This task does not change server-side rate limiting, authentication or token enforcement.', '''import { BinaryWriter } from "@bufbuild/protobuf/wire";
import { Code, ConnectError } from "@connectrpc/connect";
import { getRetryAfterSeconds, getErrorMessage } from "@/lib/error";
const makeError = (value: string, reason = "RATE_LIMITED") => {
  const writer = new BinaryWriter();
  writer.tag(1, 2).string(reason); writer.tag(2, 2).string("memos.api");
  const entry = new BinaryWriter(); entry.tag(1, 2).string("retry_after_seconds"); entry.tag(2, 2).string(value);
  writer.tag(3, 2).bytes(entry.finish());
  const error = new ConnectError("original", Code.ResourceExhausted);
  error.details.push({type: "google.rpc.ErrorInfo", value: writer.finish()}); return error;
};
it("strictly parses positive safe-integer delay metadata", () => {
  for (const value of ["1", "42", "9007199254740991"]) expect(getRetryAfterSeconds(makeError(value))).toBe(Number(value));
  for (const value of ["", "0", "-1", "+1", "01", "1.5", "1e3", "42junk", " 42", "42 ", "9007199254740992", "Infinity"]) expect(getRetryAfterSeconds(makeError(value))).toBeUndefined();
  expect(getRetryAfterSeconds(makeError("42", "OTHER"))).toBeUndefined();
  expect(getRetryAfterSeconds(new Error("x"))).toBeUndefined();
  expect(getErrorMessage(makeError("42"))).toBe("Too many requests. Try again in 42s.");
  expect(getErrorMessage(makeError("42junk"))).toBe("original");
});
'''),
    ('memoViewNames', 'memo-views.ts', 'Restrict getMemoViewId extraction to exact resource names users/<nonempty>/views/<nonempty>, with exactly four slash-separated components. Return the final component for valid names; return the input unchanged for malformed names, different collection names, empty components, bare identifiers or additional components. Do not introduce additional character restrictions within nonempty components, and preserve all other exports.', '''import { getMemoViewId, isCalendarRoute } from "@/lib/memo-views";
it("extracts only exact user-view resource names", () => {
  for (const [name, value] of [["users/steven/views/work", "work"], ["users/a b/views/x y", "x y"]]) expect(getMemoViewId(name)).toBe(value);
  for (const name of ["orgs/a/views/b", "users/a/memos/b", "users//views/x", "users/a/views/", "users/a/views/x/y", "/users/a/views/x", "work", "", "Users/a/views/b"]) expect(getMemoViewId(name)).toBe(name);
  expect(isCalendarRoute("/calendar/2026/11")).toBe(true);
});
'''),
    ('safeTagCounts', 'tag.ts', 'Make mergeTagCounts ignore counts that are not nonnegative safe integers (including negative values, fractions, nonfinite numbers, unsafe integers and runtime non-number values). Retain zero-valued tags. Saturate sums at Number.MAX_SAFE_INTEGER. Preserve own-key-only enumeration, null-prototype output, safe treatment of __proto__/constructor, undefined inputs and input immutability. Preserve all other exports.', '''import { mergeTagCounts } from "@/lib/tag";
it("merges safe counts without overflow or inherited keys", () => {
  const source = Object.freeze({a: 3, zero: 0, negative: -1, fraction: 0.5, nan: NaN, infinite: Infinity, unsafe: Number.MAX_SAFE_INTEGER + 1, text: "3"} as unknown as Record<string, number>);
  const result = mergeTagCounts(undefined, source, {a: 4, huge: Number.MAX_SAFE_INTEGER}, {huge: 1});
  expect(Object.getPrototypeOf(result)).toBeNull();
  expect({...result}).toEqual({a: 7, zero: 0, huge: Number.MAX_SAFE_INTEGER});
  expect(source.a).toBe(3);
  const dangerous = JSON.parse('{"__proto__":2,"constructor":3}') as Record<string, number>;
  const special = mergeTagCounts(dangerous, dangerous);
  expect(Object.hasOwn(special, "__proto__")).toBe(true); expect(special.__proto__).toBe(4); expect(special.constructor).toBe(6);
  const inherited = Object.assign(Object.create({inherited: 7}), {own: 1});
  expect({...mergeTagCounts(inherited)}).toEqual({own: 1});
});
'''),
]

def positive_source(task, text):
    if task == 'colorAlpha':
        text = text.replace('blue?: number }', 'blue?: number; alpha?: number }')
        return text.replace('return `#${r}${g}${b}`;', 'const alpha = color.alpha === undefined ? "" : Math.round((Number.isFinite(color.alpha) ? Math.max(0, Math.min(1, color.alpha)) : 1) * 255).toString(16).padStart(2, "0");\n  return `#${r}${g}${b}${alpha}`;')
    if task == 'legacyReleaseTag':
        return text.replace('if (!isReleaseVersion(version))', 'if (version.startsWith("v0.") && isReleaseVersion(version.slice(1))) return version;\n  if (!isReleaseVersion(version))')
    if task == 'unicodeSpaceTitles':
        start = text.index('  const seen ='); end = text.index('\n  return duplicates;', start)
        return text[:start] + '''  const counts = new Map<string, number>();
  for (const { title } of spaces) counts.set(title.normalize("NFC"), (counts.get(title.normalize("NFC")) ?? 0) + 1);
  const duplicates = new Set<string>();
  for (const { title } of spaces) if ((counts.get(title.normalize("NFC")) ?? 0) > 1) duplicates.add(title);
''' + text[end:]
    if task == 'retryMetadata':
        return text.replace('const seconds = Number.parseInt(info.metadata.retry_after_seconds ?? "", 10);\n  return Number.isFinite(seconds) && seconds > 0 ? seconds : undefined;', 'const raw = info.metadata.retry_after_seconds ?? "";\n  if (!/^[1-9][0-9]*$/.test(raw)) return undefined;\n  const seconds = Number(raw);\n  return Number.isSafeInteger(seconds) && seconds > 0 ? seconds : undefined;')
    if task == 'memoViewNames':
        return text.replace('parts.length === 4 ?', 'parts.length === 4 && parts[0] === "users" && parts[1] !== "" && parts[2] === "views" && parts[3] !== "" ?')
    if task == 'safeTagCounts':
        return text.replace('for (const [tag, count] of Object.entries(source ?? {})) result[tag] = (result[tag] ?? 0) + count;', '''for (const [tag, count] of Object.entries(source ?? {})) {
      if (typeof count !== "number" || !Number.isSafeInteger(count) || count < 0) continue;
      result[tag] = Math.min(Number.MAX_SAFE_INTEGER, (result[tag] ?? 0) + count);
    }''')
    raise ValueError(task)

def main():
    (INPUT / 'tasks').mkdir(exist_ok=True)
    (INPUT / 'evaluation').mkdir(exist_ok=True)
    index = []
    for task, source, spec, test in TASKS:
        relative = 'web/src/lib/' + source
        data = {'id': task, 'productionFile': relative, 'taskFile': f'tasks/{task}.md', 'acceptanceFile': f'evaluation/{task}.test.ts', 'positiveControl': f'evaluation/{task}.patch'}
        files = {
            INPUT / data['taskFile']: f'# {task}\n\n{spec}\n\nOnly change `{relative}` and relevant files in `web/tests/`. Add or update regression tests. Preserve unrelated behavior. Follow native project guidance and run appropriate checks. Do not use external solutions or access other runs. Do not change dependencies, generated files, test configuration or Git history. Report checks actually completed and any limitations.\n',
            INPUT / data['acceptanceFile']: 'import { expect, it } from "vitest";\n' + test,
        }
        original = (BASE / relative).read_text()
        changed = positive_source(task, original)
        assert changed != original
        files[INPUT / data['positiveControl']] = ''.join(difflib.unified_diff(original.splitlines(True), changed.splitlines(True), fromfile='a/' + relative, tofile='b/' + relative))
        for path, contents in files.items():
            if path.exists():
                raise RuntimeError(f'Refusing to overwrite {path}')
            path.write_text(contents)
        index.append(data)
    (INPUT / 'taskIndex.json').write_text(json.dumps(index, indent=2) + '\n')

if __name__ == '__main__':
    main()
