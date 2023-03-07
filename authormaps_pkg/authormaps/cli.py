import os
import sys
import click
from authormaps.sharedwork import ApiInterface
from authormaps.network import Network, Visualizer

@click.group()
def cli():
    pass

@cli.command(name="getpubmedidlist")
@click.argument("lastname", type=str)
@click.argument("firstname", type=str)
def getpubmedidlist(lastname,firstname):
    """Returns PUBMED Ids for given author name"""
    author = ApiInterface(lastname,firstname)
    author.getpubmedidlist()
    publications_list = author.pubmedidlist
    if publications_list:
        print(publications_list)
    else:
        print(f"No publications found for author")

@cli.command(name="coauthorslist")
@click.argument("lastname", type=str)
@click.argument("firstname", type=str)
@click.argument("pubmedid", type=str)
def coauthorslist(lastname,firstname,pubmedid):
    """ Query will be author name and pubmedid and it returns a co-author lists for specific publication"""
    author = ApiInterface(lastname,firstname)
    author.getpubmedidlist()
    if pubmedid in (author.pubmedidlist):
        print(author.coauthorslist(pubmedid))
    else:
        print('Author Not found')



@cli.command(name="get_publicalistfiltered")
@click.argument("lastname", type=str)
@click.argument("firstname", type=str)
def get_publicalistfiltered(lastname,firstname):
    """coauthors list filtered only for first author query to handle name collisions.
    Downloads the cache files for authors and returns co-authors list"""
    author = ApiInterface(lastname,firstname)
    author.publicalistfiltered()
    coauthors=author.nodelistunique
    print("Co-author list:", coauthors)



@cli.command(name="get_every_author_connection")
@click.argument("lastname", type=str)
@click.argument("firstname", type=str)
def get_every_author_connection(lastname,firstname):
    """Returns dict containing list of publications for every pair of authors"""
    author = ApiInterface(lastname,firstname)
    list_of_pub_author=author.get_every_author_connection()
    print(list_of_pub_author)


@cli.command()
@click.argument("first_name")
@click.argument("last_name")
@click.argument("output")
@click.option('-i', '--dpi', default=72, help="Specifies the resolution of network graph.")
@click.option('-b', '--label', default=False, is_flag=True, help="Show the number of shared publications as edge label.")
def create(first_name: str, last_name: str, output: str, label: bool, dpi: int):
    """Create a author mapping network."""
    network = Visualizer(first_name=first_name, last_name=last_name)
    graph = network.generate_graph_image(graph_output_path=output, dpi=dpi, with_edge_labels=label)
    click.echo(f"Save graph at {os.path.abspath(output)}")


@cli.command()
@click.argument("first_name")
@click.argument("last_name")
@click.option('-a1', '--author1', default=None, help="One author to be query shared publications. e.g., 'Bruce Schultz'")
@click.option('-a2', '--author2', default=None, help="The other author to be query shared publications. e.g., 'Joshua Lederberg'")
@click.option('-o', '--output', default=None, help="Path to save data in node-link format.")
def compile(first_name: str, last_name: str, output: str, author1: str, author2: str):
    """Calculate how many shared publications."""
    network = Network(first_name=first_name, last_name=last_name)
    if author1 and author2:
        click.echo(f"Author 1: {author1}")
        click.echo(f"Author 2: {author2}")
        click.echo(f"No. shared publication: {network.get_shared_publication(author1, author2)}")
    if output:
        network.generate_node_link_data(filepath=output)
        click.echo(f"Save file at {os.path.abspath(output)}")



def main():
    cli()


if __name__ == '__main__':
    main()



#testing cli
# python Cli.py getpubmedidlist "Schultz" "Bruce"
# python Cli.py coauthorslist "Bajorath" "Jurgen" "33846469"
# python Cli.py get_publicalistfiltered "srinivasan" "sanjana"
# python Cli.py get_every_author_connection "srinivasan" "sanjana"

