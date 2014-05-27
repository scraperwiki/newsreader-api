# Local install:
* `git clone git@bitbucket.org:scraperwikids/newsreader_api_flask_app.git`
* Work on a virtualenv (optional)
* `pip install -r requirements.txt`
* `python run.py`

App accessible via http://127.0.0.1:5000, which also shows up-to-date documentation

You'll need the username and password for the endpoint and have to store
these in the environment variables: NEWSREADER_USERNAME and
NEWSREADER_PASSWORD. (The deployed version has these setup already.)

# Example query usage:

## Simple query:
`/types_of_actors`

## Access pages directly with /page/<page_number>:
`http://127.0.0.1:5000/page/2/types_of_actors`

## Pass in URIs with query string value:
** WARNING: may change again if I move from `jsonurl`
to handling with Flask **
`https://newsreader.scraperwiki.com/Gevent_details_filtered_by_actor?uris.0=http://dbpedia.org/resource/David_Beckham`

Specify additional URIs with e.g.
`?uris.0=http://dbpedia.org/resource/David_Beckham&uris.1=http://dbpedia.org/resource/Bobby_Robson`

## Query that outputs JSON instead of HTML:
Use `output=json` 

`https://newsreader.scraperwiki.com/event_details_filtered_by_actor?output=json&uris.0=http://dbpedia.org/resource/David_Beckham`

# Adding a new query:
In `queries.py`, specify a new subclass of `SparqlQuery`

```
class YourNewQuery(SparqlQuery):
    def __init__(self, *args, **kwargs):
        super(YourNewQuery).__init__(*args, **kwargs)
        self.query_title = 'HTML page title for YourNewQuery'
        
        # query (and count) template may contain variable strings
        # that are injected by format in _build_query(),
        # _build_count_query()
        self.query_template = 'Your SPARQL query goes here'
        self.query = self._build_query()
        
        self.count_template = 'Your counting query goes here'
        
        # Jinja templates stored in app/templates
        # You should be able to use the generic two_column.html etc
        self.jinja_template = 'your_new_query.html'
    
        self.headers = ['actor', 'actor2']
        self.required_parameters = ["uris"]
        self.optional_parameters = ["output", "offset", "limit"]
        self.number_of_uris_required = 1

        self.query = self._build_query()

    def _build_query(self):
        # use {uri_0}, {offset} etc in your query template
        # add all named strings you specify to the format call
        # uris is a list of uris passed in by the query string
        return self.query_template.format(offset=self.offset,
                                          limit=self.limit,
                                          uri_0 = self.uris[0],
                                          uri_1 = self.uris[1])
                                         
    def _build_count_query(self):
        return self.count_template.format(uri_0=self.uris[0],
                                          uri_1=self.uris[1])
    
```
