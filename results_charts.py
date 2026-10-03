"""Saved-run chart data and Vega-Lite specs; no inference or draft mutations."""

import math
from numbers import Real

from compare import MODELS, display_answer, ordered_model_keys, ordered_results, summarize
from model_config import is_hosted


LOCAL_COLOR = "#176b8a"
API_COLOR = "#ac4b13"


def chart_identity(row):
    """Execution colors and redundant API text also work with legacy exports."""
    execution = row.get("execution") or ("hosted" if is_hosted(MODELS[row["model_key"]]) else "local")
    name = row["name"]
    return {"Model": name, "Chart model": f"API · {name}" if execution == "hosted" else name,
            "Execution": execution, "Runtime": "Hosted API" if execution == "hosted" else "Local"}


def runtime_color():
    return {"field": "Runtime", "type": "nominal", "title": "Execution",
            "scale": {"domain": ["Local", "Hosted API"], "range": [LOCAL_COLOR, API_COLOR]},
            "legend": {"symbolOpacity": 1}}


def finite_number(value, minimum=0, maximum=None):
    return (isinstance(value, Real) and not isinstance(value, bool)
            and math.isfinite(value) and value >= minimum
            and (maximum is None or value <= maximum))


def score_data(rows):
    """Reuse scoring denominators; missing accuracy never becomes zero."""
    values = []
    keys = ordered_model_keys({row['model_key'] for row in rows})
    summaries = list(zip(keys, summarize(rows)))
    # Stable sort retains registry order for exact ties. Missing accuracy stays last;
    # coverage is the displayed ranking only when no accuracy is available at all.
    has_accuracy = any(finite_number(model['accuracy_on_answered'], maximum=1) for _, model in summaries)
    field = 'accuracy_on_answered' if has_accuracy else 'coverage'
    summaries.sort(key=lambda pair: (pair[1][field] is None, -(pair[1][field] or 0)))
    identities = {r['model_key']: chart_identity(r) for r in ordered_results(rows)}
    for key, model in summaries:
        scored = sum(r['status'] == 'ok' and r['expected'] is not None
                     for r in rows if r['model_key'] == key)
        for metric, value, numerator, denominator in (
            ('Accuracy', model['accuracy_on_answered'], model['correct'], scored),
            ('Coverage', model['coverage'], model['answered'], model['cases']),
        ):
            if finite_number(value, maximum=1):
                values.append({**identities[key], 'Metric': metric, 'Value': value,
                               'Count': f'{numerator} / {denominator}'})
    return values


def probability_data(rows, question, option):
    """Plot only returned probabilities from successful answers, including zero."""
    values = []
    for row in ordered_results(rows):
        if row['status'] != 'ok':
            continue
        probability = ((row.get('probabilities') or {}).get(option) if question['type'] == 'choice'
                       else row.get('probability_yes' if option == 'Yes' else 'probability_no'))
        if question['type'] == 'noul' and probability is None and option == 'No':
            yes = row.get('probability_yes')
            if finite_number(yes, maximum=1):
                probability = 1 - yes
        if not finite_number(probability, maximum=1):
            continue
        decision = display_answer(row.get('decision', row.get('wants_refund')))
        values.append({**chart_identity(row), 'Value': probability, 'Answer': option,
                       'Decision': decision, 'Expected': display_answer(row['expected']),
                       'Selection': 'Selected answer' if decision == option else 'Other answer',
                       'Label': f'{probability:.1%}'})
    return values


def brier_data(rows, kind):
    field = 'brier_score' if kind == 'noul' else 'choice_brier_score'
    identities = {r['name']: chart_identity(r) for r in ordered_results(rows)}
    values = [{**identities[model['model']], 'Value': model[field]}
              for model in summarize(rows) if finite_number(model[field], maximum=1 if kind == 'noul' else 2)]
    return sorted(values, key=lambda value: value['Value'])


def timing_data(rows):
    """One observed timing per model/context, even for multi-question runs."""
    contexts = {}
    for row in ordered_results(rows):
        seconds = row.get('inference_seconds')
        if row['status'] == 'ok' and finite_number(seconds):
            contexts.setdefault((row['model_key'], row['case_id']), row)
    models = {}
    for row in contexts.values():
        model = models.setdefault(row['model_key'], {
            **chart_identity(row), 'seconds': [],
        })
        model['seconds'].append(row['inference_seconds'])
    values = [{**{k: v for k, v in model.items() if k != 'seconds'},
               'Seconds': sum(model['seconds']) / len(model['seconds']),
               'Timed contexts': len(model['seconds'])} for model in models.values()]
    return sorted(values, key=lambda value: value['Seconds'])


def base_spec(values, description, row_height=34):
    names = list(dict.fromkeys(value['Chart model'] for value in values))
    return {
        '$schema': 'https://vega.github.io/schema/vega-lite/v6.json',
        'description': description, 'data': {'values': values},
        'height': max(180, len(names) * row_height + 70),
        'encoding': {'y': {'field': 'Chart model', 'type': 'nominal', 'sort': names,
                           'axis': {'title': None, 'labelLimit': 155, 'labelFontSize': 11, 'labelPadding': 10,
                                    'labelOverlap': False}}},
        'config': {'view': {'stroke': None},
                   'axis': {'labelFontSize': 12, 'titleFontSize': 12, 'gridColor': '#e5eaf1'},
                   'legend': {'orient': 'top', 'direction': 'vertical', 'labelFontSize': 11}},
    }


def score_spec(values):
    spec = base_spec(values, 'Model accuracy on answered labeled pairs and coverage of all answer pairs.')
    spec['mark'] = {'type': 'point', 'filled': True, 'size': 110, 'opacity': 1}
    spec['encoding'].update({
        'x': {'field': 'Value', 'type': 'quantitative', 'scale': {'domain': [0, 1]},
              'axis': {'title': 'Share of answer pairs', 'format': '.0%', 'tickCount': 5}},
        'yOffset': {'field': 'Metric', 'scale': {'domain': ['Accuracy', 'Coverage']}},
        'color': runtime_color(),
        'shape': {'field': 'Metric', 'type': 'nominal', 'scale': {'domain': ['Accuracy', 'Coverage'],
                                             'range': ['circle', 'diamond']}},
        'tooltip': [{'field': 'Model'}, {'field': 'Runtime', 'title': 'Execution'}, {'field': 'Metric'},
                    {'field': 'Value', 'title': 'Share', 'format': '.1%'},
                    {'field': 'Count', 'title': 'Answer pairs'}],
    })
    return spec


def probability_spec(values, binary=False):
    spec = base_spec(values, 'Returned probability of the selected chart answer for each successful model.')
    spec['encoding'].update({
        'x': {'field': 'Value', 'type': 'quantitative', 'scale': {'domain': [0, 1]},
              'axis': {'title': 'Returned probability', 'format': '.0%', 'tickCount': 5}},
        'color': runtime_color(),
        'tooltip': [{'field': 'Model'}, {'field': 'Runtime', 'title': 'Execution'}, {'field': 'Answer'},
                    {'field': 'Value', 'title': 'Probability', 'format': '.2%'},
                    {'field': 'Decision'}, {'field': 'Expected'}],
    })
    spec['layer'] = [
        {'mark': {'type': 'bar', 'opacity': .2, 'height': 14}},
        {'mark': {'type': 'point', 'filled': True, 'size': 100, 'opacity': 1},
         'encoding': {
             'shape': {'field': 'Selection', 'type': 'nominal', 'scale': {'domain': ['Selected answer', 'Other answer'],
                                                       'range': ['circle', 'diamond']}},
         }},
        {'mark': {'type': 'text', 'align': 'left', 'dx': 9, 'fontSize': 11, 'color': '#172033'},
         'transform': [{'filter': 'datum.Value < 0.85'}], 'encoding': {'text': {'field': 'Label'}}},
        {'mark': {'type': 'text', 'align': 'right', 'dx': -9, 'fontSize': 11, 'color': '#172033'},
         'transform': [{'filter': 'datum.Value >= 0.85'}], 'encoding': {'text': {'field': 'Label'}}},
    ]
    if binary:
        spec['layer'].insert(0, {'data': {'values': [{'threshold': .5}]},
                                'mark': {'type': 'rule', 'color': '#94a3b8', 'strokeDash': [4, 4]},
                                'encoding': {'x': {'field': 'threshold', 'type': 'quantitative'},
                                             'y': {'value': 0}, 'y2': {'value': {'expr': 'height'}},
                                             'tooltip': {'value': 'Binary decision threshold: 50%'}}})
    return spec


def brier_spec(values, kind):
    maximum = 1 if kind == 'noul' else 2
    spec = base_spec(values, 'Brier probabilistic error on answered labeled pairs; lower is better.')
    spec['mark'] = {'type': 'bar', 'height': 17, 'cornerRadiusEnd': 3}
    spec['encoding'].update({
        'x': {'field': 'Value', 'type': 'quantitative', 'scale': {'domain': [0, maximum]},
              'axis': {'title': 'Binary Brier (0–1)' if kind == 'noul' else 'Choice Brier (0–2)',
                       'tickCount': 5}},
        'color': runtime_color(),
        'tooltip': [{'field': 'Model'}, {'field': 'Runtime', 'title': 'Execution'},
                    {'field': 'Value', 'title': 'Brier', 'format': '.8f'}],
    })
    return spec


def timing_spec(values):
    spec = base_spec(values, 'Mean observed context inference time, counting each context once per model.')
    # Relative room for end labels keeps zero fixed even on narrow mobile charts.
    maximum = max((value['Seconds'] for value in values), default=0)
    domain = [0, maximum * 1.2 if maximum else 1]
    spec['layer'] = [
        {'mark': {'type': 'bar', 'height': 17, 'cornerRadiusEnd': 3}},
        {'mark': {'type': 'text', 'align': 'left', 'dx': 6, 'fontSize': 11, 'color': '#172033'},
         'encoding': {'text': {'field': 'Seconds', 'format': '.2f'}}},
    ]
    spec['encoding'].update({
        'x': {'field': 'Seconds', 'type': 'quantitative', 'scale': {'zero': True, 'domain': domain},
              'axis': {'title': 'Mean elapsed seconds / context', 'tickCount': 5}},
        'color': runtime_color(),
        'tooltip': [{'field': 'Model'}, {'field': 'Runtime', 'title': 'Execution'}, {'field': 'Seconds', 'format': '.3f'},
                    {'field': 'Timed contexts'}],
    })
    return spec
