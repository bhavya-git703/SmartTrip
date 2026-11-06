import unittest
import json
from pathlib import Path

from ai_engine.search import bfs, dfs, greedy_best_first
from ai_engine.inference import ForwardChainingInference
from ai_engine.heuristic import score_destination
from ai_engine.recommender import recommend_destinations

ROOT = Path(__file__).resolve().parents[1]
DESTINATIONS = json.loads((ROOT / "knowledge_base" / "destinations.json").read_text())
ACTIVITIES = json.loads((ROOT / "knowledge_base" / "activities.json").read_text())
ACCOMMODATION = json.loads((ROOT / "knowledge_base" / "accommodation.json").read_text())


class SearchGraph:
    graph = {"Araku": [{"target": "Nature"}, {"target": "Train"}],
             "Nature": [{"target": "Waterfalls"}], "Train": [], "Waterfalls": []}
    def neighbors(self, node):
        return [edge["target"] for edge in self.graph.get(node, [])]


class SmartTripTests(unittest.TestCase):
    def test_bfs_and_dfs_are_real_traversals(self):
        graph = SearchGraph()
        self.assertEqual(bfs(graph, "Araku")["order"], ["Araku", "Nature", "Train", "Waterfalls"])
        self.assertEqual(dfs(graph, "Araku")["order"], ["Araku", "Nature", "Waterfalls", "Train"])

    def test_forward_chaining_araku(self):
        preferences = {"budget": 15000, "days": 3, "interests": ["Nature", "Waterfalls", "Adventure"], "transport": "Train"}
        result = ForwardChainingInference().infer(next(d for d in DESTINATIONS if d["id"] == "araku"), preferences)
        self.assertTrue(result["recommended"])
        self.assertIn("recommend_destination", result["conclusions"])

    def test_scenario_outputs_exist(self):
        scenarios = [
            {"budget": 15000, "days": 3, "interests": ["Nature", "Waterfalls", "Adventure"], "transport": "Train", "accommodation": "Any", "travel_preference": "Balanced"},
            {"budget": 10000, "days": 3, "interests": ["Beaches", "Adventure"], "transport": "Bus", "accommodation": "Any", "travel_preference": "Budget"},
            {"budget": 20000, "days": 5, "interests": ["Trekking", "Nature"], "transport": "Any", "accommodation": "Any", "travel_preference": "Balanced"},
            {"budget": 1000, "days": 3, "interests": ["Nature"], "transport": "Any", "accommodation": "Any", "travel_preference": "Budget"}
        ]
        for preferences in scenarios[:-1]:
            result = recommend_destinations(DESTINATIONS, ACTIVITIES, ACCOMMODATION, preferences)
            self.assertTrue(result["ranked"])
        empty = recommend_destinations(DESTINATIONS, ACTIVITIES, ACCOMMODATION, scenarios[-1])
        self.assertEqual(empty["ranked"], [])


if __name__ == "__main__":
    unittest.main()
