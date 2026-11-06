def is_duration_compatible(destination, requested_days, tolerance=1):
    return abs(int(destination["suggested_duration"]) - int(requested_days)) <= tolerance


def apply_constraints(destination, preferences):
    failures = []
    if float(destination["estimated_cost"]) > float(preferences["budget"]):
        failures.append("Estimated destination cost exceeds budget")
    if not is_duration_compatible(destination, preferences["days"]):
        failures.append("Suggested duration differs from requested duration by more than one day")
    preferred_transport = preferences.get("transport", "Any")
    if preferred_transport != "Any" and preferred_transport not in destination["transport"]:
        failures.append("Preferred transport is unavailable")
    return {"eligible": not failures, "rejected_for": failures}
