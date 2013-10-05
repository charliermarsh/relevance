chrome.tabs.getSelected(null, function(tab) {
    var targetURL = "http://127.0.0.1:8000/query?url=" + encodeURIComponent(tab.url);
    document.getElementById('mainFrame').src = targetURL;
});