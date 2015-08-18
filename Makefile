run:    build
	@docker run \
	    -p 127.0.0.1:8000:8000 \
	    -e NEWSREADER_PUBLIC_USERNAME \
	    -e NEWSREADER_PUBLIC_PASSWORD \
	    -e NEWSREADER_PRIVATE_USERNAME \
	    -e NEWSREADER_PRIVATE_PASSWORD \
	    -e NEWSREADER_PUBLIC_API_KEY \
	    -e NEWSREADER_PRIVATE_API_KEY \
	    --read-only \
	    --rm \
	    --volume /tmp \
	    newsreader_api

build:
	@docker build -t newsreader_api .

.PHONY: run build
