# Fly.io Deployment Notes
#TODO - this may need updating after installing pgvector

To start and deploy the app - create a new app name in `fly.toml`, then run `fly deploy`.

Chainlit serves the app by default on `0.0.0.0:8080`. For assurance, set these in your `Dockerfile` -
```docker
ENV CHAINLIT_HOST=0.0.0.0 
ENV CHAINLIT_PORT=8080
```
And env is set in your `fly.toml`-
```toml
[env]
  PORT = "8080"
  HOST = "0.0.0.0"
```

## Postgres

See - https://fly.io/docs/postgres/getting-started/create-pg-cluster/

- Run `fly postgres create`.
This will then give you a connection string for the database. In my experince, this isn't exactly what you want. Still, save it in a safe place. You'll need the password.


- Then, attach the postgres machine to the app machine - `fly postgres attach {POSTGRES APP NAME} --app {CHAINLIT APP NAME}`. It will set a `DATABASE_URL` env variable, but it's not quite right. We will override below. 

- In a seperate terminal, run `fly proxy 15433:5432 -a {POSTGRES APP NAME}`. Now you can connect a db client via port `15433` as well as run migrations from the [Chainlit Offical Datalayer](https://github.com/Chainlit/chainlit-datalayer) repo via `npx prisma migrate deploy`

## Secrets

Then set your secret environment variables -
- ```bash 
    fly secrets set OPENAI_API_KEY=sk-proj-
    ```
- ```bash 
    fly secrets set CHAINLIT_AUTH_SECRET=keepitsecretkeepitsafe
    ```
- ```bash 
    fly secrets set OPENAI_MODEL=gpt-4o-2024-11-20
    ```
- ```bash
    fly secrets set DATABASE_URL='postgres://postgres:{PASSWORD}@{POSTGRES APP NAME}.flycast:5432/postgres?sslmode=disable'
    ```
- ```bash 
    fly secrets set DEPLOYMENT=web
    ```

Now the app should be good to go with a working datalayer! 


## Helpful Fly Commands

Watch Logs -
`fly logs -a {CHAINLIT APP NAME}`

SSH -
`fly ssh console`



