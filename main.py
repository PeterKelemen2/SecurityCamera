import capture
import config
import interface

conf = None


def main():
    global conf
    conf = config.load_config()
    print(conf["rec_sec"])

    user_interface = interface.Interface()


if __name__ == '__main__':
    main()
