import docker
import os

client = docker.from_env()

def get_env(container):
    env = {}

    for item in container.attrs["Config"]["Env"]:
        key, value = item.split("=", 1)
        env[key] = value

    return env


def list_containers():
    for container in client.containers.list():

        if container.labels.get("backup.enabled") != "true":
            continue

        env = get_env(container)

        db = env["POSTGRES_DB"]
        user = env["POSTGRES_USER"]
        password = env["POSTGRES_PASSWORD"]

        print(f"Backup de {container.name} ({db})")

        result = container.exec_run(
            cmd=f"sh -c 'PGPASSWORD={password} pg_dump -U {user} -Fc {db}'",
            stdout=True,
            stderr=True,
        )

        if result.exit_code != 0:
            print(result.output.decode())
            continue

        with open(f"temp/{container.name}.dump", "wb") as f:
            f.write(result.output)

        print("Backup concluído.")