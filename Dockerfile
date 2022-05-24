FROM python:3.6.15

# Outside the container
ARG CIBYL_ROOT=.
ARG CONFIG_FILE=$CIBYL_ROOT/samples/sample-config.yaml

# Inside the container
ARG INSTALL_PATH=/app

# == Install APP ==
WORKDIR $INSTALL_PATH

# Prepare virtual environment
ENV VIRTUAL_ENV=./venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip3 install --upgrade pip

# Install dependencies
COPY $CIBYL_ROOT/requirements.txt .
RUN pip3 install -r requirements.txt

# Install Cibyl
COPY $CIBYL_ROOT/setup.py .
COPY $CIBYL_ROOT/cibyl ./cibyl
RUN pip3 install .

# Install configuration file
COPY $CONFIG_FILE /etc/cibyl/cibyl.yaml
