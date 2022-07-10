FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip wheel setuptools && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "bot.py" ]