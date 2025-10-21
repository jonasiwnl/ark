docker run \
    # -d \
    --name ark_opensearch \
    # --restart unless-stopped \
    -p 127.0.0.1:9200:9200 \
    -e "discovery.type=single-node" \
    # TODO: security
    -e "DISABLE_SECURITY_PLUGIN=true" \
    -e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" \
    -v opensearch_data:/usr/share/opensearch/data \
    opensearchproject/opensearch:3.3.0
