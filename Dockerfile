FROM python:3.12.7

WORKDIR /reduce_img

COPY requirement.txt .
RUN pip install --upgrade pip
RUN pip install -r requirement.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host 0.0.0.0"]