FROM python:3.7
ADD ./src/ /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python app.py