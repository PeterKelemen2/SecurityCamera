import capture
import config
import interface
import time
conf = None


def main():
    global conf
    conf = config.load_config()
    print(conf["rec_sec"])
    capture.run_capture_on_thread()
    time.sleep(1)
    user_interface = interface.Interface()


if __name__ == '__main__':
    main()
