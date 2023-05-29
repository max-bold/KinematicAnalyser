import dearpygui.dearpygui as dpg
import guicbs as cb
import serial.tools.list_ports as serlist

dpg.create_context()
dpg.create_viewport(title="Custom Title", width=600, height=650)

with dpg.item_handler_registry(tag="window_handler"):
    dpg.add_item_resize_handler(callback=cb.windowresize)

with dpg.window(tag="primarywindow") as mw:
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Connect")

        with dpg.menu(label="Setings"):
            dpg.add_menu_item(
                label="Connect",
                callback=cb.mconnect,
                tag="bconnect",
            )
            dpg.add_menu_item(
                label="Disconnect",
                show=False,
                tag="bdiconnect",
                callback=cb.portdisconnect,
            )
            dpg.add_menu_item(
                label="Select port",
                callback=lambda: dpg.configure_item("wportselect", show=True),
            )

        with dpg.menu(label="Tools"):
            dpg.add_menu_item(
                label="Cycle run",
                callback=lambda: dpg.configure_item("cyclewindow", show=True),
            )
            dpg.add_menu_item(label="Extruder test")
            dpg.add_menu_item(
                label="Machine control",
                callback=lambda: dpg.configure_item("wmachine", show=True),
            )

    with dpg.group(horizontal=True):
        with dpg.group(pos=[8, 25]):
            with dpg.plot(tag="posplot", callback=cb.plotcb):
                dpg.add_plot_axis(dpg.mvXAxis, no_tick_labels=True)
                with dpg.plot_axis(dpg.mvYAxis, label="mm"):
                    pass
                    # dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)")
            with dpg.plot(tag="velplot"):
                dpg.add_plot_axis(dpg.mvXAxis, no_tick_labels=True)
                with dpg.plot_axis(dpg.mvYAxis, label="m/s"):
                    pass
            with dpg.plot(tag="accplot"):
                dpg.add_plot_axis(dpg.mvXAxis, no_tick_labels=True)
                with dpg.plot_axis(dpg.mvYAxis, label="m/s2"):
                    pass
            with dpg.plot(tag="errplot"):
                dpg.add_plot_axis(dpg.mvXAxis)
                with dpg.plot_axis(dpg.mvYAxis, label="mm"):
                    pass
            with dpg.group(horizontal=True, tag="responses"):
                dpg.add_child_window(width=100, tag="respinput", indent=-5)
                with dpg.group():
                    dpg.add_checkbox(label="Commands", default_value=True, tag='filtercom')
                    dpg.add_checkbox(label="GUI", default_value=False)
                    dpg.add_checkbox(label="OK/RESEND", default_value=False)
                    dpg.add_checkbox(label="DATA", default_value=False)

        with dpg.group(tag="controls"):
            with dpg.group(horizontal=True, horizontal_spacing=5):
                dpg.add_input_float(
                    width=80,
                    on_enter=True,
                    step=0,
                    callback=cb.coordcb,
                    tag="XCOORD",
                )
                dpg.add_input_float(
                    width=80,
                    on_enter=True,
                    step=0,
                    callback=cb.coordcb,
                    tag="YCOORD",
                )
                dpg.add_input_float(
                    width=60,
                    on_enter=True,
                    step=0,
                    callback=cb.coordcb,
                    tag="ZCOORD",
                )
                dpg.add_button(width=15, label="R", callback=cb.getcoords)
            dpg.add_separator()
            with dpg.group(horizontal=True, horizontal_spacing=5):
                dpg.add_button(
                    label="X+",
                    width=80,
                    height=50,
                    callback=cb.movebtn,
                    tag="G0X",
                )
                dpg.add_button(
                    label="Y+",
                    width=80,
                    height=50,
                    callback=cb.movebtn,
                    tag="G0Y",
                )
                dpg.add_button(
                    label="Z+",
                    width=80,
                    height=50,
                    callback=cb.movebtn,
                    tag="G0Z",
                )
            with dpg.group(horizontal=True, horizontal_spacing=5):
                dpg.add_button(
                    label="X-",
                    width=80,
                    height=50,
                    callback=cb.movebtn,
                    tag="G0X-",
                )
                dpg.add_button(
                    label="Y-",
                    width=80,
                    height=50,
                    callback=cb.movebtn,
                    tag="G0Y-",
                )
                dpg.add_button(
                    label="Z-",
                    width=80,
                    height=50,
                    callback=cb.movebtn,
                    tag="G0Z-",
                )
            with dpg.group(horizontal=True, horizontal_spacing=5):
                dpg.add_button(label="XH", width=80, callback=cb.homebtncb, tag="G28X")
                dpg.add_button(label="YH", width=80, callback=cb.homebtncb, tag="G28Y")
                dpg.add_button(label="ZH", width=80, callback=cb.homebtncb, tag="G28Z")
            dpg.add_radio_button(
                ["0.01", "0.1", "1", "10", "100"],
                horizontal=True,
                tag="rstep",
                default_value="0.01",
            )
            dpg.add_separator()
            dpg.add_slider_float(
                label="V m/s",
                width=180,
                min_value=0.01,
                max_value=2,
                default_value=0.1,
                callback=cb.speedslidercb,
                tag='slspeed',
            )
            dpg.add_slider_float(
                label="A m/s2",
                width=180,
                min_value=0.1,
                max_value=20,
                default_value=3,
                callback=cb.accslidercb,
                tag='slacc'
            )
            dpg.add_separator()
            dpg.add_input_text(
                multiline=True,
                height=300,
                width=250,
                tag="cominput",
                callback=cb.cominputcb,
            )
            with dpg.group(horizontal=True, horizontal_spacing=5):
                dpg.add_button(label="Send", width=195, callback=cb.comsendcb)
                dpg.add_button(
                    label="X", width=50, callback=lambda: dpg.set_value("cominput", "")
                )
            with dpg.group(horizontal=True):
                dpg.add_checkbox(label="clear on send", tag="cbcls")
                dpg.add_checkbox(label="send on CR", tag="sendoncr")

with dpg.window(
    label="Cycle run", show=False, tag="cyclewindow", width=300, pos=[30, 40]
):
    dpg.add_radio_button(["X", "Y", "Z"], horizontal=True, tag="CRaxis", default_value='X')
    dpg.add_input_float(label="Distance, mm", width=150, default_value=30, tag="CRdist")
    dpg.add_input_float(
        label="Max speed, m/s", width=150, default_value=0.1, tag="CRspeed"
    )
    dpg.add_input_float(label="Acc, m/s2", width=150, default_value=3, tag="CRacc")
    dpg.add_input_int(label="Repitions", width=150, default_value=10, tag="CRnumber")
    dpg.add_checkbox(
        label="Run record",
        default_value=True,
        tag="cbrec",
        callback=lambda: dpg.configure_item("inpreclen", show=dpg.get_value("cbrec")),
    )
    dpg.add_input_int(
        label="Record length, ms",
        max_value=10000,
        min_value=1,
        default_value=5000,
        max_clamped=True,
        min_clamped=True,
        width=150,
        tag="CRreclength",
    )
    with dpg.group(horizontal=True):
        dpg.add_button(label="RUN", width=50, callback=cb.cycleruncb)
        dpg.add_button(label="STOP", width=50, callback=cb.cyclestopcb)

with dpg.window(
    label="Macine control",
    tag="wmachine",
    pos=[30, 40],
    show=False,
    width=350,
):
    with dpg.group(horizontal=True):
        dpg.add_button(label="OPEN")
        dpg.add_button(label="CLOSE")
        dpg.add_text("Door")
    dpg.add_separator()
    dpg.add_slider_int(label="Vacum table", width=150, min_value=0, max_value=100)
    dpg.add_slider_int(label="Table temp", width=150, min_value=0, max_value=200)
    dpg.add_separator()
    dpg.add_radio_button(
        ["E1", "E2", "All up"],
        label="Extruder",
        horizontal=True,
        default_value="All up",
    )
    dpg.add_slider_int(label="E1 temp", width=150, min_value=0, max_value=500)
    dpg.add_slider_int(label="E2 temp", width=150, min_value=0, max_value=500)
    with dpg.group(horizontal=True):
        dpg.add_radio_button(["ON", "OFF"], horizontal=True)
        dpg.add_text("Autofill")

with dpg.window(
    label="Port selection",
    width=350,
    pos=[30, 40],
    tag="wportselect",
    show=False,
    on_close=cb.wportsclose,
):
    dpg.add_text(
        "All availible ports are listed below. \nAfter connecting a new device \nplease reopen this window"
    )
    dpg.add_combo([], width=-1, tag="comboports")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Connect", callback=cb.portconnect)
        dpg.add_button(
            label="Cancell",
            callback=lambda: dpg.configure_item("wportselect", show=False),
        )

with dpg.item_handler_registry(tag="wport handler"):
    dpg.add_item_visible_handler(callback=cb.listports)

dpg.bind_item_handler_registry("primarywindow", "window_handler")
dpg.bind_item_handler_registry("wportselect", "wport handler")
dpg.set_primary_window("primarywindow", True)
dpg.setup_dearpygui()
dpg.show_viewport()
# dpg.start_dearpygui()
while dpg.is_dearpygui_running():
    cb.processqueue()
    cb.updateplots()
    dpg.render_dearpygui_frame()
dpg.destroy_context()
