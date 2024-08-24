from enum import Enum


class ContainerStatus(Enum):
    created = "created"
    restarting = "restarting"
    running = "running"
    removing = "removing"
    paused = "paused"
    exited = "exited"
    dead = "dead"
