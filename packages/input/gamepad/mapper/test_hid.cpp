#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <iomanip>

int main() {
    const char* hid_device = "/dev/hidraw2";
    
    std::cout << "Opening HID device: " << hid_device << std::endl;
    
    int fd = open(hid_device, O_RDONLY | O_NONBLOCK);
    if (fd == -1) {
        std::cerr << "Failed to open HID device: " << strerror(errno) << std::endl;
        return 1;
    }
    
    std::cout << "HID device opened successfully. Reading data..." << std::endl;
    std::cout << "Press buttons on your DualShock 4 controller to see data..." << std::endl;
    
    unsigned char buffer[64];
    int bytes_read;
    
    for (int i = 0; i < 50; i++) {
        bytes_read = read(fd, buffer, sizeof(buffer));
        if (bytes_read > 0) {
            std::cout << "Read " << bytes_read << " bytes: ";
            for (int j = 0; j < bytes_read; j++) {
                std::cout << std::hex << std::setw(2) << std::setfill('0') 
                         << (int)buffer[j] << " ";
            }
            std::cout << std::dec << std::endl;
        } else {
            usleep(100000); // 100ms
        }
    }
    
    close(fd);
    return 0;
}
