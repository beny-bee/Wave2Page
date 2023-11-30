document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('testButton').addEventListener('click', function() {
        console.log("Button clicked");
        // Send message to background script
        chrome.runtime.sendMessage({ action: "processCurrentTab" }, function(response) {
            if (response) {
                console.log("Response from background:", response);
            } else {
                console.log("No response received");
            }
        });
        window.close();
    });
});
