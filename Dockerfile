# Builder stage
FROM python:3.10-slim as builder

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.10-slim-buster

WORKDIR /usr/src/app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 5001

COPY entrypoint.sh /usr/src/app/
RUN chmod +x /usr/src/app/entrypoint.sh
CMD ["/usr/src/app/entrypoint.sh"]
