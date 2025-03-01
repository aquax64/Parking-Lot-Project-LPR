If you're compiling with Linux, you need to be very careful about how and where you place things.

First (the only website you'll have to go to) go to [HERE](https://github.com/openalpr/openalpr/releases) and download (be very careful here and download the right one) "Source code (tar.gz)" and keep in in downloads for now

**IMPORTANT**: While running these commands do NOT close the console UNLESS you know what you're doing. If you do, contact me on teams and PLEASE preserve the console (this can be done by leaving it as is OR copying everything to a text file). From there, you can shutdown the linux device. (**REMEMBER**: copying in the console is done by RIGHT-CLICKING and clicking COPY because **CTRL^C does NOT work**)

__First download the libraries required:__
 - Run the following:
  * sudo apt clean
  * sudo apt update
  * sudo apt upgrade
  * sudo apt install g++ make cmake git build-essential libdc1394-dev liblog4cplus-dev curl libcurl4-openssl-dev openexr libatlas-base-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev dkms pkg-config libicu-dev libpango1.0-dev libcairo2-dev libpixman-1-dev


- Go to a main directory where you want everything to be and for the sake of convience I'm going to call this directory "/home" (**pay attention to this part**) which also includes everything before the "/home" directory so when I mention something like "/home/opencv" this does not literally mean '/home/opencv'. EX: If you choose your "/home" directory as "/Projects/LPR" then you will replace "/home" like this "/home/opencv"->"/Projects/LPR/opencv" and NOT like this "/home/opencv"->"/LPR/opencv"
- Now in this "/home" directory extract your "Source code (tar.gz)" download here
- Run the following:
  * git clone -b 3.4.20 https://github.com/opencv/opencv.git
  * git clone -b 3.4.20 https://github.com/opencv/opencv_contrib.git
  * cd opencv
  * mkdir build && cd build
  * cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -D BUILD_EXAMPLES=ON -D BUILD_TIFF=ON -D ENABLED_PRECOMPILED_HEADERS=OFF -D WITH_FFMPEG=OFF -D WITH_AVRESAMPLE=OFF  ..
  * make -j7
  * sudo make install
  * cd ../../
  * git clone https://github.com/tesseract-ocr/tesseract.git
  * cd tesseract
  * mkdir build && cd build
  * cmake -D CMAKE_INSTALL_PREFIX=/usr/local -DBUILD_SHARED_LIBS=ON ..
  * make
  * sudo make install
  (HINT: Replace "/home" here)
  * sudo cp -r /home/tesseract/tesseract/src/ccmain /usr/local/include/tesseract/
  * sudo cp -r /home/tesseract/tesseract/src/ccutil /usr/local/include/tesseract/
  (If the console tells you that it is already there, after running the 2 commands above, do not worry and just continue. If you recieve any errors, contact me and mention that the errors occurred after or before this point)
  * cd ../../
  * cd opencv-3.4.2
  * mkdir build && cd build
  (A lot of nonsensical errors tend to happen around this part for me but they may not here)
  * cmake -D CMAKE_INSTALL_PREFIX=/usr/local -DTesseract_INCLUDE_DIRS=/usr/local/include/tesseract -DTesseract_INCLUDE_BASEAPI_DIR=/usr/local/include/tesseract -DTesseract_INCLUDE_CCSTRUCT_DIR=/usr/local/include/tesseract/ccstruct -DTesseract_INCLUDE_CCMAIN_DIR=/usr/local/include/tesseract/ccmain -DTesseract_INCLUDE_CCUTIL_DIR=/usr/local/include/tesseract/ccutil -DTesseract_LIBRARIES=/usr/local/lib/libtesseract.so ..
  * make
  * sudo make install
- Now, the hard part is over.
- Create your .cpp file anywhere you want it to be
- (There is another step with runtime_data but I need to fix it) 


********OUT OF DATE********
FROM **HERE**
 - Download the following (from this Repo):
     - openalpr.rar (contains openalpr library) 
     - opencv.rar (contains opencv library) (too big to be on GitHub so I uploaded it to my OneDrive so ask me if you need this or go find the files for opencv (version 3.4.20) and compile it using their directions)
     - runtime_data.rar (contains language files and .conf file)
 - Add both compiled libraries to your libraries
     - Extract both openalpr.rar and opencv.rar somewhere
     - cd \opencv\build\ (These 4 lines are wrong. It won't work. You have to build it yourself. Delete build folder and use cmake to build it)
     - sudo make install
     - cd \openalpr\src\build\
     - sudo make install
 - Extract the folder (called runtime_data) from runtime_data.rar and place it anywhere (but copy that path)
 - Move the openalpr.conf file to the same directory as the out file (.out) 

TO **HERE**

__TO COMPILE FOR LINUX__
- use "g++ (name of the source file).cpp -o (name of out file).out -L/usr/local/lib -lopencv_core -lopenalpr"
- Don't forget the "alpr.h" file (in the same directory as the source file) from the repo (Parking-Lot-Project-LPR/Parking Lot Project/openalpr_64/include/)
- Make sure openalpr.conf is in the same directory as both your out file (.out)
- Edit the openalpr.conf and change the part after "runtime_dir = " to the path of the folder where you put your "runtime_data" folder
- Run it (for the image, if it's in the same directory, you can just put the name of the image with the file type)  
- If you get compiler errors, check that you have all libraries present by going back through the steps above and looking for the ".so" files then (if problems persist) please reach out to me.
