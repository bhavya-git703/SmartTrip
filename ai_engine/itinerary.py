def build_itinerary(destination, activities, preferences):
    interests = {item.lower() for item in preferences.get("interests", [])}
    ranked = []
    for activity in activities:
        if activity["name"] not in destination["activities"]:
            continue
        match_count = len(interests.intersection({tag.lower() for tag in activity["tags"]}))
        ranked.append((match_count, activity))
    ranked.sort(key=lambda item: (-item[0], item[1]["name"]))

    days = int(preferences["days"])
    schedule = [[] for _ in range(days)]
    used_hours = [0 for _ in range(days)]
    for _, activity in ranked:
        eligible = [i for i, hours in enumerate(used_hours) if hours + activity["duration_hours"] <= 7]
        if not eligible:
            continue
        day = min(eligible, key=lambda i: used_hours[i])
        schedule[day].append(activity["name"])
        used_hours[day] += activity["duration_hours"]
    arrival = "Arrival, local orientation, and accommodation check-in"
    return schedule
