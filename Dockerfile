FROM ubuntu:latest
LABEL authors="glebfadeev"

ENTRYPOINT ["top", "-b"]