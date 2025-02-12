# importing base image
FROM ubuntu:22.04

# security updates and installing system dependencies
RUN /bin/bash -c "set -euo pipefail \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get -y upgrade \
    && apt install -y git --no-install-recommends \
    && apt install wget --no-install-recommends \
    && apt-get install apt-transport-https curl gnupg -yqq \
    && apt install openssh-server -y --no-install-recommends \
    && apt-get install -y openjdk-8-jdk --no-install-recommends \
    && apt-get install -y openjdk-17-jdk --no-install-recommends \
    && apt install -y python3.10-venv --no-install-recommends \
    && apt install -y nodejs --no-install-recommends \
    && apt install -y npm --no-install-recommends \
    && echo 'deb https://repo.scala-sbt.org/scalasbt/debian all main' | tee /etc/apt/sources.list.d/sbt.list \
    && echo 'deb https://repo.scala-sbt.org/scalasbt/debian /' | tee /etc/apt/sources.list.d/sbt_old.list \
    && curl -sL 'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823' | gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/scalasbt-release.gpg --import \
    && chmod 644 /etc/apt/trusted.gpg.d/scalasbt-release.gpg \
    && apt-get update \
    && apt-get install sbt \
    && rm -rf /var/lib/apt/lists/*"

# installing maven and adding it to the path
RUN wget --no-verbose -O /tmp/apache-maven-3.9.6-bin.tar.gz https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz && \
    tar xzf /tmp/apache-maven-3.9.6-bin.tar.gz -C /opt/ && \
    ln -s /opt/apache-maven-3.9.6 /opt/maven && \
    ln -s /opt/maven/bin/mvn /usr/local/bin  && \
    rm -f /tmp/apache-maven-3.9.6-bin.tar.gz

ENV MAVEN_HOME /opt/maven

# setting up the default java version for this container
RUN update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java

# installing yarrrml
RUN npm i @rmlio/yarrrml-parser -g

# creating dedicated user to avoid running container as a root
RUN useradd --create-home pipelines_user

WORKDIR /home/pipelines_user

USER pipelines_user

# creating .ssh directory and a file that will store fingerprints
RUN cd ~ \
    && mkdir .ssh \
    && cd .ssh \
    && touch known_hosts

ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64/

# cloning rmlmapper tool repository and setting up directories
RUN mkdir -p src \
    && cd src \
    && git clone --branch v7.0.0 https://github.com/RMLio/rmlmapper-java.git \
    && mkdir -p utils/rmlmapper/ \
    && mv rmlmapper-java/* utils/rmlmapper/ \
    && rm -rf rmlmapper-java/

# building rmlmapper jar using maven
RUN cd src/utils/rmlmapper \
    && mvn install -DskipTests

ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/jre/

# copying rdfconvert-binaries repository and setting up directories
RUN cd src \
    && git clone --branch main https://gitlab.pcss.pl/daisd-public/dpi-pipelines/rdfconvert-0.4-binaries.git \
    && mkdir -p utils/rdfconvert/ \
    && mv rdfconvert-0.4-binaries/* utils/rdfconvert/ \
    && rm -rf rdfconvert-0.4-binaries/

# copying geotriples-binaries repository and setting up directories
RUN cd src \
    && git clone --branch master https://gitlab.pcss.pl/daisd-public/dpi-pipelines/geotriples-binaries.git \
    && mkdir -p utils/GeoTriples/ \ 
    && mv geotriples-binaries/* utils/GeoTriples/ \
    && rm -rf geotriples-binaries/

# install and build tarql
RUN cd src/utils \
    && git clone --branch master https://github.com/cygri/tarql \
    && cd tarql \
    && mvn clean install -DskipTests

# install and build silk
RUN cd src/utils \
    && git clone --branch v3.5.0 https://github.com/silk-framework/silk.git \
    && cd silk \
    && sbt "project singlemachine" assembly

# installing csv2rdf
RUN wget --no-verbose -O /tmp/csv2rdf-linux.tar.gz https://github.com/Swirrl/csv2rdf/releases/download/v0.7.0/csv2rdf-linux.tar.gz && \
    tar xzf /tmp/csv2rdf-linux.tar.gz && \
    mkdir -p src/utils/csv2rdf && \
    mv csv2rdf src/utils/csv2rdf/ && \
    rm -f /tmp/csv2rdf-linux.tar.gz

# copying repository content into a src folder
RUN git clone --branch master https://gitlab.pcss.pl/daisd-public/dpi-pipelines/pipelines.git \ 
    && mkdir -p src \
    && mv pipelines/* src/ \
    && rm -rf pipelines/

# create virtual environment and install dependencies
RUN /bin/bash -c "python3 -m venv pipelines \
    && source pipelines/bin/activate \
    && cd src \
    && pip install -r requirements.txt"

ENTRYPOINT [ "/bin/bash" ]
