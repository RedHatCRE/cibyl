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
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install wheel

# Install Cibyl
COPY $CIBYL_ROOT/.git ./.git

COPY $CIBYL_ROOT/README.rst .
COPY $CIBYL_ROOT/setup.py .
COPY $CIBYL_ROOT/setup.cfg .
COPY $CIBYL_ROOT/requirements.txt .

COPY $CIBYL_ROOT/cibyl ./cibyl
COPY $CIBYL_ROOT/tripleo ./tripleo

RUN python3 -m pip install .

# Install configuration file
COPY $CONFIG_FILE /etc/cibyl/cibyl.yaml
