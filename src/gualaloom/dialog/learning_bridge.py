"""
Learning bridge — pattern promotion + token addition.

IMMEDIATE learning: observed patterns get promoted to templates after
count=1. Don't raise this threshold — Joe diagnosed count>=3 as confinement.
"""


def learn_pattern_immediately(response_templates, input_class, response_classes_used):
    """IMMEDIATE learning — any observed pattern becomes a candidate template
    after count=1. This is the v6 threshold. Do NOT raise it."""
    if not response_classes_used:
        return False
    template = [(c, "PREDICATE") for c in response_classes_used]
    new_signature = tuple(c for c, r in template)
    existing = response_templates.get(input_class, [])
    if existing:
        existing_sig = tuple(c for c, r in existing) if isinstance(existing[0], tuple) else (existing[0],)
        if new_signature == existing_sig:
            return False
    response_templates[input_class] = template
    return True
