// OpenALPR Test.cpp : This file contains the 'main' function. Program execution begins and ends there.


// Examples found at : https://web.archive.org/web/20200804015455/http://doc.openalpr.com/bindings.html (the link on the github didn't work)


#include <iostream>
#include "alpr.h"
#include <string>

#include <chrono>

using namespace std;
using namespace alpr;

int main()
{
    using std::chrono::high_resolution_clock;
    using std::chrono::duration_cast;
    using std::chrono::duration;
    using std::chrono::milliseconds;

    
    cout << "Loading country: us";
    cout << "Loading openalpr.conf...";
    Alpr openalpr("us", "C:/Users/mraqu/source/repos/OpenALPR Test/OpenALPR Test/libs/openalpr_64/runtime_data/openalpr.conf");
    
    
    // Set top N number of plates to return (Default: 10)
    openalpr.setTopN(20);

    cout << "Loading region as 'md' (Maryland)...\n";
    // Compares plate with region matching pattern
    openalpr.setDefaultRegion("md"); // md (Maryland) region as opposed to ca (California) or ny (New York) (maybe tn works)
    

    // Make sure the library is loaded
    if (!openalpr.isLoaded())
    {
        cerr << "Error loading OpenALPR" << endl;
        return 1;
    }

    cout << "OpenALPR Loaded\n";

    // Recognize image file...
    cout << "Input image file... \n";
    string imagePath;
    cout << "Path: ";
    getline(cin, imagePath);

    auto t1 = high_resolution_clock::now();

    AlprResults results = openalpr.recognize(imagePath);

    // Iterate through the results.  There may be multiple plates in an image,
    // and each plate return sthe top N candidates.
    for (int i = 0; i < results.plates.size(); i++)
    {
        AlprPlateResult plate = results.plates[i];
        cout << "plate" << i << ": " << plate.topNPlates.size() << " results" << endl;

        for (int k = 0; k < plate.topNPlates.size(); k++)
        {
            AlprPlate candidate = plate.topNPlates[k];
            cout << "    - " << candidate.characters << "\t confidence: " << candidate.overall_confidence;
            cout << "\t pattern_match: " << candidate.matches_template << endl;
        }
    }

    auto t2 = high_resolution_clock::now();

    auto ms_int = duration_cast<milliseconds>(t2 - t1);
    duration<double, std::milli> ms_double = t2 - t1;

    cout << ms_int.count() << "ms\n";
    cout << ms_double.count() << "ms\n";

    return 0;
}
