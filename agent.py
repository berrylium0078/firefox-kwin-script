#!/usr/bin/python3
import os, sys, json, struct, threading, signal, time, fcntl
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QSocketNotifier, QCoreApplication, QTimer
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtDBus import QDBusAbstractAdaptor, QDBusConnection, QDBusInterface, QDBusMessage

SERVICE_NAME = "org.mozilla.firefox"
OBJECT_PATH = "/extension/berrylium/kwinscript"
SCRIPT_NAME = 'pingpong.kwin.js'
WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

logFile = open('/tmp/activityintegration.log', 'w')
def log(str):
    time_str = time.strftime('%Y%m%d %H:%M:%S', time.localtime())
    print(f'[{time_str}]: {str}', file=logFile, flush=True)

class FirefoxListener(QObject):
    messageReceived = pyqtSignal(str)
    disconnected = pyqtSignal()
    def __init__(self):
        super().__init__()
    def run(self):
        while True:
            rawLength = sys.stdin.buffer.read(4)
            if len(rawLength) == 0: # ???
                self.disconnected.emit()
                break
            messageLength = struct.unpack('@I', rawLength)[0]
            message = sys.stdin.buffer.read(messageLength).decode('utf-8')
            self.messageReceived.emit(message)
 
class KWinScriptAgent(QObject):
    def __init__(self):
        super().__init__()
        self.message = []
    @pyqtSlot(str)
    def receiveMessage(self, message):
        log(f'firefox => {message}')
        self.message.append(json.loads(message))
    @pyqtSlot(result=list)
    def getPendingMessage(self):
        result, self.message = self.message, []
        return result
    @pyqtSlot('QVariantMap')
    def sendMessage(self, obj):
        log(f'kwin => {obj}')
        message = json.dumps(obj, indent=None, separators=(',', ':')).encode('utf-8')
        length = struct.pack('@I', len(message))
        sys.stdout.buffer.write(length)
        sys.stdout.buffer.write(message)
        sys.stdout.buffer.flush()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    timer = QTimer()
    timer.setInterval(1000)
    timer.timeout.connect(lambda: None)
    timer.start()

    listener = FirefoxListener()
    agent = KWinScriptAgent()
    listener.messageReceived.connect(agent.receiveMessage)

    # register DBus interface for kwin agent
    bus = QDBusConnection.sessionBus()
    if not bus.registerService(SERVICE_NAME):
        log("Failed to register D-Bus service!")
        exit(1)
    if not bus.registerObject(OBJECT_PATH, agent, QDBusConnection.RegisterOption.ExportAllSlots):
        log("Failed to register D-Bus object!")
        exit(1)
    log(f"D-Bus service '{SERVICE_NAME}' running at '{OBJECT_PATH}'")
    # load kwin script
    scriptBus = QDBusInterface('org.kde.KWin', '/Scripting',
            'org.kde.kwin.Scripting', bus)
    if scriptBus.call('isScriptLoaded', SCRIPT_NAME).arguments()[0]:
        log("{SCRIPT_NAME} already loaded! unloading...")
        scriptBus.call('unloadScript', SCRIPT_NAME)
    script_id = scriptBus.call(
            'loadScript',
            f'{WORKING_DIRECTORY}/{SCRIPT_NAME}',
            SCRIPT_NAME
        ).arguments()[0]
    if int(script_id) > -1:
        log(f"Loaded KWin script into ID: {script_id}")
        reply = QDBusInterface('org.kde.KWin',
            f'/Scripting/Script{script_id}',
            'org.kde.kwin.Script', bus).call('run')
        if reply.type() == QDBusMessage.MessageType.ErrorMessage:
            log(f"Failed to execute script! {reply.errorMessage()}")
            log(f'unloading {SCRIPT_NAME}...')
            scriptBus.call('unloadScript', SCRIPT_NAME)
            exit(1)
    else:
        log("Failed to load KWin script!")
        exit(1)
    
    threading.Thread(target=listener.run).start()
    
    def cleanup(a, b):
        log('cleaning...')
        scriptBus.call('unloadScript', SCRIPT_NAME)
        log(f'unloaded {SCRIPT_NAME}')
        exit(0)
    
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    sys.exit(app.exec())