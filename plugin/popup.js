chrome.tabs.getSelected(null, function(tab) {
    var targetURL = "http://localhost:8000/redirect?url=" + encodeURIComponent(tab.url);
    document.getElementById('mainFrame').src = targetURL;

    var targetURL = "http://localhost:8000/fbnetwork?url=" + encodeURIComponent(tab.url);
    document.getElementById('networkFrame').src = targetURL;
});