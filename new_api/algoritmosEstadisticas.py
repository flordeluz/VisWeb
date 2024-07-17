# Warnings handlers
import warnings
from statsmodels.tools.sm_exceptions import InterpolationWarning
warnings.simplefilter("ignore", InterpolationWarning)

# Essential libraries
import io
import base64
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns


def describe_data(ds):
    descriptivestats = ds.describe(include = "all")
    return descriptivestats.T.to_html(classes="table table-stripped")


def null_values_data(ds):
    gt20 = []
    gt50 = []
    reshtml = ""
    have_nulls = False
    for lookfornulls in ds.isnull().sum().to_list():
        if (lookfornulls > 0):
            have_nulls = True
            break
        #
    if (have_nulls):
        nullspercentage = (ds.isnull().sum() / ds.shape[0])*100
        reshtml += '<p style="text-align:center"><h5><b>Dataset has null values</b></h5></p>'
        for gtix in nullspercentage.keys():
            if (nullspercentage[gtix] >= 50):
                gt50.append(gtix)
            else:
                if (nullspercentage[gtix] > 20):
                    gt20.append(gtix)
                    #
        reshtml += "<p><u><b>Features with high percentage of null values</b></u><br>"
        reshtml += str(gt50) + " more than ~50% null values<br>"
        reshtml += str(gt20) + " between ~20% and ~50% null values</p>"
        reshtml += "<p><u><b>Percentage of features with null values</b></u><br>"
        reshtml += nullspercentage.to_frame("Nulls(%)").to_html(classes="table table-stripped")
        reshtml += "</p>"
        #
    else:
        reshtml += '<p style="text-align:center"><h5><b>Dataset has not null values</b></h5></p>'
        #
    return reshtml


def addinfo_data(ds, cols_list, catg_list):
    reshtml = ""
    if (ds.duplicated().sum() > 0):
        reshtml += '<p style="text-align:center"><h5><b>Dataset has duplicate records</b></h5></p>'
    else:
        reshtml += '<p style="text-align:center"><h5><b>Dataset has not duplicate records</b></h5></p>'
        #
    descriptivestats = ds.describe(include = "all")
    reshtml += '<p style="text-align:center"><h5><b>Detecting outliers with IQR</b></h5></p>'
    reshtml += "<p>"
    for nfld in cols_list:
        IQR = descriptivestats[nfld]["75%"] - descriptivestats[nfld]["25%"]
        UPF = descriptivestats[nfld]["75%"] + (1.5 * IQR)
        LOF = descriptivestats[nfld]["25%"] - (1.5 * IQR)
        if (descriptivestats[nfld]["mean"] > descriptivestats[nfld]["50%"]):
            reshtml += "<b>" + str(nfld) + " is right skewed" + (", high values outliers" if(UPF < descriptivestats[nfld]["max"]) else "") + (", low values outliers" if(LOF > descriptivestats[nfld]["min"]) else "") + "</b><br>"
        else:
            reshtml += "<b>" + str(nfld) + " is left skewed" + (", high values outliers" if(UPF < descriptivestats[nfld]["max"]) else "") + (", low values outliers" if(LOF > descriptivestats[nfld]["min"]) else "") + "</b><br>"
            #
    reshtml += "</p>"
    for cfld in catg_list:
        reshtml += "<p><b>" + cfld + " has " + str(descriptivestats[cfld]["unique"]) + " categories, \"" + descriptivestats[cfld]["top"] + "\" is the top one with " + str(descriptivestats[cfld]["freq"]) + "marks</b></p>"
        #
    return reshtml


def heatmap(data, row_labels, col_labels, ax=None, cbar_kw=None, cbarlabel="", **kwargs):
    if ax is None: ax = plt.gca()
    if cbar_kw is None: cbar_kw = {}
    im = ax.imshow(data, **kwargs)
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
    ax.set_xticks(np.arange(data.shape[1]), labels=col_labels)
    ax.set_yticks(np.arange(data.shape[0]), labels=row_labels)
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.spines[:].set_visible(False)
    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=0)
    ax.tick_params(which="minor", bottom=False, left=False)
    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}", textcolors=("black", "white"), threshold=None, **textkw):
    if not isinstance(data, (list, np.ndarray)): data = im.get_array()
    if threshold is not None: threshold = im.norm(threshold)
    else: threshold = im.norm(data.max())/2.
    kw = dict(horizontalalignment="center", verticalalignment="center")
    kw.update(textkw)
    if isinstance(valfmt, str): valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)
    return texts


def corrmat_data(ds, cols_list):
    reshtml = '<p style="text-align:center"><h5><b>Correlation Matrix</b></h5></p>'
    fig, ax = plt.subplots(figsize = (12, 6), dpi = 100)
    im, cbar = heatmap(ds[cols_list].corr(), cols_list, cols_list, ax=ax, cmap = "Spectral", vmin=-1, vmax=1, cbarlabel="Coef. corr.")
    texts = annotate_heatmap(im, threshold=0.99, textcolors=("black", "white"))
    fig.tight_layout()
    s = io.BytesIO()
    plt.savefig(s, format="png", bbox_inches="tight")
    plt.close()
    s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
    reshtml += '<img src="data:image/png;base64,%s">' % s
    return reshtml


def bivaran_data(ds, cols_list):
    reshtml = '<p style="text-align:center"><h5><b>Bivariate Analysis</b></h5></p>'
    plt.figure(figsize = (12, 6), dpi = 100)
    sns_plot = sns.pairplot(data=ds[cols_list])
    s = io.BytesIO()
    sns_plot.figure.savefig(s, format="png", bbox_inches="tight")
    s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
    reshtml += '<img src="data:image/png;base64,%s">' % s
    return reshtml


def boxhisf(data, feature, figsize = (10, 5), kde = True, dpi = 100):
    fig, (ax_box, ax_his) = plt.subplots(nrows = 2, sharex = True, gridspec_kw = {"height_ratios": (1/4, 3/4)}, figsize = figsize, dpi = dpi)
    sns.boxplot(data = data, x = feature, ax = ax_box, showmeans = True, color = "violet")
    ax_box.set(xlabel=None)
    ax_box.set_title("Feature " + str(feature))
    sns.histplot(data = data, x = feature, kde = kde, ax = ax_his)
    ax_his.axvline(data[feature].mean(), color = "green", linestyle = "--")
    ax_his.axvline(data[feature].median(), color = "black", linestyle = "-")
    ax_his.set(xlabel=None)
    return fig, ax_box, ax_his


def boxplot_data(ds, cols_list):
    reshtml = '<p style="text-align:center"><h5><b>Outliers and Distribution</b></h5></p>'
    for coln in cols_list:
        s = io.BytesIO()
        box_plot = boxhisf(ds, coln, figsize = (12, 6), dpi = 100)
        plt.savefig(s, format="png", bbox_inches="tight")
        plt.close()
        s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
        reshtml += '<img src="data:image/png;base64,%s"><br>' % s
        #
    return reshtml

