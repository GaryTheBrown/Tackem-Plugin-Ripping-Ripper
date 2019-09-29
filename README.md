# Tackem - Plugin - Ripping - Ripper

## About
This Plugin allows the user to rip Discs to the libraries. It is capable of ripping Audio CDs DVD Videos Blu Ray Videos including 3D and 4k (dependent on optical drive used). This relies on makemkv for videos and cdda2wav for audio discs.

you need to install additional software for this plugin to work and will not load until they are all installed.

## Installation

REQUIRED: ```makemkv java JRE CCExtractor libcss2 mplayer eject lsblk hwinfo blkid libdiscid0 cdda2wav```
PYTHON REQUIREDS: ```discid```

### Ubuntu commands
```
sudo add-apt-repository ppa:heyarje/makemkv-beta
sudo apt install hwinfo mplayer ffmpeg makemkv-bin makemkv-oss libdvd-pkg default-jre icedax libdiscid0
sudo dpkg-reconfigure libdvd-pkg
git clone https://github.com/CCExtractor/ccextractor.git
sudo apt install cmake gcc libcurl4-gnutls-dev tesseract-ocr libtesseract-dev libleptonica-dev autoconf
cd ccextractor/linux
./autogen.sh
./configure
make
sudo make install
```

### makemkv settings.conf
```
app_DefaultSelectionString = "+sel:all"
app_DefaultOutputFileName = "{t:N2}"
app_ccextractor = "/usr/local/bin/ccextractor"
```
