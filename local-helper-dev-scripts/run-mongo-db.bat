call docker network rm db-local-network
call docker container kill local-db
call docker container prune -f
call docker network create db-local-network
start docker run -p 27017:27017 --name local-db mongo
call timeout 4
call docker network connect --alias db db-local-network local-db