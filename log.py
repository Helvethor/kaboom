def to_file(filename, smt):
    with open(filename, "a") as f:
        f.write(smt + "\n") 

def debug(smt):
    to_file("debug.log", smt)

def server(smt):
    to_file("server.log", smt)
