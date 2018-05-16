#!/usr/bin/python
import sys
import getopt
import socket
import time

# TODO Support file containing list of sites to check
# TODO Support for expected state in sites to check
# TODO Parse response from server into plain text
# TODO Write clean output OK/ERROR/ALLOW/DENY
# TODO Add timing library

def usage():
    print('Usage: send_request [-h|--help] [-n|--n2h2|-w|--websense] [-a|--alive] [-u|--url <url>] [-s|--server <servername|ip>] [-p|--port <port number>]')


def isopen(ip,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
        s.connect((ip, int(port)))
        sockettimeout = 5
        s.settimeout(sockettimeout)
        s.shutdown(2)
        return True
   except:
        return False


def isalive(s,protocol):
    return send_alive(s, protocol)


def send_alive(s, protocol):
    data = ''
    if protocol == 'n2h2':
        print('Sending alive request')
        alive = '\x02\x03\x01\x02\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        s.sendall(bytes(alive))
        data = s.recv(256)
        print('Received', repr(data))
    else:
        print('Sending alive request')
        alive = '\x00\x0c\x00\x81\x00\x01\x00\x00\x02\x0a\x09\x09'
        s.sendall(bytes(alive))
        data = s.recv(256)
        print('Received', repr(data))
    if data != '':
        return True
    else:
        return False


def send_url(s, protocol, url):
    data = ''
    if protocol == 'n2h2':
        print('Sending url request: %s' % url)
        hdr = '\x02\x00\x01\x01\x01\x01'
        srcip = [192, 168, 0, 1]
        destip = [192, 168, 100, 1]
        url_req = hdr
        for chars in srcip:
            url_req += chr(chars)
        for chars in destip:
            url_req += chr(chars)
        len1 = len(url) / 256
        len2 = len(url) % 256
        url_req += chr(len1)
        url_req += chr(len2)
        url_req += '\x00\x00'
        url_req += str(url)
        url_req += '\x00'
        s.sendall(bytes(url_req))
        data = s.recv(1024)
        print('Received', repr(data))
    else:
        print('Sending url request: %s', url)
        len1 = (26+len(url)) / 256
        len2 = (26+len(url)) % 256
        url_req = chr(len1)
        url_req += chr(len2)
        url_req += '\x00\x80\x00\x01\x00\x00\x04\x01\x02\x05\x00\x01\x00\x00'
        srcip = [192, 168, 0, 1]
        destip = [192, 168, 100, 1]
        for chars in srcip:
            url_req += chr(chars)
        for chars in destip:
            url_req += chr(chars)
        len1 = len(url) / 256
        len2 = len(url) % 256
        url_req += chr(len1)
        url_req += chr(len2)
        url_req += str(url)
        s.sendall(bytes(url_req))
        data = s.recv(1024)
        print('Received', repr(data))
    if data != '':
        return True
    else:
        return False

def main():
    print("Openufp URL tester v1.0")
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hnwau:s:p:', ['help', 'n2h2','websense', 'alive', 'url','server','port'])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(1)

    protocol = ''
    alive = 0
    url = ''
    host = ''
    port = 0
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-n', '--n2h2'):
            protocol = 'n2h2'
        elif o in ('-w','--websense'):
            protocol = 'websense'
        elif o in ('-a', '--alive'):
            alive = 1
        elif o in ('-u', '--url'):
            url = a
        elif o in ('-s', '--server'):
            host = a
        elif o in ('-p', '--port'):
            port = a
        else:
            assert False, 'unhandled option'

    if (protocol != 'n2h2' and protocol != 'websense') or (alive == 0 and url == ''):
        usage()
        sys.exit()

    if host == '':
        host = 'localhost'

    if port == 0 and protocol == 'n2h2':
        port = 4005
    elif port == 0:
        port = 15868

    if isopen(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        if alive == 1:
            if not isalive(s, protocol):
                # Host online/port open no reply to alive request
                print("ERROR: isalive check on %s port %s failed, host online port open but no reply", host, port)
                sys.exit(3)
        if url != '':
            if not send_url(s, protocol, url):
                # Host online/port open no reply to url request
                print("ERROR: url check on %s port %s failed, host online port open but no reply", host, port)
                sys.exit(4)
        s.close()
    else:
        # Host / Port not open
        print("ERROR: isopen check on %s port %s failed", host, port)
        sys.exit(2)


if __name__ == '__main__':
    main()
