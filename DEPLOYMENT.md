# Coolify deployment

The `backend` application in the Ape-Ame project's production environment builds this Dockerfile from `main`. Waitress listens on port 8080. The frontend proxies `/api/` to this application over the private Docker network.

Configure runtime variables in Coolify:

- `REDIS_HOST`: the database resource's internal Docker hostname.
- `REDIS_PORT`: defaults to `6379`.
- `REDIS_PASSWORD`: the database password, stored in Coolify.

Enable the Coolify HTTP health check at `/healthz`. The image includes curl for Coolify's generated health check. A successful response also verifies database connectivity.

The database uses a persistent volume. Existing leaderboard data was migrated from ultra-pi and verified before cutover. Keep database backups when moving or recreating the resource.

After pushing changes, deploy this application in Coolify.
