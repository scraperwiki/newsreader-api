## Table of contents

* [For Simple API users](#markdown-header-simple-api-users)
* [Local install](#markdown-header-local-install)
* [Deployment] (#markdown-header-deployment---warning)
* [Running tests](#markdown-header-running-tests)
* [Adding a new query](#markdown-header-adding-a-new-query)
* [Adding a new KnowledgeStore](#markdown-header-adding-a-new-knowledgestore)

## Simple API Users

This API was built to access data in [KnowledgeStores](https://knowledgestore2.fbk.eu/) created by analysing
news articles as part of the [NewsReader Project](http://www.newsreader-project.eu/). Within the project we refer to this as the Simple API. The index page of the 
API provides detailed information on the available queries. An example index page can be found at [https://newsreader.scraperwiki.com/](https://newsreader.scraperwiki.com/).

The Simple API has been used at Hack Days run as part of the NewsReader Project, a bundle of links providing additional information can be found [here](http://tab.bz/ydtco/).

The Simple API uses an API key for authentication; please contact dataservices@scraperwiki.com for an API key.

## Local install

* `git clone git@github.com:scraperwiki/newsreader-api`

You'll need the username and password for the endpoint and you must store
these in the environment variables: `NEWSREADER_PUBLIC_USERNAME` and
`NEWSREADER_PUBLIC_PASSWORD`. (The deployed version has these setup already.).
You also need to define an `NEWSREADER_PUBLIC_API_KEY` for local development.

The public and private endpoints have been separated, so you also need
a set of environment variables for the private endpoint:

* `export NEWSREADER_PUBLIC_USERNAME=[public_username]`
* `export NEWSREADER_PUBLIC_PASSWORD=[public_password]`
* `export NEWSREADER_PUBLIC_API_KEY=[public_api_key]`
* `export NEWSREADER_PRIVATE_USERNAME=[private_username]`
* `export NEWSREADER_PRIVATE_PASSWORD=[private_password]`
* `export NEWSREADER_PRIVATE_API_KEY=[private_api_key]`

Multiple API keys for users can be specified in
`NEWSREADER_PUBLIC_API_KEY` and `NEWSREADER_PRIVATE_API_KEY`.
Confusingly, these should be **semicolon** separated if deploying via
`cfn.sh` but comma separated for local usage. (TODO: check and fix.)

### Running via Flask

* Work on a virtualenv (optional)
1. `pip install -r requirements.txt`
2. `python local_run.py`

App accessible via http://127.0.0.1:5000, which also shows up-to-date
documentation.

### Running via Docker

1. Do `make run`

App accessible via http://0.0.0.0:8000

## Deployment - WARNING!

The Simple API should automatically deploy to https://newsreader-dev.scraperwiki.com/ when 
code is merged onto the `dev` branch and it should automatically deploy to https://newsreader.scraperwiki.com/ when
code is merged onto the `master` branch. Deployment should only take a few minutes after merge, if it takes longer than
this then there is likely a problem. 

### Deploying via Amazon CloudFormation

The [`awscli`](https://aws.amazon.com/cli/) is required:

`pip install awscli`

In addition, you'll need AWS specific environment variables that you
can set by:

```sh
aws-env() { export AWS_DEFAULT_REGION=eu-west-1 AWS_REGION=eu-west-1 AWS_ACCESS_KEY_ID=$1 AWS_SECRET_ACCESS_KEY=$2; clear; }; aws-env <ID> <SECRET>
```

(The `<ID>` and `<SECRET>` are created by making a new Access Key on AWS
for a user. This option is found under "Manage Access Keys" on a user's
Security Credentials page for an AWS user.)

You'll need to set `NEWSREADER_VPC` and `NEWSREADER_SUBNET` environment
variables to match the VPC and subnet configuration you've set up on AWS
for Newsreader.

You'll also need the `HOOKBOT_MONITOR_URL` environment variable.
(**TODO: add details of how to generate this.**)

Once all that's done, you're set to actually deploy:

1. `cd ops`
2. `make build` (the first time or if you've deleted the PyPy Docker
   image)
3. `./cfn.sh create <stack name>`

`<stack name>` is for example `20150604-sm`; this shows up on the
CloudFormation Management Console as `newsreader-20150604-sm`.

If changing an existing stack, you can substitute `create` in 3 for
`update`.

#### Deploying master via CloudFormation

Provided hookbot is setup correctly, a push to master should
automatically cause the Docker container to pull the latest version from
GitHub, and switch to the new container if all is well.

## Running tests

This will run all available tests:

`> nosetests -v`

This will run tests of queries which are not dependent on a KnowledgeStore

`>  nosetests -v app/test_queries.py`

This will run generic tests of queries which are not strongly dependent on the underlying KnowledgeStore but may require tweaking:

`> nosetests -v app/test_generics.py`

Moving from World Cup to Cars datasets required modifications of `test_visit_a_non_existent_page()` and `test_visit_a_page_beyond_the_offset_limit()` only

This will run each of the example queries and test for the presence of the word "error" in the response:

`> nosetests -v app/test_integration.py`

## Adding a new query

In the queries subdirectory specify a new subclass of `SparqlQuery` in a file of its own.
The main action should be in adding the queries. { and } in the original need to be escaped to
{{ and }}. Once the query has been created add a line like:

`from .types_of_actors import types_of_actors`

to `__init.py__` and add an entry to `function_list` in `index` in the`queries.py` file.

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
add the endpoint path name to our server routes, e.g. /new_topic and the URL of the SPARQL endpoint to `get_endpoint_credentials()` as it already exists for cars and world_cup, in a conditional. Also update `validate_api_key()`
