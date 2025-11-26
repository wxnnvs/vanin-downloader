const runBtn = document.getElementById("runBtn");
const status = document.getElementById("status");

// Get the active tab
chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
  const tab = tabs[0];

  if (tab && tab.url.includes("https://boardbooks.vanin.be/Pages/ViewItem.aspx")) {
    status.textContent = "You are on the right page.";
    runBtn.style.display = "block";
  } else {
    status.textContent = "Not on the target page.";
  }

  // Run function in content script
  runBtn.onclick = () => {
    chrome.tabs.sendMessage(tab.id, { action: "runFunction" });
  };
});
