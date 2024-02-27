#!/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import logging
import matplotlib.pyplot as plt
import sys
from scipy.stats import gaussian_kde
import numpy as np
import pickle

from parse_tree import Node, label_clades
from pca_tree import extract_mat_leaves, do_pca, do_pca_new, extract_state_from_node


def plot_leaves_rec(node, X_transformed, id2idx, plt, p1, p2):
    _id = node._id
    if hasattr(node, "left"):
        plot_leaves_rec(node.left, X_transformed, id2idx, plt, p1, p2)
        plot_leaves_rec(node.right, X_transformed, id2idx, plt, p1, p2)
    if _id in id2idx:
        # leaf
        idx = id2idx[_id]
        x, y = X_transformed[idx, p1], X_transformed[idx, p2]
        plt.scatter(x, y, c="g", s=60)
        # if node.name == "LoloishLisu" or node.name.startswith("Burmish"):
        #     plt.annotate(node.name, (x, y),
        #                  xytext=(x + 0.03, y + 0.03),
        #                  fontsize=12)


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument("--burnin", type=int, default=0, help="discard the first n samples")
    parser.add_argument("--index", type=int, default=-1, help="use the n-th tree (default: -1)")
    parser.add_argument("--otype", choices=["pdf", "png"], default="pdf", help="pdf or png (default: pdf)")
    parser.add_argument("--show-tip", action="store_true", default=True, help="Show tip (default: True)")
    parser.add_argument("--dtype", choices=["standard", "covarion", "pdcovarion"], default="standard", help="Type of data (default: standard)")
    parser.add_argument("trees")
    parser.add_argument("tag")
    parser.add_argument("clade")
    parser.add_argument("output")
    args = parser.parse_args()
    logging.info("{}".format(vars(args)))

    # usage: input key [output]
    #   key: &japanese, &Ainu_UCLD_GRRW_SDollo, &Koreanic_CovUCLD
    trees = pickle.load(open(args.trees, "rb"))
    tid = args.index
    k = args.tag
    clade_name = args.clade
    burnin = args.burnin
    p1, p2 = 0, 1  # first and second PCs (zero-based numbering)
    dtype = args.dtype

    plt.figure(figsize=(8, 6), dpi=120)

    matched, total = 0, 0
    clade_vect_list = []
    for i in range(burnin, len(trees)):
        root = trees[i]
        clade_dict = label_clades(root)
        total += 1
        if clade_name in clade_dict:
            matched += 1
            clade = clade_dict[clade_name]
            vect = extract_state_from_node(clade, k, dtype=dtype)
            clade_vect_list.append(vect)
        if i == tid:
            X, id2idx, idx2node = extract_mat_leaves(root, k, dtype=dtype)
            pca, X_transformed = do_pca(X)

            # plt.figure()
            plt.xlabel("PC%d (%2.1f%%)" % (p1 + 1, pca.explained_variance_ratio_[p1] * 100), fontsize=18)
            plt.ylabel("PC%d (%2.1f%%)" % (p2 + 1, pca.explained_variance_ratio_[p2] * 100), fontsize=18)
            plot_leaves_rec(root, X_transformed, id2idx, plt, p1, p2)
            plt.tick_params(axis='x', labelsize=14)
            plt.tick_params(axis='y', labelsize=14)
    logging.info(f"{clade_name} matched: {matched/total} ({matched} / {total})")

    Y = np.empty((len(clade_vect_list), X.shape[1]), dtype=np.int32)
    for i, vect in enumerate(clade_vect_list):
        Y[i] = vect
    Y_transformed = do_pca_new(pca, Y)

    val = np.vstack((Y_transformed[:,p1], Y_transformed[:,p2]))
    kernel = gaussian_kde(val)
    # xmin, xmax = ax.get_xlim()
    # ymin, ymax = ax.get_ylim()
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    _X, _Y = np.mgrid[xmin:xmax:300j, ymin:ymax:300j]
    positions = np.vstack([_X.ravel(), _Y.ravel()])
    Z = np.reshape(kernel(positions).T, _X.shape)
    plt.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r, extent=[xmin, xmax, ymin, ymax], aspect="auto")
    
    if args.otype == "pdf":
        plt.savefig(args.output, format="pdf", transparent=False, dpi=160, bbox_inches='tight')
    else:
        plt.savefig(args.output, format="png", transparent=False, dpi=160)
    plt.show()


if __name__ == "__main__":
    main()
