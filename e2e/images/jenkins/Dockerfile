FROM jenkins/jenkins:lts-jdk11

# Avoid GUI setup wizard
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false

# Indicate path to configuration file
ENV CASC_JENKINS_CONFIG /var/jenkins_home/casc.yaml

# Install plugins
RUN jenkins-plugin-cli --plugins configuration-as-code

# Load Jenkin's configuration
COPY setup.yaml /var/jenkins_home/casc.yaml
