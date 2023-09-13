# AI-SPRINT-SGDE

## Installation with docker-compose

```bash
docker-compose build
docker-compose up -d
```

## Environment variables

| Name             | Description                          | Default value                    |
|------------------|--------------------------------------|----------------------------------|
| `JWT_SECRET`     | Secret used to sign JWT tokens       | `dev`                            |
| `INSTANCE_PATH`  | Path to the database instance folder | `/instance  `                    |
| `DATABASE_URL`   | Database URL                         | `sqlite:////instance/sgde_db.db` |
| `GENERATOR_PATH` | Path to the generator folder         | `/instance/generators`           |
| `PORT`           | Port to run the server on            | `8000`                           |
