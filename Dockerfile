FROM alpine:latest

WORKDIR /app

COPY . .

RUN apk add --no-cache python3 py3-pip && \
    pip3 install --no-cache-dir -r requirements.txt

EXPOSE 53

CMD ["python3", "srv.py"]