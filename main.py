import samsungctl

config = {
    "name": "samsungctl",
    "description": "PC",
    "id": "",
    "host": "192.168.2.101",
    "port": 8002,
    "method": "websocketssl",
    "timeout": 0,
}


with samsungctl.Remote(config) as remote:
    remote.control("KEY_MENU")
