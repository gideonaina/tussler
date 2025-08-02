FROM jupyter/base-notebook:latest

# switch to root so we can mkdir + chown
USER root

RUN mkdir -p /home/jovyan/work \
    && chown -R jovyan:users /home/jovyan/work

# go back to the jovyan user
USER jovyan

# make that the working dir
WORKDIR /home/jovyan/work

# EXPOSE 8888

# ensure Jupyter starts there
CMD ["start-notebook.sh", "--ServerApp.root_dir=/home/jovyan/work"]
