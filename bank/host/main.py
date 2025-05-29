import argparse
import multiprocessing
from nitro_toolkit.host import HostApp
from nitro_toolkit.util.server import logger, HOST_SERVER_PORT

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vsock", action="store_true", help="Enable vsock mode (optional)")
    parser.add_argument("--cid",type=int,default=None, help="Enclave CID (optional)")
    parser.add_argument("--server-only", action="store_true", help="Only start the server (optional)")
    parser.add_argument("--server-port", type=int, default=HOST_SERVER_PORT, help="Server port (optional)")
    args = parser.parse_args()
    
    host_app = HostApp(args.vsock, args.cid, args.server_port, args.server_only)

    try:
        host_app.start()
        host_app.server_process.join()
        if not host_app.server_only:
            host_app.proxy_process.join()
    except KeyboardInterrupt:
        logger.info("caught Ctrl+C, shutting down...")
        host_app.stop()
        logger.info("all servers shutdown cleanly.")
        return


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')  # for Windows / Mac / Linux
    main()