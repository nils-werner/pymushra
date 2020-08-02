Deploying
---------

### User Setup

Create a `webmushra` service user

    useradd --system --shell /usr/bin/nologin webmushra

### Apache

Importing SciPy into a WSGI script has proven to be tricky, so you need to change the `WSGIScriptAlias` line a bit:

    WSGIDaemonProcess webmushra user=webmushra group=webmushra python-path=/path/to/venv/pymushra:/path/to/venv/lib/python2.7/site-packages
    WSGIScriptAlias /webmushra /path/to/venv/pymushra/wsgi.py process-group=webmushra application-group=%{GLOBAL}

    <Location /webmushra>
            WSGIProcessGroup webmushra
    </Location>

    <Directory /path/to/venv/pymushra>
            WSGIScriptReloading On
            <Files wsgi.py>
                    Allow from all
                    Require all granted
            </Files>
    </Directory>


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
    ExecStart=/bin/bash -c 'cd /path/to/venv/pymushra && source ../bin/activate && uwsgi --ini uwsgi.ini'
    User=webmushra
    Group=webmushra
    Restart=on-failure
    KillSignal=SIGQUIT
    Type=notify
    StandardError=syslog
    NotifyAccess=all

    [Install]
    WantedBy=multi-user.target

and start it using `systemctl start webmushra.service`.

Then create a `pymushra/uwsgi.ini` file

    [uwsgi]
    mount = /webmushra=wsgi:application
    logto = log/%n.log

    manage-script-name = true

    socket = /tmp/webmushra.sock
    chmod-socket = 666

    touch-reload = wsgi.py
