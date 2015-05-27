run:    build
	@docker run \
	    -p 127.0.0.1:8000:8000 \
	    -e NEWSREADER_USERNAME \
	    -e NEWSREADER_PASSWORD \
	    -e NEWSREADER_SIMPLE_API_KEY \
	    --read-only \
	    --rm \
	    --volume /tmp \
	    newsreader_api

build:
	@docker build -t newsreader_api .

.PHONY: run build
