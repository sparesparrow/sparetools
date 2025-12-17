#include <iostream>
#include "{{project_name}}.h"

int main() {
    {{namespace}}::{{class_name}} instance;

    std::cout << "Version: " << instance.get_version() << std::endl;

    std::string input = "Hello, {{project_name}}!";
    std::string output = instance.process(input);

    std::cout << "Input: " << input << std::endl;
    std::cout << "Output: " << output << std::endl;

    return 0;
}