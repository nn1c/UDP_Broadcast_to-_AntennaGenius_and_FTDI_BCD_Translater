import json
import socket
import xmltodict

from tkinter import *
from tkinter import ttk

global is_on
global radio_freq

import pyftdi
from pyftdi.gpio import *
from datetime import datetime

global window_settings

init = False
radio_freq = 0
is_on = True

gpios=[]
window_settings={}

try:
    gpio1 = GpioMpsseController()
    gpio2 = GpioMpsseController()
    gpio3 = GpioMpsseController()
    gpios = pyftdi.ftdi.Ftdi.list_devices()
except Exception as e: print (e)

device_urls=[]

for device in  range (len(gpios)):
    if ((((gpios[device][0][6]))) == ("C232HM-EDHSL-0")):
        device_urls.append("ftdi://ftdi:232h:"+(str((gpios[device][0][4])))+"/1")

device_count = (len(device_urls))

def init_settings():
    global window_settings
    try:
        with open("config.json") as json_data_file:
            window_settings=json.load(json_data_file)
    except:
        window_settings={"logger_ip":"127.0.0.1","logger_udp":"12060","AG_1_IP":"192.168.1.140","AG_1_UDP_Port":"9007","AG_1_RF_Port":"1"}
    


def get_bcd(frq):
    if frq < 2000:
        return 0b0001  # 160
    elif frq < 4000:
        return 0b0010  # 80
    elif frq < 6000:
        return 0b0000  # 60
    elif frq < 8000:
        return 0b0011  # 40
    elif frq < 11000:
        return 0b0100  # 30
    elif frq < 15000:
        return 0b0101  # 20
    elif frq < 19000:
        return 0b0110  # 17
    elif frq < 22000:
        return 0b0111  # 15
    elif frq < 25000:
        return 0b1000  # 12
    elif frq < 30000:
        return 0b1001  # 10
    elif frq < 60000:
        return 0b1010  # 6


def get_Ant(frq):
    if frq < 2000:
        return (1)  # 160
    elif frq < 4000:
        return (2)  # 80
    elif frq < 6000:
        return (12)  # 60
    elif frq < 8000:
        return (3)  # 40
    elif frq < 11000:
        return (4)  # 30
    elif frq < 15000:
        return (5)  # 20
    elif frq < 19000:
        return (6)  # 17
    elif frq < 22000:
        return (7)  # 15
    elif frq < 25000:
        return (8)  # 12
    elif frq < 30000:
        return (9)  # 10
    elif frq < 60000:
        return (11)  # 6


def set_AG(ipaddr, tcp_port, radio_nr, ant_port):
    tcp_str = ("!000a!00cc80!" + (str(radio_nr)) + ";" + (str((ant_port))))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5) #if unable to make a connection after a second, time out   
            s.connect((ipaddr, tcp_port))
            s.sendall((bytes(tcp_str, 'utf-8')))


            Label(tab2, text=("AG Message Delivered!")).grid(row=3)
    except:
        Label(tab2, text=("AG Comm Failure!")).grid(row=3)


def N1MM_UDP_Freq():
    return (0)


def freq_update():
    global is_on
    global radio_freq
    global window_settings
    window_settings={"logger_ip":ipaddr.get(),"logger_udp":udpport.get(),"AG_1_IP":AG_IP.get(),"AG_1_UDP_Port":AG_TCP.get(),"AG_1_RF_Port":AG_RF.get()}
    if is_on == False:
        try:
    
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)  # UDP
            sock.bind((window_settings["logger_ip"], (eval(window_settings["logger_udp"]))))
            data, addr = sock.recvfrom(2048)
            xml_str = (data.decode("utf-8"))
            radio_dict = (json.loads((json.dumps(xmltodict.parse(xml_str)))))
            if radio_dict["RadioInfo"]["RadioNr"] == "1":
                freq = (eval(radio_dict["RadioInfo"]["Freq"]) / 100)
                radio_freq = freq
                radfreq.config(text=((str(freq)) + " kHz"))
                set_AG((window_settings["AG_1_IP"]),(eval(window_settings["AG_1_UDP_Port"])),(window_settings["AG_1_RF_Port"]),get_Ant(radio_freq))
                if device_count > 0:
                    gpio1.write(get_bcd(radio_freq))
                if device_count > 1:
                    gpio2.write(get_bcd(radio_freq))
                if device_count > 2:
                    gpio3.write(get_bcd(radio_freq))
        except Exception as e:
            print(str(e))

    window.after(500, freq_update)


def switch():
    global is_on
    if is_on:
        on_button.config(fg="red", text="Stop")
        is_on = False
    else:
        on_button.config(fg="green", text="Start")
        is_on = True


window = Tk()

window.title("IP Band Decoder")

tab_control = ttk.Notebook(window)

tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)

Label(tab1, text="Logger IP Address:").grid(row=0)
ipaddr = Entry(tab1)
ipaddr.grid(column=1, row=0)


Label(tab1, text="Logger UDP Port:").grid(row=1)
udpport = Entry(tab1)
udpport.grid(column=1, row=1)


Label(tab1, text="Radio Freq:").grid(row=4)
radfreq = Label(tab1, text="FreqHere")
radfreq.grid(column=1, row=4)

on_button = Button(tab1, text="Start", bd=0, command=switch, fg="green", )
on_button.grid(row=3, column=1)

Label(tab2, text="IP Address:").grid(row=0)
AG_IP = Entry(tab2)
AG_IP.grid(column=1, row=0)


Label(tab2, text="TCP Port:").grid(row=1)
AG_TCP = Entry(tab2)
AG_TCP.grid(column=1, row=1)


Label(tab2, text="AG Port:").grid(row=2)
AG_RF = Entry(tab2)
AG_RF.grid(column=1, row=2)

init_settings()

ipaddr.insert(0, window_settings["logger_ip"])
udpport.insert(0, window_settings["logger_udp"])
AG_IP.insert(0, window_settings["AG_1_IP"])
AG_TCP.insert(0, window_settings["AG_1_UDP_Port"])
AG_RF.insert(0, window_settings["AG_1_RF_Port"])



Label(tab3, text="FTDI Device URLs:").grid(row=0)

if device_count > 0:
    gpio1.configure(device_urls[0], direction=(0xFF & ((1 << 8) - 1)), frequency=1e3, initial=0x0)
    Label(tab3, text=device_urls[0]).grid(row=1)
if device_count > 1:
    gpio2.configure(device_urls[1], direction=(0xFF & ((1 << 8) - 1)), frequency=1e3, initial=0x0)
    Label(tab3, text=device_urls[1]).grid(row=2)
if device_count > 2:
    gpio3.configure(device_urls[2], direction=(0xFF & ((1 << 8) - 1)), frequency=1e3, initial=0x0)
    Label(tab3, text=device_urls[2]).grid(row=2)




tab_control.add(tab1, text='Freq Data')
tab_control.add(tab3, text='BPF Control')
tab_control.add(tab2, text='4O3A Band Ports')

tab_control.pack(expand=1, fill='both')
window.after(100, freq_update)
window.mainloop()

json_config_file = open("config.json", "w")
json.dump(window_settings, json_config_file)
json_config_file.close()



