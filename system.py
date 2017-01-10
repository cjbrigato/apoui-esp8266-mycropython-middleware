"""
SystemOS Module
"""
import sys
import time
import machine
import network
import socket
# import shell

#__all__ = ["SystemOS"]

# class SystemOS:


class Kernel:

    default_ssid = 'APOUI'
    default_key = 'astis4-maledictio6-pultarius-summittite'

    def __init__(self):
        self.handle()

    def system_release(self, build):
        print(" .:::.   .:::.")
        print(":::::::.:::::::")
        print(":::::::::::::::   Cystick_Handlers(tm)")
        print("':::::::::::::'    < APOUI-SYSTEMS >")
        print("  ':::::::::'              - ")
        print("    ':::::'  [Home middleware Controller]   ")
        print("      ':'        build {0}".format(build))
        print()

    def boot(self, build):
        VT100.clear()
        self.system_release(build)
        print(">> Booting KERNEL")
        # Set it at 160Mhz for full speed
        machine.freq(160000000)
        # We should have a list of wifi we can try to connect to ?
        #[i for i, v in enumerate(network.WLAN(network.STA_IF).scan()) if v[0] == 'excellency']
        wifi = MicroWifi(self.default_ssid, self.default_key)
        controller = ApouiControl('http://control.maison.apoui.net/setrelay')
        print('>> Controller Tests...')
        print("!> READY")
        print()
        return controller

    def handle(self):
        controller = self.boot('b1483918977')
        shell = KernelShell(controller)
        shell.cmdloop()
        # try:
        #    shell.cmdloop()
        # except KeyboardInterrupt:
        #    print("<< Received SIGINT from Keyboard")


class VT100:

    @staticmethod
    def clear():
        print("\x1B\x5B2J", end="")
        print("\x1B\x5BH", end="")


class KernelDriver:
    pass


class KernelTask:
    pass


class UserApp:
    pass

from cmd import Cmd


class KernelShell(Cmd):
    # class ApouiShell(Cmd):

    def __init__(self,  controller):
        super().__init__()
        self.controller = controller

    def do_relay_off(self, args):
        if len(args) == 0:
            print("<< Relay id ?")
        elif len(args) == 1:
            relay = args
            self.controller.relay_off(relay)
            print(">> Shut Relay {0} Down".format(relay))
        else:
            print("<< Ambigous : {0}".format(args))

    def do_relay_on(self, args):
        if len(args) == 0:
            print("<< Relay id ?")
        elif len(args) == 1:
            relay = args
            self.controller.relay_on(relay)
            print(">> Lighted Relay {0} Up".format(relay))
        else:
            print("<< Ambigous : {0}".format(args))

    def do_quit(self, args):
        print("> System will reset")
        machine.reset()

    def emptyline(self):
        pass


class ApouiControl:
    """
    This is firt Domotic Controller
    This has to be used to a shell class of sort
    """

    def __init__(self, relayurl):
        self.relayurl = relayurl
        self._boot_tests('1')

    def relay_on(self, relay):
        url = '{0}/{1}/on'.format(self.relayurl, relay)
        self._http_get(url)

    def relay_off(self, relay):
        url = '{0}/{1}/off'.format(self.relayurl, relay)
        self._http_get(url)

    def _http_get(self, url):
        _, _, host, path = url.split('/', 3)
        addr = socket.getaddrinfo(host, 80)[0][-1]
        s = socket.socket()
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n' %
                     (path, host), 'utf8'))
        """ Tempory buh
        while True:
            data = s.recv(8192)
            if data:
                print(str(data, 'utf8'), end='')
            else:
                break
        """
        s.close()

    def _boot_tests(self, relay):
        self.relay_off(relay)
        self.relay_on(relay)


class MicroWifi:
    """Connector to the Wifi"""

    def __init__(self, ssid, key):
        self.ssid = ssid
        self.key = key
        self._do_connect(self.ssid, self.key)

    # Should make Wifi Network choosable when cannot connect (interactive)
    # Should propose it first time
    # Sould save wifi informations in a file

    def _do_connect(self, ssid, key):
        tries = 0
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('>> Wifi Network : ', end="")
            sta_if.active(True)
            sta_if.connect(ssid, key)
            while not sta_if.isconnected():
                print('.', end="")
                tries += 1
                time.sleep_ms(500)
                if tries == 10:
                    print("Cannot Connect to Wifi :(")
                    new_ssid = input(" New SSID ? ")
                    new_key = input(" New Key ? ")
                    self._do_connect(new_ssid, new_key)
                    # print("Aborted")
                    # sys.exit(127)
        print('OK')
