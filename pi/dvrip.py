import os
import struct
import json
from time import sleep
import hashlib
import threading
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from datetime import datetime
from re import compile
import time
import logging
import sys


def vprint(x):
    print(x)


class DVRIPCam(object):
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    CODES = {
        100: "OK",
        101: "Unknown error",
        102: "Unsupported version",
        103: "Request not permitted",
        104: "User already logged in",
        105: "User is not logged in",
        106: "Username or password is incorrect",
        107: "User does not have necessary permissions",
        203: "Password is incorrect",
        511: "Start of upgrade",
        512: "Upgrade was not started",
        513: "Upgrade data errors",
        514: "Upgrade error",
        515: "Upgrade successful",
    }
    QCODES = {
        "AuthorityList": 1470,
        "Users": 1472,
        "Groups": 1474,
        "AddGroup": 1476,
        "ModifyGroup": 1478,
        "DelGroup": 1480,
        "AddUser": 1482,
        "ModifyUser": 1484,
        "DelUser": 1486,
        "ModifyPassword": 1488,
        "AlarmInfo": 1504,
        "AlarmSet": 1500,
        "ChannelTitle": 1046,
        "EncodeCapability": 1360,
        "General": 1042,
        "KeepAlive": 1006,
        "OPMachine": 1450,
        "OPMailTest": 1636,
        "OPMonitor": 1413,
        "OPNetKeyboard": 1550,
        "OPPTZControl": 1400,
        "OPSNAP": 1560,
        "OPSendFile": 0x5F2,
        "OPSystemUpgrade": 0x5F5,
        "OPTalk": 1434,
        "OPTimeQuery": 1452,
        "OPTimeSetting": 1450,
        "SystemFunction": 1360,
        "SystemInfo": 1020,
    }
    KEY_CODES = {
        "M": "Menu",
        "I": "Info",
        "E": "Esc",
        "F": "Func",
        "S": "Shift",
        "L": "Left",
        "U": "Up",
        "R": "Right",
        "D": "Down",
    }
    OK_CODES = [100, 515]
    PORTS = {
        "tcp": 34567,
        "udp": 34568,
    }

    def __init__(self, ip, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.ip = ip
        self.user = kwargs.get("user", "admin")
        hash_pass = kwargs.get("hash_pass")
        hash_pass = ''
        self.hash_pass = hash_pass or self.sofia_hash(kwargs.get("password", ""))
        self.proto = kwargs.get("proto", "tcp")
        self.port = kwargs.get("port", self.PORTS.get(self.proto))
        self.socket = None
        self.packet_count = 0
        self.session = 0
        self.alive_time = 20
        self.alive = None
        self.alarm = None
        self.alarm_func = None
        self.busy = threading.Condition()

    def connect(self, timeout=10):
        if self.proto == "tcp":
            self.socket_send = self.tcp_socket_send
            self.socket_recv = self.tcp_socket_recv
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
        elif self.proto == "udp":
            self.socket_send = self.udp_socket_send
            self.socket_recv = self.udp_socket_recv
            self.socket = socket(AF_INET, SOCK_DGRAM)
        else:
            raise 'Unsupported protocol {}'.format(self.proto)

        # it's important to extend timeout for upgrade procedure
        self.timeout = timeout
        self.socket.settimeout(timeout)

    def close(self):
        self.alive.cancel()
        self.socket.close()
        self.socket = None

    def udp_socket_send(self, bytes):
        return self.socket.sendto(bytes, (self.ip, self.port))

    def udp_socket_recv(self, bytes):
        data, _ = self.socket.recvfrom(bytes)
        return data

    def tcp_socket_send(self, bytes):
        return self.socket.sendall(bytes)

    def tcp_socket_recv(self, bufsize):
        return self.socket.recv(bufsize)

    def receive_with_timeout(self, length):
        received = 0
        buf = bytearray()
        start_time = time.time()

        while True:
            data = self.socket_recv(length - received)
            buf.extend(data)
            received += len(data)
            if length == received:
                break
            elapsed_time = time.time() - start_time
            if elapsed_time > self.timeout:
                return None
        return buf

    def receive_json(self, length):
        data = self.receive_with_timeout(length).decode('utf-8')
        if data is None:
            return {}

        self.packet_count += 1
        self.logger.debug("<= %s", data)
        reply = json.loads(data[:-2])
        return reply

    def send(self, msg, data={}, wait_response=True):
        if self.socket is None:
            return {"Ret": 101}
        # self.busy.wait()
        self.busy.acquire()
        if hasattr(data, "__iter__"):
            if sys.version_info[0] > 2:
                data = bytes(json.dumps(data, ensure_ascii=False), "utf-8")
            else:
                data = json.dumps(data, ensure_ascii=False)
        pkt = (
            struct.pack(
                "BB2xII2xHI",
                255,
                0,
                self.session,
                self.packet_count,
                msg,
                len(data) + 2,
            )
            + data
            + b"\x0a\x00"
        )
        self.logger.debug("=> %s", pkt)
        self.socket_send(pkt)
        if wait_response:
            reply = {"Ret": 101}
            (
                head,
                version,
                self.session,
                sequence_number,
                msgid,
                len_data,
            ) = struct.unpack("BB2xII2xHI", self.socket_recv(20))
            reply = self.receive_json(len_data)
            self.busy.release()
            return reply

    def sofia_hash(self, password=""):
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        if sys.version_info[0] > 2:
            md5 = hashlib.md5(bytes(password, "utf-8")).digest()
            return "".join([chars[sum(x) % 62] for x in zip(md5[::2], md5[1::2])])
        else:
            md5 = hashlib.md5(password.decode('utf-8')).digest()
            iterlist = zip(md5[::2], md5[1::2])
            cc = []
            for x in iterlist:
                su=0
                for xx in x:
                    su = su + ord(xx)
                cc.append(chars[su % 62])
            return "".join(cc)


    def login(self):
        if self.socket is None:
            self.connect()
        data = self.send(
            1000,
            {
                "EncryptType": "MD5",
                "LoginType": "DVRIP-Web",
                "PassWord": self.hash_pass,
                "UserName": self.user,
            },
        )
        if data["Ret"] not in self.OK_CODES:
            return False
        self.session = int(data["SessionID"], 16)
        self.alive_time = data["AliveInterval"]
        self.keep_alive()
        return data["Ret"] in self.OK_CODES

    def getAuthorityList(self):
        data = self.send(self.QCODES["AuthorityList"])
        if data["Ret"] in self.OK_CODES:
            return data["AuthorityList"]
        else:
            return []

    def getGroups(self):
        data = self.send(self.QCODES["Groups"])
        if data["Ret"] in self.OK_CODES:
            return data["Groups"]
        else:
            return []

    def addGroup(self, name, comment="", auth=None):
        data = self.set_command(
            "AddGroup",
            {
                "Group": {
                    "AuthorityList": auth or self.getAuthorityList(),
                    "Memo": comment,
                    "Name": name,
                },
            },
        )
        return data["Ret"] in self.OK_CODES

    def modifyGroup(self, name, newname=None, comment=None, auth=None):
        g = [x for x in self.getGroups() if x["Name"] == name]
        if g == []:
            print('Group "{}" not found!'.format(name))
            return False
        g = g[0]
        data = self.send(
            self.QCODES["ModifyGroup"],
            {
                "Group": {
                    "AuthorityList": auth or g["AuthorityList"],
                    "Memo": comment or g["Memo"],
                    "Name": newname or g["Name"],
                },
                "GroupName": name,
            },
        )
        return data["Ret"] in self.OK_CODES

    def delGroup(self, name):
        data = self.send(
            self.QCODES["DelGroup"],
            {"Name": name, "SessionID": "0x%08X" % self.session,},
        )
        return data["Ret"] in self.OK_CODES

    def getUsers(self):
        data = self.send(self.QCODES["Users"])
        if data["Ret"] in self.OK_CODES:
            return data["Users"]
        else:
            return []

    def addUser(
        self, name, password, comment="", group="user", auth=None, sharable=True
    ):
        g = [x for x in self.getGroups() if x["Name"] == group]
        if g == []:
            print('Group "{}" not found!'.format(group))
            return False
        g = g[0]
        data = self.set_command(
            "AddUser",
            {
                "User": {
                    "AuthorityList": auth or g["AuthorityList"],
                    "Group": g["Name"],
                    "Memo": comment,
                    "Name": name,
                    "Password": self.sofia_hash(password),
                    "Reserved": False,
                    "Sharable": sharable,
                },
            },
        )
        return data["Ret"] in self.OK_CODES

    def modifyUser(
        self, name, newname=None, comment=None, group=None, auth=None, sharable=None
    ):
        u = [x for x in self.getUsers() if x["Name"] == name]
        if u == []:
            print('User "{}" not found!'.format(name))
            return False
        u = u[0]
        if group:
            g = [x for x in self.getGroups() if x["Name"] == group]
            if g == []:
                print('Group "{}" not found!'.format(group))
                return False
            u["AuthorityList"] = g[0]["AuthorityList"]
        data = self.send(
            self.QCODES["ModifyUser"],
            {
                "User": {
                    "AuthorityList": auth or u["AuthorityList"],
                    "Group": group or u["Group"],
                    "Memo": comment or u["Memo"],
                    "Name": newname or u["Name"],
                    "Password": "",
                    "Reserved": u["Reserved"],
                    "Sharable": sharable or u["Sharable"],
                },
                "UserName": name,
            },
        )
        return data["Ret"] in self.OK_CODES

    def delUser(self, name):
        data = self.send(
            self.QCODES["DelUser"],
            {"Name": name, "SessionID": "0x%08X" % self.session,},
        )
        return data["Ret"] in self.OK_CODES

    def changePasswd(self, newpass="", oldpass=None, user=None):
        data = self.send(
            self.QCODES["ModifyPassword"],
            {
                "EncryptType": "MD5",
                "NewPassWord": self.sofia_hash(newpass),
                "PassWord": oldpass or self.password,
                "SessionID": "0x%08X" % self.session,
                "UserName": user or self.user,
            },
        )
        return data["Ret"] in self.OK_CODES

    def channel_title(self, titles):
        if isinstance(titles, str):
            titles = [titles]
        self.send(
            self.QCODES["ChannelTitle"],
            {
                "ChannelTitle": titles,
                "Name": "ChannelTitle",
                "SessionID": "0x%08X" % self.session,
            },
        )

    def channel_bitmap(self, width, height, bitmap):
        header = struct.pack("HH12x", width, height)
        self.socket_send(
            struct.pack(
                "BB2xII2xHI",
                255,
                0,
                self.session,
                self.packet_count,
                0x041A,
                len(bitmap) + 16,
            )
            + header
            + bitmap
        )
        reply, rcvd = self.recv_json()
        if reply and reply["Ret"] != 100:
            return False
        return True

    def reboot(self):
        self.set_command("OPMachine", {"Action": "Reboot"})
        self.close()

    def setAlarm(self, func):
        self.alarm_func = func

    def clearAlarm(self):
        self.alarm_func = None

    def alarmStart(self):
        self.alarm = threading.Thread(
            name="DVRAlarm%08X" % self.session,
            target=self.alarm_thread,
            args=[self.busy],
        )
        self.alarm.start()
        return self.get_command("", self.QCODES["AlarmSet"])

    def alarm_thread(self, event):
        while True:
            event.acquire()
            try:
                (
                    head,
                    version,
                    session,
                    sequence_number,
                    msgid,
                    len_data,
                ) = struct.unpack("BB2xII2xHI", self.socket_recv(20))
                sleep(0.1)  # Just for receive whole packet
                reply = self.socket_recv(len_data)
                self.packet_count += 1
                reply = json.loads(reply[:-2])
                if msgid == self.QCODES["AlarmInfo"] and self.session == session:
                    if self.alarm_func is not None:
                        self.alarm_func(reply[reply["Name"]], sequence_number)
            except:
                pass
            finally:
                event.release()
            if self.socket is None:
                break

    def keep_alive(self):
        self.send(
            self.QCODES["KeepAlive"],
            {"Name": "KeepAlive", "SessionID": "0x%08X" % self.session},
        )
        self.alive = threading.Timer(self.alive_time, self.keep_alive)
        self.alive.start()

    def keyDown(self, key):
        self.set_command(
            "OPNetKeyboard", {"Status": "KeyDown", "Value": key},
        )

    def keyUp(self, key):
        self.set_command(
            "OPNetKeyboard", {"Status": "KeyUp", "Value": key},
        )

    def keyPress(self, key):
        self.keyDown(key)
        sleep(0.3)
        self.keyUp(key)

    def keyScript(self, keys):
        for k in keys:
            if k != " " and k.upper() in self.KEY_CODES:
                self.keyPress(self.KEY_CODES[k.upper()])
            else:
                sleep(1)

    def ptz(self, cmd, step=5, preset=-1, ch=0):
        '''
        CMDS = [
            "DirectionUp",
            "DirectionDown",
            "DirectionLeft",
            "DirectionRight",
            "DirectionLeftUp",
            "DirectionLeftDown",
            "DirectionRightUp",
            "DirectionRightDown",
            "ZoomTile",
            "ZoomWide",
            "FocusNear",
            "FocusFar",
            "IrisSmall",
            "IrisLarge",
            "SetPreset",
            "GotoPreset",
            "ClearPreset",
            "StartTour",
            "StopTour",
        ]
        '''
        # ptz_param = { "AUX" : { "Number" : 0, "Status" : "On" }, "Channel" : ch, "MenuOpts" : "Enter", "POINT" : { "bottom" : 0, "left" : 0, "right" : 0, "top" : 0 }, "Pattern" : "SetBegin", "Preset" : -1, "Step" : 5, "Tour" : 0 }
        ptz_param = {
            "AUX": {"Number": 0, "Status": "On"},
            "Channel": ch,
            "MenuOpts": "Enter",
            "Pattern": "Start",
            "Preset": preset,
            "Step": step,
            "Tour": 1 if "Tour" in cmd else 0,
        }
        return self.set_command(
            "OPPTZControl", {"Command": cmd, "Parameter": ptz_param},
        )

    def set_info(self, command, data):
        return self.set_command(command, data, 1040)

    def set_command(self, command, data, code=None):
        if not code:
            code = self.QCODES[command]
        return self.send(
            code, {"Name": command, "SessionID": "0x%08X" % self.session, command: data}
        )

    def get_info(self, command):
        return self.get_command(command, 1042)

    def get_command(self, command, code=None):
        if not code:
            code = self.QCODES[command]

        data = self.send(code, {"Name": command, "SessionID": "0x%08X" % self.session})
        if data["Ret"] in self.OK_CODES and command in data:
            return data[command]
        else:
            return data

    def get_time(self):
        return datetime.strptime(self.get_command("OPTimeQuery"), self.DATE_FORMAT)

    def set_time(self, time=None):
        if time is None:
            time = datetime.now()
        return self.set_command("OPTimeSetting", time.strftime(self.DATE_FORMAT))

    def get_system_info(self):
        return self.get_command("SystemInfo")

    def get_general_info(self):
        return self.get_command("General")

    def get_encode_capabilities(self):
        return self.get_command("EncodeCapability")

    def get_system_capabilities(self):
        return self.get_command("SystemFunction")

    def get_camera_info(self, default_config=False):
        """Request data for 'Camera' from  the target DVRIP device."""
        if default_config:
            code = 1044
        else:
            code = 1042
        return self.get_info(code, "Camera")

    def get_encode_info(self, default_config=False):
        """Request data for 'Simplify.Encode' from the target DVRIP device.

            Arguments:
            default_config -- returns the default values for the type if True
        """
        if default_config:
            code = 1044
        else:
            code = 1042
        return self.get_info(code, "Simplify.Encode")

    def recv_json(self, buf=bytearray()):
        p = compile(b".*({.*})")

        packet = self.socket_recv(0xFFFF)
        if not packet:
            return None, buf
        buf.extend(packet)
        m = p.search(buf)
        if m is None:
            print(buf)
            return None, buf
        buf = buf[m.span(1)[1]:]
        return json.loads(m.group(1)), buf

    def get_upgrade_info(self):
        return self.get_command("OPSystemUpgrade")

    def upgrade(self, filename="", packetsize=0x8000):

        data = self.set_command(
            "OPSystemUpgrade", {"Action": "Start", "Type": "System"}, 0x5F0
        )
        if data["Ret"] not in self.OK_CODES:
            return data

        vprint("Ready to upgrade")
        blocknum = 0
        sentbytes = 0
        fsize = os.stat(filename).st_size
        rcvd = bytearray()
        with open(filename, "rb") as f:
            while True:
                bytes = f.read(packetsize)
                if not bytes:
                    break
                header = struct.pack(
                    "BB2xII2xHI", 255, 0, self.session, blocknum, 0x5F2, len(bytes)
                )
                self.socket_send(header + bytes)
                blocknum += 1
                sentbytes += len(bytes)

                reply, rcvd = self.recv_json(rcvd)
                if reply and reply["Ret"] != 100:
                    vprint("Upgrade failed")
                    return reply

                progress = sentbytes / fsize * 100
                vprint("Uploaded {:.2f}%".format(progress))
        vprint("End of file")

        pkt = struct.pack("BB2xIIxBHI", 255, 0, self.session, blocknum, 1, 0x05F2, 0)
        self.socket_send(pkt)
        vprint("Waiting for upgrade...")
        while True:
            reply, rcvd = self.recv_json(rcvd)
            if reply and reply["Name"] == "" and reply["Ret"] == 100:
                break

        while True:
            data, rcvd = self.recv_json(rcvd)
            if data["Ret"] in [512, 513]:
                vprint("Upgrade failed")
                return data
            if data["Ret"] == 515:
                vprint("Upgrade successful")
                self.socket.close()
                return data
            vprint('Upgraded {}%'.format(data['Ret']))

    def reassemble_bin_payload(self, metadata={}):
        def internal_to_type(data_type, value):
            if data_type == 0x1FC or data_type == 0x1FD:
                if value == 1:
                    return "mpeg4"
                elif value == 2:
                    return "h264"
                elif value == 3:
                    return "h265"
            elif data_type == 0x1F9:
                if value == 1 or value == 6:
                    return "info"
            elif data_type == 0x1FA:
                if value == 0xE:
                    return "g711a"
            elif data_type == 0x1FE and value == 0:
                return "jpeg"
            return None

        def internal_to_datetime(value):
            second = value & 0x3F
            minute = (value & 0xFC0) >> 6
            hour = (value & 0x1F000) >> 12
            day = (value & 0x3E0000) >> 17
            month = (value & 0x3C00000) >> 22
            year = ((value & 0xFC000000) >> 26) + 2000
            return datetime(year, month, day, hour, minute, second)

        length = 0
        buf = bytearray()
        start_time = time.time()

        while True:
            data = self.receive_with_timeout(20)
            (
                head,
                version,
                session,
                sequence_number,
                total,
                cur,
                msgid,
                len_data,
            ) = struct.unpack("BB2xIIBBHI", data)
            packet = self.receive_with_timeout(len_data)
            frame_len = 0
            if length == 0:
                media = None
                frame_len = 8
                (data_type,) = struct.unpack(">I", packet[:4])
                if data_type == 0x1FC or data_type == 0x1FE:
                    frame_len = 16
                    (media, metadata["fps"], w, h, dt, length,) = struct.unpack(
                        "BBBBII", packet[4:frame_len]
                    )
                    metadata["width"] = w * 8
                    metadata["height"] = h * 8
                    metadata["datetime"] = internal_to_datetime(dt)
                    if data_type == 0x1FC:
                        metadata["frame"] = "I"
                elif data_type == 0x1FD:
                    (length,) = struct.unpack("I", packet[4:frame_len])
                    metadata["frame"] = "P"
                elif data_type == 0x1FA:
                    (media, samp_rate, length) = struct.unpack(
                        "BBH", packet[4:frame_len]
                    )
                elif data_type == 0x1F9:
                    (media, n, length) = struct.unpack("BBH", packet[4:frame_len])
                # special case of JPEG shapshots
                elif data_type == 0xFFD8FFE0:
                    return packet
                else:
                    raise ValueError(data_type)
                if media is not None:
                    metadata["type"] = internal_to_type(data_type, media)
            buf.extend(packet[frame_len:])
            length -= len(packet) - frame_len
            if length == 0:
                return buf
            elapsed_time = time.time() - start_time
            if elapsed_time > self.timeout:
                return None

    def snapshot(self, channel=0):
        command = "OPSNAP"
        self.send(
            self.QCODES[command],
            {
                "Name": command,
                "SessionID": "0x%08X" % self.session,
                command: {"Channel": channel},
            },
            wait_response=False,
        )
        packet = self.reassemble_bin_payload()
        return packet

    def start_monitor(self, frame_callback, user={}, stream="Main"):
        params = {
            "Channel": 0,
            "CombinMode": "NONE",
            "StreamType": stream,
            "TransMode": "TCP",
        }
        data = self.set_command("OPMonitor", {"Action": "Claim", "Parameter": params})
        if data["Ret"] not in self.OK_CODES:
            return data

        self.send(
            1410,
            {
                "Name": "OPMonitor",
                "SessionID": "0x%08X" % self.session,
                "OPMonitor": {"Action": "Start", "Parameter": params},
            },
            wait_response=False,
        )
        self.monitoring = True
        while self.monitoring:
            meta = {}
            frame = self.reassemble_bin_payload(meta)
            frame_callback(frame, meta, user)

    def stop_monitor(self):
        self.monitoring = False


if __name__ == '__main__':
    ipaddr = sys.argv[1]
    cam=DVRIPCam(ipaddr)
    if cam.login():
        info = cam.get_info("AVEnc.VideoWidget")
        print(info)
        info[0]["TimeTitleAttribute"]["EncodeBlend"] = False
        info[0]["ChannelTitleAttribute"]["EncodeBlend"] = False
        cam.set_info("AVEnc.VideoWidget", info)
        print('--------')
        cam.close()
    else:
        print('login failed')
