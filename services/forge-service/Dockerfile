# ty: https://github.com/mamba-org/micromamba-docker

ARG MAMBA_CONFIG=environment.yml
ARG MAMBA_DOCKERFILE_ACTIVATE=1
ARG MAMBA_VERSION=latest

# --- Build / Environment Setup Stage ---
FROM mambaorg/micromamba:${MAMBA_VERSION} AS env_build

ARG MAMBA_CONFIG
ARG MAMBA_VERSION
ARG MAMBA_DOCKERFILE_ACTIVATE

# Report mamba version
RUN echo "Building with version: ${MAMBA_VERSION}"

# Copy environment file
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
COPY app/ ./app/

# Install dependencies into the default prefix
RUN micromamba install -y -n base -f /tmp/environment.yml && \
    micromamba clean --all --yes

# --- Final Production Stage ---
FROM mambaorg/micromamba:${MAMBA_VERSION}

ARG MAMBA_DOCKERFILE_ACTIVATE

# Copy the environment from the build stage
COPY --from=env_build --chown=$MAMBA_USER:$MAMBA_USER /opt/conda /opt/conda

WORKDIR /workspace
COPY --chown=$MAMBA_USER:$MAMBA_USER . .

EXPOSE 8000

# Ensure the micromamba environment is automatically activated for the command
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]

# Run Gunicorn with Uvicorn workers
CMD ["gunicorn", "-c", "app/gunicorn.conf.py", "app.main:app"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD ["bash", "-c", "curl -f http://localhost:8000/healthz || exit 1"]
