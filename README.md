sudo chmod 666 /var/run/docker.sock 
make docker.build   

docker run --rm -d -p 32768:8080 -v "${PWD}/searxng:/etc/searxng" -e "BASE_URL=http://localhost:$PORT/" -e "INSTANCE_NAME=my-instance" searxng/searxng

http://localhost:32768
