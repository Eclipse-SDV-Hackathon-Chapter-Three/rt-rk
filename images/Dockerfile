ank -k run workload \
helloworld \
--runtime podman \
--agent Agent2 \
--config 'image: docker.io/busybox:1.36
commandOptions: [ "-e", "MESSAGE=Hello World"]
commandArgs: [ "sh", "-c", "echo $MESSAGE"]'