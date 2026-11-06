def clamp(value):
    return max(0.0, min(100.0, float(value)))


def score_destination(destination, preferences):
    budget = float(preferences["budget"])
    days = int(preferences["days"])
    interests = {item.lower() for item in preferences.get("interests", [])}
    transport = preferences.get("transport", "Any")

    estimate = float(destination["estimated_cost"])
    if budget <= 0:
        budget_score = 0.0
    elif estimate <= budget:
        budget_score = 100.0 - (max(0.0, estimate / budget - 0.8) * 100.0)
    else:
        budget_score = max(0.0, 100.0 * budget / estimate)
    budget_score = clamp(budget_score)

    destination_interests = {item.lower() for item in destination["interests"]}
    matching = len(interests & destination_interests)
    interest_score = clamp(100.0 * matching / len(interests)) if interests else 100.0

    available = {item.lower() for item in destination["transport"]}
    if transport.lower() == "any" or transport.lower() in available:
        transport_score = 100.0
    else:
        transport_score = 0.0

    suggested = int(destination["suggested_duration"])
    duration_score = clamp(100.0 - min(100.0, abs(suggested - days) / max(days, 1) * 100.0))

    final_score = 0.4 * budget_score + 0.3 * interest_score + 0.2 * transport_score + 0.1 * duration_score
    return {
        "destination": destination["name"],
        "budget_score": round(budget_score, 2),
        "interest_score": round(interest_score, 2),
        "transport_score": round(transport_score, 2),
        "duration_score": round(duration_score, 2),
        "weighted_score": round(final_score, 2),
        "matching_interests": sorted(interests & destination_interests, key=str.lower)
    }
