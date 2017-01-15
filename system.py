"""
SystemOS Module
"""
import os
import sys
import time
import machine
import network
import socket
import gc
import micropython

# import shell

#__all__ = ["SystemOS"]

# class SystemOS:

from ssd1306 import SSD1306_I2C
from cmd import Cmd


""" Constants """
WIDTH = const(128)
HEIGHT = const(64)
#pscl = machine.Pin(5)  # GPIO4_CLK , machine.Pin.OUT_PP)
#psda = machine.Pin(4)  # GPIO5_DAT, machine.Pin.OUT_PP)
#i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
oled = SSD1306_I2C(WIDTH, HEIGHT, machine.I2C(scl=machine.Pin(5),
                                              sda=machine.Pin(4)))

class Kernel:

    default_controller = 'http://control.maison.apoui.net/setrelay'

    def __init__(self):
        gc.collect()
        self.handle()

    def system_release(self, build):
        oled.text('<APOUI-SYSTEMS>', 0, 0)
        oled.text('---------------', 0, 10)
        oled.text('> KERNEL [OK]',0,20)
        oled.show()
        oled.text('> RAMFREE:{0}'.format(gc.mem_free()),0,30)
        oled.show()
        print(" .:::.   .:::.")
        print(":::::::.:::::::")
        print(":::::::::::::::   Cystick_Handlers(tm)")
        print("':::::::::::::'    < APOUI-SYSTEMS >")
        print("  ':::::::::'              - ")
        print("    ':::::'  [Home middleware Controller]   ")
        print("      ':'        build {0}".format(build))
        print()
        print('-> HEAPFREE:{0}'.format(gc.mem_free()))

    def boot(self, build):
        VT100.uart_clear()
        VT100.display_clear()
        self.system_release(build)
        print(">> Booting KERNEL")
        # Set it at 160Mhz for full speed
        machine.freq(160000000)
        print('-> Clocked to : {0}'.format(machine.freq()))
        oled.text('->CLK160MHZ!',0,40)
        oled.show()
        wifi = MicroWifi()
        controller = ApouiControl(Kernel.default_controller)
        print('>> Controller Tests...')
        print("!> READY")
        print()
        return controller

    def handle(self):
        controller = self.boot('bBK3v40003')
        shell = KernelShell(controller)
        shell.cmdloop()
        # try:
        #    shell.cmdloop()
        # except KeyboardInterrupt:
        #    print("<< Received SIGINT from Keyboard")


class VT100:

    _xcursor = 0
    _ycursor = 0

    @staticmethod
    def uart_clear():
        print("\x1B\x5B2J", end="")
        print("\x1B\x5BH", end="")

    @staticmethod
    def display_clear():
        oled.fill(0)
        oled.show()

class KernelDriver:
    pass


class KernelTask:
    pass


class UserApp:
    pass


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

    def do_network_force_flush(self,args):
        print("> Destroyed network conf")
        os.remove('wlan.conf')
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
        self._boot_tests('-1') #booh

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
        """ Tempory bug
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

    def __init__(self):
        #self.ssid = ssid
        #self.key = key
        self._do_connect()

    # Should make Wifi Network choosable when cannot connect (interactive)
    # Should propose it first time
    # Sould save wifi informations in a file

    def _register_connect(self):
        print('!> Registering new connection :')
        try:
            os.remove('wlan.conf')
            print('i> removed wlan.conf')
        except:
            print('i> no wlan.conf')
        VT100.display_clear()
        oled.text('!>RST WIFI CONF !',0,0)
        oled.show()
        new_ssid = input("   New SSID ? ")
        new_key = input("   New Key ? ")
        print('wt> wlan.conf')
        f = open('wlan.conf', 'wt')
        print('i> writing config')
        f.write('{0}0X0EB{1}'.format(new_ssid, new_key))
        f.close()
        del(f)
        print('d> reboot()')
        machine.reset()

    def _do_connect(self):
        oled.text('> WIFI...',0,50)
        oled.show()
        tries = 0
        try:
            f = open('wlan.conf', 'rt')
            winfo = f.readall()
            f.close()
            del(f)
            gc.collect()
            print('i> wlan.conf SAK')#.format(winfo))
        except:
            print('E> No wlan chosen | or broken conf')
            input('   Press ENTER to register connection')
            self._register_connect()
            return
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            ssid, key = winfo.split('0X0EB')
            print('>> Wifi Network : [{0}]'.format(ssid), end="")
            sta_if.active(True)
            sta_if.connect(ssid, key)
            while not sta_if.isconnected():
                print('.', end="")
                tries += 1
                time.sleep_ms(500)
                if tries == 20:
                    print("Cannot Connect to Wifi :(")
                    q = input(" NR:NewReg / RT:Retry : ")
                    if q == "NR":
                        self._register_connect()
                        return
                    else:
                        self._do_connect(ssid, key)
                        return
                    # print("Aborted")
                    # sys.exit(127)
        print('OK')
        print('*> IP Address:', sta_if.ifconfig()[0])
        oled.text('> IP:{0}'.format(sta_if.ifconfig()[0]),0,60)
        oled.show()
