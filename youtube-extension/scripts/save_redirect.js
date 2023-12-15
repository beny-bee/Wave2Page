chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    console.log("Background: Received message", message);
    if (message.action === "processCurrentTab") {
        // Add the logic you want to execute
        console.log("Background: Processing current tab");
        // Get the active tab's URL
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            var activeTab = tabs[0];
            var activeTabUrl = activeTab.url;

            // Check if it's a YouTube video URL
            if (activeTabUrl.includes("youtube.com/")) {

                if (message.filename) {
                    console.log('Filename: ' + message.filename);
                    // Store the filename in Chrome storage
                    chrome.storage.local.set({ 'filename': message.filename }, function() {
                        console.log('Filename is saved in storage.');
                    });
                } else {
                    console.log('No filename entered');
                }

                console.log("YouTube URL detected:", activeTabUrl);
                    // Store the URL
                chrome.storage.local.set({ 'youtubeURL': activeTabUrl }, function() {
                    console.log('URL is stored in chrome.storage.local');
                });
                sendResponse({ status: "YouTube URL processed", url: activeTabUrl });
                chrome.tabs.update(activeTab.id, { url: "http://127.0.0.1:5000/service" });
                console.log("Redirecting...");
            } else {
                console.log("Not a YouTube URL.");
                sendResponse({status: "Not a YouTube URL"});
            }
        });
        return true; 
    }
});

