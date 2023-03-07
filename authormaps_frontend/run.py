import os 
import datetime
import networkx as nx
import time

from flask import Flask, flash, request, redirect, url_for, render_template, session, send_file, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path

# Later we import from the module not from a folder
#from authormaps.network import Network, Visualizer
#from authormaps.sharedwork import APInterface 

from authormaps.network import Network, Visualizer
from authormaps.sharedwork import ApiInterface 


# Define constants
app = Flask(__name__)
app.secret_key = "group2secretkey"
app.config['MAX_CONTENT_PATH'] = 10 * 1024 * 1024  # Max 10MB

@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """convert a datetime to a different format."""
    return value.strftime(format)


app.jinja_env.filters['datetimefilter'] = datetimefilter


@app.route("/")
def home():
    return render_template('home.html', current_time=datetime.datetime.now())

@app.route('/getauthornetwork', methods=['GET', 'POST'])
def getauthornetwork():
    if request.method == 'POST':
        # get author's name
        author = request.form['search']
        if any(invalid_char in author for invalid_char in list('@€µ*+~!"§$%&/()=?`,´#;:_<>|^°ßüÜäÄöÖ')):
            error_msg = 'invalid_char'
            return render_template('somethingwentwrong.html', error_msg=error_msg)
        else:
            author = author.strip().split(' ')
            if len(author) == 1:
                error_msg = 'only_first_name'
                return render_template('somethingwentwrong.html', error_msg=error_msg)
            elif len(author) == 2:
                first_name = author[0]
                last_name = author[1]
                full_name = ' '.join([first_name, last_name])
            elif len(author) > 2:
                first_name = ' '.join(author[0:-1])
                last_name = author[-1]
                full_name = ' '.join([first_name + last_name]) 
        
        # reduplicated names check
        if last_name == first_name:
            error_msg = 'reduplicated_name'
            return render_template('somethingwentwrong.html', error_msg=error_msg)
        session['first_name'] = first_name
        session['last_name'] = last_name

        # Initialize number of shared publications as None 
        num_shared_pub = 'None'
        
        # Initialize / refresh status code and status data
        status_code = None
        status_data = None


        # get list of coauthors via backend methods        
        api_interface = ApiInterface(firstname=first_name, lastname=last_name)
        
        # Call backend and catch status code 
        api_interface.make_dataframe()
        print(api_interface.messagefrontend)
        
        status_code, status_data = api_interface.messagefrontend
        # Check for bad status code:
        if status_code != 700:
            if status_code == 400: 
                pass
            elif status_code == 701: 
                # No publications found for this author
                return render_template('nopublicationsfound.html', first_name=first_name, last_name=last_name)
            elif status_code == 702: 
                # Author not found by API
                return render_template('authornotfound.html', first_name=first_name, last_name=last_name)
            elif status_code == 704: 
                # Author not found but similiar authors were found
                return render_template('authornotfoundbutsimiliar.html', first_name=first_name, last_name=last_name, similiar_authors=status_data)
            elif status_code == 705: 
                # Over a thousand publications were found
                return render_template('overthousandpublications.html', first_name=first_name, last_name=last_name)
           
        # Get list of co-authors
        coauthors = []
        for coauthor in api_interface.nodelistunique:
            split_coauthor = coauthor.split(' ')
            co_last_name = split_coauthor[0]
            co_first_and_middle = ' '.join(split_coauthor[1:])
            full_coauthor_name = ' '.join([co_first_and_middle, co_last_name])
            coauthors.append(full_coauthor_name)
        print(sorted(coauthors))
        coauthors = sorted(coauthors)
        # create network and create graph_image
        visualizer = Visualizer(first_name=first_name, last_name=last_name)
        visualizer.generate_graph_image(graph_output_path = str(Path(__file__).parent.resolve() / 'static/images/authormap_plot.png'), with_edge_labels = False, dpi=300)

        if status_code == 703: # Author was found and also similar authors
            print(status_data)
            return render_template('authormap.html', first_name=first_name, last_name=last_name, coauthors=coauthors, similiar_authors=status_data, num_shared_pub=num_shared_pub, current_time=datetime.datetime.now())

        # render results page
        return render_template('authormap.html', first_name=first_name, last_name=last_name, coauthors=coauthors, similiar_authors=None, num_shared_pub=num_shared_pub, current_time=datetime.datetime.now())


@app.route('/getsharedpublications', methods=['GET'])
def get_num_shared_publications():
    # get author1 and author2 from the javascript call
    author1 = request.args.get('author1')
    author2 = request.args.get('author2')
    
    
    # get number of shared publications between checked authors 
    network = Network(first_name=session['first_name'], last_name=session['last_name'])
    num_shared_pub = network.get_shared_publication(author1, author2)
    
    # write to json (retrieved by AJAX GET call)
    json = jsonify(num_shared_pub=num_shared_pub)
    return jsonify(num_shared_pub=num_shared_pub)


@app.route("/downloadauthormap", methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        # Get filetype, first name and last name
        filetype, first_name, last_name  = request.form['downloadformat'].split(',')
        
        # Initialize Visualizer() and generate graph image with filetype 
        visualizer = Visualizer(first_name = first_name, last_name=last_name)
        visualizer.generate_graph_image(graph_output_path = str(Path(__file__).parent.resolve() / f'static/images/authormap_plot.{filetype}'), with_edge_labels = False, dpi=300)
        return send_file(f'static/images/authormap_plot.{filetype}', attachment_filename=f'authormap_plot.{filetype}', as_attachment=True)

@app.route("/about")
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('FLASK_PORT', 8080))
