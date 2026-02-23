FROM jupyter/minimal-notebook:latest

USER root

# Install Python packages needed for ETL labs
RUN pip install --no-cache-dir \
    sqlalchemy==2.0.41 \
    psycopg2-binary==2.9.10 \
    pandas==2.2.3 \
    ipython-sql==0.5.0

USER ${NB_UID}

# Set working directory to the mounted workspace
WORKDIR /home/jovyan/work
