import test from "node:test";
import assert from "node:assert/strict";
import { validateGameText, validateTextFiles } from "../src/ingestion-linter.js";

test("accepts correctly formatted combat tokens and resource costs", () => {
  assert.deepEqual(validateGameText("[MELEE] then spend 3 SP or 1-3 SP."), {
    valid: true,
    errors: [],
  });
});

test("flags an unbracketed combat token", () => {
  const result = validateGameText("Use MELEE now.");
  assert.equal(result.valid, false);
  assert.equal(result.errors[0].code, "MALFORMED_COMBAT_TOKEN");
  assert.equal(result.errors[0].token, "MELEE");
  assert.equal(result.errors[0].line, 1);
});

test("flags lowercase and incomplete combat-token brackets", () => {
  const result = validateGameText("[melee]\n[MELEE\nMELEE]");
  assert.equal(result.errors.length, 3);
  assert.ok(result.errors.every((error) => error.code === "MALFORMED_COMBAT_TOKEN"));
});

test("flags a likely misspelling of a bracketed combat token", () => {
  const result = validateGameText("Resolve [MELE].");
  assert.equal(result.valid, false);
  assert.ok(result.errors.some((error) => error.code === "POSSIBLE_COMBAT_TOKEN_TYPO"));
});

test("flags lowercase resource tokens", () => {
  const result = validateGameText("Spend 2 sp.");
  assert.ok(result.errors.some((error) =>
    error.code === "MALFORMED_RESOURCE_TOKEN" && error.token === "sp"
  ));
});

test("flags numeric amounts glued to SP", () => {
  const result = validateGameText("Pay 3SP, then 1SP.");
  assert.deepEqual(result.errors.map((error) => error.token), ["3SP", "1SP"]);
  assert.ok(result.errors.every((error) => error.code === "MALFORMED_RESOURCE_TOKEN"));
});

test("does not mistake ordinary words containing sp for resource tokens", () => {
  assert.deepEqual(
    validateGameText("The spell was spent in a spacious chamber."),
    { valid: true, errors: [] },
  );
});

test("reports line, column, and source-line context", () => {
  const result = validateGameText("Valid line\nPay 3SP.");
  assert.equal(result.errors[0].line, 2);
  assert.equal(result.errors[0].column, 5);
  assert.equal(result.errors[0].context, "Pay 3SP.");
});

test("validates multiple named text files independently", () => {
  const result = validateTextFiles({
    "good.txt": "[MELEE] costs 2 SP.",
    "bad.txt": "Pay 2SP.",
  });
  assert.equal(result["good.txt"].valid, true);
  assert.equal(result["bad.txt"].valid, false);
  assert.equal(result["bad.txt"].errors[0].token, "2SP");
});

test("allows the combat-token vocabulary to be configured", () => {
  assert.deepEqual(
    validateGameText("[MAGIC] and [MELEE]", { combatTokens: ["MAGIC", "MELEE"] }),
    { valid: true, errors: [] },
  );
});

test("rejects non-string input clearly", () => {
  assert.throws(() => validateGameText(null), TypeError);
});
