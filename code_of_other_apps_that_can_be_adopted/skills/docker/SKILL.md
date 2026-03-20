---
name: docker
description: Manage Docker containers, images, volumes, and docker-compose stacks via the docker CLI.
always: false
script: docker
metadata: {"clawlite":{"emoji":"🐳","requires":{"bins":["docker"]}}}
---

# Docker

Use this skill when the user wants to manage containers, images, or compose stacks.

## Containers

```bash
docker ps                              # list running containers
docker ps -a                           # list all containers
docker start <name|id>
docker stop <name|id>
docker restart <name|id>
docker rm <name|id>
docker logs <name|id> --tail 100 -f
docker exec -it <name|id> bash
docker inspect <name|id>
docker stats --no-stream
```

## Images

```bash
docker images
docker pull image:tag
docker build -t name:tag .
docker rmi image:tag
docker image prune -f
```

## Docker Compose

```bash
docker compose up -d
docker compose down
docker compose ps
docker compose logs -f service
docker compose restart service
docker compose pull
docker compose exec service bash
```

## Volumes & Networks

```bash
docker volume ls
docker volume inspect vol_name
docker network ls
docker network inspect net_name
```

## Cleanup

```bash
docker system prune -f             # remove stopped containers, dangling images
docker system prune -af            # also remove unused images (destructive)
docker volume prune -f
```

## Safety notes

- Always confirm before `docker system prune -af` or removing named volumes.
- Prefer `docker compose down` over `docker rm -f` for compose stacks.
- Check container logs before forceful removal to capture error context.
