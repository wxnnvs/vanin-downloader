chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'batchDownload' && Array.isArray(msg.files)) {
        for (let f of msg.files) {
            chrome.downloads.download({
                url: f.url,
                filename: f.filename,
                conflictAction: 'uniquify' // avoid overwriting
            }, id => {
                // optional callback; check chrome.runtime.lastError if needed
            });
        }
        sendResponse({ ok: true });
    }
    return true; // keep sendResponse valid if async
});