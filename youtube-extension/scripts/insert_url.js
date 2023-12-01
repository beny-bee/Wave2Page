chrome.storage.local.get('youtubeURL', function(data) {
    if (data && data.youtubeURL) { // Check if data and data.youtubeURL are defined
        console.log("Retrieved URL: ", data.youtubeURL);
        document.getElementById('video_url').value = data.youtubeURL;

        // Find the button and click it
        var submitButton = document.getElementById('submitButtonYT'); // Replace with the actual button ID
        if (submitButton) {
            submitButton.click();
            console.log('Button clicked.');
        } else {
            console.log('Button not found.');
        }

        // Optional: Clear the stored URL
        chrome.storage.local.remove('youtubeURL', function() {
            console.log('youtubeURL has been removed from storage');
        });
        
    }
});