# MACVLAN.md

Create a macvlan network and bridge

> [!Note]
> May require a shim 
> [vegcom/cozy-salt://srv/salt/_templates/macvlan-shim.jinja](https://raw.githubusercontent.com/vegcom/cozy-salt/develop/srv/salt/_templates/macvlan-shim.jinja)

```bash
# 10.0.0.0/16 is a standin
# Dictates ingress, make sure every host that needs on is includd in your subnet
docker network create -d macvlan \
  --subnet=10.0.0.0/16 \
  --gateway=10.0.0.1 \
  -o parent=eth0 \
  frontend
```
