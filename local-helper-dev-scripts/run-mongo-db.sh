docker container kill local-db
docker network rm db-local-network
docker container prune -f
docker network create db-local-network
docker run -p 27017:27017 --name local-db mongo > /dev/null &
sleep 10
docker network connect --alias db db-local-network local-db
echo "Done"