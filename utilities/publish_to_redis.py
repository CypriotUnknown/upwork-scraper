import redis
import json
from .get_configuration import get_configuration_file


def redis_client():
    config_file = get_configuration_file()

    redis_host: str | None = config_file.get("redis").get("host")
    redis_port: str | None = config_file.get("redis").get("port")
    channel_pattern: str | None = config_file.get("redis").get("channel_pattern")

    if (
        redis_host is not None
        and redis_port is not None
        and channel_pattern is not None
    ):
        channel_pattern = (
            channel_pattern
            if channel_pattern[-1] != "."
            else channel_pattern.removesuffix(".")
        )

        return (
            redis.Redis(
                redis_host,
                port=redis_port,
                decode_responses=True,
                username=config_file.get("redis").get("username"),
                password=config_file.get("redis").get("password"),
            ),
            channel_pattern,
        )


def publish_to_redis(jobs: list[dict]):
    (rc, channel_pattern) = redis_client()

    if rc is not None:
        channel_name = ".".join([channel_pattern, "upwork", "work", "jobs"])

        dict_to_send = {
            "jobs": jobs,
            "notificationFlag": "lastJobTitle",
        }

        jobs_json = json.dumps(dict_to_send, indent=4)

        rc.publish(channel_name, jobs_json)
