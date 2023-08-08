import atexit


first_time = True


@atexit.register
def on_quit():
    global first_time
    if not first_time:
        return
    print("[brush_manager] atexit::on_quit()")
    first_time = False
