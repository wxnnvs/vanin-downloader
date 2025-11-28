
function go_to_iframe(){
  // find the path that is in the url after ?cp=
  const urlParams = new URLSearchParams(window.location.search);
  const cp = urlParams.get('cp');
  if (cp) {
    window.location.href = cp;
  }
}

function find_image_url(){
  // find an image with src starting with https://boardbooks.vanin.be/CMS/CDS/Van%20In/Published%20Content
  const images = document.querySelectorAll('img');
  for (const img of images) {
    if (img.src.startsWith('https://boardbooks.vanin.be/CMS/CDS/Van%20In/Published%20Content')) {
      // strip the ending /*.png
      return img.src.replace(/\/\d+\.png$/, '');
    }
  }
  return null;
}

function get_page_count(){
  // find the text that contains "Aantal pagina's: X"
  const texts = document.querySelectorAll('body *');
  for (const text of texts) {
    const match = text.textContent.match(/van\s*(\d+)/);
    if (match) {
      return parseInt(match[1], 10);
    }
  }
  return null;
}

function get_name(){
  // for example the url is https://boardbooks.vanin.be/CMS/CDS/Van%20In/Published%20Content/GENIE/GENIE%205%20biologie/GENIE%205%20Biologie%20Leerboek/js/index.html
  // extract the "GENIE 5 Biologie Leerboek"
  const path = window.location.pathname;
  const parts = path.split('/');
  if (parts.length >= 5) {
    return decodeURIComponent(parts[parts.length - 3]);
  }
  return null;
}

function downloadPages() {
    const url_base = find_image_url();
    if (!url_base) {
        alert("Could not find image URL base.");
        return;
    }

    let amount = get_page_count();
    if (!amount) {
        alert("Could not determine the number of pages.");
        return;
    }

    if (confirm(`Start downloading ${amount} pages?`)) {
    // if (true) {
        amount = amount + 5; // buffer
        const urls = [];
        for (let i = 0; i < amount; i++) {
            urls.push({ url: `${url_base}/${i}.png`, filename: `vanin-${i}.png` });
        }
        chrome.runtime.sendMessage({ type: 'batchDownload', files: urls });
    }
}

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "runFunction") {
    downloadPages();
  }
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "goBack") {
    go_to_iframe();
  }
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "getName") {
    // response with the name
    const name = get_name();
    return Promise.resolve({ name: name });
  }
});

// Automatically go to iframe on page load
window.addEventListener('load', () => {
  go_to_iframe();
});
