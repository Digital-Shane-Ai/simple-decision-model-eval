"""Markdown tables and a browser-side clipboard button (no model rerun)."""

import html
import json
from numbers import Integral, Real

import pandas as pd
import streamlit.components.v2 as components

from compare import display_answer


def table_markdown(frame):
    def cell(value, column):
        if pd.isna(value):
            return ""
        if "Brier" not in column and isinstance(value, Real) and not isinstance(value, Integral):
            value = f"{value:.2f}"
        text = html.escape(str(value), quote=False).replace("\r\n", "\n").replace("\r", "\n")
        for char in ("\\", "|", "`", "*", "_", "[", "]", "~"):
            text = text.replace(char, "\\" + char)
        return text.replace("\n", "<br>")

    def row(values):
        return "| " + " | ".join(cell(value, column) for column, value in zip(frame.columns, values)) + " |"

    return "\n".join([row(frame.columns), row(["---"] * len(frame.columns)),
                      *(row(values) for values in frame.itertuples(index=False, name=None))])


def cases_table(cases, questions=None):
    if questions is not None:
        return pd.DataFrame([{
            "Case ID": c["id"], "Context": c["message"], "Question ID": qid,
            "Question": question["instructions"],
            "Expected": display_answer(expected),
            **({"Choices": json.dumps(question["criteria"], ensure_ascii=False)} if question.get("type") == "choice" else {}),
        } for c in cases for qid, question in questions.items()
          for expected in [c.get("expected_answers", {}).get(qid, c.get("expected") if qid == "refund_requested" else None)]],
          columns=["Case ID", "Context", "Question ID", "Question", "Expected"] +
                  (["Choices"] if any(q.get("type") == "choice" for q in questions.values()) else []))
    return pd.DataFrame([{
        "Case ID": c["id"], "Customer message": c["message"],
        "Expected": "Unknown" if c["expected"] is None else "Yes" if c["expected"] else "No",
    } for c in cases], columns=["Case ID", "Customer message", "Expected"])


def make_copy_table_button():
    _copy = components.component(
        "markdown_copy",
        html='<span role="status" aria-live="polite"></span>'
             '<textarea hidden readonly aria-label="Markdown to copy manually"></textarea>',
        css="""
        textarea { box-sizing: border-box; width: 100%; height: 10rem;
          color: var(--st-text-color); background: var(--st-background-color); }
        """,
        js="""
        export default function({ data, parentElement }) {
          const host = (parentElement.host || parentElement).closest('[data-testid="stElementContainer"]');
          // v2 rerenders data without unmounting the component. Release the
          // previous observer/button before attaching this render's values.
          host.__decisionCopyCleanup?.();
          const table = host.previousElementSibling?.querySelector('[data-testid="stDataFrame"]');
          const status = parentElement.querySelector('[role="status"]');
          const fallback = parentElement.querySelector('textarea');
          fallback.value = data.markdown;
          fallback.hidden = true;
          let button, wrapper, timer;
          const copyIcon = '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>';
          const showFallback = () => {
            host.style.display = '';
            status.textContent = 'Select and copy the Markdown below.';
            fallback.hidden = false;
            fallback.focus();
            fallback.select();
          };
          const attach = () => {
            if (button?.isConnected) return;
            const download = table?.querySelector('button[aria-label="Download as CSV"]');
            if (!download) return;
            const downloadWrapper = download.closest('[data-testid="stElementToolbarButton"]');
            wrapper = downloadWrapper.cloneNode(false);
            button = download.cloneNode(false);
            button.setAttribute('aria-label', data.label);
            button.setAttribute('title', data.label);
            button.setAttribute('data-testid', 'copy-markdown');
            button.innerHTML = copyIcon;
            button.onclick = async () => {
              try {
                await navigator.clipboard.writeText(data.markdown);
                button.title = 'Copied!';
                button.innerHTML = '<span aria-hidden="true">✓</span>';
                clearTimeout(timer);
                timer = setTimeout(() => { button.innerHTML = copyIcon; button.title = data.label; }, 1500);
              } catch { showFallback(); }
            };
            wrapper.appendChild(button);
            downloadWrapper.after(wrapper);
            host.style.display = 'none';
          };
          // Streamlit can remount the toolbar when a table enters fullscreen.
          const observer = new MutationObserver(attach);
          if (table) {
            observer.observe(table, {childList:true, subtree:true});
            attach();
          } else { showFallback(); }
          const cleanup = () => {
            observer.disconnect();
            clearTimeout(timer);
            if (button) button.onclick = null;
            wrapper?.remove();
            host.style.display = '';
          };
          host.__decisionCopyCleanup = cleanup;
          return cleanup;
        }
        """,
    )


    def copy_table_button(frame, label, key):
        # Pass user text as data, never interpolate it into executable HTML or JS.
        _copy(data={"label": label, "markdown": table_markdown(frame)}, key=key)

    return copy_table_button
