# ---------- Services ----------

all:
	$(MAKE) -j3 opensearch server fe

server:
	uv run server.py

opensearch:
	./opensearch.sh

fe:
	cd frontend && npm run dev


# ---------- Development ----------

format:
	$(MAKE) formatb formatf

formatb:
	uvx ruff format .
	uvx ruff check . --fix

formatf:
	cd frontend && npm run format

clean:
	rm imessage_last_timestamp.txt
	docker stop ark_opensearch
	docker rm ark_opensearch
	docker volume rm opensearch_data
