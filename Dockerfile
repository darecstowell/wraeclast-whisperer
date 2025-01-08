FROM condaforge/mambaforge:24.9.2-0
WORKDIR /usr/src/app

# Install poetry and binaries
COPY environment.yaml .
RUN mamba env update --file environment.yaml \
    && mamba clean --all -yf

# Install python dependencies
COPY pyproject.toml .
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root \
    && poetry cache clear pypi --all

# Install playwright and cleanup
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=America/Chicago
RUN playwright install-deps \
    && playwright install \
    && rm -rf /root/.cache/ms-playwright \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the files
COPY . .
   
# Set the environment variables
ENV PYTHONPATH=/usr/src/app
ENV CHAINLIT_HOST=0.0.0.0 
ENV CHAINLIT_PORT=8080

# Run the app
# When developing, comment this out and run the app manually using `docker exec ww bash; chainlit run app/main.py -w`
CMD ["python", "-m", "chainlit", "run", "app/main.py"]
# CMD ["sleep", "infinity"]
