# Import packages
import os
import pandas as pd
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import pandana
from pandana.loaders import osm


###########################
## PANDANA ACCESSIBILITY ##
###########################

def get_pandana_network(osm_bbox, impedance=5000):
    """
    Utility function to get pandana nodes within analysis bounding box
     - Function also filters out poorly connected nodes. Still uncertain 
    if this is required. And if it is, can we find a better set of values?
    - Pandana network is saved to disk to avoid re-download
    
    Args:
     osm_bbox: OSM-spec'd bounding box as list  
     impedance: used for filtering poorly connected nodes
    Returns:
     network: pandana network
    """
    
    # Define some parameters
    bbox_string = '_'.join([str(x) for x in osm_bbox])
    net_filename = 'data/network_{}.h5'.format(bbox_string)

    if os.path.isfile(net_filename):
        # if a street network file already exists, just load the dataset from that
        network = pandana.network.Network.from_hdf5(net_filename)
    else:
        # otherwise, query the OSM API for the street network within the specified bounding box
        network = osm.pdna_network_from_bbox(osm_bbox[0],
                                             osm_bbox[1],
                                             osm_bbox[2],
                                             osm_bbox[3], 
                                             network_type='walk')


        # identify nodes that are connected to fewer than some threshold
        # of other nodes within a given distance
        lcn = network.low_connectivity_nodes(impedance, count=10, imp_name='distance')
        network.save_hdf5(net_filename, rm_nodes=lcn)


    return network


def get_accessibility(network, pois_df, distance=5000, num_pois=10):
    """
    Calculate accesibility metric per node in pandana network
    
    Args:
     network: pandana network
     pois_df: dataframe of POIS. Fuel stations here. 
     distance: Limit of accessibility analysis. 
     num_pois: integer to calculate nth closest POIS
    
    Returns:
     accessibility: dataframe. Size is #nodes rows, num_pois columns 
    """
    
    network.precompute(distance + 1)
    network.set_pois(category='all',
                     x_col=pois_df['lon'],
                     y_col=pois_df['lat'],
                     maxdist=distance,
                     maxitems=num_pois)
    accessibility = network.nearest_pois(distance=distance, category='all', num_pois=num_pois)
    return accessibility


def plot_accessibility(network, accessibility,
                       osm_bbox,
                       amenity_type = 'Z fuel station',
                       place_name='Wellington',
                       fig_kwargs={}, plot_kwargs={},
                       cbar_kwargs={}, bmap_kwargs={}):
    """
    Plotting accessibiity heatmap
    """

    title = 'Walking distance (m) to nearest {} around {}'.format(amenity_type,
                                                                  place_name)
 
    # network aggregation plots are the same as regular scatter plots,
    # but without a reversed colormap
    # Make the cmap management more generic?
    agg_plot_kwargs = plot_kwargs.copy()
    agg_plot_kwargs['cmap'] = plot_kwargs['cmap'].strip('_r')
    
    # Plot
    bmap, fig, ax = network.plot(accessibility, 
                                 bbox=osm_bbox, 
                                 plot_kwargs=plot_kwargs, 
                                 fig_kwargs=fig_kwargs, 
                                 bmap_kwargs=bmap_kwargs, 
                                 cbar_kwargs=cbar_kwargs)
    ax.set_title(title,  fontsize=15)
    ax.set_facecolor('w')
    return
