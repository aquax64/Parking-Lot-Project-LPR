// OpenALPR Test.cpp : This file contains the 'main' function. Program execution begins and ends there.


// Examples found at : https://web.archive.org/web/20200804015455/http://doc.openalpr.com/bindings.html (the link on the github didn't work)

// LOOK HERE VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
// RUN 
//	- sudo apt-get install python3-dev
//	- sudo apt-get install pybind11-dev
//	- sudo apt-get install python3-pip
//	- pip3 install pybind11
// 
// (Replace "-I/usr/include/python3.10 -I/usr/local/lib/python3.10/dist-packages/pybind11/include" with whatever running "python3 -m pybind11 --includes" displays)
// (Also replace libraries as needed (EX: openalpr source library may be -L/openalpr-2.3.0/src/openalpr instead of -L/openalpr/src/openalpr))
// USE THIS TO COMPILE IT: 
//	- g++ python_binding_test.cpp -fPIC -shared -I/usr/include/python3.10 -I/usr/local/lib/python3.10/dist-packages/pybind11/include -L/openalpr/src/openalpr -L/usr/local/lib -lopencv_core -lopenalpr -o LPR$(python3-config --extension-suffix)
//
// TO IMPORT IT IN PYTHON: (either have it in the same directory or somewhere that python will find it)
// import LPR # or whatever is after "PYBIND11_MODULE(" below
// LPR.testAlpr() # input and everything in C++ works in python

#include <iostream>
#include "alpr.h"
#include <string>
#include <chrono>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

// namespace py = pybind11;

struct Plate {
    std::string character;
    float confidence;

    Plate()
    {

    }

    Plate(std::string a, float b)
    {
        character = a;
        confidence = b;
    }
};

// Returns an error code
Plate testAlpr(pybind11::array_t<char*> img) {
    using std::chrono::high_resolution_clock;
    using std::chrono::duration_cast;
    using std::chrono::duration;
    using std::chrono::milliseconds;

    // std::cout << typeid(img).name() << std::endl;

    pybind11::buffer_info buf = img.request();

    unsigned char* ptr = static_cast<unsigned char*>(buf.ptr);

    std::vector<char> imageBytes(ptr, ptr + buf.size);

    std::cout << "Loading country: us\n";
    std::cout << "Loading openalpr.conf...\n";
    alpr::Alpr openalpr("us", "openalpr.conf");


    // Set top N number of plates to return (Default: 10)
    openalpr.setTopN(20);

    std::cout << "Loading region as 'md' (Maryland)...\n";
    // Compares plate with region matching pattern
    openalpr.setDefaultRegion("tn"); // md (Maryland) region as opposed to ca (California) or ny (New York) (maybe tn works)


    // Make sure the library is loaded
    if (!openalpr.isLoaded())
    {
        std::cerr << "Error loading OpenALPR" << std::endl;
        return Plate();
    }

    std::cout << "OpenALPR Loaded\n";

    // Recognize image file...
    // std::cout << "Input image file... \n";
    // std::string imagePath;
    // std::cout << "Path: ";
    // std::getline(std::cin, imagePath);

    auto t1 = high_resolution_clock::now();

    // alpr::AlprResults results = openalpr.recognize(imagePath);
    alpr::AlprResults results = openalpr.recognize(imageBytes);

    // alpr::AlprPlate returnPlate = alpr::AlprPlate();
    Plate returnPlate;

    // Iterate through the results.  There may be multiple plates in an image,
    // and each plate returns the top N candidates.
    for (int i = 0; i < results.plates.size(); i++)
    {
        alpr::AlprPlateResult plate = results.plates[i];
        std::cout << "plate" << i << ": " << plate.topNPlates.size() << " results" << std::endl;

        for (int k = 0; k < plate.topNPlates.size(); k++)
        {
            alpr::AlprPlate candidate = plate.topNPlates[k];
            if (candidate.overall_confidence > 89.0)
            {
                // returnPlate = candidate;
                returnPlate = Plate(std::string(candidate.characters), float(candidate.overall_confidence));
            }
            std::cout << "    - " << candidate.characters << "\t confidence: " << candidate.overall_confidence;
            std::cout << "\t pattern_match: " << candidate.matches_template << std::endl;
        }
    }

    if (results.plates.size() == 0)
    {
        std::cout << "No license plates found...\n";
        return returnPlate;
    }

    auto t2 = high_resolution_clock::now();

    auto ms_int = duration_cast<milliseconds>(t2 - t1);
    duration<double, std::milli> ms_double = t2 - t1;

    std::cout << ms_int.count() << "ms\n";
    std::cout << ms_double.count() << "ms\n";

    return returnPlate;
}

PYBIND11_MODULE(LPR, m) {
    pybind11::class_<Plate>(m, "Plate")
        .def(pybind11::init<>()) // Make struct be available before function
        .def_readwrite("character", &Plate::character)
        .def_readwrite("confidence", &Plate::confidence);

    m.def("testAlpr", &testAlpr, "A function to test a python binding for alpr in python");
}
