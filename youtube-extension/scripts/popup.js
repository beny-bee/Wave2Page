document.addEventListener('DOMContentLoaded', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const currentTab = tabs[0];
        const isYoutubeVideo = currentTab.url.includes('youtube.com/watch');
        
        if (!isYoutubeVideo) {
            document.getElementById('testButton').disabled = true;
            document.getElementById('error-message').style.display = 'block';
        }
    });

    document.getElementById('testButton').addEventListener('click', function () {
        console.log("Button clicked");
            
        // Retrieve the filename from the input field
        const filename = document.getElementById('filename').value;
        console.log('Filename: ' + filename);

        //Send message to background script
        chrome.runtime.sendMessage({ action: "processCurrentTab", filename: filename }, function(response) {
            if (response) {
                console.log("Response from background:", response);
            } else {
                console.log("No response received");
            }
        });
        window.close();
    });
    const contactButton = document.getElementById('contactButton');

    contactButton.addEventListener('click', function() {
        chrome.tabs.create({'url': 'http://127.0.0.1:5000/contact'}); // Replace with your desired URL
    });
});
