## Table of contents

* [For Simple API users](#markdown-header-simple-api-users)
* [Local install](#markdown-header-local-install)
* [Running tests](#markdown-header-running-tests)
* [Adding a new query](#markdown-header-adding-a-new-query)
* [Adding a new KnowledgeStore](#markdown-header-adding-a-new-knowledgestore)

## Simple API Users

This API was built to access data in [KnowledgeStores](https://knowledgestore2.fbk.eu/) created by analysing
news articles as part of the [NewsReader Project](http://www.newsreader-project.eu/). Within the project we refer to this as the Simple API. The index page of the 
API provides detailed information on the available queries. An example index page can be found at [https://newsreader.scraperwiki.com/](https://newsreader.scraperwiki.com/).

The Simple API has been used at Hack Days run as part of the NewsReader Project, a bundle of links providing additional information can be found [here](http://tab.bz/ydtco/).

## Local install
* `git clone git@bitbucket.org:scraperwikids/newsreader_api_flask_app.git`
* Work on a virtualenv (optional)
* `pip install -r requirements.txt`
* `python local_run.py`

App accessible via http://127.0.0.1:5000, which also shows up-to-date
documentation.

You'll need the username and password for the endpoint and have to store
these in the environment variables: NEWSREADER_USERNAME and
NEWSREADER_PASSWORD. (The deployed version has these setup already.)
This can be done by adding lines like:

* `export NEWSREADER_USERNAME=[username]`
* `export NEWSREADER_PASSWORD=[password]`

To your `.profile` file (in Linux).

`newsreader.fcgi` is a FastCGI server file for deployment.

## Running tests

This will run all available tests, a number of which will fail because they are dependent on a particular KnowledgeStore containing World Cup data:

`> nosetests -v`

This will run tests of queries which are not dependent on a KnowledgeStore

`>  nosetests -v app/test_queries.py`

This will run generic tests of queries which are not strongly dependent on the underlying KnowledgeStore but may require tweaking:

`> nosetests -v app/test_generics.py`

Moving from World Cup to Cars datasets required modifications of `test_visit_a_non_existent_page()` and `test_visit_a_page_beyond_the_offset_limit()` only

## Adding a new query
In the queries subdirectory specify a new subclass of `SparqlQuery` in a file of its own.
The main action should be in adding the queries. { and } in the original need to be escaped to
{{ and }}. Once the query has been created add a line like:

`from .types_of_actors import types_of_actors`

to `__init.py__` and add an entry to `function_list` in `index` in the`queries.py` file 

## Adding a new KnowledgeStore

To get a new endpoint "new_topic" to work in future:

add a class to `make_documentation` that's copy-pasted from the existing `WorldCupDocsCreator` and replace `query_object.world_cup_example` with `query_object.new_topic_example`;
add a `query_object.new_topic_example` to every query. Alternatively, do this in your `NewTopicDocsCreator`:
```Python
try:
    return query_object.new_topic_example
except AttributeError:
    return query_object.world_cup_example
```
copy-paste the existing `cars_index()` in `views.py` and replace cars with `new_topic` throughout it, including replacing `CarsDocsCreator` with `NewTopicDocsCreator`;
add the endpoint path name to our server routes, e.g. /new_topic and the URL of the SPARQL endpoint to `get_endpoint_url()` as it already exists for cars and world_cup, in a conditional.