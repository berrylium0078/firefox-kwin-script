SERVICE_NAME = 'org.mozilla.firefox'
OBJECT_PATH = '/extension/berrylium/kwinscript'
INTERFACE_NAME = 'local.py.agent.KWinScriptAgent'

timer = new QTimer()
timer.interval = 1000

function verbose(obj) {
    if (typeof(obj) !== "object")
        return obj;
    let str = '{';
    let keys = Object.keys(obj);
    for (let i = 0; i < keys.length; i++) {
        let key = keys[i];
        str += key;
        if (obj[key] !== undefined)
            str += ': ' + verbose(obj[key]);
        if (i < keys.length - 1) {
            str += ', ';
        }
    }
    str += '}';
    return str
}   
function callService(...args) {
    callDBus(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, ...args)
}
getPendingMessage = function() {
    callService('sendMessage', {str: 'ping!'}, function(){
    });
    callService('getPendingMessage', function(list){
        for(let i=0; i<list.length; i++) {
            print(verbose(list[i]));
            callService('sendMessage', list[i], function(){
            });
        }
    })
}
timer.timeout.connect(getPendingMessage);
timer.start()