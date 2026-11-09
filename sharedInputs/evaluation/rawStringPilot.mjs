import assert from "node:assert/strict";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const root = resolve(process.argv[2]);
const modulePath = pathToFileURL(resolve(root, "web/src/lib/suggestion-expression.ts"));
const { parseSuggestionExpression: parse, readStringList } = await import(modulePath.href);
const outcomes = [];
function check(id, group, body) {
  try { body(); outcomes.push({ id, group, passed: true }); }
  catch (error) { outcomes.push({ id, group, passed: false, error: String(error.message) }); }
}
function firstValue(source) {
  const expression = parse(source);
  assert.equal(expression?.kind, "atom");
  assert.equal(expression.tokens.length, 3);
  assert.equal(expression.tokens[1].text, "in");
  assert.equal(expression.tokens[2].text, "tags");
  return expression.tokens[0].value;
}
for (const [id, source, expected] of [
  ["rawLowerDouble", 'r"work" in tags', "work"],
  ["rawUpperSingle", "R'work/project' in tags", "work/project"],
  ["rawLowerSingle", "r'release' in tags", "release"],
  ["rawUpperDouble", 'R"personal" in tags', "personal"],
  ["rawBackslashN", String.raw`r"work\nproject" in tags`, String.raw`work\nproject`],
  ["rawUnicodeEscape", String.raw`R"\u5de5\u4f5c" in tags`, String.raw`\u5de5\u4f5c`],
  ["rawUnknownEscape", String.raw`r'work\q' in tags`, String.raw`work\q`],
  ["rawOperators", 'r"work&&release||personal//literal" in tags', "work&&release||personal//literal"],
]) check(id, "acceptance", () => assert.equal(firstValue(source), expected));
check("mixedStringList", "acceptance", () => {
  const expression = parse(`tag in [r"work", R'release', "ordinary",]`);
  assert.equal(expression?.kind, "atom");
  assert.deepEqual(readStringList(expression.tokens.slice(2)), ["work", "release", "ordinary"]);
});
check("rawBooleanStructure", "acceptance", () => {
  const expression = parse(`!(r"work" in tags) && (R'personal' in tags || "release" in tags)`);
  assert.equal(expression?.kind, "and");
  assert.equal(expression.left.kind, "not");
  assert.equal(expression.left.child.tokens[0].value, "work");
  assert.equal(expression.right.kind, "or");
  assert.equal(expression.right.left.tokens[0].value, "personal");
});
for (const [id, source, expected] of [
  ["normalDouble", '"work" in tags', "work"],
  ["normalSingle", "'work/project' in tags", "work/project"],
  ["normalDecodedUnicode", String.raw`"\u5de5\u4f5c" in tags`, "工作"],
  ["normalDecodedNewline", String.raw`"work\nproject" in tags`, "work\nproject"],
]) check(id, "regression", () => assert.equal(firstValue(source), expected));
for (const [id, source] of [
  ["unclosedRawDouble", 'r"work in tags'],
  ["unclosedRawSingle", "R'work in tags"],
  ["danglingAnd", '"work" in tags &&'],
  ["unclosedParenthesis", '("work" in tags'],
  ["mismatchedBracket", '"work" in tags && x[)'],
  ["unsupportedToken", '"work" in tags && @'],
]) check(id, "regression", () => assert.equal(parse(source), undefined));
check("normalComment", "regression", () => assert.equal(firstValue('"work" in tags // ignored && syntax'), "work"));
check("ordinaryList", "regression", () => {
  const expression = parse('tag in ["work", "release",]');
  assert.deepEqual(readStringList(expression.tokens.slice(2)), ["work", "release"]);
});
check("nonLiteralList", "regression", () => {
  const expression = parse('tag in ["work", variable]');
  assert.equal(readStringList(expression.tokens.slice(2)), undefined);
});
console.log(JSON.stringify({ outcomes, passed: outcomes.every((item) => item.passed) }, null, 2));
process.exitCode = outcomes.every((item) => item.passed) ? 0 : 1;
