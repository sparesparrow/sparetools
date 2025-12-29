//
// main.cpp
// Main entry point for NucleusESP32 unit tests
// Following oms-dev/Src/Tests/OmsUnitTests/main.cpp pattern
//

#include "pch.h"

int main(int argc, char** argv)
{
    testing::InitGoogleTest(&argc, argv);
    
    // Add global test environments if needed
    // testing::AddGlobalTestEnvironment(new NucleusTestEnvironment);
    
    return RUN_ALL_TESTS();
}
