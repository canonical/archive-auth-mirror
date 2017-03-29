# Overview

This charm deploys an application to mirror and periodically sync an Ubuntu
archive and expose it through static file serve via Nginx.


## Managing basic authentication

Credentials for basic authentication can be created with:

```bash
$ juju run --application archive-auth-mirror '/srv/archive-auth-mirror/bin/manage-user add <user> <pass>'
```

If the user is already present, its password will be updated.

To remove a user, run

```bash
$ juju run --application archive-auth-mirror '/srv/archive-auth-mirror/bin/manage-user remove <user>'
```
