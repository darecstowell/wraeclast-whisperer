FROM condaforge/mambaforge:24.9.2-0
WORKDIR /usr/src/app

COPY environment.yaml .
RUN mamba env update --file environment.yaml \
    && mamba clean --all -yf

COPY pyproject.toml .
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction \
    && poetry cache clear pypi --all

COPY . .
