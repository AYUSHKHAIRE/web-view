import subprocess
import os 
import shutil
import json
from browse.logger_config import logger
from accessweb.settings import BASE_DIR
DOCKER_IMAGE = "selenium_capture"

# control all sessions
class sessionManager():
    def __init__(
        self
    ):
        self.shared_memory_pool = {} 
        
    def setup_docker(
        self, 
        user_id,
        screendex
    ):
        path = os.path.join(
            BASE_DIR, 
            "browse",
            "docker_containers", 
            f'docker_{user_id}'
        )
        os.makedirs(
            path, 
            exist_ok=True
        )
        container_name = f'docker_con_{user_id}'
        # subprocess.run(["docker", "rm", "-f", container_name], check=False, text=True)
        cookie_file_path = os.path.join(
            path, 
            'cookie.json'
        )
        with open(
            cookie_file_path, 
            'r'
        ) as cookie_file:
            auth_token = json.load(
                cookie_file
            )
        auth_token = auth_token.get('cookie')
        try:
            result_check = subprocess.run(
                [
                    "docker", 
                    "container", 
                    "inspect", 
                    container_name
            ], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )

            if result_check.returncode == 0:  # Container exists
                logger.warning(f"[ SESSION ] Container '{container_name}' already exists.")
                try:
                    output_start = subprocess.run(
                        [
                            "docker", 
                            "start", 
                            container_name
                        ], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE , 
                            check=True, 
                            text=True
                    )
                    logger.warning(f"[ SESSION ] {output_start.stdout.strip()}",)
                except subprocess.CalledProcessError as e:
                    logger.error(f"[ SESSION ] Failed to start Docker container '{container_name}'.")
                    logger.error(f"[ SESSION ] Error output: {e.stderr}")

            else:  # Container does not exist, create it
                logger.debug(f"[ SESSION ] Starting a new container for user {user_id}...")
                result = subprocess.run( 
                        [
                            "docker", "run", "-d",
                            "--name", container_name,
                            "--network", "host",
                            "--ipc=host",
                            "-v", f"{path}:/session",
                            "-e", f"CONTAINER_USER_ID={user_id}" ,
                            "-e", f"CONTAINER_USER_AUTH_TOKEN={auth_token}" ,
                            "-e", f"SCREENDEX={screendex}" ,
                            DOCKER_IMAGE
                    ], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True, check=True
                    )
                output = result.stdout.strip()
                dictionary = {
                    "user": user_id,
                    "container_id" : output
                }
                with open(
                    f"{path}/config.json", 
                    "w"
                ) as outfile:
                    json.dump(
                        dictionary, 
                        outfile
                    )
                    logger.debug(f"[ SESSION ] Container started successfully: {output}")

        except subprocess.CalledProcessError as e:
            logger.error(f"[ SESSION ] Failed to check or start Docker container '{container_name}'.")
            logger.error(f"[ SESSION ] Command: {e.cmd}")
            logger.error(f"[ SESSION ] Return code: {e.returncode}")
            logger.error(f"[ SESSION ] Error output: {e.stderr}")

    def terminate(
        self,
        user_id,
        all = None
    ):
        if all:
            for item in self.shared_memory_pool.items():
                item.close()
                item.unlink()
        self.shared_memory_pool[f'sms_{user_id}'].close()
        self.shared_memory_pool[f'sms_{user_id}'].unlink()