"""Keep editable tables stable across question changes and Streamlit reruns."""
from copy import deepcopy
import json
from pathlib import Path

from compare import validate_cases, validate_questions
from refund_demo import QUESTIONS

ROOT = Path(__file__).resolve().parent
DRAFT_FIELDS = ('questions_current', 'choices_current', 'suite_latest', 'next_question', 'next_case')


def preset_draft(mode):
    if mode == 'choice':
        questions = json.loads((ROOT / 'examples/choice-refund-questions.json').read_text())
        cases = json.loads((ROOT / 'examples/choice-refund-cases.json').read_text())
    else:
        questions = deepcopy(QUESTIONS)
        cases = json.loads((ROOT / 'examples/refund-cases.json').read_text())
    return {'questions_current': [{'id': qid, 'instructions': q['instructions']} for qid, q in questions.items()],
            'choices_current': {qid: [{'name': key, 'meaning': value} for key, value in q.get('criteria', {}).items()]
                                for qid, q in questions.items()},
            'suite_latest': validate_cases(cases, questions), 'next_question': 2, 'next_case': 13}


def draft_questions(rows, mode, choices):
    questions = {}
    for row in rows:
        question = {'type': mode, 'instructions': row['instructions']}
        if mode == 'choice':
            criteria = {}
            for option in choices.get(row['id'], []):
                key, meaning = option.get('name'), option.get('meaning')
                if not isinstance(key, str) or not key.strip():
                    raise ValueError('Every choice needs a nonempty name.')
                key = key.strip()
                if key in criteria:
                    raise ValueError(f'Question {row["id"]}: choice names must be unique ({key}).')
                criteria[key] = meaning
            question['criteria'] = criteria
        questions[row['id']] = question
    return questions


def reconcile_questions(previous, edited, next_id):
    """Assign permanent IDs to new rows; identify wording changes for label reset."""
    previous_text = {row["id"]: row["instructions"].strip() for row in previous}
    explicit_ids = {row.get("id") for row in edited if isinstance(row.get("id"), str)}
    pending_ids = iter(row["id"] for row in previous if row["id"] not in explicit_ids)
    rows = []
    for row in edited:
        qid = row.get("id")
        if not isinstance(qid, str) or not qid.strip():
            qid = next(pending_ids, None)
            if qid is None:
                qid = f"question_{next_id}"
                next_id += 1
        text = row.get("instructions")
        rows.append({"id": qid, "instructions": text if isinstance(text, str) else ""})
    changed = {row["id"] for row in rows
               if previous_text.get(row["id"]) != row["instructions"].strip()}
    return rows, changed, next_id


def reconcile_labels(cases, question_ids, changed=()):
    cases = deepcopy(cases)
    for case in cases:
        labels = case.get("expected_answers", {})
        case["expected_answers"] = {qid: None if qid in changed else labels.get(qid) for qid in question_ids}
    return cases


def context_rows(cases, questions):
    return [{"id": case["id"], "message": case["message"],
             **{qid: case['expected_answers'].get(qid) if question['type'] == 'choice' else
                "Unknown" if case["expected_answers"].get(qid) is None
                else "Yes" if case["expected_answers"][qid] else "No" for qid, question in questions.items()}}
            for case in cases]


def rows_to_cases(rows, questions):
    labels = {"Unknown": None, "Yes": True, "No": False}
    return [{"id": row.get("id"), "message": row.get("message"),
             "expected_answers": {qid: (row.get(qid) if isinstance(row.get(qid), str) else None)
                                  if question['type'] == 'choice' else labels.get(row.get(qid))
                                  for qid, question in questions.items()}} for row in rows]
