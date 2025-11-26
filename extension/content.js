// The function you want to run in the page
function myInjectedFunction() {
    let amount = parseInt(prompt("Enter amount of pages\n(see bottom):"), 10);
    if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid positive number.");
        return;
    }

    if (confirm(`Start downloading ${amount} pages?`)) {
        amount = amount + 10; // buffer
        for (let i = 0; i < amount; i++) {
            const a = document.createElement('a');
            a.href = `https://boardbooks.vanin.be/CMS/CDS/Van%20In/Published%20Content/GENIE/GENIE%205%20biologie/GENIE%205%20Biologie%20Leerboek/Resources/606864_01_GENIE_5_BIO.pdf_/${i}.png`;
            a.download = `${i}.png`;
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
