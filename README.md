# SmartTrip

SmartTrip is a Flask-based intelligent travel planner that visibly implements BFS, DFS, greedy best-first search, heuristic scoring, a JSON/frame knowledge base, a semantic network and forward/backward rule inference.

## Run
1. `python -m pip install -r requirements.txt`
2. `python app.py`
3. Open `http://127.0.0.1:5000`
4. Open **How SmartTrip Thinks** for live algorithm execution.

## AI implementation map
- `knowledge_base/destinations.json`, `activities.json`, etc.: frame-style attribute/value knowledge.
- `knowledge_base/semantic_network.py`: semantic graph relationships.
- `ai_engine/search.py`: manual queue BFS, stack/recursive DFS and heap priority-queue greedy search.
- `ai_engine/heuristic.py`: normalized 0.4 budget + 0.3 interests + 0.2 transport + 0.1 duration scoring.
- `ai_engine/constraints.py`: hard budget, duration and transport constraints.
- `ai_engine/inference.py`: data-driven forward chaining and backward-condition demonstration.
- `ai_engine/recommender.py`: constraint filtering, inference, ranking and component recommendations.
- `ai_engine/itinerary.py`: interest-ranked time-bounded itinerary scheduling.
- `app.py`: Flask pages and JSON APIs.

## Tests
`python -m unittest discover -s tests -v`
