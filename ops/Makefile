all: generated/newsreader.json \

generated/newsreader.json: build generate.py
	@mkdir -p generated
	@docker run \
		--volume $$PWD/generate.py:/code/generate.py \
		--volume $$PWD/user-data/:/code/user-data \
		--rm \
		newsreader-pypy > generated/newsreader.json
	@echo Built generated/\*.json

build: .FORCE
	@docker build -t newsreader-pypy .

.PHONY: all .FORCE
.FORCE:
