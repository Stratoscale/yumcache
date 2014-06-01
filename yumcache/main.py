import socket
import argparse
from yumcache import connectionthread
from yumcache import common
import logging


def main(args):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", args.port))
    server.listen(10)
    commonInstance = common.Common(args.storage, bogusURLs=_parseBogusURLs(args))
    logging.info("YumCache server is up and running")
    while True:
        connection, peer = server.accept()
        connectionthread.ConnectionThread(connection, commonInstance)


def _parseBogusURLs(args):
    if args.bogusURL is None:
        return dict()
    result = dict()
    for bogusURLArgument in args.bogusURL:
        parts = bogusURLArgument.split("::")
        result[parts[0]] = parts[1:]
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    requestsLogger = logging.getLogger('requests.packages.urllib3.connectionpool')
    requestsLogger.setLevel(logging.CRITICAL)
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1012)
    parser.add_argument("--storage", default="/var/lib/yumcache")
    parser.add_argument("--bogusURL", action="append", help="Example: www.idontexist.com::localhost:8080/firstMirror::10.0.0.1/moreMirrors")
    args = parser.parse_args()
    main(args)
