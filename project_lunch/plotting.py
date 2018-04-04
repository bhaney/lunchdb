#!/usr/bin/env python3.6
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from os import getenv

def histRatings(username,rating_list):
    plt.hist(rating_list, bins=10, range=[1, 11])
    #name labels on the axis
    plt.title(username+"'s Lunch Ratings")
    plt.ylabel('# of Reviews')
    plt.xlabel('Rating')
    #y axis ticks
    plt.axes().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    #x axis ticks
    mml = ticker.MultipleLocator(1)
    plt.axes().xaxis.set_major_locator(mml)
    plt.axes().set_xticklabels('')
    plt.axes().tick_params(axis='x',which='minor',length=0)
    plt.axes().set_xticks([1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5], minor=True)
    plt.axes().set_xticklabels(['1','2','3','4','5','6','7','8','9','10'], minor=True)
    #save figure
    plt.savefig(getenv("PLOT_PATH")+'/'+username+'_ratings.png');

