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
                "comboports",
                items=portnames,
                default_value=portnames[0],
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
    dpg.configure_item("bdiconnect", show=True)
    back.run(portname)
    speed = dpg.get_value("CRspeed")
    acc = dpg.get_value("CRacc") * 1000
    back.sendqueue.put(f"G0F{speed*60000:.0f}")
    back.sendqueue.put(f"M201 X{acc:.0f} Y{acc:.0f} Z{acc:.0f}")
    back.sendqueue.put(f"M202 X{acc:.0f} Y{acc:.0f} Z{acc:.0f}")
    # dpg.configure_item('wportconnect', show=False)


def portdisconnect():
    back.stop()


def mconnect():
    if dpg.get_value("comboports"):
        portconnect()
    else:
        dpg.configure_item("wportselect", show=True)


def updatecoords(resp: str):
    coords = []
    resp = resp.split("\r")[0]
    for part in resp.split(" "):
        coords.append(float(part.split(":")[1]))
    dpg.set_value("XCOORD", coords[0])
    dpg.set_value("YCOORD", coords[1])
    dpg.set_value("ZCOORD", coords[2])


def processqueue():
    if not back.recivequeue.empty():
        resp: str = back.recivequeue.get(block=False)
        if not resp == "wait\r":
            print([resp])
        if resp:
            if resp == "Connected":
                dpg.configure_item("bconnect", show=False)
                dpg.configure_item("bdiconnect", show=True)
                resappend(resp)
            elif resp == "Disconnected":
                dpg.configure_item("bconnect", show=True)
                dpg.configure_item("bdiconnect", show=False)
                resappend(resp)
            elif resp.startswith("X:"):
                updatecoords(resp)
            elif resp.endswith("\x00\x00\n"):
                pass
            elif resp.startswith(">") and not dpg.get_value("filtercom"):
                pass
            elif resp == "wait\r":
                pass
            elif resp.startswith("GUI") and not dpg.get_value("filtergui"):
                pass
            else:
                resappend(resp)


def updateplots():
    pass


def movebtn(sender, appdata):
    step = float(dpg.get_value("rstep"))
    back.sendqueue.put("G91")
    back.sendqueue.put(f"{sender}{step}")
    back.sendqueue.put("M114")


def speedslidercb(sender, appdata):
    back.sendqueue.put(f"G0F{appdata*60000:.0f}")


def accslidercb(sender, appdata):
    acc = f"{appdata*1000:.0f}"
    back.sendqueue.put(f"M201 X{acc} Y{acc} Z{acc}")
    back.sendqueue.put(f"M202 X{acc} Y{acc} Z{acc}")


def homebtncb(sender):
    back.sendqueue.put(sender)
    back.sendqueue.put("M114")
    speed = dpg.get_value("CRspeed")
    acc = dpg.get_value("CRacc")
    speedslidercb(None, speed)
    accslidercb(None, acc)


def comsendcb():
    if dpg.get_value("cominput"):
        for com in dpg.get_value("cominput").split("\n"):
            if com:
                back.sendqueue.put(com)

    if dpg.get_value("cbcls"):
        dpg.set_value("cominput", "")


def cominputcb(sender, appdata: str):
    print([appdata])
    if dpg.get_value("sendoncr"):
        # if appdata.endswith("\n"):
        for com in appdata.split("\n"):
            if com:
                back.sendqueue.put(com)
        if dpg.get_value("cbcls"):
            dpg.set_value("cominput", "")


def coordcb(sender, appdata: str):
    if sender == "XCOORD":
        com = f"G0X{float(appdata):.3f}"
    if sender == "YCOORD":
        com = f"G0Y{float(appdata):.3f}"
    if sender == "ZCOORD":
        com = f"G0Z{float(appdata):.3f}"
    back.sendqueue.put("G90")
    back.sendqueue.put(com)
    back.sendqueue.put("M114")


def getcoords():
    back.sendqueue.put("M114")


def clearsendqueue():
    while not back.sendqueue.empty():
        back.sendqueue.get()


def cycleruncb():
    axis = dpg.get_value("CRaxis")
    dist = dpg.get_value("CRdist")
    speed = dpg.get_value("CRspeed")
    acc = dpg.get_value("CRacc")
    speedslidercb(None, speed)
    dpg.set_value("slspeed", speed)
    accslidercb(None, acc)
    dpg.set_value("slacc", acc)
    back.sendqueue.put("G91")
    if dpg.get_value("cbrec"):
        reclen = dpg.get_value("CRreclength")

        back.sendqueue.put(f"G405{axis}{reclen}")
    for i in range(dpg.get_value("CRnumber")):
        back.sendqueue.put(f"G0{axis}{dist}")
        back.sendqueue.put(f"G0{axis}{-dist}")
    back.sendqueue.put("M114")


def cyclestopcb():
    clearsendqueue()
    back.sendqueue.put("M0")
    back.sendqueue.put("M112")
