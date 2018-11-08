# -*- coding: utf-8 -*-


import socket
from xml.etree import ElementTree
import requests
import threading


MCAST_GRP = "239.255.255.250"

request = (
    "M-SEARCH * HTTP/1.1\r\n"
    "HOST: 239.255.255.250:1900\r\n"
    "MAN: \"ssdp:discover\"\r\n"
    "MX: 1\r\n"
    "ST: urn:samsung.com:device:RemoteControlReceiver:1\r\n"
    "CONTENT-LENGTH: 0\r\n\r\n"
)


def discover(timeout):
    '''

    Received 6/11/2018 at 9:38:51 AM (828)

    HTTP/1.1 200 OK
    CACHE-CONTROL: max-age = 1800
    EXT:
    LOCATION: http://192.168.1.63:52235/rcr/RemoteControlReceiver.xml
    SERVER: Linux/9.0 UPnP/1.0 PROTOTYPE/1.0
    ST: urn:samsung.com:device:RemoteControlReceiver:1
    USN: uuid:2007e9e6-2ec1-f097-f2df-944770ea00a3::urn:samsung.com:device:RemoteControlReceiver:1
    CONTENT-LENGTH: 0
    '''

    if timeout > 0:
        socket.setdefaulttimeout(timeout)
    else:
        socket.setdefaulttimeout(3)

    events = []
    found = []

    for address_type, sock_addr in socket.getaddrinfo('', None)[-1:1]:
        if address_type != socket.AF_INET:
            continue

        local_address = sock_addr[0]

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
        sock.bind((local_address, 0))

        while True:
            for _ in xrange(5):
                sock.sendto(request, ("239.255.255.250", 1900))
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    addr, port = addr

                    for line in data.split('\n'):
                        line = line.strip().split(': ')
                        if len(line) < 2:
                            continue

                        if line[0].lower() == 'location':
                            location = line[1].strip()

                            events += [threading.Event()]

                            def do(a, p, l, e):
                                try:
                                    d = _read_xml(l)
                                    d['ip'] = a
                                    if d and d not in found:
                                        found.append(d)
                                except:
                                    pass

                                e.set()

                            t = threading.Thread(
                                target=do,
                                args=(addr, port, location, events[-1])
                            )
                            t.daemon = True
                            t.start()

            except socket.timeout:
                for evt in events:
                    evt.wait()

                del events[:]

                break

    return found


def _parse_model(model):
    '''

    [U] N 55 D 8000

    Q = QLED
    U = LED
    P = Plasma
    L = LCD
    H = DLP
    K = OLED

    U [N] 55 D 8000

    N = North America
    E = Europe
    A = Asia

    U N [55] D 8000

    Size in inches

    U N 55 [D] 8000

    Q = 2017 QLED
    MU = 2017 UHD
    M = 2017 HD
    KS = 2016 SUHD
    KU =2016 UHD
    L = 2015
    H = 2014
    HU = 2014 UHD
    F = 2013
    E = 2012
    D = 2011
    C = 2010
    B = 2009
    A = 2008
    '''

    year_mapping = dict(
        Q=(2017, 'UHD'),
        MU=(2017, 'UHD'),
        M=(2017, 'HD'),
        KS=(2016, 'SUHD'),
        KU=(2016, 'UHD'),
        L=(2015, 'HD'),
        H=(2014, 'HD'),
        HU=(2014, 'UHD'),
        F=(2013, 'HD'),
        E=(2012, 'HD'),
        D=(2011, 'HD'),
        C=(2010, 'HD'),
        B=(2009, 'HD'),
        A=(2008, 'HD')
    )
    type_mapping = dict(
        Q='QLED',
        U='LED',
        P='Plasma',
        L='LCD',
        H='DLP',
        K='OLED'
    )

    location_mapping = dict(
        N='North America',
        E='Europe',
        A='Asia'
    )
    year, resolution = year_mapping[model[4]]
    return dict(
        model=model,
        type=type_mapping[model[0]],
        location=location_mapping[model[1]],
        size=int(model[2:4]),
        year=year,
        resolution=resolution,
        series=model[5:]
    )


def _read_xml(url):
    '''
    <?xml version="1.0"?>
    <root xmlns:dlna="urn:schemas-dlna-org:device-1-0" xmlns:sec="http://www.sec.co.kr/dlna" xmlns="urn:schemas-upnp-org:device-1-0">
        <specVersion>
            <major>1</major>
            <minor>0</minor>
        </specVersion>
        <device>
            <deviceType>urn:samsung.com:device:RemoteControlReceiver:1</deviceType>
            <friendlyName>[TV]UN55D8000</friendlyName>
            <manufacturer>Samsung Electronics</manufacturer>
            <manufacturerURL>http://www.samsung.com/sec</manufacturerURL>
            <modelDescription>Samsung TV RCR</modelDescription>
            <modelName>UN55D8000</modelName>
            <modelNumber>1.0</modelNumber>
            <modelURL>http://www.samsung.com/sec</modelURL>
            <serialNumber>20090804RCR</serialNumber>
            <UDN>uuid:2007e9e6-2ec1-f097-f2df-944770ea00a3</UDN>
            <sec:deviceID>MTCN4UQJAZBMQ</sec:deviceID>
            <serviceList>
                <service>
                    <serviceType>urn:samsung.com:service:TestRCRService:1</serviceType>
                    <serviceId>urn:samsung.com:serviceId:TestRCRService</serviceId>
                    <controlURL>/RCR/control/TestRCRService</controlURL>
                    <eventSubURL>/RCR/event/TestRCRService</eventSubURL>
                    <SCPDURL>TestRCRService.xml</SCPDURL>
                </service>
            </serviceList>
        </device>
    </root>
    '''

    response = requests.get(url)
    xml = ElementTree.fromstring(response.content)

    if '}' in xml[0].tag:
        schema = xml[0].tag[:xml[0].tag.find('}') + 1]
    else:
        schema = ''

    device = xml.find(schema + 'device')
    friendly_name = device.find(schema + 'friendlyName')
    serial_number = device.find(schema + 'serialNumber')
    model_name = device.find(schema + 'modelName')

    if friendly_name is not None:
        friendly_name = friendly_name.text
    else:
        friendly_name = ''

    if serial_number is not None:
        serial_number = serial_number.text
    else:
        serial_number = ''

    if model_name is not None:
        model_name = model_name.text
    else:
        model_name = ''

    if '[TV]' not in friendly_name or not model_name:
        return None

    model_data = _parse_model(model_name)
    model_data['serial_number'] = serial_number
    return model_data

