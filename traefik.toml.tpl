[entryPoints]
  [entryPoints.web]
    address = ":80"
  [entryPoints.web.http]
    [entryPoints.web.http.redirections]
      [entryPoints.web.http.redirections.entryPoint]
        to = "websecure"
        scheme = "https"

  [entryPoints.websecure]
    address = ":443"
    [entryPoints.websecure.forwardedHeaders]
      insecure="true"

[accessLog]

[providers]
  [providers.docker]
    exposedByDefault = false

[certificatesResolvers.letsencrypt.acme]
  email = "{{.Env.CERTBOT_EMAIL}}"
  storage= "/etc/traefik/acme/acme.json"
  [certificatesResolvers.letsencrypt.acme.httpChallenge]
    entryPoint = "web"
