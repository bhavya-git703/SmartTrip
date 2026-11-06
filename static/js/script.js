const money = value => `₹${Number(value).toLocaleString("en-IN")}`;
document.getElementById("trip-form").addEventListener("submit", async event => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const interests = [...document.querySelectorAll(".interest-grid input:checked")].map(input => input.value);
  if (!interests.length) { alert("Select at least one interest."); return; }
  const preferences = {starting_location: form.get("starting_location"), budget: Number(form.get("budget")),
    days: Number(form.get("days")), travellers: Number(form.get("travellers")), transport: form.get("transport"),
    accommodation: form.get("accommodation"), travel_preference: form.get("travel_preference"), interests};
  const response = await fetch("/api/plan", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(preferences)});
  const data = await response.json();
  const output = document.getElementById("plan-output");
  if (!response.ok) { output.innerHTML = `<div class="alert alert-danger">${data.error}</div>`; return; }
  if (!data.recommendations.length) { output.innerHTML = `<div class="alert alert-warning">${data.message}</div>`; return; }
  output.innerHTML = data.recommendations.map((plan, index) => `
    <article class="result-card"><h2>${index ? "" : "Recommended: "}${plan.destination.name}</h2>
    <p>${plan.destination.location} · ${plan.destination.type}</p><h3>Estimated total: ${money(plan.estimated_total)}</h3>
    <div class="score-grid"><span>Budget <strong>${plan.inference.facts.destination_cost_lte_budget}</strong></span><span>Interest <strong>${plan.inference.facts.interest_match}</strong></span><span>Transport <strong>${plan.inference.facts.transport_available}</strong></span><span>Greedy score <strong>${plan.heuristic_score}</strong></span></div>
    <h4>Cost breakdown</h4>${Object.entries(plan.component_costs).map(([name,cost]) => `<div class="cost-row"><span>${name}</span><b>${money(cost)}</b></div>`).join("")}
    <h4>Transport</h4><p>${plan.transport.mode} — ${money(plan.transport.cost)} (illustrative)</p>
    <h4>Accommodation</h4>${plan.accommodation_options.slice(0,3).map(stay => `<p>${stay.type}: ${money(stay.cost_per_night)} × ${stay.nights} nights = ${money(stay.total_cost)}</p>`).join("") || "<p>No accommodation option fits the trip budget.</p>"}
    <h4>Activities</h4>${plan.activities.map(activity => `<p>${activity.name} · ${activity.duration_hours}h · ${money(activity.cost)} · ${activity.tags.join(", ")}</p>`).join("")}
    <h4>Day-wise itinerary</h4>${plan.itinerary.map((items,i) => `<p><b>Day ${i+1}:</b> ${i === 0 ? "Arrival/check-in. " : ""}${items.join(", ") || "Local exploration and buffer time."}</p>`).join("")}
    <h4>Why it was selected</h4><ul>${plan.inference.rules_fired.map(rule => `<li>${rule.rule}: ${rule.explanation}</li>`).join("")}</ul></article>`).join("");
  document.getElementById("results").scrollIntoView({behavior:"smooth"});
});
