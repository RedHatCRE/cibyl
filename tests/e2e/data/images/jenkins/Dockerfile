FROM jenkins/jenkins:lts-jdk11

# Define environmental conditions
ENV JAVA_OPTS \
    # Avoid GUI setup wizard
    -Djenkins.install.runSetupWizard=false \
    # Allow unsecure POST commands
    -Dhudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION=true

# Indicate path to configuration file
ENV CASC_JENKINS_CONFIG /var/jenkins_home/casc.yaml

# Install plugins
RUN jenkins-plugin-cli --plugins configuration-as-code

# Load Jenkin's configuration
COPY ./setup.yaml /var/jenkins_home/casc.yaml
