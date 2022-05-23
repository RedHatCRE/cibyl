FROM python:3.6.15

ARG CIBYL_ROOT=.
ARG CONFIG_FILE=$CIBYL_ROOT/samples/sample-config.yaml
ARG INSTALL_PATH=/app

# Prepare virtual environment
ENV VIRTUAL_ENV=$INSTALL_PATH/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip3 install --upgrade pip

WORKDIR $INSTALL_PATH

# Install dependencies
COPY $CIBYL_ROOT/requirements.txt .
RUN pip3 install -r requirements.txt

# Install Cibyl
COPY $CIBYL_ROOT/setup.py .
COPY $CIBYL_ROOT/cibyl ./cibyl
RUN pip3 install .

# Install configuration file
COPY $CONFIG_FILE /etc/cibyl/cibyl.yaml
