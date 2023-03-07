import requests
import xmltodict as xmltodict
from itertools import combinations
from Bio import Entrez
from Bio import Medline
import os

Entrez.email = 'dhwanisolanki128@gmail.com'
import json
from authormaps.startup import DATA_DIR
import time
import pandas as pd
from tqdm import tqdm
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple


class ApiInterface:
    def __init__(self,  lastname,firstname,):
        """

        Parameters
        ----------
        firstname
        lastname
        """

        self.firstname = firstname.capitalize()
        self.lastname = lastname.capitalize()
        self.pubmedidlist = None
        self.nodelistunique = None
        self.messagefrontend = None
        self.searchlist = False
        self.nodelistunique_filter = None


    def getpubmedidlist(self):
        """get list of publication for a queried author saved as xml file in cache or from API """
        
        path = os.path.join(DATA_DIR, f'{self.firstname}{self.lastname}.xml')
        # checks if we have the pubmed ids of author in cache
        if f'{self.firstname}{self.lastname}.xml' in os.listdir(DATA_DIR):
            self.pubmedidlist = xmltodict.parse(ET.tostring(ET.parse(path).getroot()))['eSearchResult']['IdList']['Id']
            if not isinstance(self.pubmedidlist, list):
                self.pubmedidlist = [self.pubmedidlist]
            self.searchlist = True
        else:
            self.messagefrontend = 'searching pubmed database for list of publication of authors'
            api_query = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={self.lastname}+{self.firstname}%5Bauthor%5D&retmax=9999'

            header = {"Accept": "text/xml"}
            r = requests.get(api_query, headers=header)
            if r.status_code == 200:
                if xmltodict.parse(r.text)['eSearchResult']['IdList'] is None:
                    print("No list of publications for this author found :", f'{self.firstname} {self.lastname}')
                    # author not found
                    self.messagefrontend = (702, f"No list of publications for this author found: {self.firstname} {self.lastname}")

                elif xmltodict.parse(r.text)['eSearchResult']['IdList']['Id'] != None:
                    self.pubmedidlist = xmltodict.parse(r.text)['eSearchResult']['IdList']['Id']
                    self.messagefrontend = f'downloading {len(self.pubmedidlist)} publications  of author, it may take a moment'
                    if not isinstance(self.pubmedidlist, list):
                        self.pubmedidlist = [self.pubmedidlist]
                    with open(path, "w") as f:
                        f.write(r.text)          # write to xml file
                    self.searchlist = True

            elif r.status_code == 400:
                print(f'Bad Request!! for {self.firstname}{self.lastname}')
                self.messagefrontend = (702, f'Bad Request!! for {self.firstname} {self.lastname}')
            else:
                self.messagefrontend = (702, 'Other errors while requesting pubmed')
            time.sleep(0.4)


    def coauthorslist(self, pubmedid:str) -> List:
        """ get authors list by giving pubmed Id
           Parameters
           ----------
           pubmedid: str

           Returns
           -------
           coauthors: List containing the coauthors

        """
        # check if we have the json file for publication in cache
        if f'{pubmedid}.json' in os.listdir(DATA_DIR):
            path = os.path.join(DATA_DIR, f'{pubmedid}.json')
            with open(path) as json_file:
                content = json.load(json_file)
                if 'FAU' in content:
                    co_authors = [i.replace(',','') for i in content['FAU']]
                    return co_authors
                else:
                    self.messagefrontend = (701, 'FAU Key Not Found')
        else:
            from urllib.error import HTTPError

            self.messagefrontend = 'downloading all publications of author'
            try:
                Entrez.efetch(db="pubmed", id=pubmedid, rettype="medline", retmode="text")
            except HTTPError as e:  # using urllib2.HTTPError
                print(f'publication {pubmedid} not found, {e}')
                self.messagefrontend = f'publication {pubmedid} not found, {e}' 
            else:
                filedb = Entrez.efetch(db="pubmed", id=pubmedid, rettype="medline", retmode="text")
                for i in Medline.parse(filedb):
                    dicfiledb = dict(i)

                if 'FAU' in dicfiledb:
                    co_authors = [i.replace(',','') for i in dicfiledb['FAU']]
                    with open(os.path.join(DATA_DIR, f'{pubmedid}.json'), 'w') as fp:
                        json.dump(dicfiledb, fp)
                    time.sleep(0.4)
                    return co_authors
                else:
                    self.messagefrontend = (701,'FAU Key Not Found')


    def publicalistfiltered(self) -> List:
        """ coauthors list filtered only for first author query to handle name collisions
            Returns
            -------
            self.nodelistunique: Node list containing coauthors
            
        """
        
        nodelist_filter = []
        nodelist = []
        self.getpubmedidlist()

        if self.pubmedidlist:
            # check for max. allowed publications
            if len(self.pubmedidlist) > 1000:
                self.messagefrontend = (705, f"PLease specify your search, too many publications found {len(self.pubmedidlist)}")
            else:
                if self.searchlist:
                    for pubmedid in tqdm(self.pubmedidlist, total=len(self.pubmedidlist)):
                        authorlist = self.coauthorslist(pubmedid)

                        if authorlist:
                            if len(authorlist) > 1 and len(authorlist) < 51 :  # restricts articles that have more than 50 authors
                                if f'{self.lastname} {self.firstname}'.lower() in [a.lower() for a in authorlist]:

                                    nodelist.append(authorlist)
                            nodelist_filter.append(authorlist)



        self.nodelistunique = list(set(sum(nodelist, [])))
        self.nodelistunique_filter = list(set(sum(nodelist_filter, [])))
        return self.nodelistunique

    def get_every_author_connection(self) -> Dict:
        """ Returns dict containing list of publications for every pair of authors
        
            Returns
            -------
            common_dict: key: Tuple, value: List

        """
        common_dict = {}
        pub_dict = {}
        author_list = self.publicalistfiltered()

        # fetching pub details of every author
        for a in tqdm(author_list, total=len(author_list)):

            lastname,firstname = a.split(' ')[0], ' '.join(a.split(' ')[1:])

            obj_a = ApiInterface(lastname,firstname) #+ order name
            obj_a.getpubmedidlist()
            pub_list = obj_a.pubmedidlist
            pub_dict[a] = pub_list

        author_combination = combinations(author_list, 2)
        dict_keys = pub_dict.keys()
        for a_tuple in author_combination:
            if a_tuple[0] in dict_keys and a_tuple[1] in dict_keys:
                if pub_dict[a_tuple[0]] and pub_dict[a_tuple[1]]:
                    common_publication = set(pub_dict[a_tuple[0]]).intersection(set(pub_dict[a_tuple[1]]))
                    if common_publication:
                        common_dict[a_tuple] = list(common_publication)


        return common_dict


    def printmessage(self):
        """ print message to frontend web server to notify when potential name collisions happen"""

        if self.nodelistunique_filter and self.nodelistunique:

            listnamecollision=[i for i in self.nodelistunique_filter if self.lastname in i]

            if listnamecollision:

                if len(listnamecollision) > 1:
                    listnamecollisionrev=[' '.join(l.split()[1:])+' '+l.split()[0] for l in listnamecollision]
                    self.messagefrontend = (703,listnamecollisionrev)
                elif len(listnamecollision)==1:
                    self.messagefrontend = (700, f'Done')
            else:
                self.messagefrontend = (700, f'Done')

        elif self.nodelistunique_filter:
            self.messagefrontend =(704, [" ".join(l.split()[1:])+" "+l.split()[0] for l in self.nodelistunique_filter if self.lastname.lower() in l.lower()])

        else:

            if not self.pubmedidlist:
                self.messagefrontend = (702, f'No result were found for {self.lastname} {self.firstname}')






    @staticmethod
    def reduced_name(name: str) -> str:
        """Returns a shortened version of given string
            Parameters
            ----------
            name: Full name of the author """
            
           
        return name.split(' ')[0]+'_'+ '_'.join([i[0] for i in (name.split(' ')[1:])]) #+ order name


    def make_dataframe(self) -> "Dataframe":
        """ Returns node and edge dataframes
            Returns 
            -------
            node_df, edge_df
        """

        author_dict = self.get_every_author_connection()

        if self.nodelistunique:
            nodes_from_edges = set([item for t in author_dict.keys() for item in t])
            nodes_set = set(self.nodelistunique)

             # removing node discrepensies
            if nodes_from_edges != nodes_set:
                diff = nodes_set.difference(nodes_from_edges)
                for elem in diff:
                    nodes_set.discard(elem)
                self.nodelistunique = list(nodes_set)


            if self.searchlist:
                edge_list = []
                for k, v in author_dict.items():
                    edge_list.append([k[0], k[1], len(v)])

                edge_df = pd.DataFrame(edge_list, columns=['author1', 'author2', 'pub_id'])

                node_df = pd.DataFrame.from_records([self.nodelistunique]).transpose()
                node_df.columns = ['full_name']
                node_df['short_name'] = node_df['full_name'].apply(self.reduced_name)
                node_df = node_df[node_df.columns[::-1]]
                edge_df['author1'] = edge_df['author1'].apply(self.reduced_name)
                edge_df['author2'] = edge_df['author2'].apply(self.reduced_name)
                self.printmessage() 
                return node_df, edge_df


        else:
            self.printmessage()



if __name__ == "__main__":

    nodeedge = ApiInterface( 'Hofmann-Apitius','Martin')
    n,e=nodeedge.make_dataframe()
    print(n,e)
    print(nodeedge.messagefrontend)

# from authormaps.pkg.authormaps import startup
# change to import startup
# and copy startup in the same folder as run.py
