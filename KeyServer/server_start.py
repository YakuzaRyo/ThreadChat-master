from ChatServer.server import Server
import argparse

if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8878)
    parser.add_argument('--interface', type=str, default='tokennnnnnnnn')
    args = parser.parse_args()
    server = Server()
    server.start(args.port,args.interface)
