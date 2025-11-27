
function go_to_iframe(){
  // find the path that is in the url after ?cp=
  const urlParams = new URLSearchParams(window.location.search);
  const cp = urlParams.get('cp');
  if (cp) {
    window.location.href = cp;
  }
}

function find_image_ulr(){
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

// The function you want to run in the page
function myInjectedFunction() {
    const url_base = find_image_ulr();
    if (!url_base) {
        alert("Could not find image URL base.");
        return;
    }

    let amount = parseInt(prompt("Enter amount of pages\n(see bottom):"), 10);
    if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid positive number.");
        return;
    }

    if (confirm(`Start downloading ${amount} pages?`)) {
        amount = amount + 10; // buffer
        for (let i = 0; i < amount; i++) {
            const a = document.createElement('a');
            a.href = `${url_base}/${i}.png`;
            a.download = `vanin-${i}.png`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        }
    }
}

// Listen for popup message
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "runFunction") {
    myInjectedFunction();
  }
});


// Listen for popup message
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "goBack") {
    go_to_iframe();
  }
});
