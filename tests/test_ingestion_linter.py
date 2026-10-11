"""Unit tests for the Middara ingestion linter."""

import unittest

from src.ingestion_linter import validate_game_text, validate_text_files


class ValidateGameTextTests(unittest.TestCase):
    def test_accepts_correct_combat_tokens_and_resource_costs(self):
        self.assertEqual(
            validate_game_text("[MELEE] then spend 3 SP or 1-3 SP."),
            {"valid": True, "errors": []},
        )

    def test_flags_unbracketed_combat_token(self):
        result = validate_game_text("Use MELEE now.")
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["code"], "MALFORMED_COMBAT_TOKEN")
        self.assertEqual(result["errors"][0]["token"], "MELEE")
        self.assertEqual(result["errors"][0]["line"], 1)

    def test_flags_lowercase_and_incomplete_combat_brackets(self):
        result = validate_game_text("[melee]\n[MELEE\nMELEE]")
        self.assertEqual(len(result["errors"]), 3)
        self.assertTrue(all(
            error["code"] == "MALFORMED_COMBAT_TOKEN"
            for error in result["errors"]
        ))

    def test_flags_likely_bracketed_combat_token_typo(self):
        result = validate_game_text("Resolve [MELE].")
        self.assertFalse(result["valid"])
        self.assertTrue(any(
            error["code"] == "POSSIBLE_COMBAT_TOKEN_TYPO"
            for error in result["errors"]
        ))

    def test_flags_lowercase_resource_token(self):
        result = validate_game_text("Spend 2 sp.")
        self.assertTrue(any(
            error["code"] == "MALFORMED_RESOURCE_TOKEN" and error["token"] == "sp"
            for error in result["errors"]
        ))

    def test_flags_numeric_amount_glued_to_sp(self):
        result = validate_game_text("Pay 3SP, then 1SP.")
        self.assertEqual(
            [error["token"] for error in result["errors"]], ["3SP", "1SP"]
        )
        self.assertTrue(all(
            error["code"] == "MALFORMED_RESOURCE_TOKEN"
            for error in result["errors"]
        ))

    def test_does_not_match_ordinary_words_containing_sp(self):
        self.assertEqual(
            validate_game_text("The spell was spent in a spacious chamber."),
            {"valid": True, "errors": []},
        )

    def test_reports_line_column_and_context(self):
        result = validate_game_text("Valid line\nPay 3SP.")
        error = result["errors"][0]
        self.assertEqual(error["line"], 2)
        self.assertEqual(error["column"], 5)
        self.assertEqual(error["context"], "Pay 3SP.")

    def test_validates_multiple_files_independently(self):
        result = validate_text_files({
            "good.txt": "[MELEE] costs 2 SP.",
            "bad.txt": "Pay 2SP.",
        })
        self.assertTrue(result["good.txt"]["valid"])
        self.assertFalse(result["bad.txt"]["valid"])
        self.assertEqual(result["bad.txt"]["errors"][0]["token"], "2SP")

    def test_allows_combat_vocabulary_configuration(self):
        self.assertEqual(
            validate_game_text("[MAGIC] and [MELEE]", combat_tokens=("MAGIC", "MELEE")),
            {"valid": True, "errors": []},
        )

    def test_rejects_non_string_input(self):
        with self.assertRaises(TypeError):
            validate_game_text(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
