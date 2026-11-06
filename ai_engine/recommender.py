from ai_engine.heuristic import score_destination
from ai_engine.constraints import apply_constraints
from ai_engine.inference import ForwardChainingInference


TRANSPORT_COST = {"Train": 1800, "Bus": 1200, "Flight": 6500}


def recommend_destinations(destinations, activities, accommodation, preferences):
    inference = ForwardChainingInference()
    activity_by_name = {activity["name"]: activity for activity in activities}
    ranked = []
    evaluations = []
    for destination in destinations:
        constraint_result = apply_constraints(destination, preferences)
        scores = score_destination(destination, preferences)
        inferred = inference.infer(destination, preferences)
        evaluations.append({
            "destination": destination["name"],
            "constraint": constraint_result,
            "scores": scores,
            "inference": inferred
        })
        if not constraint_result["eligible"]:
            continue
        if not inferred["recommended"]:
            continue

        transport = choose_transport(destination, preferences)
        nights = max(1, int(preferences["days"]) - 1)
        stays = choose_accommodation(destination, accommodation, preferences, nights)
        selected_activities = rank_activities(destination, activities, preferences)
        activity_cost = sum(activity_by_name[name]["cost"] for name in selected_activities)
        estimated_total = destination["estimated_cost"] + transport["cost"] + (stays[0]["total_cost"] if stays else 0) + activity_cost
        if estimated_total > float(preferences["budget"]):
            continue
        ranked.append({
            "destination": destination,
            "heuristic_score": scores["weighted_score"],
            "transport": transport,
            "accommodation_options": stays,
            "activities": selected_activities,
            "estimated_total": estimated_total,
            "component_costs": {
                "destination": destination["estimated_cost"],
                "transport": transport["cost"],
                "accommodation": stays[0]["total_cost"] if stays else 0,
                "activities": activity_cost
            }
        })
    ranked.sort(key=lambda item: (-item["heuristic_score"], item["destination"]["name"]))
    return {"ranked": ranked, "evaluations": evaluations}


def choose_transport(destination, preferences):
    preferred = preferences.get("transport", "Any")
    options = [mode for mode in destination["transport"] if preferred == "Any" or mode == preferred]
    if not options:
        options = destination["transport"]
    selected = min(options, key=lambda mode: TRANSPORT_COST.get(mode, 999999))
    return {"mode": selected, "cost": TRANSPORT_COST.get(selected, 0),
            "illustrative": True, "preferred_unavailable": preferred != "Any" and preferred not in destination["transport"]}


def choose_accommodation(destination, accommodation, preferences, nights):
    preferred_type = preferences.get("accommodation", "Any")
    comfort = preferences.get("travel_preference", "Balanced")
    options = []
    budget = float(preferences["budget"])
    for item in accommodation:
        if item["type"] not in destination["accommodation"]:
            continue
        if preferred_type != "Any" and item["type"] != preferred_type:
            continue
        if comfort == "Budget" and item["comfort"] != "Budget" and item["type"] not in ("Hostel", "Homestay"):
            continue
        total = item["cost_per_night"] * nights
        if total <= budget * 0.35:
            options.append({"type": item["type"], "cost_per_night": item["cost_per_night"],
                            "nights": nights, "total_cost": total, "comfort": item["comfort"]})
    options.sort(key=lambda item: (item["total_cost"], item["type"]))
    return options[:5]


def rank_activities(destination, activities, preferences):
    user_interests = {tag.lower() for tag in preferences.get("interests", [])}
    matched = []
    by_name = {activity["name"]: activity for activity in activities}
    for name in destination["activities"]:
        activity = by_name.get(name)
        if not activity:
            continue
        count = len(user_interests.intersection({tag.lower() for tag in activity["tags"]}))
        matched.append((count, activity["name"]))
    matched.sort(key=lambda item: (-item[0], item[1]))
    return [name for _, name in matched]
