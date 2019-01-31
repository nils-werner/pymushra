import pandas as pd
import uuid
import itertools
import datetime
from . import utils


def escape_objects(df, columns=None):
    df = df.copy()

    if columns is None:
        columns = [
            ('questionaire', 'uuid'),
            ('wm', 'id',),
        ]

    # Add flattened columns too, so we catch JSON and CSV column names
    columns = columns + utils.flatten_columns(columns)

    for col in columns:
        try:
            df[col] = df[col].astype(str)
        except KeyError:
            pass

    return df


def collection_to_df(collection):
    """ Transform TinyDB collection to DataFrame

    Parameters
    ----------
    collection : TinyDB collection
        The collection to transform. The entire collection is taken.

    Returns
    -------
    d : DataFrame
        The DataFrame

    Notes
    -----

    Turns dataset inside out:

    .. code-block:: yaml

        Trial: Something
        Questionaire:
          Name: Nils
        Responses:               # Notice the list here
          - Stimulus: C3
            Score: 100
          - Stimulus: C1
            Score: 80

    must become

    .. code-block:: yaml

        - Trial: Something       # Notice the list here
          Questionaire:
            Name: Nils
          Responses:
            Stimulus: C3
            Score: 100
        - Trial: Something
          Questionaire:
            Name: Nils
          Responses:
            Stimulus: C1
            Score: 80

    For each row in responses we need an aditional row in our DataFrame

    """
    rawdata = list(collection.all())

    if not rawdata:
        return pd.DataFrame()

    dataset = []

    for trial in rawdata:
        for response in trial['responses']:
            outitem = {}

            for key, item in response.items():
                outitem[('responses', key)] = item

            for key, item in trial['questionaire'].items():
                outitem[('questionaire', key)] = item

            for key, item in trial.items():
                if key not in ('responses', 'questionaire'):
                    outitem[('wm', key)] = item

            outitem[('wm', 'id')] = str(outitem[('wm', 'id')])
            dataset.append(outitem)

    columns = list(set(itertools.chain(*map(lambda x: x.keys(), dataset))))

    df = pd.DataFrame(
        dataset,
        columns=pd.MultiIndex.from_tuples(columns)
    )

    df[('wm', 'date')] = pd.to_datetime(df[('wm', 'date')])

    return df


def json_to_dict(payload):
    """ Transform webMUSHRA JSON dict to sane structure

    Parameters
    ----------
    payload : dict_like
        The container to be transformed

    Returns
    -------
    d : dict_like
        The transformed container

    Notes
    -----

    Actions taken:

    1. One dataset per trial is generated
    2. Config from global payload is inserted into all datasets
    3. TestId from global payload is inserted into all datasets
    4. date is added to all datasets
    5. Questionaire structure

        .. code-block:: python

            {'name': ['firstname', 'age'], 'response': ['Nils', 29]}

        becomes

        .. code-block:: python

            {'firstname': 'Nils', 'age': 29}

    6. UUID4 field is added to questionaire

    """
    questionaire = payload['participant']
    questionaire = dict(
        zip(questionaire['name'], questionaire['response'])
    )
    questionaire['uuid'] = str(uuid.uuid4())
    insert = []

    for trial in payload['trials']:
        data = trial

        data['config'] = payload['config']
        data['testId'] = payload['testId']
        data['date'] = str(datetime.datetime.now())
        data['questionaire'] = questionaire

        insert.append(data)

    return insert


def bool_or_fail(v):
    """ A special variant of :code:`bool` that raises :code:`ValueError`s
    if the provided value was not :code:`True` or :code:`False`.

    This prevents overeager casting like :code:`bool("bla") -> True`

    Parameters
    ----------
    v : mixed
        Value to be cast

    Returns
    -------
    b : boolean
        The result of the cast

    """
    try:
        if v.lower() == 'true':
            return True
        elif v.lower() == 'false':
            return True
    except Exception:
        pass
    raise ValueError()


def cast_recursively(d, castto=None):
    """ Traverse list or dict recursively, trying to cast their items.

    Parameters
    ----------
    d : iterable or dict_like
        The container to be casted
    castto : list of callables
        The types to cast to. Defaults to :code:`bool_or_fail, int, float`

    Returns
    -------
    d : iterable or dict_like
        The transformed container

    """
    if castto is None:
        castto = (bool_or_fail, int, float)

    if isinstance(d, dict):
        return {
            k: cast_recursively(v, castto=castto)
            for k, v in d.items()
        }
    elif isinstance(d, list):
        return [cast_recursively(v, castto=castto) for v in d]
    else:
        for tp in castto:
            try:
                return tp(d)
            except (ValueError, TypeError):
                pass
        return d
