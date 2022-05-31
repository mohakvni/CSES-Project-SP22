#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 17:58:28 2022

@author: saathvikdirisala
"""

import pandas as pd
import matplotlib.pyplot as plt
from kneed import KneeLocator
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import numpy as np
import os

# IGNORE: For debugging
# csv = "Songs.csv"
# num_songs = 5

def similar_songs(songs, num_songs) -> pd.DataFrame:

    # Retrieves original song from first index and saves song id
    og_song = songs.iloc[0, :]
    
    # print("Original song: " + og_song["name"] + " by " + og_song["artist"] + "\n")
    
    # Detects numerical data in file
    features = np.array(songs.iloc[:, 4:])
    
    # print(features)
    
    # Scales the numerical data (standardization)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # METHOD 1: Find a large enough cluster to meet the song number 
    # requirements within the restraints of the algorithm
    num_clusters = scaled_features.shape[0] // num_songs
    num_collected_songs = 0
    iteration = 1
    while (num_collected_songs < num_songs and num_clusters > 1):
        kmeans = KMeans(
            init="random",
            n_clusters=num_clusters,
            n_init=10,
            max_iter=300,
            random_state=42
        )
        kmeans.fit(scaled_features)
        
        # print(f"Iteration #{iteration}")
        # print("Number of clusters: " + str(num_clusters))
        # print("Inertia: " + str(kmeans.inertia_))
        
        songs["Label"] = kmeans.labels_
        og_label = songs.iloc[0, -1]
        similar_songs = songs[songs.Label == og_label]
        num_collected_songs = similar_songs.shape[0] - 1
        # print("Number of songs: " + str(num_collected_songs) + "\n")
        
        num_clusters -= 1
        
        iteration += 1
    
    if num_collected_songs < num_songs:
        print("WARNING: maximum number of relevant songs reached")
        print("Expand input csv")
        
    return similar_songs.iloc[1:, 1:4]

# Testing
# print(similar_songs("Songs.csv", 6))


def helper_songs():
    i = 0
    while os.path.exists("temp_data/Songs{}.csv".format(i)):
        csv = "temp_data/Songs{}.csv".format(i)
        print(i)
        try:
            songs = pd.read_csv(csv)
            shape = songs.shape
            result = pd.DataFrame(similar_songs(songs, min(shape[0], 5)))
            if i > 0:
                result.to_csv("Queue.csv", mode = "a", index = True, header = False)
            else:
                print("hello")
                result.to_csv("Queue.csv")
            os.remove(csv)
            i += 1
        except:
             continue
        

    
# METHOD 2: Find relevant songs given the initial cluster size and then move
# onto the next set of songs within the same genre
#
# More space-intensive but it doesn't really matter because there will always be
# at least one other song queued up. Also, it will allow us to find a better
# pool of songs
# TODO



# inertia_vals = []
# diff_inertia = []

# for i in range(1,100):
#     kmeans = KMeans(
#         init="random",
#         n_clusters=i,
#         n_init=10,
#         max_iter=300,
#         random_state=42
#     )
#     kmeans.fit(scaled_features)
#     if i > 1:
#         diff_inertia.append(inertia_vals[-1] - kmeans.inertia_)
#         if i > 2:
#             if diff_inertia[-1] - diff_inertia[-2] > -10:
#                 inertia_vals.append(kmeans.inertia_)
#                 break
#     inertia_vals.append(kmeans.inertia_)

# plt.figure(0)
# plt.plot(np.arange(1,len(inertia_vals) + 1), inertia_vals)
# plt.savefig("plot.png")

# plt.figure(1)
# plt.plot(np.arange(1,len(diff_inertia) + 1), diff_inertia)
# plt.savefig("diff_plot.png")

# ideal_cluster_size = len(inertia_vals)