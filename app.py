import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from ai_engine.constraints import apply_constraints
from ai_engine.heuristic import score_destination
from ai_engine.inference import ForwardChainingInference
from ai_engine.itinerary import build_itinerary
from ai_engine.recommender import recommend_destinations
from ai_engine.search import bfs, dfs, greedy_best_first
from knowledge_base.semantic_network import SemanticNetwork

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "knowledge_base"


def load_json(name):
    return json.loads((KB_DIR / name).read_text(encoding="utf-8"))


app = Flask(__name__)
DESTINATIONS = load_json("destinations.json")
ACTIVITIES = load_json("activities.json")
ACCOMMODATION = load_json("accommodation.json")
RULES = load_json("rules.json")
TRANSPORTATION = load_json("transportation.json")
SEMANTIC_NETWORK = SemanticNetwork(DESTINATIONS, ACTIVITIES)


def validate_preferences(data):
    required = ["budget", "days", "interests", "transport"]
    missing = [key for key in required if key not in data]
    if missing:
        return None, f"Missing fields: {', '.join(missing)}"
    try:
        budget = float(data["budget"])
        days = int(data["days"])
    except (TypeError, ValueError):
        return None, "Budget and days must be numbers"
    if budget <= 0 or days <= 0:
        return None, "Budget and days must be greater than zero"
    interests = data["interests"]
    if isinstance(interests, str):
        interests = [interests]
    normalized = {
        "budget": budget,
        "days": days,
        "interests": interests,
        "transport": data["transport"],
        "accommodation": data.get("accommodation", "Any"),
        "travel_preference": data.get("travel_preference", "Balanced"),
        "travellers": int(data.get("travellers", 1))
    }
    return normalized, None


def serializable_plan(plan, preferences):
    destination = plan["destination"]
    itinerary = build_itinerary(destination, ACTIVITIES, preferences)
    inference = ForwardChainingInference(RULES).infer(destination, preferences)
    backward = ForwardChainingInference(RULES).backward_check(destination, preferences)
    activities = []
    for name in plan["activities"]:
        activity = next(item for item in ACTIVITIES if item["name"] == name)
        activities.append({"name": name, "tags": activity["tags"], "duration_hours": activity["duration_hours"],
                           "cost": activity["cost"]})
    return {
        "destination": destination,
        "heuristic_score": plan["heuristic_score"],
        "transport": plan["transport"],
        "accommodation_options": plan["accommodation_options"],
        "activities": activities,
        "itinerary": itinerary,
        "component_costs": plan["component_costs"],
        "estimated_total": plan["estimated_total"],
        "inference": inference,
        "backward_chaining": backward
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/insights")
def insights():
    return render_template("insights.html")


@app.route("/api/plan", methods=["POST"])
def api_plan():
    preferences, error = validate_preferences(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    result = recommend_destinations(DESTINATIONS, ACTIVITIES, ACCOMMODATION, preferences)
    if not result["ranked"]:
        return jsonify({"recommendations": [], "evaluations": result["evaluations"],
                        "message": "No destination satisfies both the hard constraints and the available budget."})
    return jsonify({"recommendations": [serializable_plan(plan, preferences) for plan in result["ranked"]],
                    "evaluations": result["evaluations"]})


@app.route("/api/destinations")
def api_destinations():
    return jsonify(DESTINATIONS)


@app.route("/api/ai-insights")
def api_ai_insights():
    return jsonify({"frames": DESTINATIONS, "semantic_network": SEMANTIC_NETWORK.facts(),
                    "rules": RULES})


@app.route("/api/search", methods=["POST"])
def api_search():
    payload = request.get_json(silent=True) or {}
    algorithm = payload.get("algorithm", "BFS").upper()
    preferences, error = validate_preferences(payload.get("preferences", {
        "budget": 15000, "days": 3, "interests": ["Nature"], "transport": "Any"}))
    if error:
        return jsonify({"error": error}), 400
    start = payload.get("start") or DESTINATIONS[0]["name"]
    if algorithm == "DFS":
        result = dfs(SEMANTIC_NETWORK, start)
    elif algorithm in ("GREEDY", "BEST-FIRST", "GREEDY BEST-FIRST"):
        def heuristic(node):
            destination = next((item for item in DESTINATIONS if item["name"] == node), None)
            if not destination:
                return 0
            return score_destination(destination, preferences)["weighted_score"]
        result = greedy_best_first(SEMANTIC_NETWORK, start, DESTINATIONS, heuristic)
    else:
        result = bfs(SEMANTIC_NETWORK, start)
    return jsonify(result)


@app.route("/api/inference", methods=["POST"])
def api_inference():
    payload = request.get_json(silent=True) or {}
    destination_id = payload.get("destination_id")
    destination = next((item for item in DESTINATIONS if item["id"] == destination_id), None)
    if not destination:
        return jsonify({"error": "Destination not found"}), 404
    preferences, error = validate_preferences(payload.get("preferences", {}))
    if error:
        return jsonify({"error": error}), 400
    inference = ForwardChainingInference(RULES)
    return jsonify({"forward": inference.infer(destination, preferences),
                    "backward": inference.backward_check(destination, preferences)})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
