
include .env

build: 
	docker build -t bom_bot .

run:
	docker run \
	--network=host \
	-e TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN} \
	-v $(shell pwd)/app/:/app/ \
	bom_bot \
	python3 app.py


test:
	docker run \
	--network=host \
	-e TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN} \
	-v $(shell pwd)/app/:/app/ \
	bom_bot \
	 python -m unittest discover  -p '*_test.py'