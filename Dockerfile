FROM ubuntu:18.04

# Install dependencies
RUN apt-get -y update && apt-get install -y --no-install-recommends \
    wget ghostscript ffmpeg libsm6 libxext6 gnupg gnupg2 unzip gsfonts-x11 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Miniconda
ENV CONDA_DIR /opt/conda
RUN wget --no-check-certificate https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && chmod +x /tmp/miniconda.sh \
    && /tmp/miniconda.sh -b -p $CONDA_DIR \
    && rm /tmp/miniconda.sh
ENV PATH=$CONDA_DIR/bin:$PATH

# Copy environment.yml and set up Conda
COPY environment.yml environment.yml
RUN conda init bash && conda env create -f environment.yml

# Copy the key file from the host to the container
COPY docker-context/linux_signing_key.pub /tmp/linux_signing_key.pub

# Install Google Chrome
RUN echo "Adding Google Chrome GPG key" && \
    cat /tmp/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y --no-install-recommends google-chrome-stable


# Install curl
RUN apt-get update && apt-get install -y --no-install-recommends curl

# Install Chromedriver
RUN LATEST_CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget https://chromedriver.storage.googleapis.com/$LATEST_CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver

# Install xpdf tools
RUN wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.05.tar.gz \
    && tar -zxvf xpdf-tools-linux-4.05.tar.gz \
    && mv xpdf-tools-linux-4.05/bin64/pdftohtml /usr/local/bin \
    && rm -rf xpdf-tools-linux-4.05.tar.gz xpdf-tools-linux-4.04