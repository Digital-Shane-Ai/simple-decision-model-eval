"""Table-focused decision-model testing workbench."""

import json
from copy import deepcopy
from pathlib import Path
from threading import Lock
from time import monotonic

import pandas as pd
import streamlit as st

from compare import (MODELS, QUESTION, default_model_keys, ordered_model_keys, ordered_results,
                     report, run_model, summarize, validate_cases, validate_questions, display_answer,
                     add_log_loss, log_loss_fields, display_log_loss)
from model_config import model_eligibility, print_startup_diagnostics
from markdown_copy import cases_table, make_copy_table_button
from ui_state import (reconcile_questions, reconcile_labels,
                      context_rows, rows_to_cases, preset_draft, draft_questions, DRAFT_FIELDS)
from results_charts import (score_data, score_spec, brier_data, brier_spec,
                            probability_data, probability_spec, timing_data, timing_spec,
                            log_loss_data, log_loss_spec)

ROOT = Path(__file__).resolve().parent
# Raw Streamlit launches retain gating; the supported serve.py launcher prints
# this before the server starts. This fallback also prints once per process.
print_startup_diagnostics(MODELS)
copy_table_button = make_copy_table_button()
st.set_page_config(page_title="Decision models", page_icon="⚖", layout="wide")
st.html("""<style>
[data-testid="stMainBlockContainer"] { max-width: 1480px; padding: 2.7rem 2.4rem 3rem; }
h1 { font-size: 1.8rem !important; letter-spacing: -.03em; padding-bottom: .15rem !important; }
h2, h3 { font-size: 1.1rem !important; padding-top: .45rem !important; padding-bottom: .25rem !important; }
[data-testid="stVerticalBlock"] { gap: .65rem; }
[data-testid="stCaptionContainer"] { line-height: 1.5; }
@media (max-width: 700px) {
  [data-testid="stMainBlockContainer"] { padding: 2.5rem .8rem 2rem; }
}
</style>""")


@st.cache_resource
def inference_lock():
    return Lock()


def rebase_draft():
    st.session_state.questions_base = deepcopy(st.session_state.questions_current)
    st.session_state.choices_base = deepcopy(st.session_state.choices_current)
    st.session_state.suite_base = deepcopy(st.session_state.suite_latest)
    for key in ('question_revision', 'choices_revision', 'suite_revision'):
        st.session_state[key] = st.session_state.get(key, 0) + 1


def switch_mode():
    old_mode = st.session_state.active_mode
    st.session_state.mode_drafts[old_mode] = {key: deepcopy(st.session_state[key]) for key in DRAFT_FIELDS}
    new_mode = st.session_state.answer_mode
    draft = st.session_state.mode_drafts.get(new_mode, preset_draft(new_mode))
    for key, value in draft.items():
        st.session_state[key] = deepcopy(value)
    st.session_state.active_mode = new_mode
    st.session_state.pop('choices_for', None)
    rebase_draft()


def refresh_contexts(changed=()):
    qids = [row['id'] for row in st.session_state.questions_current]
    cases = reconcile_labels(st.session_state.suite_latest, qids, changed)
    st.session_state.suite_base = cases
    st.session_state.suite_latest = deepcopy(cases)
    st.session_state.suite_revision += 1


def accept_questions(edited):
    previous = st.session_state.questions_current
    rows, changed, next_id = reconcile_questions(previous, edited, st.session_state.next_question)
    structural = [r['id'] for r in rows] != [r['id'] for r in previous]
    st.session_state.questions_current = rows
    st.session_state.next_question = next_id
    for row in rows:
        st.session_state.choices_current.setdefault(row['id'], [])
        st.session_state.choices_base.setdefault(row['id'], [])
    if changed or structural:
        refresh_contexts(changed)
    rebase = len(rows) < len(previous)
    if rebase:
        st.session_state.questions_base = deepcopy(rows)
        st.session_state.question_revision += 1
    return rebase


def accept_contexts(rows, questions):
    used = {row.get('id') for row in rows if isinstance(row.get('id'), str)}
    pending_ids = iter(c['id'] for c in st.session_state.suite_latest if c['id'] not in used)
    for row in rows:
        if not isinstance(row.get('id'), str) or not row['id'].strip():
            row['id'] = next(pending_ids, None)
            if row['id'] is None:
                while f'case_{st.session_state.next_case}' in used:
                    st.session_state.next_case += 1
                row['id'] = f'case_{st.session_state.next_case}'
                st.session_state.next_case += 1
            used.add(row['id'])
    st.session_state.suite_latest = rows_to_cases(rows, questions)


def results_table(rows):
    return pd.DataFrame([{
        "Model": r["name"], "Case": r["case_id"], "Context": r["message"], "Question ID": r.get("question_id", "refund_requested"),
        "Question": r.get("question", QUESTION), "Answer type": r.get("question_type", "noul"),
        "Choices": json.dumps(r["criteria"], ensure_ascii=False) if r.get("criteria") else None, "Status": r["status"],
        "Decision": display_answer(r.get("decision", r.get("wants_refund"))) if r["status"] == "ok" else "Unavailable",
        "Probabilities": json.dumps(r["probabilities"], ensure_ascii=False) if r.get("probabilities") else None,
        "P(yes)": r.get("probability_yes"), "P(no)": r.get("probability_no"),
        "Selected probability": r.get("selected_probability"), "Returned confidence": r.get("returned_confidence"),
        "Returned answer confidence": r.get("returned_answer_confidence"),
        "Expected": display_answer(r["expected"]),
        "Log loss (nats)": display_log_loss(loss["log_loss"], loss["log_loss_status"]),
        "Log loss status": loss["log_loss_status"], "Zero-probability truths": loss["log_loss_zero_probability_count"],
        "Correct": r.get("correct"), "Context inference (s)": r.get("inference_seconds"),
        "Load (s)": r.get("load_seconds"), "Device": r.get("device"),
        "Execution": r.get("execution", "local"), "Context API cost (USD)": r.get("cost_usd"),
    } for r in ordered_results(rows) for loss in [log_loss_fields([r])]])


def summary_table(rows):
    summaries = summarize(rows)
    frame = pd.DataFrame(summaries).rename(columns={
        "model": "Model", "cases": "Answer pairs", "contexts": "Contexts", "answered": "Answered", "errors": "Errors",
        "labelled": "Labeled", "correct": "Correct", "accuracy_on_answered": "Accuracy (answered)",
        "correct_over_labelled": "Correct / all labeled", "coverage": "Coverage", "brier_score": "Binary Brier", "choice_brier_score": "Choice Brier",
        "mean_inference_seconds": "Mean context inference (s)", "load_seconds": "Load (s)",
        "log_loss": "Log loss (nats)", "log_loss_status": "Log loss status",
        "log_loss_scored": "Log loss scored", "log_loss_zero_probability_count": "Zero-probability truths",
    })
    frame["Log loss (nats)"] = [display_log_loss(s["log_loss"], s["log_loss_status"]) for s in summaries]
    return frame


def show_score_chart(rows, key, view):
    if not rows:
        st.info('No answers are available for this saved run.')
        return
    if view == 'Brier scores':
        available = False
        for kind, label in (('noul', 'Binary'), ('choice', 'Multiple choice')):
            values = brier_data(rows, kind)
            if values:
                available = True
                st.caption(f'{label} Brier · sorted lowest first; ties retain registry order')
                st.vega_lite_chart(brier_spec(values, kind), width='stretch', key=f'{key}_{kind}')
                st.caption('Scored on answered labeled pairs. Teal: local; orange / API prefix: hosted API. Exact values are in the table below.')
        if not available:
            st.info('Brier scores need successful answers with expected labels and probabilities.')
    elif view == 'Log loss':
        values = log_loss_data(rows)
        if values:
            st.caption('Log loss · nats · lower is better; finite scores sorted ascending, then infinity; ties retain registry order')
            st.vega_lite_chart(log_loss_spec(values), width='stretch', key=f'{key}_log_loss')
            st.caption('Mean −ln P(expected) on valid answered labeled pairs. Exact zero truth probabilities give ∞, with their count shown; infinite scores have no finite bar. Teal: local; orange / API prefix: hosted API. Missing scores are unavailable. One-hot perfect scores do not establish calibration.')
        else:
            st.info('Log loss needs successful answers with expected labels and valid probabilities.')
    else:
        values = score_data(rows)
        if values:
            st.vega_lite_chart(score_spec(values), width='stretch', key=key)
        st.caption('● Accuracy: correct / answered labeled pairs. ◆ Coverage: answered / all pairs. Sorted by accuracy, highest first; ties retain registry order and missing accuracy stays last. Without accuracy, sorted by coverage. Teal: local; orange / API prefix: hosted API. Exact values are in the table below.')


if 'mode_drafts' not in st.session_state:
    st.session_state.mode_drafts = {}
    st.session_state.answer_mode = st.session_state.active_mode = 'noul'
    draft = preset_draft('noul')
    # Preserve an existing suite when the app is hot-reloaded from the older UI.
    if 'questions_current' in st.session_state:
        draft['questions_current'] = deepcopy(st.session_state.questions_current)
        draft['suite_latest'] = deepcopy(st.session_state.get('suite_latest', st.session_state.get('suite_base', draft['suite_latest'])))
    for key, value in draft.items():
        st.session_state[key] = value
    rebase_draft()

st.title('Decision models')
st.caption('Test model decisions against your own questions, choices, and contexts.')
mode_col, models_col, device_col, run_col = st.columns([2.4, 1.2, 1.3, 1.2], vertical_alignment='bottom')
mode = mode_col.radio('Answer type', ['noul', 'choice'], horizontal=True, key='answer_mode',
                      format_func=lambda v: 'Yes / No' if v == 'noul' else 'Multiple choice',
                      label_visibility='collapsed', on_change=switch_mode)
with models_col.popover('Models', width='stretch'):
    eligibility = {key: model_eligibility(spec) for key, spec in MODELS.items()}
    regular_keys = [key for key, spec in MODELS.items()
                    if spec.get('default_selected', True) and eligibility[key].enabled]
    optional_keys = [key for key, spec in MODELS.items()
                     if not spec.get('default_selected', True) and eligibility[key].enabled]
    # Remove stale hosted selections before creating widgets if config changed.
    for state_key, options, defaults in (('selected_models', regular_keys, default_model_keys()),
                                         ('selected_optional_models', optional_keys, [])):
        current = st.session_state.get(state_key, defaults)
        cleaned = [key for key in current if key in options]
        if state_key not in st.session_state or cleaned != current:
            st.session_state[state_key] = cleaned
    keys = st.multiselect('Run these models', regular_keys,
                          key='selected_models', disabled=not regular_keys, format_func=lambda k: MODELS[k]['name'])
    keys += st.multiselect('Optional Cloudflare models', optional_keys,
                           key='selected_optional_models', disabled=not optional_keys, format_func=lambda k: MODELS[k]['name'])
    blocked_keys = [key for key in MODELS if not eligibility[key].enabled]
    if blocked_keys:
        st.caption('Unavailable API models · configure these variables in the launching shell, then restart the server.')
        for key in blocked_keys:
            st.checkbox(f"{MODELS[key]['name']} · disabled", value=False, disabled=True,
                        key=f'disabled_model_{key}', help=eligibility[key].error)
            st.caption(eligibility[key].error)
    st.caption('Local models run sequentially. Hosted models use provider credits. Present configuration does not verify key validity or account access.')
    with st.expander('Checkpoints and runtimes'):
        for spec in MODELS.values():
            url = spec.get('url', f"https://huggingface.co/{spec['repo']}")
            st.markdown(f"**{spec['name']}** · [{spec['repo']}]({url})")
            st.caption(spec['note'] + (f" · Revision {spec['revision'][:12]}" if spec.get('revision') else ''))
keys = ordered_model_keys([key for key in keys if model_eligibility(MODELS[key]).enabled])
device = device_col.selectbox('Device', ['mps', 'auto', 'cpu', 'cuda'], label_visibility='collapsed',
                               format_func=lambda d: {'mps': 'Mac GPU (Metal)', 'auto': 'Auto device', 'cpu': 'CPU', 'cuda': 'NVIDIA GPU'}[d])
run_requested = run_col.button('Run comparison', type='primary', width='stretch', disabled=not keys)
status_slot = st.empty()
st.caption('Each answer type keeps its own draft. New drafts start with a 12-row refund example.')
if 'jev' in keys:
    st.caption('Jev sends contexts and questions to OpenRouter/TypeSafe and uses credits. Expected labels stay local.')
if any(MODELS[key].get('backend') == 'cloudflare' for key in keys):
    st.caption('CLEF sends contexts and questions to Cloudflare Workers AI and uses account billing. Expected labels stay local. Account access is unverified.')
st.subheader('Questions')
st.caption('Double-click cells to edit. Add rows with +; select rows to delete. Changing wording or choices clears only that question’s expected answers.')
revision = st.session_state.question_revision
edited_questions = st.data_editor(
    pd.DataFrame(st.session_state.questions_base, columns=['id', 'instructions']),
    num_rows='dynamic', hide_index=True, width='stretch', height=min(300, 36 + 42 * (len(st.session_state.questions_base) + 1)),
    key=f'questions_editor_{revision}', disabled=['id'], row_height=42, column_order=['instructions'],
    column_config={'id': None, 'instructions': st.column_config.TextColumn('Question', width=850, required=True)},
)
if accept_questions(edited_questions.to_dict('records')):
    st.rerun()
if mode == 'choice' and st.session_state.questions_current:
    qids = [row['id'] for row in st.session_state.questions_current]
    wording = {row['id']: row['instructions'] or '(Untitled question)' for row in st.session_state.questions_current}
    if st.session_state.get('choices_for') not in qids:
        st.session_state.choices_for = qids[0]
    choices_qid = st.selectbox('Choices for question', qids, format_func=lambda q: wording[q], key='choices_for')
    choice_base = st.session_state.choices_base[choices_qid]
    edited_choices = st.data_editor(
        pd.DataFrame(choice_base, columns=['name', 'meaning']), num_rows='dynamic', hide_index=True,
        width='stretch', height=min(300, 36 + 42 * (len(choice_base) + 1)), row_height=42,
        key=f'choices_editor_{st.session_state.choices_revision}_{choices_qid}',
        column_config={'name': st.column_config.TextColumn('Choice', width=180, required=True),
                       'meaning': st.column_config.TextColumn('Meaning', width=850, required=True)},
    ).to_dict('records')
    if edited_choices != st.session_state.choices_current[choices_qid]:
        st.session_state.choices_current[choices_qid] = edited_choices
        refresh_contexts([choices_qid])
    st.caption('Provide 2–255 distinct choice names and meanings. A model selects one choice; expected answers use the same names.')
input_error = None
try:
    questions = draft_questions(st.session_state.questions_current, mode, st.session_state.choices_current)
except ValueError as exc:
    input_error = str(exc)
    questions = {row['id']: {'type': mode, 'instructions': row['instructions'], 'criteria': {}}
                 for row in st.session_state.questions_current}

st.subheader('Contexts & expected answers')
st.caption('Every question runs against every context. Keep one context by deleting the other rows. Unknown leaves a pair unscored.')
base = st.session_state.suite_base
edited_contexts = st.data_editor(
    pd.DataFrame(context_rows(base, questions), columns=['id', 'message', *questions]),
    num_rows='dynamic', hide_index=True, width='stretch', height=min(380, 36 + 52 * (len(base) + 1)), row_height=52,
    key=f'suite_editor_{st.session_state.suite_revision}',
    column_config={'id': st.column_config.TextColumn('Case ID', width=140),
                   'message': st.column_config.TextColumn('Context', required=True, width=700),
                   **{qid: st.column_config.SelectboxColumn(f'Q{i} expected',
                        options=['Unknown', 'Yes', 'No'] if q['type'] == 'noul' else [None, *q.get('criteria', {})],
                        format_func=lambda value: 'Unknown' if value is None else str(value),
                        width=150, help=q['instructions']) for i, (qid, q) in enumerate(questions.items(), 1)}},
)
accept_contexts(edited_contexts.to_dict('records'), questions)
pending_cases = deepcopy(st.session_state.suite_latest)
status_slot.caption(f'{len(pending_cases)} contexts · {len(questions)} questions · {len(keys)} models · {len(pending_cases) * len(questions) * len(keys)} answers per run')

if run_requested:
    try:
        if input_error:
            raise ValueError(input_error)
        run_questions = validate_questions(questions)
        cases = validate_cases(pending_cases, run_questions)
    except ValueError as exc:
        status_slot.error(str(exc))
    else:
        lock = inference_lock()
        if not lock.acquire(blocking=False):
            status_slot.warning("Another comparison is running. Wait for it to finish.")
        else:
            rows = []
            live = st.empty()
            try:
                with status_slot.status("Running comparison…", expanded=False) as execution:
                    progress = st.progress(0)
                    last_live_update = 0.0
                    for index, key in enumerate(keys):
                        execution.update(label=f"Running {MODELS[key]['name']} · {index + 1}/{len(keys)}")
                        rows.extend(run_model(key, cases, device, questions=run_questions))
                        if monotonic() - last_live_update >= .25 or index == len(keys) - 1:
                            live.dataframe(results_table(rows)[["Model", "Case", "Question ID", "Status", "Decision", "Selected probability"]],
                                           hide_index=True, width="stretch")
                            last_live_update = monotonic()
                        progress.progress((index + 1) / len(keys))
                    st.session_state.comparison = report(cases, keys, rows, run_questions)
                    error_count = sum(r["status"] == "error" for r in rows)
                    execution.update(label=f"Completed · {len(rows)} answers · {error_count} errors", state="complete")
                live.empty()
            finally:
                lock.release()

st.divider()
if "comparison" not in st.session_state:
    st.subheader("Results")
    st.caption("Run a comparison to see model scores and inspect individual answers.")
else:
    comparison = add_log_loss(st.session_state.comparison)
    saved_questions = comparison.get("questions") or {"refund_requested": {"type": "noul", "instructions": comparison.get("question", QUESTION)}}
    heading, json_col, csv_col = st.columns([5, 1, 1], vertical_alignment="bottom")
    heading.subheader("Results")
    json_col.download_button("Export JSON", json.dumps(comparison, indent=2, allow_nan=False), file_name="decision-comparison.json", mime="application/json", width="stretch")
    csv_col.download_button("Export CSV", results_table(comparison["results"]).to_csv(index=False), file_name="decision-results.csv", mime="text/csv", width="stretch")
    changed = True
    try:
        changed = (validate_questions(questions) != saved_questions or
                   validate_cases(pending_cases, questions) != validate_cases(comparison["cases"], saved_questions) or
                   keys != list(comparison["models"]))
    except ValueError:
        pass
    stamp = comparison["created_at"].replace("T", " ").split(".")[0] + " UTC"
    st.caption(f"{'Inputs changed · showing saved run' if changed else 'Saved run'} · {stamp} · {len(comparison['cases'])} context(s) · {len(saved_questions)} question(s)")
    overview, inspector, details = st.tabs(
        ["Model overview", "Inspect answers", "Run details"],
        key="results_tab", on_change="rerun",
    )
    summary = summary_table(comparison["results"])
    score_columns = (["Binary Brier"] if any(q["type"] == "noul" for q in saved_questions.values()) else []) + (["Choice Brier"] if any(q["type"] == "choice" for q in saved_questions.values()) else [])
    score_columns += ["Log loss (nats)", "Zero-probability truths"]
    with overview:
        chart_view = st.radio('Overview chart', ['Accuracy & coverage', 'Brier scores', 'Log loss'],
                              horizontal=True, key='overview_chart')
        show_score_chart(comparison['results'], 'model_scores', chart_view)
        summary_display = summary[["Model", "Answer pairs", "Answered", "Errors", "Accuracy (answered)", "Coverage", *score_columns]]
        st.dataframe(summary_display, hide_index=True, width="stretch", column_config={
            "Model": st.column_config.TextColumn(width=220),
            **{k: st.column_config.NumberColumn(format="percent") for k in ["Accuracy (answered)", "Coverage"]}
        })
        copy_table_button(summary_display, "Copy summary as Markdown", "copy_summary")
        if not any(r["expected"] is not None for r in comparison["results"]):
            st.caption("This run has no expected answers. Accuracy and Brier scores remain blank; log loss is unavailable.")
        if len(saved_questions) > 1:
            qid = st.selectbox("Scores for question", list(saved_questions), format_func=lambda q: saved_questions[q]["instructions"])
            question_rows = [r for r in comparison["results"] if r.get("question_id", "refund_requested") == qid]
            show_score_chart(question_rows, 'question_scores', chart_view)
            question_summary = summary_table(question_rows)
            st.dataframe(question_summary[["Model", "Correct", "Labeled", "Accuracy (answered)", "Coverage", *score_columns]], hide_index=True, width="stretch")
            copy_table_button(question_summary, "Copy question summary as Markdown", "copy_question_summary")
    with inspector:
        context_col, question_col = st.columns(2)
        case_id = context_col.selectbox("Inspect context", [c["id"] for c in comparison["cases"]])
        question_id = question_col.selectbox("Inspect question", list(saved_questions), format_func=lambda q: saved_questions[q]["instructions"])
        case = next(c for c in comparison["cases"] if c["id"] == case_id)
        st.write(case["message"])
        st.caption(f"Question: {saved_questions[question_id]['instructions']}")
        expected = case.get("expected_answers", {}).get(question_id, case.get("expected") if question_id == "refund_requested" else None)
        st.caption("Expected: " + display_answer(expected))
        selected = [r for r in comparison["results"] if r["case_id"] == case_id and r.get("question_id", "refund_requested") == question_id]
        chart_question = saved_questions[question_id]
        options = list(chart_question['criteria']) if chart_question['type'] == 'choice' else ['Yes', 'No']
        chart_option = st.selectbox('Probability to compare', options,
                                   key=f'probability_option_{question_id}_{json.dumps(options, ensure_ascii=False)}')
        chart_probabilities = probability_data(selected, chart_question, chart_option)
        if chart_probabilities:
            st.vega_lite_chart(probability_spec(chart_probabilities, chart_question['type'] == 'noul'),
                               width='stretch', key='answer_probabilities')
            st.caption('● This answer was selected. ◆ Another answer was selected. Registry order stays fixed across answers; probability is support for this answer, not correctness. Teal: local; orange / API prefix: hosted API. Only successful returned probabilities are plotted; failed answers remain in the table.' +
                       (' The dashed line marks 50%; binary Yes uses P(yes) ≥ 50%.' if chart_question['type'] == 'noul' else
                        ' Compare another choice with the selector; the table retains the full distribution.'))
        else:
            st.info('No successful probabilities are available for this context and question. Inspect the status table below.')
        inspected = results_table(selected)
        if saved_questions[question_id]["type"] == "choice":
            probability_columns = []
            for option in saved_questions[question_id]["criteria"]:
                column = f"P · {option}"
                probability_columns.append(column)
                inspected[column] = [(row.get("probabilities") or {}).get(option) for row in ordered_results(selected)]
        else:
            probability_columns = ["P(yes)", "P(no)"]
        compact = inspected[["Model", "Status", "Decision", *probability_columns, "Selected probability", "Correct", "Log loss (nats)"]].rename(columns={"Selected probability": "P(decision)"})
        st.dataframe(compact, hide_index=True, width="stretch", column_config={
            k: st.column_config.NumberColumn(format="percent") for k in [*probability_columns, "P(decision)"]
        })
        copy_table_button(compact, "Copy case results as Markdown", "copy_case_results")
    with details:
        st.subheader('Context timing')
        st.caption('Sorted by mean elapsed time, lowest first; ties retain registry order. Each model/context is counted once across all questions. Teal local calls exclude model loading; orange / API calls include network and provider queue. Local inference and hosted service latency use different execution environments. The shared seconds axis shows observed elapsed times, without hardware normalization.')
        observed_timings = timing_data(comparison['results'])
        if observed_timings:
            st.vega_lite_chart(timing_spec(observed_timings), width='stretch', key='context_timings')
            timing_table = pd.DataFrame(observed_timings)[['Model', 'Execution', 'Seconds', 'Timed contexts']].rename(columns={'Seconds': 'Mean context inference (s)'})
            st.dataframe(timing_table, hide_index=True, width='stretch')
            copy_table_button(timing_table, 'Copy timing summary as Markdown', 'copy_timings')
        else:
            st.info('No successful context timings were recorded for this run.')
        st.subheader('Saved inputs & detailed results')
        saved_table = cases_table(comparison["cases"], saved_questions)
        st.dataframe(saved_table, hide_index=True, width="stretch")
        copy_table_button(saved_table, "Copy run test cases as Markdown", "copy_run_cases")
        st.dataframe(summary, hide_index=True, width="stretch")
        copy_table_button(summary, "Copy detailed summary as Markdown", "copy_detailed_summary")
        all_results = results_table(comparison["results"])
        st.dataframe(all_results, hide_index=True, width="stretch")
        copy_table_button(all_results, "Copy all results as Markdown", "copy_all_results")
        st.caption("Context timing and API cost repeat across question rows; do not sum them across questions. Jev timing includes network/provider queue; local timing excludes loading.")
        with st.expander("Raw outputs & worker diagnostics"):
            st.json(comparison)
    errors = [r for r in comparison["results"] if r["status"] == "error"]
    if errors:
        st.warning(f"{len(errors)} answer(s) failed. Failures count against coverage; they are not No decisions.")
        with st.expander("Failed answers", expanded=True):
            st.dataframe(pd.DataFrame([{"Model": r["name"], "Case": r["case_id"], "Question": r.get("question_id", "refund_requested"),
                                        "Error": r.get("error", "Model failed")} for r in errors]), hide_index=True, width="stretch")

with st.expander("Scoring, model execution & input table"):
    st.write("Binary Yes means P(yes) ≥ 50%. Multiple choice selects the largest probability; ties retain the native selection. P(decision) is the selected answer’s probability. Native confidence fields retain each model’s definition.")
    st.write("Accuracy scores answered labeled context/question pairs. Coverage and correct / all labeled pairs expose failures. Binary Brier is mean (P(yes) − label)². Choice Brier is the mean sum of squared errors across all choices (0–2); lower is better. The two scales stay separate. Labels stay local.")
    st.write("Log loss is mean −ln P(expected), in nats, on valid answered labeled pairs; lower is better. P(expected)=0 gives infinity, without clipping. JSON stores a null value with an explicit infinite or unavailable status, scored-pair count, and zero-probability count. Failures remain in coverage and correct / all labeled. Genuine one-hot outputs are preserved; a perfect one-hot score alone does not establish calibrated confidence.")
    st.write("Every context carries all questions in one call. Long contexts or many questions can exceed model input limits. Local models run sequentially; Kev uses MLX on Metal and other local models use PyTorch MPS. Jev uses OpenRouter; CLEF uses Cloudflare Workers AI.")
    table = cases_table(pending_cases, questions)
    st.dataframe(table, hide_index=True, width="stretch")
    copy_table_button(table, "Copy test cases as Markdown", "copy_pending_cases")
