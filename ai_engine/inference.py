import json
from pathlib import Path


class ForwardChainingInference:
    def __init__(self, rules=None):
        if rules is None:
            rules_path = Path(__file__).resolve().parents[1] / "knowledge_base" / "rules.json"
            rules = json.loads(rules_path.read_text(encoding="utf-8"))
        self.rules = rules

    def infer(self, destination, preferences):
        facts = {"user_budget": float(preferences["budget"]),
                 "requested_duration": int(preferences["days"]),
                 "preferred_transport": preferences.get("transport", "Any"),
                 "travel_preference": preferences.get("travel_preference", "Balanced")}
        interests = set(preferences.get("interests", []))
        facts["destination_cost_lte_budget"] = destination["estimated_cost"] <= facts["user_budget"]
        facts["interest_match"] = bool(interests.intersection(destination["interests"]))
        facts["transport_available"] = facts["preferred_transport"] == "Any" or facts["preferred_transport"] in destination["transport"]

        fired = []
        conclusions = []
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                conditions = rule["if"]
                if rule["then"] in facts and facts[rule["then"]]:
                    continue
                applies = True
                for key, expected in conditions.items():
                    if key == "user_interest":
                        applies = applies and expected in interests
                    elif key not in facts or facts[key] != expected:
                        applies = False
                if applies:
                    facts[rule["then"]] = True
                    conclusions.append(rule["then"])
                    fired.append({"rule": rule["id"], "then": rule["then"], "explanation": rule["explanation"]})
                    changed = True
        return {"facts": facts, "rules_fired": fired, "conclusions": conclusions,
                "recommended": facts.get("recommend_destination", False)}

    def backward_check(self, destination, preferences):
        result = self.infer(destination, preferences)
        required = [("destination_is_affordable", result["facts"].get("destination_cost_lte_budget", False)),
                    ("destination_is_relevant", result["facts"].get("interest_match", False)),
                    ("transport_is_suitable", result["facts"].get("transport_available", False))]
        goal_reached = result["recommended"]
        return {"goal": f"Is {destination['name']} suitable for this user?",
                "conditions": required, "goal_reached": goal_reached}
