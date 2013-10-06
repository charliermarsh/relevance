var updateIcon = function(url) {
    xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", url, false);
    xmlhttp.send();

    if (xmlhttp.responseText == "True") {
        chrome.browserAction.setIcon({path: '19x19-glow.png'});
    } else {
        chrome.browserAction.setIcon({path: '19x19.png'})
    }
}

var update = function(tabId, changeInfo, tab) {
    var url = "http://localhost:8000/fbexists?url=" + encodeURIComponent(tab.url);

    chrome.tabs.executeScript({
        code: 'console.log("' + url + '")'
    });

    updateIcon(url);
}

var activate = function(activeInfo) {
    chrome.tabs.get(activeInfo.tabId, function(tab) {
        var url = "http://localhost:8000/fbexists?url=" + encodeURIComponent(tab.url);

        chrome.tabs.executeScript({
            code: 'console.log("' + url + '")'
        });

        updateIcon(url);
    });
}

chrome.tabs.onUpdated.addListener(update);
chrome.tabs.onActivated.addListener(activate);
