FROM condaforge/mambaforge:24.9.2-0
WORKDIR /usr/src/app

# Install poetry and binaries
COPY environment.yaml .
RUN mamba env update --file environment.yaml \
    && mamba clean --all -yf

# Install python dependencies
COPY pyproject.toml .
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction \
    && poetry cache clear pypi --all

# Install playwright
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Chicago
RUN playwright install-deps \
    && playwright install

# Copy the rest of the files
COPY . .
   
# Set the environment variables
ENV PYTHONPATH=/usr/src/app
ENV CHAINLIT_HOST=0.0.0.0 
ENV CHAINLIT_PORT=8080

# Run the app
CMD ["python", "-m", "chainlit", "run", "app/main.py"]
