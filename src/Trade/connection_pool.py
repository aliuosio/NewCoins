#!/usr/bin/env python3
"""
MEXC API Connection Pool Server

This module provides a persistent connection pool for the MEXC API
that can be shared between different processes.
"""
import os
import sys
import time
import json
import socket
import threading
import logging
import signal
import datetime
from typing import Dict, Any, Optional
import socketserver
from mexc_sdk import Spot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Socket configuration
SOCKET_PATH = "/dev/shm/mexc_connection.sock"
PID_FILE = "/dev/shm/mexc_connection.pid"
LAST_ACTIVITY_FILE = "/dev/shm/mexc_connection_last_activity.txt"

# Get idle timeout from environment (default: 20 minutes in seconds)
IDLE_TIMEOUT = int(os.getenv('MEXC_POOL_TIMEOUT', 1200))

# Log the configuration
logger.info(f"Connection pool timeout: {IDLE_TIMEOUT} seconds")

# Command constants
CMD_PING = "PING"
CMD_NEW_ORDER = "NEW_ORDER"
CMD_ACCOUNT_INFO = "ACCOUNT_INFO"
CMD_EXCHANGE_INFO = "EXCHANGE_INFO"
CMD_TICKER_PRICE = "TICKER_PRICE"
CMD_TIME = "TIME"
CMD_SHUTDOWN = "SHUTDOWN"
CMD_FUTURES_EXISTS = "FUTURES_EXISTS"

class MEXCConnectionHandler(socketserver.BaseRequestHandler):
    """
    Handler for MEXC API connection requests
    """
    def handle(self):
        try:
            # Receive data
            data = self.request.recv(4096).decode('utf-8')
            if not data:
                return
            
            # Update last activity timestamp
            self.server.update_last_activity()
            
            # Parse command and parameters
            try:
                command_data = json.loads(data)
                command = command_data.get('command')
                params = command_data.get('params', {})
            except json.JSONDecodeError:
                self.send_response({"error": "Invalid JSON format"})
                return
            
            # Process command
            if command == CMD_PING:
                response = self.server.mexc_client.ping()
                self.send_response({"result": response})
            
            elif command == CMD_NEW_ORDER:
                symbol = params.get('symbol')
                side = params.get('side')
                order_type = params.get('type')
                options = params.get('options', {})
                
                if not all([symbol, side, order_type]):
                    self.send_response({"error": "Missing required parameters"})
                    return
                
                response = self.server.mexc_client.new_order(symbol, side, order_type, options=options)
                self.send_response({"result": response})
            
            elif command == CMD_ACCOUNT_INFO:
                response = self.server.mexc_client.account_info()
                self.send_response({"result": response})
            
            elif command == CMD_EXCHANGE_INFO:
                response = self.server.mexc_client.exchange_info()
                self.send_response({"result": response})
            
            elif command == CMD_TICKER_PRICE:
                symbol = params.get('symbol')
                response = self.server.mexc_client.ticker_price(symbol) if symbol else self.server.mexc_client.ticker_price()
                self.send_response({"result": response})
            
            elif command == CMD_TIME:
                response = self.server.mexc_client.time()
                self.send_response({"result": response})
            
            elif command == CMD_SHUTDOWN:
                logger.info("Shutdown command received")
                self.send_response({"result": "Shutting down"})
                threading.Thread(target=self.server.shutdown).start()
            
            elif command == CMD_FUTURES_EXISTS:
                base_currency = params.get('symbol')
                if not base_currency:
                    self.send_response({"error": "Missing required parameter: symbol"})
                    return
                try:
                    from mexc_sdk import Futures
                    futures_client = Futures()
                    contracts = futures_client.market_get_contracts()
                    target_symbol = f"{base_currency.upper()}_USDT"
                    exists = False
                    for contract in contracts['data']:
                        if contract['symbol'] == target_symbol and contract['state'] == 'online':
                            exists = True
                            break
                    self.send_response({"result": exists})
                except Exception as e:
                    logger.error(f"Error checking futures contract: {str(e)}")
                    self.send_response({"error": str(e)})
            else:
                self.send_response({"error": f"Unknown command: {command}"})
        
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            self.send_response({"error": str(e)})
    
    def send_response(self, data: Dict[str, Any]) -> None:
        """Send JSON response back to client"""
        try:
            response = json.dumps(data).encode('utf-8')
            self.request.sendall(response)
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")

class MEXCConnectionServer(socketserver.ThreadingUnixStreamServer):
    """
    Server that maintains a persistent connection to MEXC API
    """
    def __init__(self, server_address):
        self.mexc_client = None
        self.initialize_client()
        self.idle_timeout = IDLE_TIMEOUT
        self.idle_check_interval = 60  # Check for idle timeout every 60 seconds
        socketserver.ThreadingUnixStreamServer.__init__(self, server_address, MEXCConnectionHandler)
        
        # Initialize last activity time
        self.update_last_activity()
        
        # Start idle timeout checker thread
        self.idle_checker = threading.Thread(target=self._check_idle_timeout, daemon=True)
        self.idle_checker.start()
    
    def initialize_client(self) -> None:
        """Initialize MEXC API client"""
        try:
            api_key = os.getenv('MEXC_API_KEY')
            api_secret = os.getenv('MEXC_API_SECRET')
            if not api_key or not api_secret:
                raise ValueError("MEXC_API_KEY and MEXC_API_SECRET must be set in the .env file.")
            
            self.mexc_client = Spot(api_key=api_key, api_secret=api_secret)
            # Test connection
            self.mexc_client.ping()
            logger.info("MEXC API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MEXC API client: {str(e)}")
            raise
    
    def update_last_activity(self) -> None:
        """Update the last activity timestamp"""
        current_time = datetime.datetime.now().isoformat()
        try:
            with open(LAST_ACTIVITY_FILE, 'w') as f:
                f.write(current_time)
            logger.debug(f"Updated last activity timestamp: {current_time}")
        except Exception as e:
            logger.error(f"Failed to update last activity timestamp: {str(e)}")
    
    def _check_idle_timeout(self) -> None:
        """Check if the server has been idle for too long and shut it down if necessary"""
        while True:
            try:
                # Sleep first to avoid immediate shutdown
                time.sleep(self.idle_check_interval)
                
                # Check if last activity file exists
                if not os.path.exists(LAST_ACTIVITY_FILE):
                    self.update_last_activity()
                    continue
                
                # Read last activity timestamp
                try:
                    with open(LAST_ACTIVITY_FILE, 'r') as f:
                        last_activity_str = f.read().strip()
                    last_activity = datetime.datetime.fromisoformat(last_activity_str)
                except (ValueError, IOError) as e:
                    logger.error(f"Error reading last activity timestamp: {str(e)}")
                    self.update_last_activity()
                    continue
                
                # Calculate idle time
                now = datetime.datetime.now()
                idle_seconds = (now - last_activity).total_seconds()
                
                # Log idle time periodically
                if idle_seconds > 300:  # Log every 5 minutes of inactivity
                    idle_minutes = int(idle_seconds / 60)
                    logger.info(f"Connection pool has been idle for {idle_minutes} minutes")
                
                # Check if idle timeout has been reached
                if idle_seconds > self.idle_timeout:
                    logger.info(f"Connection pool idle timeout reached ({self.idle_timeout} seconds). Shutting down.")
                    # Clean up and shut down
                    if os.path.exists(PID_FILE):
                        os.remove(PID_FILE)
                    if os.path.exists(SOCKET_PATH):
                        os.remove(SOCKET_PATH)
                    if os.path.exists(LAST_ACTIVITY_FILE):
                        os.remove(LAST_ACTIVITY_FILE)
                    # Shut down the server
                    threading.Thread(target=self.shutdown).start()
                    break
            except Exception as e:
                logger.error(f"Error in idle timeout checker: {str(e)}")
                time.sleep(60)  # Sleep for a minute on error

def is_server_running() -> bool:
    """Check if the connection pool server is already running"""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            # Check if process is still running
            os.kill(pid, 0)  # This will raise an exception if the process is not running
            return True
        except (ProcessLookupError, ValueError, FileNotFoundError):
            # Process not running or PID file is invalid
            cleanup_server_files()
            return False
    return False

def cleanup_server_files() -> None:
    """Clean up server files"""
    for file_path in [PID_FILE, SOCKET_PATH, LAST_ACTIVITY_FILE]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Removed file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to remove file {file_path}: {str(e)}")

def start_server() -> None:
    """Start the connection pool server"""
    if is_server_running():
        logger.info("Connection pool server is already running")
        return
    
    # Clean up any existing server files
    cleanup_server_files()
    
    # Start server
    server = MEXCConnectionServer(SOCKET_PATH)
    
    # Save PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    # Handle signals for clean shutdown
    def handle_signal(signum, frame):
        logger.info(f"Received signal {signum}, shutting down")
        cleanup_server_files()
        server.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    timeout_minutes = IDLE_TIMEOUT // 60
    logger.info(f"Connection pool server started at {SOCKET_PATH} (idle timeout: {timeout_minutes} minutes)")
    server.serve_forever()

class MEXCPoolClient:
    """
    Client for the MEXC API connection pool
    """
    def futures_contract_exists(self, symbol: str) -> bool:
        response = self._send_command(CMD_FUTURES_EXISTS, {"symbol": symbol})
        if "error" in response:
            raise Exception(response["error"])
        return response.get("result", False)

    def __init__(self, start_if_not_running: bool = False):
        self.socket_path = SOCKET_PATH
        if start_if_not_running and not is_server_running():
            self._start_server()
        elif is_server_running():
            # Update last activity timestamp to prevent timeout during initialization
            self._touch_activity_file()
    
    def _start_server(self) -> None:
        """Start the connection pool server as a background process"""
        import subprocess
        logger.info("Starting connection pool server")
        subprocess.Popen([sys.executable, __file__, "start"], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        # Wait for server to start
        for _ in range(10):
            if is_server_running():
                logger.info("Connection pool server started")
                return
            time.sleep(0.5)
        logger.warning("Timed out waiting for connection pool server to start")
    
    def _touch_activity_file(self) -> None:
        """Update the last activity timestamp"""
        current_time = datetime.datetime.now().isoformat()
        try:
            with open(LAST_ACTIVITY_FILE, 'w') as f:
                f.write(current_time)
        except Exception as e:
            logger.error(f"Failed to update last activity timestamp: {str(e)}")
    
    def _send_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send command to the connection pool server"""
        if not os.path.exists(self.socket_path):
            raise ConnectionError(f"Connection pool server not running at {self.socket_path}")
        
        # Update last activity timestamp before sending command
        self._touch_activity_file()
        
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(self.socket_path)
            data = {
                "command": command,
                "params": params or {}
            }
            client.sendall(json.dumps(data).encode('utf-8'))
            response = client.recv(65536).decode('utf-8')
            return json.loads(response)
        finally:
            client.close()
    
    def ping(self) -> Dict[str, Any]:
        """Ping the MEXC API"""
        return self._send_command(CMD_PING)
    
    def new_order(self, symbol: str, side: str, order_type: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Place a new order"""
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "options": options or {}
        }
        response = self._send_command(CMD_NEW_ORDER, params)
        if "error" in response:
            raise Exception(response["error"])
        return response.get("result", {})
    
    def account_info(self) -> Dict[str, Any]:
        """Get account information"""
        response = self._send_command(CMD_ACCOUNT_INFO)
        if "error" in response:
            raise Exception(response["error"])
        return response.get("result", {})
    
    def exchange_info(self) -> Dict[str, Any]:
        """Get exchange information"""
        response = self._send_command(CMD_EXCHANGE_INFO)
        if "error" in response:
            raise Exception(response["error"])
        return response.get("result", {})
    
    def ticker_price(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get ticker price"""
        params = {"symbol": symbol} if symbol else {}
        response = self._send_command(CMD_TICKER_PRICE, params)
        if "error" in response:
            raise Exception(response["error"])
        return response.get("result", {})
    
    def time(self) -> Dict[str, Any]:
        """Get server time"""
        response = self._send_command(CMD_TIME)
        if "error" in response:
            raise Exception(response["error"])
        return response.get("result", {})
    
    def shutdown(self) -> None:
        """Shutdown the connection pool server"""
        try:
            self._send_command(CMD_SHUTDOWN)
        except:
            pass  # Ignore errors during shutdown

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            start_server()
        elif sys.argv[1] == "status":
            if is_server_running():
                # Check idle time
                try:
                    with open(LAST_ACTIVITY_FILE, 'r') as f:
                        last_activity_str = f.read().strip()
                    last_activity = datetime.datetime.fromisoformat(last_activity_str)
                    now = datetime.datetime.now()
                    idle_seconds = (now - last_activity).total_seconds()
                    idle_minutes = int(idle_seconds / 60)
                    timeout_minutes = IDLE_TIMEOUT // 60
                    print(f"Connection pool server is running")
                    print(f"Idle for: {idle_minutes} minutes")
                    print(f"Timeout after: {timeout_minutes} minutes")
                    print(f"Time remaining: {timeout_minutes - idle_minutes} minutes")
                except Exception as e:
                    print(f"Connection pool server is running but could not read idle time: {str(e)}")
            else:
                print("Connection pool server is not running")
        elif sys.argv[1] == "stop":
            if is_server_running():
                try:
                    with open(PID_FILE, 'r') as f:
                        pid = int(f.read().strip())
                    os.kill(pid, signal.SIGTERM)
                    print("Sent shutdown signal to connection pool server")
                except Exception as e:
                    print(f"Failed to stop connection pool server: {str(e)}")
                    cleanup_server_files()
            else:
                print("Connection pool server is not running")
        else:
            print("Usage: python connection_pool.py [start|status|stop]")
    else:
        print("Usage: python connection_pool.py [start|status|stop]")

if __name__ == "__main__":
    main()
