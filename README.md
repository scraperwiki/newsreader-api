# Local install:
* `git clone git@bitbucket.org:scraperwikids/newsreader_api_flask_app.git`
* Work on a virtualenv (optional)
* `pip install -r requirements.txt`
* `python run.py`

App accessible via http://127.0.0.1:5000

You'll need the username and password for the endpoint and have to store
these in the environment variables: NEWSREADER_USERNAME and
NEWSREADER_PASSWORD. (The deployed version has these setup already.)

# Example query usage:

## Simple query:
`http://127.0.0.1:5000/EntitiesThatAreActorsQuery`

## Access pages directly with /page/<page_number>:
`http://127.0.0.1:5000/EntitiesThatAreActorsQuery/page/2`

## Pass in URIs with query string value:
**URI format may change; may use `jsonurl` package to make nicer.**

`https://newsreader.scraperwiki.com/SynerscopeQuery?uris=["<http://dbpedia.org/resource/David_Beckham>"]`

## Query that outputs JSON instead of HTML:
Use `output="json"` (the requirement for quotes around strings is a known
issue; again should be fixable with `jsonurl`)

`https://newsreader.scraperwiki.com/SynerscopeQuery?output="json"&uris=["<http://dbpedia.org/resource/David_Beckham>"]`

# Adding a new query:
In `queries.py`, specify a new subclass of SparqlQuery

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
        self.jinja_template = 'your_new_query.html'
    
    def _build_query(self):
        # use {uri_0}, {offset} etc in your query template
        # add all named strings you specify to the format call
        # uris is a list of uris passed in by the query string
        return self.query_template.format(offset=self.offset,
                                          limit=self.limit,
                                          uri_0 = self.uris[0],
                                          uri_1 = self.uris[1])
                                         
        
    def parse_query_results(self):
        """ Returns nicely parsed values to pass into jinja_template """
        # do things to the JSON to get the data you want out
        return data_that_can_be_handled_in_template

    def _build_count_query(self):
        return self.count_template.format(uri_0=self.uris[0],
                                          uri_1=self.uris[1])
    
    def get_total_result_count(self):
        # Probably could be moved into parent class; same everytime
        count_query = CountQuery(self._build_count_query())
        return count_query.get_count()
```
