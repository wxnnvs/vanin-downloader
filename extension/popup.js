const runBtn = document.getElementById("runBtn");
const gobackBtn = document.getElementById("gobackBtn");
const statusThing = document.getElementById("status");
const command = document.getElementById("downloadName");

let downloadStarted = false;

// Get the active tab
chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
  const tab = tabs[0];

  if (tab && tab.url.includes("boardbooks.vanin.be")) {
    if (tab.url.includes("/Pages/ViewItem.aspx")) {
      statusThing.textContent = "You are on the iframe relay page.";
      gobackBtn.style.display = "block";
    } else {
      chrome.tabs.sendMessage(tab.id, { action: "getName" }, (response) => {
        if (response && response.name) {
          statusThing.textContent = `python3 merger.py --output "${response.name}.pdf"`;
        }
      });
      runBtn.style.display = "block";
    }
  } else {
    statusThing.textContent = "Not on the target page.";
  }

  // Run function in content script
  runBtn.onclick = () => {
    chrome.tabs.sendMessage(tab.id, { action: "runFunction" });
  };
  gobackBtn.onclick = () => {
    chrome.tabs.sendMessage(tab.id, { action: "goBack" });
  };
});
