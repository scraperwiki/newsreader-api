run:    build
	@docker run \
	    -p 127.0.0.1:8000:8000 \
	    -e NEWSREADER_USERNAME \
	    -e NEWSREADER_PASSWORD \
	    -e NEWSREADER_API_KEY \
	    --rm newsreader_api_flask_app

build:
	@docker build -t newsreader_api_flask_app .

.PHONY: run build
