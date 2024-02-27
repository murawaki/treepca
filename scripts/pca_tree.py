#!/bin/env python
# -*- coding: utf-8 -*-
# project a tree onto a PCA-generated space
from argparse import ArgumentParser
import logging
import matplotlib.pyplot as plt
import numpy as np
import pickle
import sys
from sklearn.decomposition import PCA

from parse_tree import Node


def extract_state_from_node(node, k, dtype="standard"):
    dat = node.annotation["&" + k]
    dat = dat.replace('"', '')
    if dtype == "standard":
        f = int
    elif dtype == "covarion":
        m = {
            '0': 0,
            '1': 1,
            'A': 0,
            'B': 1,
        }
        f = lambda x: m[x]
    elif dtype == "pdcovarion":
        m = {
            'A': 0, # absent
            '1': 1, # present
            'B': 0, # removed
            '0': 0, # absentS
            '?': 1, # presentS
        }
        f = lambda x: m[x]
    else:
        raise NotImplementedError
    if "," in dat:
        vect = list(map(lambda x: f(x), dat.split(",")))
    else:
        vect = list(map(lambda x: f(x), dat))
    return vect


def extract_mat(root, k, dtype="standard"):
    mat_orig = {}
    stack = [root]
    size = -1
    while len(stack) > 0:
        node = stack.pop(0)
        vect = extract_state_from_node(node, k, dtype=dtype)
        size = len(vect)
        mat_orig[node._id] = vect
        if hasattr(node, "left"):
            stack.append(node.left)
            stack.append(node.right)
    mat = np.empty((len(mat_orig), size), dtype=np.int32)
    for _id, vect in mat_orig.items():
        mat[_id] = vect
    return mat


def extract_mat_leaves(root, k, dtype="standard"):
    mat_orig = {}
    id2idx = {}
    idx2node = {}
    stack = [root]
    size = -1
    while len(stack) > 0:
        node = stack.pop(0)
        if hasattr(node, "left"):
            stack.append(node.left)
            stack.append(node.right)
        else:
            vect = extract_state_from_node(node, k, dtype=dtype)
            size = len(vect)
            idx = id2idx[node._id] = len(id2idx)
            idx2node[idx] = node
            mat_orig[idx] = vect
    mat = np.empty((len(mat_orig), size), dtype=np.int32)
    for idx, vect in mat_orig.items():
        mat[idx] = vect
    return mat, id2idx, idx2node


def do_pca(X):
    pca = PCA()
    U, S, V = pca._fit(X)
    X_transformed = np.dot(X - pca.mean_, pca.components_.T)
    return pca, X_transformed


def do_pca_new(pca, X):
    return np.dot(X - pca.mean_, pca.components_.T)


def plot_rec(node, X_transformed, plt, p1, p2, show_tip=True):
    _id = node._id
    if hasattr(node, "parent"): # non-root
        _id2 = node.parent._id
        x1, x2 = X_transformed[_id2, p1], X_transformed[_id, p1]
        y1, y2 = X_transformed[_id2, p2], X_transformed[_id, p2]
        if min(abs(x1 - x2), abs(y1 - y2)) > 0.1:
            length_includes_head=True
        else:
            length_includes_head=False
        plt.arrow(x1, y1, x2 - x1, y2 - y1, fc="k", ec="k",
                  length_includes_head=length_includes_head)
    if hasattr(node, "left"):
        plot_rec(node.left, X_transformed, plt, p1, p2, show_tip=show_tip)
        plot_rec(node.right, X_transformed, plt, p1, p2, show_tip=show_tip)
    if hasattr(node, "left"):
        # internal
        if not hasattr(node, "parent"): # root
            plt.scatter(X_transformed[_id, p1], X_transformed[_id, p2], c="blue", s=25, marker='s')
            plt.annotate("ROOT", (X_transformed[_id, p1], X_transformed[_id, p2]), fontsize=18)
        else:
            plt.scatter(X_transformed[_id, p1], X_transformed[_id, p2], c="r", s=15, marker='s')
    else:
        # leaf
        x, y = X_transformed[_id, p1], X_transformed[_id, p2]
        plt.scatter(x, y, c="g", s=60)
        if show_tip:
            plt.annotate(node.name, (x, y),
                         xytext=(x + 0.10, y + 0.05),
                         fontsize=6)


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument("--index", type=int, default=-1, help="use the n-th tree (default: -1)")
    parser.add_argument("--otype", choices=["pdf", "png"], default="pdf", help="pdf or png (default: pdf)")
    parser.add_argument("--show-tip", action="store_true", default=True, help="Show tip (default: True)")
    parser.add_argument("--dtype", choices=["standard", "covarion", "pdcovarion"], default="standard", help="Type of data (default: standard)")
    parser.add_argument("trees")
    parser.add_argument("tag")
    parser.add_argument("output")
    args = parser.parse_args()
    logging.info("{}".format(vars(args)))

    trees = pickle.load(open(args.trees, "rb"))
    root = trees[args.index]
    show_tip = args.show_tip
    use_internal = False
    dtype = args.dtype

    X = extract_mat(root, args.tag, dtype=dtype)
    if use_internal:
        pca, X_transformed = do_pca(X)
    else:
        Y, id2idx, idx2node = extract_mat_leaves(root, args.tag, dtype=dtype)
        pca, Y_transformed = do_pca(Y)
        X_transformed = do_pca_new(pca, X)

    p1, p2 = 0, 1  # first and second PCs (zero-based numbering)

    plt.figure(figsize=(8, 6), dpi=120)
    plt.xlabel("PC%d (%2.1f%%)" % (p1 + 1, pca.explained_variance_ratio_[p1] * 100), fontsize=8)
    plt.ylabel("PC%d (%2.1f%%)" % (p2 + 1, pca.explained_variance_ratio_[p2] * 100), fontsize=8)
    plot_rec(root, X_transformed, plt, p1, p2, show_tip=show_tip)

    plt.tick_params(axis='x', labelsize=6)
    plt.tick_params(axis='y', labelsize=6)

    if args.otype == "pdf":
        plt.savefig(args.output, format="pdf", transparent=False, dpi=160, bbox_inches='tight')
    else:
        plt.savefig(args.output, format="png", transparent=False, dpi=160)
    plt.show()


if __name__ == "__main__":
    main()
