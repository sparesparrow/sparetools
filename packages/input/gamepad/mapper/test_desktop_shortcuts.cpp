#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include "gamepad_mapper.h"
#include "backends/keyboard_shortcut_handler.h"

using namespace gamepad_mapper;

int main() {
    std::cout << "🎮 Gamepad Desktop Shortcuts Test" << std::endl;
    std::cout << "=================================" << std::endl;
    
    // Initialize gamepad mapper
    GamepadMapper mapper;
    if (!mapper.initialize()) {
        std::cerr << "❌ Failed to initialize gamepad mapper!" << std::endl;
        return 1;
    }
    
    std::cout << "✅ Gamepad mapper initialized successfully!" << std::endl;
    
    // Load desktop shortcuts configuration
    if (!mapper.load_mappings("config/desktop_shortcuts_mappings.json")) {
        std::cerr << "❌ Failed to load desktop shortcuts configuration!" << std::endl;
        return 1;
    }
    
    std::cout << "✅ Desktop shortcuts configuration loaded!" << std::endl;
    
    // Get connected controllers
    auto controllers = mapper.get_connected_controllers();
    if (controllers.empty()) {
        std::cout << "⚠️  No controllers detected. Please connect a gamepad." << std::endl;
        std::cout << "   The program will wait for a controller to be connected..." << std::endl;
        
        // Wait for controller connection
        while (controllers.empty()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
            mapper.scan_for_controllers();
            controllers = mapper.get_connected_controllers();
        }
    }
    
    std::cout << "🎮 Connected controllers:" << std::endl;
    for (const auto& controller : controllers) {
        std::cout << "   - " << controller.name << " (ID: " << controller.id << ")" << std::endl;
    }
    
    // Start the mapper
    mapper.start();
    std::cout << "🚀 Gamepad mapper started! Press buttons on your gamepad to test shortcuts." << std::endl;
    std::cout << std::endl;
    
    // Display control information
    std::cout << "📋 Available Shortcuts:" << std::endl;
    std::cout << "=======================" << std::endl;
    std::cout << "Basic Controls:" << std::endl;
    std::cout << "  A Button     → Enter" << std::endl;
    std::cout << "  B Button     → Escape" << std::endl;
    std::cout << "  X Button     → Space" << std::endl;
    std::cout << "  Y Button     → Tab" << std::endl;
    std::cout << "  D-Pad        → Arrow Keys" << std::endl;
    std::cout << "  Triggers     → Mouse Clicks" << std::endl;
    std::cout << "  Left Stick   → Mouse Movement" << std::endl;
    std::cout << "  Right Stick  → Mouse Scroll" << std::endl;
    std::cout << std::endl;
    
    std::cout << "Modifier Combinations:" << std::endl;
    std::cout << "  LB + A       → Alt+Tab (Window Switcher)" << std::endl;
    std::cout << "  LB + B       → Alt+F4 (Close Window)" << std::endl;
    std::cout << "  RB + A       → Ctrl+Alt+Tab (Task Switcher)" << std::endl;
    std::cout << "  RB + B       → Ctrl+Alt+Delete (System Menu)" << std::endl;
    std::cout << "  LT + A       → Alt+Shift+Tab (Reverse Window Switcher)" << std::endl;
    std::cout << "  RT + A       → Meta+Enter (Terminal)" << std::endl;
    std::cout << "  RT + B       → Meta+Escape (Activities)" << std::endl;
    std::cout << std::endl;
    
    std::cout << "Text Editing Shortcuts:" << std::endl;
    std::cout << "  SELECT + A   → Ctrl+A (Select All)" << std::endl;
    std::cout << "  SELECT + C   → Ctrl+C (Copy)" << std::endl;
    std::cout << "  SELECT + V   → Ctrl+V (Paste)" << std::endl;
    std::cout << "  SELECT + X   → Ctrl+X (Cut)" << std::endl;
    std::cout << "  SELECT + S   → Ctrl+S (Save)" << std::endl;
    std::cout << "  SELECT + Z   → Ctrl+Z (Undo)" << std::endl;
    std::cout << "  SELECT + Y   → Ctrl+Y (Redo)" << std::endl;
    std::cout << "  SELECT + F   → Ctrl+F (Find)" << std::endl;
    std::cout << "  SELECT + H   → Ctrl+H (Find & Replace)" << std::endl;
    std::cout << "  SELECT + N   → Ctrl+N (New)" << std::endl;
    std::cout << "  SELECT + O   → Ctrl+O (Open)" << std::endl;
    std::cout << "  SELECT + P   → Ctrl+P (Print)" << std::endl;
    std::cout << "  SELECT + W   → Ctrl+W (Close Tab/Window)" << std::endl;
    std::cout << "  SELECT + T   → Ctrl+T (New Tab)" << std::endl;
    std::cout << "  SELECT + Q   → Ctrl+Q (Quit)" << std::endl;
    std::cout << std::endl;
    
    std::cout << "Browser Shortcuts:" << std::endl;
    std::cout << "  START + A    → Ctrl+T (New Tab)" << std::endl;
    std::cout << "  START + B    → Ctrl+W (Close Tab)" << std::endl;
    std::cout << "  START + X    → Ctrl+Tab (Next Tab)" << std::endl;
    std::cout << "  START + Y    → Ctrl+Shift+Tab (Previous Tab)" << std::endl;
    std::cout << "  START + ←    → Alt+← (Back)" << std::endl;
    std::cout << "  START + →    → Alt+→ (Forward)" << std::endl;
    std::cout << std::endl;
    
    std::cout << "Function Keys:" << std::endl;
    std::cout << "  RS + A       → F1" << std::endl;
    std::cout << "  RS + B       → F2" << std::endl;
    std::cout << "  RS + X       → F3" << std::endl;
    std::cout << "  RS + Y       → F4" << std::endl;
    std::cout << "  RS + ↑       → F5" << std::endl;
    std::cout << "  RS + ↓       → F6" << std::endl;
    std::cout << "  RS + ←       → F7" << std::endl;
    std::cout << "  RS + →       → F8" << std::endl;
    std::cout << std::endl;
    
    std::cout << "Press Ctrl+C to exit the program." << std::endl;
    std::cout << "=================================" << std::endl;
    
    // Keep the program running
    try {
        while (true) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
    
    // Cleanup
    mapper.stop();
    std::cout << "👋 Gamepad mapper stopped. Goodbye!" << std::endl;
    
    return 0;
}
