If you're compiling with Linux, you need to be very careful about how and where you place things.

__First download the libraries required:__
 - Run the following:
       - sudo apt clean
       - sudo apt update
       - sudo apt upgrade
       - sudo apt install g++
 - Download the following (from this Repo):
     - alpr_so.rar (contains all alpr.so files)
     - opencv_so.rar (contains all opencv.so files)
     - runtime_data.rar (contains language files and .conf file)
 - Extract ALL ".so" files (within the alpr_so.rar and opencv_so.rar) into "/usr/local/lib/"
 - Extract the folder (called runtime_data) from runtime_data.rar and place it anywhere (but copy that path)
 - Move the openalpr.conf file to the same directory as the out file (.out) 


__TO COMPILE FOR LINUX__
- use "g++ (name of the source file).cpp -o (name of out file).out -L/usr/local/lib -lopencv_core -lopenalpr"
- Don't forget the "alpr.h" file (in the same directory as the source file) from the repo (Parking-Lot-Project-LPR/Parking Lot Project/openalpr_64/include/)
- Make sure openalpr.conf is in the same directory as both your out file (.out)
- Edit the openalpr.conf and change the part after "runtime_dir = " to the path of the folder where you put your "runtime_data" folder
- Run it (for the image, if it's in the same directory, you can just put the name of the image with the file type)  
- If you get compiler errors, check that you have all libraries present by going back through the steps above and looking for the ".so" files then (if problems persist) please reach out to me.
