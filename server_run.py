import server, log


def main():

    game_server = server.GameServer()
    game_server.start()


if __name__ == "__main__":

    try:
        main()

    except Exception as e:
        log.server("server.main:: exception: {}".format(e))


