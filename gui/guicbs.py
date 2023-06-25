import dearpygui.dearpygui as dpg
from serial.tools import list_ports
from printer import Printer

p = Printer()


def windowresize():
    """Adjasts main window layout on window resize
    """
    pwwidth = dpg.get_item_width("primarywindow")
    pwheight = dpg.get_item_height("primarywindow")
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


def listports():
    ports = list_ports.comports()
    portnames = []
    for port in ports:
        portnames.append(port.name)
    return portnames


def wportsclose():
    global state
    state = False


def resappend(line: str):
    texts = dpg.get_item_children("respinput")[1]
    if texts:
        pos = dpg.get_item_pos(texts[-1])
        pos[1] += 15
    else:
        pos = [8, 0]
    dpg.add_text(line, parent="respinput", pos=pos)
    dpg.set_y_scroll("respinput", -1)


def portconnect():
    portname = dpg.get_value("comboports")
    resappend(f"Connecting {portname}")
    dpg.configure_item("wportselect", show=False)
    dpg.configure_item("bdiconnect", show=True)
    if p.connect(portname):
        speed = dpg.get_value("CRspeed") * 60000
        acc = dpg.get_value("CRacc") * 1000
        p.write(f"G0F{speed:.0f}")
        p.write(f"M201 X{acc:.0f} Y{acc:.0f} Z{acc:.0f}")
        p.write(f"M202 X{acc:.0f} Y{acc:.0f} Z{acc:.0f}")
        for com in ["M114", "T2", "M155 S0"]:
            p.write(com)


def portdisconnect():
    p.disconnect()


def mselectport():
    portnames = listports()
    dpg.configure_item(
        "comboports",
        items=portnames,
        default_value=portnames[0],
    )
    dpg.configure_item("wportselect", show=True)


def mconnect():
    if dpg.get_value("comboports"):
        portconnect()
    else:
        mselectport()


def updatecoords(resp: str):
    coords = []
    resp = resp.split("\r")[0]
    for part in resp.split(" "):
        coords.append(float(part.split(":")[1]))
    dpg.set_value("XCOORD", coords[0])
    dpg.set_value("YCOORD", coords[1])
    dpg.set_value("ZCOORD", coords[2])


def connected(s):
    dpg.configure_item("bconnect", show=False)
    dpg.configure_item("bdiconnect", show=True)
    resappend("Connected")


p.onconnect += connected


def disconnected(s):
    dpg.configure_item("bconnect", show=True)
    dpg.configure_item("bdiconnect", show=False)
    resappend("Disconnected")


p.ondisconnect += disconnected


def recieved(s: str):
    if s:
        if s == "wait\r":
            pass
        elif s.startswith("X:"):
            updatecoords(s)
        elif s.startswith("GUI") and not dpg.get_value("filtergui"):
            pass
        elif s.startswith("ok") and not dpg.get_value("filterok"):
            pass
        else:
            resappend(s)


p.onrecieve += recieved
p.onerror += recieved


def sended(num: int, s: bytes):
    if dpg.get_value("filtercom"):
        resappend(f">>> {s.decode('ascii').split('*')[0]}")


p.onsend += sended


def updateplots(data):
    pass


p.ondataready += updateplots


def movebtn(sender, appdata):
    step = float(dpg.get_value("rstep"))
    p.write("G91")
    p.write(f"{sender}{step}")
    p.write("M114")


def speedslidercb(sender, appdata):
    p.write(f"G0F{appdata*60000:.0f}")


def accslidercb(sender, appdata):
    acc = f"{appdata*1000:.0f}"
    p.write(f"M201 X{acc} Y{acc} Z{acc}")
    p.write(f"M202 X{acc} Y{acc} Z{acc}")


def homebtncb(sender):
    p.write(sender)
    p.write("M114")
    speed = dpg.get_value("CRspeed")
    acc = dpg.get_value("CRacc")
    speedslidercb(None, speed)
    accslidercb(None, acc)


def comsendcb():
    if dpg.get_value("cominput"):
        for com in dpg.get_value("cominput").split("\n"):
            if com:
                p.write(com)

    if dpg.get_value("cbcls"):
        dpg.set_value("cominput", "")


def cominputcb(sender, appdata: str):
    print([appdata])
    if dpg.get_value("sendoncr"):
        for com in appdata.split("\n"):
            if com:
                p.write(com)
        if dpg.get_value("cbcls"):
            dpg.set_value("cominput", "")


def coordcb(sender, appdata: str):
    if sender == "XCOORD":
        com = f"G0X{float(appdata):.3f}"
    if sender == "YCOORD":
        com = f"G0Y{float(appdata):.3f}"
    if sender == "ZCOORD":
        com = f"G0Z{float(appdata):.3f}"
    p.write("G90")
    p.write(com)
    p.write("M114")


def getcoords():
    p.write("M114")


def cycleruncb():
    axis = dpg.get_value("CRaxis")
    dist = dpg.get_value("CRdist")
    speed = dpg.get_value("CRspeed")
    acc = dpg.get_value("CRacc")
    speedslidercb(None, speed)
    dpg.set_value("slspeed", speed)
    accslidercb(None, acc)
    dpg.set_value("slacc", acc)
    p.write("G91")
    if dpg.get_value("cbrec"):
        reclen = dpg.get_value("CRreclength")

        p.write(f"G405{axis}{reclen}")
    for i in range(dpg.get_value("CRnumber")):
        p.write(f"G0{axis}{dist}")
        p.write(f"G0{axis}{-dist}")
    p.write("M114")


def cyclestopcb():
    p.clear()
    p.write("M0")
    p.write("M112")


def pmerrorclose():
    dpg.delete_item("pmerror")
    dpg.remove_alias("pmerror")


def pmonitorcb():
    dpg.configure_item("pmonitor", show=True)


def pmgetnewpos():
    texts = dpg.get_item_children("pmtext")[1]
    if texts:
        pos = dpg.get_item_pos(texts[-1])
        pos[1] += 15
    else:
        pos = [8, 0]
    return pos


def pmonrecieve(s):
    dpg.add_text(f"<<< {s}\n", parent="pmtext", pos=pmgetnewpos())
    dpg.set_y_scroll("pmtext", -1)


p.onerror += pmonrecieve
p.onrecieve += pmonrecieve


def pmonsend(num, s: bytes):
    dpg.add_text(
        f">>> {s.decode('ascii').split('*')[0]}\n", parent="pmtext", pos=pmgetnewpos()
    )
    dpg.set_y_scroll("pmtext", -1)


p.onsend += pmonsend


def pmclosecb():
    dpg.configure_item("pmonitor", show=False)


def pmresizecb():
    width = dpg.get_item_width("pmonitor")
    height = dpg.get_item_height("pmonitor")
    dpg.set_item_height("pmtext", height - 60)
    dpg.set_item_width("pmtext", width - 15)
    dpg.set_y_scroll("pmtext", -1)


def pmclear():
    for text in dpg.get_item_children("pmtext")[1]:
        dpg.delete_item(text)


# def pemulatorcb():
#     ports = list_ports.comports()
#     portnames = []
#     for port in ports:
#         portnames.append(port.name)
#     dpg.configure_item("peport", items=portnames)
#     dpg.configure_item("pewindow", show=True)


# responder = Responder()


# def pestart():
#     responder.start(dpg.get_value("peport"))


# def pestop():
#     responder.stop()
#     responder.join()
#     dpg.configure_item("pewindow", show=False)
