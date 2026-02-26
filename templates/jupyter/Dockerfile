FROM jupyter/minimal-notebook:python-3.11

USER root

# Install Python packages needed for ETL labs
RUN pip install --no-cache-dir \
    sqlalchemy==2.0.41 \
    psycopg2-binary==2.9.10 \
    pandas==2.2.3 \
    ipython-sql==0.5.0

USER ${NB_UID}

# Disable the "Would you like to receive official Jupyter news?" popup
RUN mkdir -p /opt/conda/share/jupyter/lab/settings && \
    echo '{ "@jupyterlab/apputils-extension:notification": { "fetchNews": "false", "checkForUpdates": false } }' \
    > /opt/conda/share/jupyter/lab/settings/overrides.json

# Widen the file browser sidebar so full filenames are readable.
# Append a <style> tag to JupyterLab's index.html — works across all versions.
RUN sed -i 's|</head>|<style>#jp-left-stack{min-width:330px!important}</style></head>|' \
    /opt/conda/share/jupyter/lab/static/index.html

# Set working directory to the mounted workspace
WORKDIR /home/jovyan/work
