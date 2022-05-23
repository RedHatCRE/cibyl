FROM python:3.6.15

WORKDIR /

# Prepare virtual environment
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip3 install --upgrade pip

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Install Cibyl
COPY ./setup.py .
COPY ./cibyl ./cibyl
RUN pip3 install .

WORKDIR /etc/cibyl

# Install configuration file
COPY ./samples/sample-config.yaml ./cibyl.yaml
