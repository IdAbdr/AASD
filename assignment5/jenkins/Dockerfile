FROM docker:28-cli AS dockercli
FROM jenkins/jenkins:lts-jdk21
USER root
COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=dockercli /usr/local/libexec/docker/cli-plugins /usr/local/libexec/docker/cli-plugins
COPY init.groovy /usr/share/jenkins/ref/init.groovy.d/01-public-url.groovy
USER jenkins
RUN jenkins-plugin-cli --plugins workflow-aggregator git junit pipeline-stage-view timestamper
