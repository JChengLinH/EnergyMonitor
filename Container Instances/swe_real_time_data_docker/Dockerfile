FROM python:3.9

ADD real_time_prod_data_main.py .
ADD real_time_prod_data.py .
ADD creds.env .


# RUN pip install --upgrade virtualenv
RUN pip install selenium azure-storage-blob python-dotenv

RUN curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub |\
apt-key add - && echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' |\
 tee /etc/apt/sources.list.d/google-chrome.list && apt-get update && apt-get install -y google-chrome-stable

RUN apt-get install -yqq unzip curl
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

CMD [ "python", "./real_time_prod_data_main.py" ]

