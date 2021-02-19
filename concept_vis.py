#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 11:49:10 2021

@author: Caleb Powell
"""
# import libraries
import argparse
import os
import pandas as pd
import geopandas
# additionally requires rtree for a geopandas function
import matplotlib.pyplot as plt


# define helpful functions
def gen_markersize(df, col, expansion=4):
    """
    Parameters
    ----------
    df : dataframe
        the dataframe to operate on.
    col : str
        the column name from which to generate the markersizes.
    expansion : int (optional)
        the integer by which the col is expanded for markerSize generation.

    Returns
    -------
    dataframe with "markerSize" column
    """
    # generate a markerSize column by exponential value expansion
    df["markerSize"] = df[col] ** int(expansion)
    df["markerSize"] = df["markerSize"].astype(int)
    return df

def _dir_path(path):
    """
    used internally to verify input string is a directory
    """
    if os.path.isfile(path) and str(path).endswith(".csv"):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid file path")

def _is_cmap(name):
    """
    used internally to verify input string is a matplotlib cmap
    """
    if name in plt.colormaps():
        return name
    else:
        print(f"Must Choose cmaps from the following list:\n{plt.colormaps()}\n")
        raise argparse.ArgumentTypeError(f"{name} is not a valid cmap.\nSee above list for valid options.")
        

# handle user arguments
parser = argparse.ArgumentParser()

parser.add_argument("input",
                    help="path to input data",
                    type=_dir_path)

parser.add_argument("output",
                    help="file name for output figure",
                    type=str)

parser.add_argument("feature",
                    help="column name for feature of interest",
                    type=str)

parser.add_argument("--cmap",
                    help="matplotlib colormap string",
                    default="autumn",
                    type=_is_cmap)

parser.add_argument("--expansion",
                    help="value by which features are expanded to determine marker sizes",
                    default="3",
                    type=int)

parser.add_argument("--lat",
                    help="column name for the decimalLatitude",
                    default="decimalLatitude",
                    type=str)

parser.add_argument("--lon",
                    help="column name for the decimalLongitude",
                    default="decimalLongitude",
                    type=str)

parser.add_argument("--position",
                    help='legend position string (e.g.,"lower right")',
                    default="upper left",
                    type=str)

parser.add_argument("--fontsize",
                    help="The fontsize used in the legend",
                    default="10",
                    type=int)

parser.add_argument("--fullmap",
                    help="if the shapefile should be restricted to the states with points in them.",
                    default="False",
                    type=str)

parser.add_argument("--dpi",
                    help="The dpi used for the figure",
                    default=300,
                    type=int)

args = parser.parse_args()
# load the dataframe into pandas
df = pd.read_csv(args.input)

#  load the lat/lon as geopoints
geoPoints = geopandas.points_from_xy(df[args.lon], df[args.lat])
# generate a GeoDataFrame using the df & geoPoints
gdf = geopandas.GeoDataFrame(df, geometry=geoPoints).set_crs("EPSG:4269")

# state shape file from:
#    https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
state_shp = geopandas.read_file("./data/cb_2018_us_state_5m/cb_2018_us_state_5m.shp")

# identify which state polygons contain a point of interest
polygons_contains = geopandas.sjoin(state_shp, gdf, op='contains')
# build a keep list of state names based on those polygons
keep_states = polygons_contains["NAME"].unique().tolist()

if args.fullmap in ["1", "true", "True"]:
    states = state_shp
else:
    # Restrict the figure to those states of interest
    states = state_shp[state_shp["NAME"].isin(keep_states)]

fig = plt.figure()
ax = states.plot(color='white', edgecolor='black')
ax.axis("off")
plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
# generate the markersize column
gdf = gen_markersize(gdf, args.feature, expansion=args.expansion)

# We can now plot our ``GeoDataFrame``.
gdf.plot(ax=ax,
         markersize="markerSize",
         c=args.feature,
         cmap=args.cmap,
         column=args.feature,
         categorical=True,
         legend=True,
         legend_kwds={'loc': args.position.lower(),
                      'fontsize' : args.fontsize,
                      'title': f"# {args.feature}"},
         edgecolors='k') # edgecolors make a border

# force a tight layout
plt.savefig(args.output, dpi=args.dpi, pad_inches=0)