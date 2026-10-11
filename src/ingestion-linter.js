/**
 * Strict validator for Middara game-text tokens.
 *
 * This module reports issues without modifying source text. The combat-token
 * vocabulary is intentionally explicit/configurable so ordinary game prose is
 * not mistaken for a token the linter does not know about.
 */

const DEFAULT_COMBAT_TOKENS = ["MELEE", "RANGED"];

function levenshteinDistance(a, b) {
  const row = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i += 1) {
    let diagonal = row[0];
    row[0] = i;
    for (let j = 1; j <= b.length; j += 1) {
      const above = row[j];
      row[j] = Math.min(
        row[j] + 1,
        row[j - 1] + 1,
        diagonal + (a[i - 1] === b[j - 1] ? 0 : 1),
      );
      diagonal = above;
    }
  }
  return row[b.length];
}

function locationAt(text, offset) {
  const lines = text.slice(0, offset).split("\n");
  return { line: lines.length, column: lines[lines.length - 1].length + 1 };
}

function makeError(text, offset, token, code, message) {
  const location = locationAt(text, offset);
  return {
    code,
    token,
    message,
    ...location,
    context: text.split("\n")[location.line - 1].trim(),
  };
}

/**
 * Validate a string of game text.
 * @param {string} text Source text to inspect.
 * @param {{ combatTokens?: string[] }} options Known combat stance/action tokens.
 * @returns {{ valid: boolean, errors: Array<object> }}
 */
export function validateGameText(text, options = {}) {
  if (typeof text !== "string") {
    throw new TypeError("validateGameText expects a string");
  }

  const combatTokens = (options.combatTokens ?? DEFAULT_COMBAT_TOKENS)
    .map((token) => token.toUpperCase());
  const errors = [];

  // Check known combat tokens whether bracketed, unbracketed, or mis-cased.
  for (const token of combatTokens) {
    const escaped = token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const tokenPattern = new RegExp(`\\[?\\b${escaped}\\b\\]?`, "gi");
    for (const match of text.matchAll(tokenPattern)) {
      if (match[0] !== `[${token}]`) {
        errors.push(makeError(
          text,
          match.index,
          match[0],
          "MALFORMED_COMBAT_TOKEN",
          `Combat token must be exactly [${token}] (uppercase and enclosed in square brackets).`,
        ));
      }
    }
  }

  // Flag likely misspellings in square-bracket token syntax, e.g. [MEELE].
  const bracketTokens = /\[([A-Za-z]+)\]?|\b([A-Za-z]+)\]/g;
  for (const match of text.matchAll(bracketTokens)) {
    const candidate = (match[1] ?? match[2] ?? "").toUpperCase();
    if (!candidate || combatTokens.includes(candidate)) continue;
    const closest = combatTokens.find((known) =>
      levenshteinDistance(candidate, known) === 1
    );
    if (closest) {
      errors.push(makeError(
        text,
        match.index,
        match[0],
        "POSSIBLE_COMBAT_TOKEN_TYPO",
        `Possible typo of [${closest}]; found "${match[0]}".`,
      ));
    }
  }

  // SP must be uppercase and separated from any preceding numeric amount.
  const resourcePattern = /(?<![A-Za-z])(?:\d+)?sp(?![A-Za-z])/gi;
  for (const match of text.matchAll(resourcePattern)) {
    const found = match[0];
    const hasNumber = /^\d/.test(found);
    if (found !== "SP" || hasNumber) {
      errors.push(makeError(
        text,
        match.index,
        found,
        "MALFORMED_RESOURCE_TOKEN",
        hasNumber
          ? 'Numeric resource amounts must be separated from "SP" by a space (for example, "3 SP").'
          : 'Resource token must be uppercase "SP".',
      ));
    }
  }

  errors.sort((a, b) => a.line - b.line || a.column - b.column);
  return { valid: errors.length === 0, errors };
}

/**
 * Validate multiple named text files without changing their contents.
 * @param {Record<string, string>} files File path to source text.
 * @param {object} options Options forwarded to validateGameText.
 */
export function validateTextFiles(files, options = {}) {
  return Object.fromEntries(
    Object.entries(files).map(([path, text]) => [path, validateGameText(text, options)]),
  );
}

export { DEFAULT_COMBAT_TOKENS };
