"""Tests for the network."""
import os
import json
import pytest

from authormaps.network import Network, Visualizer


class TestNetwork:
    """Tests Network class"""

    def test_get_shared_publication(self):
        """Test get_shared_publication method"""
        network = Network(first_name="Bruce", last_name="Schultz")
        author1 = "Manuel Peitsch"
        author2 = "Julia Hoeng"
        shared_pub = network.get_shared_publication(author1, author2)

        assert shared_pub == 163

    def test_generate_node_link_data(self):
        """Test generate_node_link_data method"""
        data_path = "./test_data/BruceSchultz_node_link_data.json"
        network = Network(first_name="Bruce", last_name="Schultz")
        network.generate_node_link_data(filepath=data_path)

        assert os.path.exists(data_path) is True
        with open(data_path) as f:
            node_link_data = json.load(f)
        assert isinstance(node_link_data["nodes"], list)
        assert isinstance(node_link_data["links"], list)
        assert len(node_link_data["nodes"]) == 35
        assert len(node_link_data["links"]) == 476


class TestVisualizer:
    """Tests Visualizer class"""

    def test_generate_graph_image(self):
        """Tests generate_graph_image method"""
        graph_pdf_path = "./test_data/BruceSchultz_network.pdf"
        network = Visualizer(first_name="Bruce", last_name="Schultz")
        network.generate_graph_image(graph_output_path=graph_pdf_path, with_edge_labels=True, dpi=300)

        assert os.path.exists(graph_pdf_path) is True

        graph_fake_path = "./test_data/BruceSchultz_network.fake"

        with pytest.raises(ValueError):
            network.generate_graph_image(graph_output_path=graph_fake_path, with_edge_labels=True, dpi=300)
