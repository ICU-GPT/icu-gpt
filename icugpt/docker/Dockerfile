FROM python:3.11
WORKDIR /icu
RUN pip install https://github.com/ICU-GPT/icu-gpt.git
COPY webdemo.py /icu/
ENTRYPOINT python3 webdemo.py