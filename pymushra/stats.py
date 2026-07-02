from io import BytesIO
from typing import Tuple
from uuid import UUID

import matplotlib as mpl
import pandas as pd
import scipy
import seaborn as sns
import statsmodels.stats.anova
import statsmodels.stats.diagnostic
import statsmodels.stats.multicomp
from flask import render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from statsmodels.formula.api import ols


def significance_class(p: float, alpha: float = 0.05) -> int:
    if p < 0.0001:
        return 4
    elif p < 0.001:
        return 3
    elif p < 0.01:
        return 2
    elif p < 0.05:
        return 1
    else:
        return 0


def significance_stars(p: float, alpha: float = 0.05, star: str = "*") -> str:
    return "".join([star] * significance_class(p, alpha))


def detect_outliers(df: pd.DataFrame, method: str | None = None) -> pd.DataFrame:
    if method is None:
        # add simple median based outlier detection here
        return df
    elif method == "mushra":
        # get 'bad' responses according to mushra rec
        bad_responses = df[
            (df.responses_stimulus == "reference") & (df.responses_score < 90)
        ]

        # select allowed number of bad trials
        allwd_bad_trials = len(df.wm_id.unique()) * 0.15

        # build condition
        condi = (
            bad_responses.groupby(["questionaire_uuid"]).count().wm_id
            > allwd_bad_trials
        )

        # return cleaned data
        return df[~df[("questionaire_uuid")].isin(condi.index)]
    else:
        return df


def mushra_preprocess(df: pd.DataFrame) -> Tuple[int, int, pd.DataFrame]:
    df = df[df["wm_type"] == "mushra"]

    # counting participants
    n_pre = df.drop_duplicates(("questionaire_uuid")).count()[("questionaire_uuid")]

    df = detect_outliers(df, method="mushra")

    # counting participants
    n_post = df.drop_duplicates(("questionaire_uuid")).count()[("questionaire_uuid")]

    # Filter Dataframe to only get the systems under test
    disallowed_conditions = ["reference", "anchor35", "anchor70"]
    # all conditions NOT in allowed conditions
    return n_pre, n_post, df[~df[("responses_stimulus")].isin(disallowed_conditions)]


def render_mushra(testid: UUID, df: pd.DataFrame) -> str:
    if len(df) == 0:
        raise ValueError("Dataset was empty")

    n_pre, n_post, df_dut = mushra_preprocess(df)

    # Kolmogorov Smirnov Test for normality
    ks_ps = {}
    for stimulus in df_dut[("responses_stimulus")].unique():
        ks, ks_p = statsmodels.stats.diagnostic.kstest_normal(
            df_dut[df_dut[("responses_stimulus")] == stimulus][("responses_score")]
        )
        ks_ps[stimulus] = ks_p

    # Levene test for equal variances.
    groups = []
    for stimulus in df_dut[("responses_stimulus")].unique():
        groups.append(
            df_dut[df_dut[("responses_stimulus")] == stimulus][
                ("responses_score")
            ].to_numpy()
        )
    W, lev_p = scipy.stats.levene(*tuple(groups))

    # ANOVA
    lm = ols("responses_score ~ responses_stimulus", df_dut).fit()
    aov_table = statsmodels.stats.anova.anova_lm(lm)

    pc_table = statsmodels.stats.multicomp.pairwise_tukeyhsd(
        df_dut[("responses_score")], df_dut[("responses_stimulus")]
    )

    # render boxplot to base64
    boxplot_uri = render_boxplot(testid=testid, df=df)
    return render_template(
        "stats/mushra.html",
        url=testid,
        n_pre=n_pre,
        n_post=n_post,
        alpha=0.05,
        ks=ks_ps,
        lev_p=lev_p,
        aov=aov_table,
        pair=pc_table,
        boxplot_uri=boxplot_uri,
    )


def render_boxplot(testid: UUID, df: pd.DataFrame) -> BytesIO:
    _, _, df = mushra_preprocess(df)

    fig = Figure(facecolor=(0, 0, 0, 0))
    ax = fig.add_subplot(111)

    sns.set_style("whitegrid")
    sns.set_style(
        "darkgrid",
        {
            "axes.facecolor": (1, 1, 1, 0),
            "figure.facecolor": (1, 1, 1, 0),
            "axes.edgecolor": ".8",
            "grid.color": ".8",
            "ytick.minor.size": 0,
            "ytick.color": "0",
        },
    )

    sns.boxplot(
        df,
        x="responses_stimulus",
        y="responses_score",
        ax=ax,
    )

    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(visible=True, which="minor", color="0.8", linewidth=0.5)
    ax.set_ylim((0, 101))

    sns.despine(left=True, ax=ax, trim=False)

    canvas = FigureCanvas(fig)

    png_output = BytesIO()
    canvas.print_png(png_output)
    png_output.seek(0)  # rewind the data

    return png_output
