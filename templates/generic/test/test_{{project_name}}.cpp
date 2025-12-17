#include <gtest/gtest.h>
#include "{{project_name}}.h"

class {{class_name}}Test : public ::testing::Test {
protected:
    {{namespace}}::{{class_name}} instance;
};

TEST_F({{class_name}}Test, GetVersion) {
    std::string version = instance.get_version();
    EXPECT_FALSE(version.empty());
    EXPECT_EQ(version, "{{version}}");
}

TEST_F({{class_name}}Test, Process) {
    std::string input = "test input";
    std::string result = instance.process(input);
    EXPECT_FALSE(result.empty());
    EXPECT_NE(result.find(input), std::string::npos);
}

TEST_F({{class_name}}Test, ProcessEmpty) {
    std::string result = instance.process("");
    EXPECT_FALSE(result.empty());
}