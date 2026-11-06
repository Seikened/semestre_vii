FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr-spa tesseract-ocr-eng libglib2.0-0 libgl1 libgomp1 \
    && apt-get clean
WORKDIR /proyecto
COPY backend/pyproject.toml backend/uv.lock ./backend/
RUN uv sync --project backend --frozen --no-dev --no-install-project
COPY backend/app ./backend/app
RUN uv sync --project backend --frozen --no-dev
COPY demo ./demo
ENV MOTOR_OCR=tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
ENV PATH="/proyecto/backend/.venv/bin:$PATH"
ENV OMP_NUM_THREADS=2
ENV TOKENIZERS_PARALLELISM=false
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
