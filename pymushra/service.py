from __future__ import division, absolute_import, print_function

import os
import json
import pickle
from flask import Flask, request, send_from_directory, send_file, \
    render_template, redirect, url_for, abort
from tinyrecord import transaction
from functools import wraps

from . import stats, casting, utils

from io import BytesIO
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

app = Flask(__name__)

def only_admin_allowlist(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if request.remote_addr in app.config['admin_allowlist']:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return wrapped


@app.route('/')
@app.route('/<path:url>')
def home(url='index.html'):
    return send_from_directory(app.config['webmushra_dir'], url)


@app.route('/service/write.php', methods=['POST'])
@app.route('/<testid>/collect', methods=['POST'])
@app.route('/collect', methods=['POST'])
def collect(testid=''):
    if request.headers['Content-Type'].startswith(
            'application/x-www-form-urlencoded'
    ):
        try:
            db = app.config['db']
            payload = json.loads(request.form['sessionJSON'])
            payload = casting.cast_recursively(payload)
            insert = casting.json_to_dict(payload)

            collection = db.table(payload['trials'][0]['testId'])
            with transaction(collection):
                inserted_ids = collection.insert_multiple(insert)
            print(inserted_ids)

            return {
                'error': False,
                'message': "Saved as ids %s" % ','.join(map(str, inserted_ids))
            }
        except Exception as e:
            return {
                'error': True,
                'message': "An error occurred: %s" % str(e)
            }
    else:
        return "415 Unsupported Media Type", 415


@app.route('/admin/')
@app.route('/admin/list')
@only_admin_allowlist
def admin_list():
    db = app.config['db']
    collection_names = db.tables()

    collection_dfs = [
        casting.collection_to_df(db.table(name)) for name in collection_names
    ]

    print(collection_dfs)

    collections = [
        {
            'id': name,
            'participants': len(df['questionaire', 'uuid'].unique()),
            'last_submission': df['wm', 'date'].max(),
        } for name, df in zip(collection_names, collection_dfs)
        if len(df) > 0
    ]

    configs = utils.get_configs(
        os.path.join(app.config['webmushra_dir'], "configs")
    )

    return render_template(
        "admin/list.html",
        collections=collections,
        configs=configs
    )


@app.route('/admin/delete/<testid>/')
@only_admin_allowlist
def admin_delete(testid):
    app.config['db'].drop_table(testid)
    return redirect(url_for('admin_list'))


@app.route('/admin/info/<testid>/')
@only_admin_allowlist
def admin_info(testid):
    collection = app.config['db'].table(testid)
    df = casting.collection_to_df(collection)
    try:
        configs = df['wm']['config'].unique().tolist()
    except KeyError:
        configs = []

    configs = map(os.path.basename, configs)

    return render_template(
        "admin/info.html",
        testId=testid,
        configs=configs
    )


@app.route('/admin/latest/<testid>/')
@only_admin_allowlist
def admin_latest(testid):
    collection = app.config['db'].table(testid)
    latest = sorted(collection.all(), key=lambda x: x['date'], reverse=True)[0]
    return latest


@app.route('/admin/stats/<testid>/<stats_type>')
@only_admin_allowlist
def admin_stats(testid, stats_type='mushra'):
    collection = app.config['db'].table(testid)
    df = casting.collection_to_df(collection)
    df.columns = utils.flatten_columns(df.columns)
    # analyse mushra experiment
    try:
        if stats_type == "mushra":
            return stats.render_mushra(testid, df)
    except ValueError as e:
        return render_template(
            'error/error.html', type="Value", message=str(e)
        )
    return render_template('error/404.html'), 404


@app.route(
    '/admin/download/<testid>.<filetype>',
    defaults={'show_as': 'download'})
@app.route(
    '/admin/download/<testid>/<statstype>.<filetype>',
    defaults={'show_as': 'download'})
@app.route(
    '/download/<testid>/<statstype>.<filetype>',
    defaults={'show_as': 'download'})
@app.route(
    '/download/<testid>.<filetype>',
    defaults={'show_as': 'download'})
@app.route(
    '/admin/show/<testid>.<filetype>',
    defaults={'show_as': 'text'})
@app.route(
    '/admin/show/<testid>/<statstype>.<filetype>',
    defaults={'show_as': 'text'})
@only_admin_allowlist
def download(testid, show_as, statstype=None, filetype='csv'):
    allowed_types = ('csv', 'pickle', 'json', 'html')

    if show_as == 'download':
        as_attachment = True
    else:
        as_attachment = False

    if filetype not in allowed_types:
        return render_template(
            'error/error.html',
            type="Value",
            message="File type must be in %s" % ','.join(allowed_types)
        )

    if filetype == "pickle" and not as_attachment:
        return render_template(
            'error/error.html',
            type="Value",
            message="Pickle data cannot be viewed"
        )

    collection = app.config['db'].table(testid)
    df = casting.collection_to_df(collection)

    if statstype is not None:
        # subset by statstype
        df = df[df[('wm', 'type')] == statstype]

    # Merge hierarchical columns
    if filetype not in ("pickle", "html"):
        df.columns = utils.flatten_columns(df.columns.values)

    if len(df) == 0:
        return render_template(
            'error/error.html',
            type="Value",
            message="Data Frame was empty"
        )

    if filetype == "csv":
        # We need to escape certain objects in the DF to prevent Segfaults
        mem = StringIO()
        casting.escape_objects(df).to_csv(
            mem,
            sep=";",
            index=False,
            encoding='utf-8'
        )

    elif filetype == "html":
        mem = StringIO()
        df.sort_index(axis=1).to_html(mem, classes="table table-striped")

    elif filetype == "pickle":
        mem = BytesIO()
        pickle.dump(df, mem)

    elif filetype == "json":
        mem = StringIO()
        # We need to escape certain objects in the DF to prevent Segfaults
        casting.escape_objects(df).to_json(mem, orient='records')

    mem.seek(0)

    if (as_attachment or filetype != "html") and not isinstance(mem, BytesIO):
        mem2 = BytesIO()
        mem2.write(mem.getvalue().encode('utf-8'))
        mem2.seek(0)
        mem = mem2

    if as_attachment:
        return send_file(
            mem,
            download_name="%s.%s" % (testid, filetype),
            as_attachment=True,
            max_age=-1
        )
    else:
        if filetype == "html":
            return render_template('admin/table.html', table=mem.getvalue())
        else:
            return send_file(
                mem,
                mimetype="text/plain",
                cache_timeout=-1
            )


@app.context_processor
def utility_processor():
    def significance_stars(p, alpha=0.05):
        return ''.join(
            [
                '<span class="glyphicon glyphicon-star small"'
                'aria-hidden="true"></span>'
            ] * stats.significance_class(p, alpha)
        )

    return dict(significance_stars=significance_stars)


@app.template_filter('datetime')
def datetime_filter(value, format='%x %X'):
    return value.strftime(format)
