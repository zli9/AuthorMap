import logging
from pathlib import Path
from typing import Optional, Union
from collections import Counter

import json
import pandas as pd
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph

import authormaps.startup
from authormaps.sharedwork import ApiInterface


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Network:
    """Represent an author mapping network."""

    def __init__(self, first_name: str = None, last_name: str = None):
        self.graph = None
        self.shared_pb_num = None
        self.node_mapping = None
        self.reverse_node_mapping = None

        # Request author relationships via api
        node_list, authormap_file = ApiInterface(firstname=first_name, lastname=last_name).make_dataframe()
        logger.debug(f"Shared co-author mapping has been loaded.")

        self.create_network(node_list=node_list, authormap_file=authormap_file)    # Assigns self.graph AND self.shared_pb_num

    def create_network(self, node_list: pd.DataFrame, authormap_file: pd.DataFrame) -> None:
        """Generate author mapping network."""
        author_pairs = self.__extract_author_pairs(authormap_file)    # Count the number of publications shared between every combination of authors
        edge_list = self.__extract_edges(author_pairs)
        graph = nx.parse_edgelist(edge_list)

        self.node_mapping = self.__extract_nodes(node_list)
        self.reverse_node_mapping = self.__extract_reversed_nodes(node_list)
        self.shared_pb_num = author_pairs
        self.graph = graph

    def get_shared_publication(self, author1: str, author2: str) -> int:
        """Return the number of shared publication between author1 and author2."""
        # transform from full name to node id
        a1 = self.reverse_node_mapping[author1]
        a2 = self.reverse_node_mapping[author2]
        # ensure name tuple in alphabetical order
        if a1 > a2:
            a1, a2 = a2, a1
        return self.shared_pb_num.get((a1, a2), 0)

    def generate_node_link_data(self, filepath: Union[str, Path]) -> None:
        """Generate and save data in node-link format."""
        data = json_graph.node_link_data(self.graph)
        with open(filepath, 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def __extract_edges(author_pairs: dict) -> list:
        """Return a list of edges."""
        edge_list = [f"{pair[0]} {pair[1]} {{'shared_publication': {num}}}" for pair, num in author_pairs.items()]
        return edge_list

    @staticmethod
    def __extract_author_pairs(author_mapping: pd.DataFrame = None) -> dict:
        """Generate a dict of every author combinations and the number of their shared publications."""
        all_author_pairs = author_mapping.to_records(index=False).tolist()
        author_pair_dict = {}
        for i in range(len(all_author_pairs)):
            a1, a2, pb_num = all_author_pairs[i]
            if a1 < a2:
                author_pair_dict[(a1, a2)] = pb_num
            else:
                author_pair_dict[(a2, a1)] = pb_num  # ensure author names are sorted alphabetically
        return author_pair_dict

    @staticmethod
    def __extract_nodes(node_list: pd.DataFrame = None) -> dict:
        """Return a dictionary whose keys are node id and values are author name."""
        # fix the bug of sharework.py
        temp = node_list['full_name'].str.split(' ', n=1, expand=True)
        node_list['full_name'] = temp[1].str.cat(temp[0], sep=" ")
        return dict(zip(node_list['short_name'], node_list['full_name']))

    @staticmethod
    def __extract_reversed_nodes(node_list: pd.DataFrame = None) -> dict:
        """Return a dictionary whose keys are author name and values are node id."""
        return dict(zip(node_list['full_name'], node_list['short_name']))


class Visualizer(Network):
    """Generate a network image."""

    def __init__(self, first_name: str = None, last_name: str = None):
        super().__init__(first_name, last_name)
        self.edge_widths = self.__edges_width_mapping()
        self.edge_colors = self.__edges_color_mapping()
        self.node_colors = self.__nodes_color_mapping(first_name=first_name, last_name=last_name)

    def generate_graph_image(self, graph_output_path: Union[str, Path] = None, dpi: int = 72, with_edge_labels: bool = False) -> plt:
        """Generate a graph of network.

        Parameters
        ----------
        graph_output_path: Union[str, Path]
            Path to saving output image. Image extension must be either ".pdf", ".svg", ".png", or ".jpg".
        dpi: int
            Specifies the resolution of the network graph.
        with_edge_labels: bool
            Print edge label or not. Default: False
        Returns
        -------
            matplotlib object
        """

        plt.figure(figsize=(15, 15), dpi=dpi)
        graph_pos = nx.spring_layout(self.graph)
        nx.draw_networkx(self.graph, pos=graph_pos,
                         with_labels=True,
                         labels=self.node_mapping,
                         font_size=3,
                         node_color=self.node_colors,
                         edge_color=self.edge_colors,
                         width=self.edge_widths,
                         alpha=1,
                         node_size=100)
        if with_edge_labels:
            edge_labels = nx.get_edge_attributes(self.graph, 'shared_publication')
            nx.draw_networkx_edge_labels(self.graph, pos=graph_pos, edge_labels=edge_labels, font_size=2)
        if graph_output_path:
            self.__check_output(graph_output_path)
            plt.savefig(graph_output_path, bbox_inches="tight", dpi=dpi)
            logger.info(f"New graph image saved to {graph_output_path}")
        return plt

    def __nodes_color_mapping(self, first_name: str = None, last_name: str = None) -> list:
        """Get a list of colors for nodes."""
        labels = [self.node_mapping[node_name] for node_name in self.graph.nodes()]
        colors = []
        for label in labels:
            if (first_name + ' ' + last_name) in label:
                colors.append("#fdd0a2")
            else:
                colors.append("#c6dbef")
        return colors

    def __edges_color_mapping(self) -> list:
        """Get a list of colors for edges."""
        edges = self.graph.edges()
        shared_pub = [self.graph[u][v]['shared_publication'] for u, v in edges]
        cmap = mpl.colors.LinearSegmentedColormap.from_list(name="cmap", colors=["#f8f7b1", "#edf8b1", "#c7e9b4", "#7fcdbb", "#4dd4d6", "#41b6c4", "#1d91c0", "#225ea8", "#253494"])
        norm = mpl.colors.Normalize(vmin=min(shared_pub), vmax=10)
        colors = list(map(lambda n: cmap(norm(n)), shared_pub))
        return colors

    def __edges_width_mapping(self) -> list:
        """Get a list of widths for edges."""
        edges = self.graph.edges()
        shared_pub = [self.graph[u][v]['shared_publication'] for u, v in edges]
        if max(shared_pub) == 1:
            k = 1
        else:
            k = 9 / (max(shared_pub) - min(shared_pub))     # normalization to [1, 10]
        weights = [k*(x-min(shared_pub))+1 for x in shared_pub]
        return weights

    @staticmethod
    def __check_output(graph_output_path: Union[str, Path]) -> None:
        """Check if the output path extension is valid."""
        accepted_extensions = (".pdf", ".svg", ".png", ".jpg")
        if not isinstance(graph_output_path, Path):
            graph_output_path = Path(graph_output_path)
        output_extension = graph_output_path.suffix
        if output_extension not in accepted_extensions:
            logger.error(f"Wrong output file format passed: {output_extension}.\n"
                         f'Graph image must be either ".pdf", ".svg", ".png", or ".jpg"!')
            raise ValueError('Graph image must be either ".pdf", ".svg", ".png", or ".jpg"!')
