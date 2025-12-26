FROM mcr.microsoft.com/devcontainers/python:3.14

# Install uv for dependency management during build
RUN pip install uv

# Copy dependency files for caching
COPY pyproject.toml uv.lock ./

# Install dependencies only (not the local project, since source isn't in container yet)
# The local project will be installed when the workspace is mounted
RUN uv sync --frozen --no-install-project

# Install Playwright browsers to a shared location accessible by all users
# The devcontainer runs as 'vscode' user, but Dockerfile runs as root
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN /.venv/bin/playwright install --with-deps && \
    chmod -R 755 /ms-playwright
