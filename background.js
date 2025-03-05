let port = browser.runtime.connectNative("kwinscript.berrylium.pyagent");

port.onMessage.addListener(function(msg) {
    console.log(msg);
});