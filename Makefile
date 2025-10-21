format:
	uvx ruff format .
	uvx ruff check . --fix

opensearch:
	./opensearch.sh

dev_clean:
	rm imessage_last_timestamp.txt
	docker stop ark_opensearch
	docker rm ark_opensearch
	docker volume rm opensearch_data
