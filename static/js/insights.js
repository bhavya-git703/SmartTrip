async function loadInsights() {
  const response = await fetch("/api/ai-insights");
  const data = await response.json();
  document.getElementById("frames").innerHTML = data.frames.map(frame => `<article class="frame-card"><h3>${frame.name}</h3>
    <p><b>Location:</b> ${frame.location}</p><p><b>Estimated cost:</b> ₹${frame.estimated_cost}</p>
    <p><b>Duration:</b> ${frame.suggested_duration} days</p><p><b>Interests:</b> ${frame.interests.join(", ")}</p></article>`).join("");
  document.getElementById("rules").innerHTML = data.rules.map(rule => `<div class="rule-card"><b>${rule.id}</b>: IF ${JSON.stringify(rule.if)} THEN ${rule.then}</div>`).join("");
}
async function runSearch(algorithm) {
  document.getElementById("search-output").textContent = "Executing...";
  const response = await fetch("/api/search", {method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({algorithm,preferences:{budget:15000,days:3,interests:["Nature","Waterfalls","Adventure"],transport:"Any"}})});
  document.getElementById("search-output").textContent = JSON.stringify(await response.json(), null, 2);
}
loadInsights();
