version: '3.7'

# DB config
x-dbconfig_env: &dbconfig_env
  DB_HOST: db
  DB_USER: &dbuser postgres
  DB_DATABASE: &dbname pvarki
  DB_PASSWORD: &dbpass {{.Env.DB_PASSWORD}} # pragma: allowlist secret
  DB_PORT: &dbport 5432


x-security_env: &security_env
  JWT_PRIVKEY_PATH: "0"
  JWT_PUBKEY_PATH: "/app/jwtRS256.pub"
  # Use these while we cannot use security principals to access the keyvauls
  PIPELINE_SSHKEY_OVERRIDE: "{{getenv "PIPELINE_SSHKEY_OVERRIDE" ""}}"
  PIPELINE_TOKEN_OVERRIDE: "{{getenv "PIPELINE_TOKEN_OVERRIDE" ""}}"


services:
  db:
    image: postgres:15.1
    environment:
      POSTGRES_USER: *dbuser
      POSTGRES_DB: *dbname
      POSTGRES_PASSWORD: *dbpass # pragma: allowlist secret
      LC_COLLATE: "C.UTF-8"
    ports:
      - target: 5432
        published: *dbport
        protocol: tcp
        mode: host
    networks:
      - dbnet
    healthcheck:
      test: "pg_isready --dbname=$$POSTGRES_DB --username=$$POSTGRES_USER -q"
      interval: 5s
      timeout: 5s
      retries: 3
      start_period: 5s
    volumes:
      - 'db_data:/var/lib/postgresql/data'

  dbinit:
    image: pvarkiprojekti/pttbackend:migrations
    build:
      context: .
      dockerfile: Dockerfile
      target: migrations
    environment:
      <<: *dbconfig_env
    networks:
      - dbnet
    depends_on:
      db:
        condition: service_healthy

  api:
    image: pvarkiprojekti/pttbackend:latest
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    environment:
      <<: *dbconfig_env
      <<: *security_env
    volumes:
      - {{.Env.JWT_PUBKEY_PATH}}:/app/jwtRS256.pub
    depends_on:
      db:
        condition: service_healthy
      dbinit:
        condition: service_completed_successfully
    networks:
      - dbnet
    expose:
      - 8000
    ports:
      - "8000:8000"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.fastapi.rule=Host(`{{.Env.SERVER_ADDRESS}}`)"
      - "traefik.http.routers.fastapi.tls=true"
      - "traefik.http.routers.fastapi.tls.certresolver=letsencrypt"

  traefik:
    image: traefik:v2.2
    networks:
      - dbnet
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./traefik.toml:/etc/traefik/traefik.toml"
      - "le_data:/letsencrypt"

networks:
  dbnet:

volumes:
  le_data:
    driver: local
  db_data:
    driver: local
