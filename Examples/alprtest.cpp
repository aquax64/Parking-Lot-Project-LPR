// OpenALPR Test.cpp : This file contains the 'main' function. Program execution begins and ends there.


// Examples found at : https://web.archive.org/web/20200804015455/http://doc.openalpr.com/bindings.html (the link on the github didn't work)


#include <iostream>
#include "alpr.h"
#include <string>

#include <chrono>


int main()
{
    using std::chrono::high_resolution_clock;
    using std::chrono::duration_cast;
    using std::chrono::duration;
    using std::chrono::milliseconds;

    
    std::cout << "Loading country: us\n";
    std::cout << "Loading openalpr.conf...\n";
    alpr::Alpr openalpr("us", "openalpr.conf");
    
    
    // Set top N number of plates to return (Default: 10)
    openalpr.setTopN(20);

    std::cout << "Loading region as 'md' (Maryland)...\n";
    // Compares plate with region matching pattern
    openalpr.setDefaultRegion("md"); // md (Maryland) region as opposed to ca (California) or ny (New York) (maybe tn works)
    

    // Make sure the library is loaded
    if (!openalpr.isLoaded())
    {
        std::cerr << "Error loading OpenALPR" << std::endl;
        return 1;
    }

    std::cout << "OpenALPR Loaded\n";

    // Recognize image file...
    std::cout << "Input image file... \n";
    std::string imagePath;
    std::cout << "Path: ";
    std::getline(std::cin, imagePath);

    auto t1 = high_resolution_clock::now();

    alpr::AlprResults results = openalpr.recognize(imagePath);

    // Iterate through the results.  There may be multiple plates in an image,
    // and each plate return sthe top N candidates.
    for (int i = 0; i < results.plates.size(); i++)
    {
        alpr::AlprPlateResult plate = results.plates[i];
        std::cout << "plate" << i << ": " << plate.topNPlates.size() << " results" << std::endl;

        for (int k = 0; k < plate.topNPlates.size(); k++)
        {
            alpr::AlprPlate candidate = plate.topNPlates[k];
            std::cout << "    - " << candidate.characters << "\t confidence: " << candidate.overall_confidence;
            std::cout << "\t pattern_match: " << candidate.matches_template << std::endl;
        }
    }

    auto t2 = high_resolution_clock::now();

    auto ms_int = duration_cast<milliseconds>(t2 - t1);
    duration<double, std::milli> ms_double = t2 - t1;

    std::cout << ms_int.count() << "ms\n";
    std::cout << ms_double.count() << "ms\n";

    return 0;
}
