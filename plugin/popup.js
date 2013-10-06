chrome.tabs.getSelected(null, function(tab) {

    document.getElementById("networkFrame").style.display = "none";

    var targetURL = "http://localhost:8000/redirect?url=" + encodeURIComponent(tab.url);
    document.getElementById('mainFrame').src = targetURL;

    var targetURL = "http://localhost:8000/fbnetwork?url=" + encodeURIComponent(tab.url);
    document.getElementById('networkFrame').src = targetURL;
});

document.getElementById("networkLink").onclick = function showNetworkView(){

    document.getElementById("mainFrame").style.display = "none";
    document.getElementById("networkFrame").style.display = "block";

}

document.getElementById("keywordLink").onclick = function showKeywordView(){

    document.getElementById("networkFrame").style.display = "none";
    document.getElementById("mainFrame").style.display = "block";

}