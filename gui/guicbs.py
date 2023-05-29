import dearpygui.dearpygui as dpg
from serial.tools import list_ports
import gsender2 as back
import queue


def windowresize(sender, appdata):
    pwwidth = dpg.get_item_width("primarywindow")
    pwheight = dpg.get_item_height("primarywindow")
    # if not dpg.get_y_scroll_max("primarywindow"):
    x_off = pwwidth - 258.0
    dpg.set_item_pos("controls", [x_off, 25])
    dpg.set_item_height("cominput", pwheight - 315)
    for tag in ["posplot", "velplot", "accplot", "errplot"]:
        dpg.set_item_height(tag, (pwheight - 50) / 5)
        dpg.set_item_width(tag, pwwidth - 272)
    dpg.set_item_height("responses", (pwheight - 50) / 5)
    dpg.set_item_width("respinput", pwwidth - 370)


def plotcb(sender, appdata):
    print(sender, appdata)


state = False


def listports():
    global state
    wshow = dpg.get_item_configuration("wportselect")["show"]
    if wshow != state:
        state = wshow
        if state:
            ports = list_ports.comports()
            portnames = []
            for port in ports:
                portnames.append(port.name)
            dpg.configure_item(
                "comboports", items=portnames, default_value=portnames[0]
            )


def wportsclose():
    global state
    state = False


def resappend(line: str):
    dpg.add_text(line, parent="respinput")
    dpg.set_y_scroll("respinput", -1)


def portconnect():
    portname = dpg.get_value("comboports")
    resappend(f"Connecting {portname}")
    dpg.configure_item("wportselect", show=False)
    back.run(portname)
    # dpg.configure_item('wportconnect', show=False)


def mconnect():
    if dpg.get_value("comboports"):
        portconnect()
    else:
        dpg.configure_item("wportselect", show=True)


def processqueue():
    try:
        resappend(back.recivequeue.get(block=False))
    except queue.Empty:
        pass


def updateplots():
    pass


def movebtn(sender, appdata):
    step = float(dpg.get_value("rstep"))
    back.sendqueue.put("G91")
    back.sendqueue.put(f"{sender}{step}")
    back.sendqueue.put("M114")


def homebtncb(sender):
    back.sendqueue.put(sender)
    back.sendqueue.put("M114")


def speedslidercb(sender, appdata):
    back.sendqueue.put(f"G0F{appdata*60000:.0f}")


def accslidercb(sender, appdata):
    acc = f"{appdata*1000:.0f}"
    back.sendqueue.put(f"M201 X{acc} Y{acc} Z{acc}")
    back.sendqueue.put(f"M202 X{acc} Y{acc} Z{acc}")


def comsendcb():
    if dpg.get_value("cominput"):
        for com in dpg.get_value("cominput").split("\n"):
            if com:
                back.sendqueue.put(com)

    if dpg.get_value("cbcls"):
        dpg.set_value("cominput", "")


def cominputcb(sender, appdata: str):
    if dpg.get_value("sendoncr"):
        if appdata.endswith("\n"):
            com = appdata.split("\n")[-2]
            if com:
                back.sendqueue.put(com)
