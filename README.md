# Tackem - Plugin - Ripping - Ripper

REQUIRED: makemkv java JRE CCExtractor libcss2 mplayer eject lsblk hwinfo blkid libdiscid0 cdda2wav  
PYTHON REQUIREDS: discid  
  
[Ubuntu commands]  
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
  
  
makemkv settings.conf  
app_DefaultSelectionString = "+sel:all"  
app_DefaultOutputFileName = "{t:N2}"  
app_ccextractor = "/usr/local/bin/ccextractor"  