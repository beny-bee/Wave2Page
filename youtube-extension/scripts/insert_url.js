chrome.storage.local.get('youtubeURL', function(data) {
    if (data && data.youtubeURL) { // Check if data and data.youtubeURL are defined
        console.log("Retrieved URL: ", data.youtubeURL);
        document.getElementById('video_url').value = data.youtubeURL;

        chrome.storage.local.get('filename', function (data) {
            if (data && data.filename) {
                console.log("Retrieved filename: ", data.filename);
                document.getElementById('filename').value = data.filename;
        
                // Optional: Clear the stored filename
                chrome.storage.local.remove('filename', function () {
                    console.log('filename has been removed from storage');
                });

                // Find the button and click it
                var submitButton = document.getElementById('submitButtonYT');
                if (submitButton) {
                    submitButton.click();
                    console.log('Button clicked.');
                } else {
                    console.log('Button not found.');
                }
            }
            
        });

        // Optional: Clear the stored URL
        chrome.storage.local.remove('youtubeURL', function() {
            console.log('youtubeURL has been removed from storage');
        });
        
    }
});
