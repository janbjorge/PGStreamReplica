ARG POSTGRES_VERSION
FROM postgres:${POSTGRES_VERSION}
ENV POSTGRES_USER=testuser
ENV POSTGRES_PASSWORD=testpassword
ENV POSTGRES_HOST_AUTH_METHOD=trust

# Copy the combined database setup script into the container
COPY ./init_db.sh /docker-entrypoint-initdb.d/init_db.sh

# Ensure the script is executable
RUN chmod +x /docker-entrypoint-initdb.d/init_db.sh
CMD ["postgres", "-c", "wal_level=logical", "-c", "max_wal_senders=10", "-c", "max_replication_slots=10"]
