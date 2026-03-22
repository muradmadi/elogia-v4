// Script to clear stale asset state from localStorage
// Run this in browser console if you see old asset IDs

console.log("Clearing stale asset state from localStorage...");

// Clear asset state
localStorage.removeItem("asset_state");
localStorage.removeItem("asset_state_timestamp");

// Clear enrichment state too (just in case)
localStorage.removeItem("enrichment_state");

console.log("✅ LocalStorage cleared!");
console.log("Refresh the page to see clean state.");

// Optional: Show what was cleared
console.log("Previous asset_state:", localStorage.getItem("asset_state"));
console.log(
  "Previous enrichment_state:",
  localStorage.getItem("enrichment_state"),
);
