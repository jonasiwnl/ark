#!/bin/bash

colima start

# -d \
# --restart unless-stopped \
# TODO: security
docker run \
    --name ark_opensearch \
    -p 127.0.0.1:9200:9200 \
    -e "discovery.type=single-node" \
    -e "DISABLE_SECURITY_PLUGIN=true" \
    -e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" \
    -v opensearch_data:/usr/share/opensearch/data \
    opensearchproject/opensearch:3.3.0
