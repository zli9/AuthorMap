"""Tests for sharedwork.py containing the API part"""


import pandas
import os

from authormaps.sharedwork import ApiInterface
from authormaps.startup import DATA_DIR


class TestApiInterface:
    """Class comprising of unit tests for ApiInterface methods found in sharedwork.py."""

    def test_getpubmedidlist(self):
        """Tests if correct pubmed list is generated"""
        author = ApiInterface("Srinivasan", "Sanjana")
        author.getpubmedidlist()
        path = os.path.join(DATA_DIR, 'SanjanaSrinivasan.xml')
        assert os.path.exists(path)
        assert len(author.pubmedidlist) == 10
        # should I test for number of publications ? What if new publications are getting added ?
        assert '34754938' in author.pubmedidlist
        assert '31316073' in author.pubmedidlist

    def test_coauthorslist(self):
        """Tests if correct coauthorlist is generated for pubmed id"""
        author = ApiInterface("Srinivasan", "Sanjana")
        author.coauthorslist('34754938')
        assert "Srinivasan Sanjana" in author.coauthorslist('34754938')

    def test_publicalistfiltered(self):
        """Tests to check for name collisions"""
        author = ApiInterface("Srinivasan", "Sanjana")
        author.publicalistfiltered()
        assert "Srinivasan Sanjana" in [i for i in author.nodelistunique_filter if author.lastname in i]

    def test_printmessage(self):
        """Tests to check for printmessage method"""
        author = ApiInterface("Srinivasan", "Sanjana")
        author.publicalistfiltered()
        author.printmessage()
        assert "Done" in author.messagefrontend[1]

    def test_get_every_author_connection(self):
        """Tests to check the coauthor connections"""
        author = ApiInterface("Srinivasan", "Sanjana")
        coauthor_dict = author.get_every_author_connection()
        assert isinstance(coauthor_dict,dict)
        if ('Concina Isabella', 'Srinivasan Sanjana') in coauthor_dict.keys():
            assert coauthor_dict[('Concina Isabella', 'Srinivasan Sanjana')] == ['34062049']
        else:
            assert coauthor_dict[('Srinivasan Sanjana', 'Concina Isabella')] == ['34062049']

    def test_reduced_name(self):
        """Tests for reduced_name method"""
        author = ApiInterface("Srinivasan", "Sanjana")
        new_name1 = author.reduced_name("Srinivasan Sanjana")
        assert new_name1 == 'Srinivasan_S'
        new_name2 = author.reduced_name("Srinivasan Sanjana S")
        assert new_name2 == 'Srinivasan_S_S'

    def test_make_dataframe(self):
        """Test make_dataframe method"""
        author = ApiInterface("Srinivasan", "Sanjana")
        node_df, edge_df = author.make_dataframe()
        assert type(node_df) == pandas.core.frame.DataFrame
        assert type(edge_df) == pandas.core.frame.DataFrame
        assert len(node_df.columns) == 2
        assert len(edge_df.columns) == 3

