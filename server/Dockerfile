FROM python:3

RUN apt update

ADD http://archive.ubuntu.com/ubuntu/pool/universe/p/pstotext/pstotext_1.9-6build1_amd64.deb pstotext_1.9-6build1_amd64.deb
RUN apt install -y ./pstotext_1.9-6build1_amd64.deb

RUN apt install -y \
  python-dev \
  libxml2-dev \
  libxslt1-dev \
  antiword \
  unrtf \
  poppler-utils \
  tesseract-ocr \
  flac \
  ffmpeg \
  lame \
  libmad0 \
  libsox-fmt-mp3 \
  sox \
  libjpeg-dev \
  swig \
  libpulse-dev
RUN apt clean

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "run"]
