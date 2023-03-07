import os
import click
import pytest
from click.testing import CliRunner
from authormaps import cli
from authormaps.sharedwork import ApiInterface
from authormaps.startup import DATA_DIR

class TestCli:
    """Testing cli file"""
    def test_getpubmedidlist(self):
        runner = CliRunner()
        result = runner.invoke(cli.getpubmedidlist, "'Srinivasan'  'Sanjana'")
        assert result
        assert result.exit_code == 0
        assert "34754938" in result.output
        assert "34062049" in result.output
        assert "34039636" in result.output
        assert "33745946" in result.output

        result = runner.invoke(cli.getpubmedidlist, "'Solanki' 'Dhwani'")
        assert result
        assert result.exit_code == 0
        #assert result.output == ('No list of publications for this author found : Dhwani Solanki\n'\n 'No publications found for author\n')
        
        
    def test_coauthorslist(self):
        runner = CliRunner()
        result = runner.invoke(cli.coauthorslist,  "'Bajorath' 'Jurgen', '33846469'")
        assert result
        assert "Feldmann Christian", 'Bajorath Jurgen' in result.output


    def test_get_publicalistfiltered(self):
        runner = CliRunner()
        result = runner.invoke(cli.get_publicalistfiltered, "'Srinivasan'  'Sanjana'")
        assert result
        assert result.exit_code == 0
        assert 'Carugo Alessandro' in result.output
        assert 'Tripathi Durga N' in result.output


    def test_get_every_author_connection(self):
        runner = CliRunner()
        result = runner.invoke(cli.get_every_author_connection, "'Srinivasan'  'Sanjana'")
        assert result
        assert result.exit_code == 0
        if "('Dasgupta Pushan', 'Yu Fei'): ['34039636']" in  result.output:
            assert "('Dasgupta Pushan', 'Yu Fei'): ['34039636']" in  result.output
        else:
            assert "('Yu Fei', 'Dasgupta Pushan'): ['34039636']" in  result.output

    def test_create(self):
        runner = CliRunner()
        GRAPH_FILE = "./test_data/network.pdf"

        result = runner.invoke(cli.create, f"Bruce Schultz {GRAPH_FILE}")
        assert result
        assert result.exit_code == 0
        assert os.path.abspath(GRAPH_FILE)
        os.remove(GRAPH_FILE)

    def test_compile(self):
        runner = CliRunner()
        result = runner.invoke(cli.compile, "Bruce Schultz --author1 'Manuel Peitsch' --author2 'Julia Hoeng'")
        assert result.exit_code == 0





