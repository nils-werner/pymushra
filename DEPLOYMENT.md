Deploying
---------

### User Setup

Create a `webmushra` service user

    useradd --system --shell /usr/bin/nologin webmushra

### Apache

Importing SciPy into a WSGI script has proven to be tricky, so you need to change the `WSGIScriptAlias` line a bit:

    WSGIDaemonProcess webmushra user=webmushra group=webmushra python-path=/path/to/venv/pymushra/pymushra:/path/to/venv/env/lib/python3.6/site-packages home=/path/to/venv

    Alias /webmushra/admin /path/to/venv/pymushra/pymushra/wsgi.py/admin
    Alias /webmushra/collect /path/to/venv/pymushra/pymushra/wsgi.py/collect
    Alias /webmushra/download /path/to/venv/pymushra/pymushra/wsgi.py/download
    Alias /webmushra /path/to/venv/webmushra

    <Directory /path/to/venv/pymushra/pymushra>
            WSGIProcessGroup webmushra
            WSGIApplicationGroup %{GLOBAL}
            Require all granted
            WSGIScriptReloading On

            Options ExecCGI
            AddHandler wsgi-script .py
    </Directory>

    <Directory /path/to/venv/webmushra>
            Require all granted
    </Directory>

#### Debugging

See

    tail -f /var/log/apache2/errors.log

### Nginx

Install uWSGI

    pip install uwsgi

Create a hosts file `/etc/nginx/sites-enabled/webmushra`

    server {
      listen 80;
      server_name ext1.myserver.de;

      location = /webmushra {
        rewrite ^(.*[^/])$ $1/ permanent;
      }

      location /webmushra {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/webmushra.sock;
      }

      location /webmushra/admin {
        allow 131.188.0.0/16;
        deny all;
      }

    }

link it to `/etc/nginx/sites-available` and restart Nginx `systemctl restart nginx`.

Create a Systemd service file `/etc/systemd/system/webmushra.service`

    [Unit]
    Description=uWSGI instance to serve pyMUSHRA

    [Service]
    ExecStart=/path/to/venv/bin/uwsgi --ini /path/to/venv/uwsgi.ini'
    User=webmushra
    Group=webmushra
    Restart=on-failure
    KillSignal=SIGQUIT
    Type=notify
    StandardError=syslog
    NotifyAccess=all

    [Install]
    WantedBy=multi-user.target

Then create a `uwsgi.ini` file

    [uwsgi]
    mount = /webmushra=wsgi:application
    logto = log/%n.log
    virtualenv = /path/to/venv

    manage-script-name = true

    socket = /tmp/webmushra.sock
    chmod-socket = 666

    touch-reload = wsgi.py

and start the service using `systemctl start webmushra.service`.

#### Debugging

See

    tail -f /path/to/venv/log/webmushra.log
