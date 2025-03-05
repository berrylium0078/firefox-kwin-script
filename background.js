let port = browser.runtime.connectNative("kwinscript.berrylium.pyagent");

port.onMessage.addListener(function(msg) {
    console.log(msg);
});

// port.postMessage({a:1, b:'23', c:[4, 5, 6]});