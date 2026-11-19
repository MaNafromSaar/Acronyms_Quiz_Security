import contextlib
import io
import json
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import quiz


class QuizTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.acronyms = quiz.load_acronyms(Path(__file__).with_name("List.json"))

    def test_select_round_defaults_to_fifteen_and_prioritizes_review_cards(self) -> None:
        review = {"SIEM", "RTO"}

        questions = quiz.select_round(
            self.acronyms, review, quiz.DEFAULT_QUESTION_COUNT, random.Random(4)
        )

        self.assertEqual(len(questions), 15)
        self.assertTrue(review.issubset({item["acronym"] for item in questions}))
        self.assertEqual(
            {item["acronym"] for item in questions[:2]},
            review,
        )

    def test_build_choices_contains_one_correct_unique_answer(self) -> None:
        target = self.acronyms[0]

        choices = quiz.build_choices(target, self.acronyms, random.Random(9))

        self.assertEqual(len(choices), 4)
        self.assertEqual(len(set(choices)), 4)
        self.assertEqual(choices.count(target["full_name"]), 1)
        wrong_answers = set(choices) - {target["full_name"]}
        if target["acronym"] in quiz.PLAUSIBLE_EXPANSIONS:
            self.assertTrue(
                wrong_answers <= set(quiz.PLAUSIBLE_EXPANSIONS[target["acronym"]])
            )
        else:
            correct_initials = [
                word[0].upper()
                for word in target["full_name"].split()
                if word.casefold() not in quiz.UNCHANGED_EXPANSION_WORDS
            ]
            for wrong_answer in wrong_answers:
                wrong_initials = [
                    word[0].upper()
                    for word in wrong_answer.split()
                    if word.casefold() not in quiz.UNCHANGED_EXPANSION_WORDS
                ]
                self.assertEqual(wrong_initials, correct_initials)

    def test_every_loaded_acronym_has_expansion_decoys_and_a_situation(self) -> None:
        for entry in self.acronyms:
            with self.subTest(acronym=entry["acronym"]):
                choices = quiz.build_choices(entry, self.acronyms, random.Random(42))
                self.assertEqual(len(choices), 4)
                self.assertEqual(len(set(choices)), 4)
                self.assertEqual(choices.count(entry["full_name"]), 1)
                self.assertTrue(entry["description"])
                self.assertNotEqual(
                    entry["description"].strip(), quiz.SITUATIONS.get(entry["acronym"])
                )
                scenario_choices = quiz.build_scenario_choices(
                    entry, self.acronyms, random.Random(42)
                )
                self.assertEqual(len(scenario_choices), 4)
                self.assertEqual(scenario_choices.count(entry["acronym"]), 1)

    def test_scenario_mode_uses_acronym_choices_and_explains_wrong_answer(self) -> None:
        target = self.acronyms[0]
        wrong = next(
            entry for entry in self.acronyms if entry["acronym"] != target["acronym"]
        )
        choices = [wrong["acronym"], target["acronym"], "RTO", "XDR"]

        with (
            patch.object(quiz, "select_round", return_value=[target]),
            patch.object(quiz, "build_scenario_choices", return_value=choices),
            patch("builtins.input", side_effect=["A", "B"]),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            _, first_try_correct, completed = quiz.run_quiz_round(
                self.acronyms, set(), 1, random.Random(0), "scenario"
            )

        self.assertTrue(completed)
        self.assertEqual(first_try_correct, 0)
        self.assertIn(wrong["full_name"], output.getvalue())
        self.assertIn("does not address the situation", output.getvalue())
        self.assertGreaterEqual(output.getvalue().count(target["description"]), 2)

    def test_two_wrong_attempts_schedule_acronym_for_next_round(self) -> None:
        target = self.acronyms[0]
        choices = [target["full_name"], "Wrong 1", "Wrong 2", "Wrong 3"]

        with (
            patch.object(quiz, "select_round", return_value=[target]),
            patch.object(quiz, "build_choices", return_value=choices),
            patch("builtins.input", side_effect=["B", "C", "A"]),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            review, first_try_correct, completed = quiz.run_quiz_round(
                self.acronyms, set(), 1, random.Random(0), "expansion"
            )

        self.assertTrue(completed)
        self.assertEqual(review, {target["acronym"]})
        self.assertEqual(first_try_correct, 0)
        self.assertIn("Scheduled for the next quiz", output.getvalue())
        self.assertGreaterEqual(output.getvalue().count(target["description"]), 3)

    def test_review_queue_round_trips_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            quiz.save_review_queue(state_path, {"SIEM", "RTO"})

            loaded = quiz.load_review_queue(
                state_path, {item["acronym"] for item in self.acronyms}
            )

            self.assertEqual(loaded, {"SIEM", "RTO"})
            self.assertEqual(
                json.loads(state_path.read_text(encoding="utf-8")),
                {"review_acronyms": ["RTO", "SIEM"]},
            )


if __name__ == "__main__":
    unittest.main()
