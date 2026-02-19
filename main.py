import argparse
import sys
from broadcast_client import BroadcastClient
from server import BroadcastServer
from config import DEFAULT_HOST, DEFAULT_PORT

def start_server(args):
    server = BroadcastServer(host=args.host, port=args.port)
    server.start()

def start_client(args):
    client = BroadcastClient(host=args.host, port=args.port)
    client.connect()

def main():
    parser = argparse.ArgumentParser(
        description='Broadcast Server - Real-time message broadcasting'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute', required=True)

    start_parser = subparsers.add_parser('start', help='Start the broadcast server')
    start_parser.add_argument(
        '--host',
        default=DEFAULT_HOST,
        help=f"Host to bind to (default: {DEFAULT_HOST})"
    )
    start_parser.add_argument(
        '--port',
        type=int,
        default=DEFAULT_PORT,
        help=f'Port to listen on (default: {DEFAULT_PORT})'
    )


    connect_parser = subparsers.add_parser(
        'connect',
        help='Connect to a broadcast server'
    )
    connect_parser.add_argument(
        '--host',
        default=DEFAULT_HOST, 
        help=f"Server host to connect to (default: {DEFAULT_HOST})"
    )
    connect_parser.add_argument(
        '--port',
        type=int, 
        default=DEFAULT_PORT,
         help=f'Server port to connect to (default: {DEFAULT_PORT})'
    )


    args = parser.parse_args()

    if args.command == 'start':
        start_server(args)
    elif args.command == 'connect':
        start_client(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
