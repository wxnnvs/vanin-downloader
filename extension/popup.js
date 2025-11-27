const runBtn = document.getElementById("runBtn");
const gobackBtn = document.getElementById("gobackBtn");
const status = document.getElementById("status");

// Get the active tab
chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
  const tab = tabs[0];

  if (tab && tab.url.includes("boardbooks.vanin.be")) {
    if (tab.url.includes("/Pages/ViewItem.aspx")) {
      status.textContent = "You are on the iframe relay page.";
      gobackBtn.style.display = "block";
    } else {
      status.textContent = "Ready to download pages.";
      runBtn.style.display = "block";
    }
  } else {
    status.textContent = "Not on the target page.";
  }

  // Run function in content script
  runBtn.onclick = () => {
    chrome.tabs.sendMessage(tab.id, { action: "runFunction" });
  };
  gobackBtn.onclick = () => {
    chrome.tabs.sendMessage(tab.id, { action: "goBack" });
  };
});
