import paramiko
import ftplib
import os
import queue
import concurrent.futures
from tqdm import tqdm
import fnmatch
from utils.logging_utils import logger
from sources.base_connector import BaseConnector


class SFTPConnector(BaseConnector):
    def __init__(self, host, port, username, password, remote_path, temp_dir, file_patterns, private_key=None, protocol="sftp"):
        """
        Initializes the SFTP/FTP Connector.

        Args:
        - host (str): SFTP/FTP server hostname.
        - port (int): SFTP/FTP server port.
        - username (str): Username for authentication.
        - password (str): Password for authentication (optional if using private key).
        - remote_path (str): Path on the remote server to fetch files from.
        - temp_dir (str): Local temporary directory for storing downloaded files.
        - file_patterns (list, optional): List of file patterns to match (e.g., `["*.csv", "*.json"]`).
        - private_key (str, optional): Path to the private key file for key-based authentication.
        - protocol (str): Either `"sftp"` or `"ftp"`.
        """
        super().__init__("SFTP" if protocol == "sftp" else "FTP")
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.remote_path = remote_path
        self.temp_dir = temp_dir
        self.file_patterns = file_patterns if file_patterns else ["*"]
        self.private_key_path = private_key
        self.protocol = protocol.lower()

        os.makedirs(self.temp_dir, exist_ok=True)

        # Connection pool
        self.max_connections = min(8, os.cpu_count()) 
        self.connection_pool = queue.Queue(self.max_connections)
        self._initialize_connection_pool()


    def test_connection(self):
        """Checks if the SFTP/FTP connection is valid."""
        if self.protocol == "sftp":
            return self._validate_sftp()
        elif self.protocol == "ftp":
            return self._validate_ftp()
        return False

    def _validate_sftp(self):
        """Validates SFTP connection."""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, port=self.port, username=self.username, password=self.password, pkey=self.private_key, timeout=5)
            sftp = ssh.open_sftp()
            sftp.listdir(self.remote_path)  # Check if we can access the directory
            sftp.close()
            ssh.close()
            logger.info(f"Successfully connected to SFTP `{self.host}`.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SFTP `{self.host}`: {e}")
            return False

    def _validate_ftp(self):
        """Validates FTP connection."""
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.host, self.port, timeout=5)
            ftp.login(self.username, self.password)
            ftp.cwd(self.remote_path)  # Check if we can access the directory
            ftp.quit()
            logger.info(f"Successfully connected to FTP `{self.host}`.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to FTP `{self.host}`: {e}")
            return False

    def _initialize_connection_pool(self):
        """Pre-creates SFTP/FTP connections and adds them to the connection pool."""
        for _ in range(self.max_connections):
            if self.protocol == "sftp":
                self.connection_pool.put(self._create_sftp_connection())
            elif self.protocol == "ftp":
                self.connection_pool.put(self._create_ftp_connection())

    def _create_sftp_connection(self):
        """Creates and returns an SFTP connection."""
        try:
            transport = paramiko.Transport((self.host, self.port))
            transport.connect(username=self.username, password=self.password)
            sftp_client = paramiko.SFTPClient.from_transport(transport)
            logger.info("SFTP connection created and added to the pool")
            return sftp_client
        except Exception as e:
            logger.error(f"SFTP connection failed: {e}")
            return None

    def _create_ftp_connection(self):
        """Creates and returns an FTP connection."""
        try:
            ftp_client = ftplib.FTP()
            ftp_client.connect(self.host, self.port)
            ftp_client.login(self.username, self.password)
            logger.info("FTP connection created and added to the pool")
            return ftp_client
        except Exception as e:
            logger.error(f"FTP connection failed: {e}")
            return None

    def list_files_sftp(self, sftp_client):
        """Lists files in the SFTP directory matching patterns."""
        try:
            files = sftp_client.listdir(self.remote_path)
            matched_files = [f for f in files if any(fnmatch.fnmatch(f, pattern) for pattern in self.file_patterns)]
            print(self.file_patterns, matched_files, files)
            return matched_files
        except Exception as e:
            logger.error(f"Error listing SFTP files: {e}")
            return []

    def list_files_ftp(self, ftp_client):
        """Lists files in the FTP directory matching patterns."""
        try:
            files = ftp_client.nlst(self.remote_path)
            matched_files = [f for f in files if any(fnmatch.fnmatch(f, pattern) for pattern in self.file_patterns)]
            return matched_files
        except Exception as e:
            logger.error(f"Error listing FTP files: {e}")
            return []

    def download_file_sftp(self, filename):
        """Downloads a single file from SFTP using a pooled connection."""
        sftp_client = self.connection_pool.get()  # Get a connection from the pool
        try:
            local_file = os.path.join(self.temp_dir, filename)
            remote_file = f"{self.remote_path}/{filename}"

            logger.info(f"Downloading `{filename}` from `{remote_file}` to `{local_file}`")
            sftp_client.get(remote_file, local_file)
            logger.info(f"Downloaded `{filename}` successfully!")

            return filename, local_file
        except Exception as e:
            logger.error(f"Failed to download `{filename}`: {e}")
            return filename, None
        finally:
            self.connection_pool.put(sftp_client)  # Return the connection to the pool

    def download_file_ftp(self, filename):
        """Downloads a single file from FTP using a pooled connection."""
        ftp_client = self.connection_pool.get()  # Get a connection from the pool
        try:
            local_file = os.path.join(self.temp_dir, filename)
            remote_file = f"{self.remote_path}/{filename}"

            with open(local_file, "wb") as f:
                logger.info(f"Downloading `{filename}` from `{remote_file}` to `{local_file}`")
                ftp_client.retrbinary(f"RETR {remote_file}", f.write)
                logger.info(f"Downloaded `{filename}` successfully!")

            return filename, local_file
        except Exception as e:
            logger.error(f"Failed to download `{filename}`: {e}")
            return filename, None
        finally:
            self.connection_pool.put(ftp_client)  # Return the connection to the pool

    def fetch_data(self):
        """Fetch all files using multithreading with connection pooling."""
        if self.protocol == "sftp":
            sftp_client = self.connection_pool.get()
            file_list = self.list_files_sftp(sftp_client)
            self.connection_pool.put(sftp_client)
            download_func = self.download_file_sftp
        elif self.protocol == "ftp":
            ftp_client = self.connection_pool.get()
            file_list = self.list_files_ftp(ftp_client)
            self.connection_pool.put(ftp_client)
            download_func = self.download_file_ftp
        else:
            raise ValueError("Invalid protocol. Choose 'sftp' or 'ftp'.")

        logger.info(f"Found {len(file_list)} files to download from `{self.remote_path}`.")

        downloaded_files = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_connections) as executor:
            future_to_file = {executor.submit(download_func, filename): filename for filename in file_list}

            with tqdm(total=len(file_list), desc="Downloading Files") as progress_bar:
                for future in concurrent.futures.as_completed(future_to_file):
                    filename = future_to_file[future]
                    try:
                        _, file_path = future.result()
                        if file_path:
                            downloaded_files[filename] = file_path
                    except Exception as e:
                        logger.error(f"Error processing `{filename}`: {e}")
                    progress_bar.update(1)

        logger.info("All files downloaded successfully!")
        return downloaded_files
