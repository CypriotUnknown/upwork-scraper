import time
import docker
from models import ContainerStatus


class DockerManager:

    def __init__(self) -> None:
        self.pw_server_already_started = False
        self.pw_server_name = "playwright-server"

    def stop_playwright_browser(self):
        if self.pw_server_already_started == False:
            client = docker.from_env()
            container = client.containers.get(self.pw_server_name)

            if container.status not in [
                ContainerStatus.exited.value,
                ContainerStatus.dead.value,
                ContainerStatus.removing.value,
            ]:
                container.stop()

    def start_playwright_browser(self):
        client = docker.from_env()
        container = client.containers.get(self.pw_server_name)
        if container.status != ContainerStatus.running.value:
            container.start()

            timeout = 60

            while True:
                if timeout == 0:
                    raise "PLAYWRIGHT SERVER IS NOT HEALTHY AFTER 60S"

                container.reload()
                if container.health == "healthy":
                    break
                time.sleep(1)
                timeout -= 1
        else:
            self.pw_server_already_started = True
