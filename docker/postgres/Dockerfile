FROM postgres:14-alpine

# Install pgvector
RUN apk update && \
    apk add --no-cache postgresql-dev gcc g++ make git && \
    git clone https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    cd .. && \
    rm -rf pgvector