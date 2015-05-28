all: generated/newsreader.json \

generated/newsreader.json: build generate.py newsreader-user-data.yml
	@mkdir -p generated
	@docker run \
		--volume $$PWD/generate.py:/code/generate.py \
		--volume $$PWD/newsreader-user-data.yml:/code/newsreader-user-data.yml \
	        --rm \
		newsreader-pypy > generated/newsreader.json
	@echo Built generated/\*.json

build: .FORCE
	@docker build -t newsreader-pypy .

.PHONY: all .FORCE
.FORCE:
