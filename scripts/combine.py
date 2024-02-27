#!/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import logging
import sys
import os
import re
import pickle

from nexus import NexusReader

from parse_tree import TreeParser

def combine_nodes(nodes, k):
    # merge annotation
    combined_node = nodes[0]
    combined_dat = ""
    has_quote = False
    for node in nodes:
        dat = node.annotation["&" + k]
        if dat.startswith('"'):
            has_quote = True
            dat = dat.replace('"', '')
        combined_dat += dat
    if has_quote:
        combined_dat = '"' + combined_dat + '"'
    combined_node.annotation["&" + k] = combined_dat
    if hasattr(combined_node, "left"):
        left_nodes = [node.left for node in nodes]
        combine_nodes(left_nodes, k)
        right_nodes = [node.right for node in nodes]
        combine_nodes(right_nodes, k)
    return combined_node

def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument("--index", type=int, default=-1, help="use the n-th tree (default: -1)")
    parser.add_argument("template")
    parser.add_argument("items")
    parser.add_argument("tag")
    parser.add_argument("output")
    args = parser.parse_args()
    logging.info("{}".format(vars(args)))

    file_template = args.template
    k = args.tag
    _id = args.index
    
    items = []
    with open(args.items) as f:
        for line in f:
            line = line.rstrip()
            items.append(line)
    trees = []
    for item in items:
        fp = file_template.format(item)
        logging.info(f"processing {fp}")
        tp = TreeParser(fp)
        tp.n.trees.detranslate()
        tree = tp.parse(_id)
        trees.append(tree)
    logging.info("combining nodes...")
    combined_tree = combine_nodes(trees, k)

    with open(args.output, "wb") as f:
        pickle.dump([combined_tree], f)


if __name__ == "__main__":
    main()
