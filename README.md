# firefox-kwin-script

This is a demo project.

The Firefox extension registers a KWin script (`pingpong.kwin.js`) and then communicates with it, via a native messaging host.
Every second, the KWin script sends a `{str: 'ping!'}` object, checks its 'inbox', and sends the received messages back as is.
- Apparently, there is no way to listen for a D-Bus signal in a KWin script, which is why the script asks the native host for incoming messages.
- The native host only accepts messages with the type signature a{sv} in D-Bus, which means a JSON object should work.

How to use:
- Edit the `path` field in `kwinscript.berrylium.pyagent.json`, then copy it to the [proper location](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_manifests#manifest_location)
- Follow the [link](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Your_first_WebExtension#installing)
- Open the extension's debug console. Messages received from KWin script will be printed here.
- Call `port.postMessage` to send a message to KWin script.
- Call `port.disconnect()` to stop the KWin script.
- Check `/tmp/firefox-kwin-script.log` for native host's log,
  
  and `journalctl -f QT_CATEGORY=js QT_CATEGORY=kwin_scripting` for KWin script's log.
