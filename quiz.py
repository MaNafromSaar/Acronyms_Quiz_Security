#!/usr/bin/env python3
"""Command-line acronym quiz for CompTIA Security+ study."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any, TypedDict


DEFAULT_DATA_FILE = Path(__file__).with_name("List.json")
DEFAULT_STATE_FILE = Path(__file__).with_name(".quiz_progress.json")
DEFAULT_QUESTION_COUNT = 15
CHOICE_COUNT = 4
QUESTION_MODES = ("mixed", "expansion", "scenario")

PLAUSIBLE_EXPANSIONS = {
    "SIEM": (
        "Secure Incident and Event Monitoring",
        "Security Intelligence and Endpoint Management",
        "System Integrity and Event Management",
    ),
    "SOAR": (
        "Security Operations Analysis and Reporting",
        "Secure Orchestration and Automated Remediation",
        "System Operations Alert Response",
    ),
    "XDR": (
        "Extended Data Response",
        "Cross-domain Detection and Remediation",
        "Expanded Device Recognition",
    ),
    "CASB": (
        "Cloud Application Security Boundary",
        "Central Access Security Broker",
        "Controlled Application Service Boundary",
    ),
    "SASE": (
        "Secure Application Service Environment",
        "Software-defined Access Security Edge",
        "Secure Authentication and Session Endpoint",
    ),
    "ZTNA": (
        "Zero Trust Network Authentication",
        "Zone-based Trusted Network Access",
        "Zoned Transport Network Architecture",
    ),
    "SAML": (
        "Secure Access Markup Language",
        "Security Authentication Messaging Layer",
        "System Assertion Management Language",
    ),
    "OIDC": (
        "Online Identity Data Connector",
        "Open Identity Directory Control",
        "OAuth Identity and Directory Client",
    ),
    "PAM": (
        "Protected Account Management",
        "Policy-based Access Monitoring",
        "Privileged Authentication Manager",
    ),
    "RPO": (
        "Recovery Process Objective",
        "Resilience Planning Operation",
        "Risk Protection Objective",
    ),
    "RTO": (
        "Restore Time Operation",
        "Recovery Threshold Objective",
        "Resilience Timing Order",
    ),
    "MTTR": (
        "Mean Time to Resolution and Recovery",
        "Maximum Time to Threat Response",
        "Measured Time to Risk Reduction",
    ),
    "MTBF": (
        "Mean Time Before Failure",
        "Maximum Time Between Faults",
        "Monitored Time for Business Functions",
    ),
    "SLE": (
        "Security Loss Estimate",
        "System Liability Exposure",
        "Single Liability Evaluation",
    ),
    "ALE": (
        "Aggregated Loss Estimate",
        "Annual Liability Exposure",
        "Annualized Loss Evaluation",
    ),
    "DLP": (
        "Data Leak Protection",
        "Digital Loss Prevention",
        "Document Lifecycle Protection",
    ),
    "HSM": (
        "Host Security Manager",
        "Hardware-based Secrets Management",
        "High-assurance Security Module",
    ),
    "TPM": (
        "Trust Platform Monitor",
        "Tamper Protection Module",
        "Technical Platform Management",
    ),
    "OCSP": (
        "Online Certificate Security Protocol",
        "Operational Certificate Status Process",
        "Open Credential Status Protocol",
    ),
    "CVE": (
        "Critical Vulnerability Enumeration",
        "Common Vector Exploit",
        "Cybersecurity Vulnerability Evaluation",
    ),
}

EXPANSION_WORDS = {
    "A": ("Advanced", "Automated", "Application", "Access", "Authentication"),
    "B": ("Business", "Based", "Broker", "Block", "Behavioral"),
    "C": ("Control", "Cryptographic", "Certificate", "Cloud", "Central"),
    "D": ("Data", "Detection", "Digital", "Device", "Distributed"),
    "E": ("Enterprise", "Encryption", "Event", "Endpoint", "Extended"),
    "F": ("Framework", "File", "Federated", "Failure", "Firewall"),
    "G": ("General", "Group", "Gateway", "Governance", "Global"),
    "H": ("Hardware", "Host", "Hybrid", "High-assurance", "Hash"),
    "I": ("Information", "Identity", "Incident", "Integrated", "Infrastructure"),
    "J": ("Journal", "Joint", "JavaScript", "Job", "Just-in-time"),
    "K": ("Key", "Knowledge", "Kernel", "Keystore", "Kubernetes"),
    "L": ("Layer", "Logical", "Local", "Loss", "Lifecycle"),
    "M": ("Management", "Monitoring", "Message", "Managed", "Mobile"),
    "N": ("Network", "Notification", "National", "Node", "Non-repudiation"),
    "O": ("Operational", "Online", "Open", "Orchestration", "Objective"),
    "P": ("Protocol", "Protected", "Platform", "Policy", "Persistent"),
    "Q": ("Quality", "Query", "Qualified", "Quarantine", "Queue"),
    "R": ("Risk", "Response", "Remote", "Recovery", "Resource"),
    "S": ("Security", "System", "Service", "Secure", "Standard"),
    "T": ("Threat", "Trusted", "Transport", "Technical", "Time"),
    "U": ("User", "Unified", "Universal", "Unauthorized", "Untrusted"),
    "V": ("Virtual", "Vulnerability", "Validation", "Verified", "Vector"),
    "W": ("Wireless", "Web", "Wide-area", "Workload", "Workflow"),
    "X": ("Extended", "Exchange", "Cross-platform", "XML", "External"),
    "Y": ("Yield", "Yearly", "Yara", "YAML", "YubiKey"),
    "Z": ("Zero-trust", "Zone", "Zonal", "Zipped", "Zigbee"),
}
UNCHANGED_EXPANSION_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
}

SITUATIONS = {
    "SIEM": (
        "A security analyst needs one place to collect, correlate, and investigate "
        "logs from firewalls, servers, and cloud services."
    ),
    "SOAR": (
        "An incident-response team wants approved playbooks to automatically enrich "
        "alerts, open tickets, and isolate compromised devices."
    ),
    "XDR": (
        "A detection team wants correlated threat data across endpoints, networks, "
        "email, and cloud workloads rather than separate tools."
    ),
    "CASB": (
        "An organization needs a control point that enforces policy between its "
        "employees and multiple SaaS providers."
    ),
    "SASE": (
        "A distributed company is replacing branch-network appliances with a cloud "
        "architecture combining wide-area networking and security services."
    ),
    "ZTNA": (
        "A remote user should receive access only to an explicitly authorized "
        "application after identity and device checks, not broad network access."
    ),
    "SAML": (
        "A web application needs an XML-based standard for accepting an identity "
        "assertion from a separate identity provider during single sign-on."
    ),
    "OIDC": (
        "An application needs an authentication layer on top of OAuth 2.0 to learn "
        "who the user is and establish a login session."
    ),
    "PAM": (
        "Administrators need their elevated accounts checked out, monitored, and "
        "protected with recorded sessions and controlled access."
    ),
    "RPO": (
        "Business leaders decide that after a disaster, the company can tolerate "
        "losing no more than one hour of newly created data."
    ),
    "RTO": (
        "Business leaders require a critical service to be operational again no more "
        "than four hours after an outage begins."
    ),
    "MTTR": (
        "An operations report measures the average elapsed time from a failure until "
        "the affected component has been repaired or restored."
    ),
    "MTBF": (
        "A reliability team measures the average operating time a system runs between "
        "one failure and the next."
    ),
    "SLE": (
        "A risk analyst estimates the financial loss from one occurrence of a "
        "particular threat against an asset."
    ),
    "ALE": (
        "A risk manager estimates the expected total annual loss for a risk by "
        "combining single-event cost and expected yearly occurrence."
    ),
    "DLP": (
        "A company needs controls that detect and block confidential documents from "
        "leaving through email, cloud uploads, or removable media."
    ),
    "HSM": (
        "An organization needs a tamper-resistant appliance dedicated to generating, "
        "protecting, and using cryptographic keys."
    ),
    "TPM": (
        "A laptop must store cryptographic material and verify platform integrity "
        "using a security chip built into the motherboard."
    ),
    "OCSP": (
        "A client must quickly ask whether a digital certificate has been revoked "
        "without downloading an entire revocation list."
    ),
    "CVE": (
        "A vulnerability report needs a standardized identifier and public reference "
        "that uniquely names a known security flaw."
    ),
}


class Acronym(TypedDict):
    acronym: str
    full_name: str
    category: str
    description: str


def load_acronyms(path: Path) -> list[Acronym]:
    try:
        raw_data: Any = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Acronym list not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(raw_data, list):
        raise ValueError(f"{path} must contain a JSON array")

    acronyms: list[Acronym] = []
    seen: set[str] = set()
    for index, item in enumerate(raw_data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Entry {index} in {path} must be an object")

        values = {
            key: item.get(key)
            for key in ("acronym", "full_name", "category", "description")
        }
        if not all(isinstance(value, str) and value.strip() for value in values.values()):
            raise ValueError(
                f"Entry {index} in {path} must have non-empty acronym, full_name, "
                "category, and description fields"
            )

        entry = Acronym(
            acronym=values["acronym"],
            full_name=values["full_name"],
            category=values["category"],
            description=values["description"],
        )
        key = entry["acronym"]
        if key in seen:
            raise ValueError(f"Duplicate acronym {entry['acronym']!r} in {path}")
        seen.add(key)
        acronyms.append(entry)

    if len(acronyms) < CHOICE_COUNT:
        raise ValueError(
            f"{path} needs at least {CHOICE_COUNT} entries to create multiple choices"
        )
    return acronyms


def load_review_queue(path: Path, known_acronyms: set[str]) -> set[str]:
    if not path.exists():
        return set()

    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid progress JSON in {path} at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(data, dict) or not isinstance(data.get("review_acronyms"), list):
        raise ValueError(f"{path} must contain a review_acronyms array")
    queued = data["review_acronyms"]
    if not all(isinstance(acronym, str) for acronym in queued):
        raise ValueError(f"{path} contains a non-string review acronym")

    return {acronym for acronym in queued if acronym in known_acronyms}


def save_review_queue(path: Path, queue: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"review_acronyms": sorted(queue)}, indent=2) + "\n",
        encoding="utf-8",
    )


def select_round(
    acronyms: list[Acronym],
    review_queue: set[str],
    question_count: int,
    rng: random.Random,
) -> list[Acronym]:
    count = min(question_count, len(acronyms))
    queued = [entry for entry in acronyms if entry["acronym"] in review_queue]
    remaining = [entry for entry in acronyms if entry["acronym"] not in review_queue]
    rng.shuffle(queued)
    rng.shuffle(remaining)
    return (queued + remaining)[:count]


def build_choices(
    target: Acronym, acronyms: list[Acronym], rng: random.Random
) -> list[str]:
    distractors = list(PLAUSIBLE_EXPANSIONS.get(target["acronym"], ()))
    if len(distractors) < CHOICE_COUNT - 1:
        distractors = generate_plausible_expansions(target["full_name"], rng)
    if len(distractors) < CHOICE_COUNT - 1:
        raise ValueError(
            f"Could not generate plausible expansion distractors for "
            f"{target['acronym']!r}"
        )

    choices = rng.sample(distractors, CHOICE_COUNT - 1) + [target["full_name"]]
    rng.shuffle(choices)
    return choices


def generate_plausible_expansions(
    full_name: str, rng: random.Random
) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z-]*", full_name)
    replaceable = [
        index
        for index, word in enumerate(words)
        if word.casefold() not in UNCHANGED_EXPANSION_WORDS
        and word[0].upper() in EXPANSION_WORDS
    ]
    alternatives: set[str] = set()

    for attempt in range(30):
        if len(alternatives) == CHOICE_COUNT - 1:
            break
        selected_indexes = set(
            rng.sample(replaceable, min(len(replaceable), 1 + attempt % 3))
        )
        replacements = {
            index: rng.choice(EXPANSION_WORDS[words[index][0].upper()])
            for index in selected_indexes
        }
        candidate = full_name
        for index in sorted(selected_indexes, reverse=True):
            positions = list(re.finditer(r"[A-Za-z][A-Za-z-]*", full_name))
            start, end = positions[index].span()
            candidate = candidate[:start] + replacements[index] + candidate[end:]
        if candidate != full_name:
            alternatives.add(candidate)

    return sorted(alternatives)


def build_scenario_choices(
    target: Acronym, acronyms: list[Acronym], rng: random.Random
) -> list[str]:
    distractors = [
        entry["acronym"]
        for entry in acronyms
        if entry["acronym"] != target["acronym"]
    ]
    choices = rng.sample(distractors, CHOICE_COUNT - 1) + [target["acronym"]]
    rng.shuffle(choices)
    return choices


def choose_question_mode(mode: str, rng: random.Random) -> str:
    if mode == "mixed":
        return rng.choice(("expansion", "scenario"))
    return mode


def explain_scenario_wrong_choice(choice: str, acronyms: list[Acronym]) -> str:
    selected = next(entry for entry in acronyms if entry["acronym"] == choice)
    return (
        f"{selected['acronym']} means {selected['full_name']}. "
        "That control or concept does not address the situation described."
    )


def ask_for_choice() -> int | None:
    answer = input("Your answer (A-D, or Q to quit): ").strip().upper()
    if answer == "Q":
        return None
    if len(answer) == 1 and "A" <= answer <= chr(ord("A") + CHOICE_COUNT - 1):
        return ord(answer) - ord("A")
    print(f"Please enter a letter from A to {chr(ord('A') + CHOICE_COUNT - 1)}, or Q.")
    return -1


def run_quiz_round(
    acronyms: list[Acronym],
    review_queue: set[str],
    question_count: int,
    rng: random.Random,
    mode: str = "mixed",
) -> tuple[set[str], int, bool]:
    questions = select_round(acronyms, review_queue, question_count, rng)
    played = {entry["acronym"] for entry in questions}
    next_review = review_queue - played
    first_try_correct = 0

    print(
        f"\nStarting round: {len(questions)} questions in {mode} mode."
    )

    for number, entry in enumerate(questions, start=1):
        question_mode = choose_question_mode(mode, rng)
        if question_mode == "scenario":
            prompt = (
                f"Situation: {SITUATIONS.get(entry['acronym'], entry['description'])}\n"
                "Which acronym best fits this situation?"
            )
            choices = build_scenario_choices(entry, acronyms, rng)
            correct_choice = entry["acronym"]
        else:
            prompt = f"What does {entry['acronym']} stand for?"
            choices = build_choices(entry, acronyms, rng)
            correct_choice = entry["full_name"]
        available = set(range(CHOICE_COUNT))
        wrong_attempts = 0

        print(f"\nQuestion {number}/{len(questions)}: {prompt}")
        print(f"Category: {entry['category']}")
        if entry["acronym"] in review_queue:
            print("(Review card)")

        while True:
            for index, choice in enumerate(choices):
                status = "" if index in available else " (eliminated)"
                print(f"  {chr(ord('A') + index)}) {choice}{status}")

            selected = ask_for_choice()
            if selected is None:
                next_review.update(review_queue & played)
                return next_review, first_try_correct, False
            if selected == -1:
                continue
            if selected not in available:
                print("That choice was already eliminated. Try another one.")
                continue

            if choices[selected] == correct_choice:
                if wrong_attempts == 0:
                    first_try_correct += 1
                print("Correct!")
                break

            wrong_attempts += 1
            available.remove(selected)
            if question_mode == "scenario":
                print(explain_scenario_wrong_choice(choices[selected], acronyms))
            else:
                print(
                    f"{choices[selected]} is a plausible-looking but incorrect "
                    f"expansion of {entry['acronym']}."
                )
            print(f"Notiz: {entry['description']}")
            print("Try again.")

        print(f"Answer: {entry['acronym']} = {entry['full_name']}")
        print(f"Notiz: {entry['description']}")
        if wrong_attempts >= 2:
            next_review.add(entry["acronym"])

    percentage = first_try_correct / len(questions) * 100
    print("\nRound complete!")
    print(f"First-try grade: {first_try_correct}/{len(questions)} ({percentage:.0f}%)")
    if percentage == 100:
        print("Grade: A - Perfect round!")
    elif percentage >= 90:
        print("Grade: B")
    elif percentage >= 80:
        print("Grade: C")
    elif percentage >= 70:
        print("Grade: D")
    else:
        print("Grade: F")

    if next_review:
        print("Scheduled for the next quiz:", ", ".join(sorted(next_review)))
    else:
        print("No new review cards were scheduled.")

    return next_review, first_try_correct, True


def ask_to_continue() -> bool:
    while True:
        answer = input("\nStart the next quiz round? (y/N): ").strip().casefold()
        if answer in ("", "n", "no"):
            return False
        if answer in ("y", "yes"):
            return True
        print("Please answer y or n.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Practice CompTIA Security+ acronyms from a JSON list."
    )
    parser.add_argument(
        "-n",
        "--questions",
        type=int,
        default=DEFAULT_QUESTION_COUNT,
        help=f"questions per round (default: {DEFAULT_QUESTION_COUNT})",
    )
    parser.add_argument(
        "--list",
        dest="list_path",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="path to the acronym JSON file",
    )
    parser.add_argument(
        "--state",
        dest="state_path",
        type=Path,
        default=DEFAULT_STATE_FILE,
        help="path to the saved review queue",
    )
    parser.add_argument(
        "--reset-progress",
        action="store_true",
        help="clear saved review cards before starting",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="random seed for reproducible question and choice order",
    )
    parser.add_argument(
        "--mode",
        choices=QUESTION_MODES,
        default="mixed",
        help="question mode: mixed (default), expansion, or scenario",
    )
    args = parser.parse_args()
    if args.questions <= 0:
        parser.error("--questions must be greater than zero")
    return args


def main() -> int:
    args = parse_args()
    try:
        acronyms = load_acronyms(args.list_path)
        known_acronyms = {entry["acronym"] for entry in acronyms}
        review_queue = (
            set()
            if args.reset_progress
            else load_review_queue(args.state_path, known_acronyms)
        )
        rng = random.Random(args.seed)

        if args.reset_progress:
            save_review_queue(args.state_path, set())
        if review_queue:
            print(f"Review cards due this round: {len(review_queue)}")

        while True:
            review_queue, _, completed = run_quiz_round(
                acronyms, review_queue, args.questions, rng, args.mode
            )
            save_review_queue(args.state_path, review_queue)
            if not completed or not ask_to_continue():
                break
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nQuiz ended.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
