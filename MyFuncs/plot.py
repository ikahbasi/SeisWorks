# create: 1402-05-07
# -----------------------------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pandas as pd
from scipy import interpolate
from obspy.imaging.cm import pqlx

def _finalise_figure(fig, **kwargs):  # pragma: no cover
    '''
    Create: 1402-05-08
    '''
    #
    title = kwargs.get("title")
    show = kwargs.get("show", True)
    save = kwargs.get("save", False)
    savefile = kwargs.get("savefile", "EQcorrscan_figure.png")
    return_fig = kwargs.get("return_figure", False)
    size = kwargs.get("size", (10.5, 7.5))
    fig.set_size_inches(size)
    if title:
        fig.suptitle(title)
    if save:
        fig.savefig(savefile, bbox_inches="tight")
        print("Saved figure to {0}".format(savefile))
    if show:
        plt.show(block=True)
    if return_fig:
        return fig
    #fig.clf()
    # plt.close(fig)
    # return None

def fill_nan(input_array):
    '''
    interpolate to fill nan values
    '''
    indexs = np.arange(input_array.shape[0])
    good = np.where(np.isfinite(input_array))
    f = interpolate.interp1d(
            indexs[good], input_array[good], bounds_error=False)
    output_array = np.where(np.isfinite(input_array), input_array, f(indexs))
    return output_array

def rolling_mode(x, y, window, step):
    '''
    Create: 1402-05-07
    '''
    lst_mean = []
    lst_mode = []
    lst_time = []
    #
    end = x.max() + window
    t = x.min()
    while (t+window) < end:
        # print(f'{t=}')
        msk = np.logical_and(t<=x, x<=(t+window))
        y_msk = y[msk]
        mean = y_msk.mean()
        mode = np.nan
        if np.any(y_msk):
            try:
                bins = np.linspace(np.floor(y_msk.min()),
                                   np.ceil(y_msk.max()),
                                   20)
                abandence, values = np.histogram(y_msk, bins=bins)
                argmax = abandence.argmax()
                mode = values[argmax] + (values[1]-values[0])/2
            except:
                mode = np.nan
        lst_mean.append(mean)
        lst_mode.append(mode)
        lst_time.append(t)
        t += step
    arr_mean = fill_nan(np.array(lst_mean))
    arr_mode = fill_nan(np.array(lst_mode))
    return lst_time, arr_mean, arr_mode

import prettytable

props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

def Table(arr, ax):
    '''
    updated: 1402-10-10
    '''
    table = {'Count': [arr.size],
             #'STD':   [arr.std()],
             'VAR':   [arr.var()],
             'Mean':  [arr.mean()]}
    table = pd.DataFrame(table)
    table = table.round(2)
    table['Count'] = table['Count'].astype(int).astype(str)
    ###
    # bbox=[xmin, ymin, width, height]
    ax.table(cellText=table.values,
             colLabels=table.columns,
             loc='bottom', bbox=[0.1, 1-0.2, 1-0.1, 0.2],
             cellLoc='center',
             rowLoc='center')
    '''
    ax.table(cellText=data_table,
             rowLabels=rows_table,
             loc='upper right',
             colWidths=[1/3],
             cellLoc='center')
    '''


def ResidualHistogramVertical(arr, ax, ylim=[-5, 5], ystep=0.5):
    bins = np.arange(ylim[0]+ystep/2, ylim[1], ystep)
    bins[0] = ylim[0]
    bins[-1] = ylim[1]
    ax.hist(arr, bins=bins,
             alpha=1, edgecolor='k', facecolor='g',
             orientation='horizontal', log=False)

def ResidualDensity(x, y, ystep, zreplace=0.9):
    bins_y = np.arange(y.min()-ystep/2, y.max()+ystep*2, ystep)
    bins_x = int(50*1.5)
    hight, xedges, yedges = np.histogram2d(x, y,
                                           bins=(bins_x, bins_y),
                                           density=False)
    xcenters = (xedges[:-1] + xedges[1:]) / 2
    ycenters = (yedges[:-1] + yedges[1:]) / 2
    z = hight.T
    z[z==0] = zreplace
    return xcenters, ycenters, z

def PickerLabel(label, ax):
    ax.text(0.02, 0.97,
            label, transform=ax.transAxes,
            fontsize=12, bbox=props,
            ha="left", va="top", weight='bold')

def ResidualDistanceDensity(xcenters, ycenters, z,
                            vmin, vmax,
                            label=None,
                            fig=None, ax=None,
                            ystep=0.5, norm='log', show_cmap=False, **kwargs):
    '''
    Create: 1402-10-11
    '''
    im = ax.pcolormesh(xcenters, ycenters, z,
                       cmap=pqlx, vmin=vmin, vmax=vmax,
                       shading='gouraud', norm=norm)
    if show_cmap:
        cbaxes = inset_axes(ax, width="20%", height="2%", loc=1,
                            bbox_to_anchor=(-0.02, 0., 1, 1),
                            bbox_transform=ax.transAxes,) 
        cbar = fig.colorbar(im, cax=cbaxes, orientation='horizontal')
        cbaxes.xaxis.set_ticks_position("bottom")
        cbar.ax.set_xlabel('Counts')
    #
    ax.set_xlabel('Distance [km]')
    ax.set_ylabel('$T_{Picker}$ - $T_{Manual}$')
    ax.grid()
    _finalise_figure(fig, **kwargs)
    return im


def ResidualDistance(x, y, w=None, spectrom_mode=True,
                     label=None, fig=None, ax=None,
                     ylim=[-10, 10], ystep=0.5, norm=None, **kwargs):
    '''
    Create: 1402-05-07
    updated: 1402-05-08
    updated: 1402-05-09
    updated: 1402-06-30
    updated: 1402-07-01
    updated: 1402-07-02
    updated: 1402-10-10
    '''
    ax.text(0.02, 0.97,
            label, transform=ax.transAxes,
            fontsize=12, bbox=props,
            ha="left", va="top", weight='bold')
    if not spectrom_mode:
        cmap = plt.get_cmap('jet_r')
        edge_colors = cmap(w)
        #
        ax.scatter(x, y, facecolor="None", edgecolor=edge_colors, lw=1, alpha=1, s=50)
        #
        lst_time, lst_mean, lst_mode = rolling_mode(x, y, window=40, step=20)
        ax.plot(lst_time, lst_mode, '-', color='k', lw=3)
        ax.plot(lst_time, lst_mode, '-', color='r', lw=2, label='Mode')
        
        ax.plot(lst_time, lst_mean, '-', color='k', lw=3)
        ax.plot(lst_time, lst_mean, '-', color='g', lw=2, label='Mean')
        ax.legend(loc=4)
        # Create a ScalarMappable object for the colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap)
        # Set the color bar using the ScalarMappable object
        cbaxes = inset_axes(ax, width="30%", height="3%", loc=1) 
        cbar = plt.colorbar(sm, cax=cbaxes, ticks=[0, 1], orientation='horizontal')
        cbar.set_label('Probability', labelpad=-10)
    else:
        ystep2 = ystep / 2
        bins_y = np.arange(ylim[0]-ystep2/2, ylim[1]+ystep2, ystep2)
        bins_x = int(50*1.5)
        #bins_y = int(30*1.5)
        hight, xedges, yedges = np.histogram2d(x, y,
                                               bins=(bins_x, bins_y),
                                               density=False)#,
        #                                       range=([0, 1800],
        #                                              [ylim[0]-ystep, ylim[1]+ystep]))
        xcenters = (xedges[:-1] + xedges[1:]) / 2
        ycenters = (yedges[:-1] + yedges[1:]) / 2
        z = hight.T
        z[z==0] = 0.9
        im = ax.pcolormesh(xcenters, ycenters, z, cmap=pqlx, shading='gouraud', norm=norm)
        
        cbaxes = inset_axes(ax, width="20%", height="2%", loc=1) 
        cbar = fig.colorbar(im, cax=cbaxes, orientation='horizontal')
        cbaxes.xaxis.set_ticks_position("bottom")
        cbar.ax.set_xlabel('Counts')
    #
    ax.set_xlabel('Distance [km]')
    ax.set_ylabel('$T_{Picker}$ - $T_{Manual}$')
    ax.grid()
    # fig.suptitle(title, fontsize=16)
    _finalise_figure(fig, **kwargs)

def plot_residual_traveltime_3(xp, yp, xs, ys, wp=None, ws=None, title=None):
    '''
    Create: 1402-05-07
    '''
    fig, axs = plt.subplots(2, 2,
                            figsize=(12, 6), sharey='row', sharex='col',
                            gridspec_kw={'width_ratios': [5, 1],
                                         'height_ratios':[4, 4]})
    axs = axs.flatten()
    
    ResidualDistance(xp, yp, w=wp, title=None, fig=fig, axs=(axs[0], axs[1]))
    ResidualDistance(xs, ys, w=ws, title=None, fig=fig, axs=(axs[2], axs[3]))

def plot_residual_station(df, title, **kwargs):
    '''
    Create: 1402-05-07
    updated: 1402-05-08
    '''
    df_selection = df.sort_values(by=['station'])
    #
    phase = df_selection['phasetype'].values
    #
    x = df_selection['station'].values#.astype(str)
    y = df_selection['residuals']
    #
    xp = x[phase=='P']
    yp = y[phase=='P']
    xs = x[phase=='S']
    ys = y[phase=='S']
    #
    fig, axs = plt.subplots(2, 1, figsize=(15, 6), sharex=True, height_ratios=[1.5, 4])
    axs0 = axs[0]
    axs1 = axs[1]
    axs1.grid()
    #
    axs1.scatter(xp, yp, edgecolors='r', facecolors='none', marker='.', label='P-phase', alpha=0.7, s=150)
    axs1.scatter(xs, ys, edgecolors='b', facecolors='none', marker='.', label='S-phase', alpha=0.7, s=150)
    # print(xp, yp, xs , ys)
    #####
    group = df_selection.groupby(['station'])['residuals']
    mean = group.mean()
    mode = group.apply(pd.Series.mode)
    std = group.std()
    counts = group.count().values
    #
    # axs1.plot(mode.index, mode.values, 'k-.', label='Mode')
    axs1.plot(mean.index, mean.values, 'g', label='Mean')
    axs1.fill_between(mean.index,
                    mean.values - std.values,
                    mean.values + std.values, alpha=0.2, label='Std')

    # ax.set_yscale('log')
    # plt.ylim([-5, 5])
    # plt.title('PhaseNet')
    plt.xlabel('Station Name')
    axs1.set_ylabel('$T_{DL}$ - $T_{man}$')
    plt.xticks(rotation = 45) # Rotates X-Axis Ticks by 45-degrees
    axs1.legend(loc=4)
    plt.subplots_adjust(bottom=0.15, hspace=0)
    #
    counts = df_selection.groupby(['station'])['residuals'].count()
    bars = axs[0].bar(counts.index, counts.values, align='center', log=False)
    axs0.bar_label(bars, size=8)
    axs0.set_ylim(top=counts.values.max()*1.1)
    _finalise_figure(fig, **kwargs)


def limited_hist(data, bins, title=None, label=None):
    '''
    Create: 1402-05-10
    '''
    bins_label = bins.copy()
    min_data = min(data)
    max_data = max(data)
    delta_bins = bins[1] - bins[0]
    if min_data < bins[0]:
        data[data < bins[0]] = bins[0] + (delta_bins/2)
        bins_label[0] = min_data
    if bins[-1] < max_data:
        data[data > bins[-1]] = bins[-1] - (delta_bins/2)
        bins_label[-1] = max_data
    ##########################################################################################
    fig = plt.figure(figsize=(10, 5))
    rects = plt.hist(data, bins, align='mid', edgecolor='black', linewidth=1.2, label=label)
    autolabel(rects)
    plt.ylabel('Abundance [count]', fontsize=17)
    plt.xlabel('RMS [s]', fontsize=17)
    plt.xticks(bins, bins_label)
    plt.title(title)
    #fig = _finalise_figure(fig=fig, **kwargs)
