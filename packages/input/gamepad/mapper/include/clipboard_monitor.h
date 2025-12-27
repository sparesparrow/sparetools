#pragma once

#include <string>
#include <vector>
#include <functional>
#include <memory>
#include <atomic>
#include <thread>
#include <mutex>

namespace gamepad_mapper {

// Forward declarations for GTK types
typedef struct _GtkClipboard GtkClipboard;
typedef struct _GdkPixbuf GdkPixbuf;
typedef struct _GtkWidget GtkWidget;

// Clipboard content types
enum class ClipboardContentType {
    TEXT,
    IMAGE,
    FILES,
    UNKNOWN
};

// Clipboard content structure
struct ClipboardContent {
    ClipboardContentType type;
    std::string text_content;
    std::vector<unsigned char> image_data;
    std::vector<std::string> file_paths;
    std::string mime_type;
    size_t data_size;

    ClipboardContent() : type(ClipboardContentType::UNKNOWN), data_size(0) {}
};

// Clipboard change callback function type
using ClipboardChangeCallback = std::function<void(const ClipboardContent& content)>;

// Clipboard monitor class
class ClipboardMonitor {
public:
    ClipboardMonitor();
    ~ClipboardMonitor();

    // Initialize the clipboard monitor
    bool initialize();

    // Start monitoring clipboard changes
    bool start();

    // Stop monitoring clipboard changes
    void stop();

    // Get current clipboard content
    ClipboardContent get_current_content();

    // Set clipboard content
    bool set_text_content(const std::string& text);
    bool set_image_content(const std::vector<unsigned char>& image_data, const std::string& mime_type);
    bool clear_clipboard();

    // Register callback for clipboard changes
    void register_change_callback(ClipboardChangeCallback callback);

    // Check if clipboard monitoring is active
    bool is_monitoring() const;

private:
    // GTK clipboard instance
    GtkClipboard* clipboard_;

    // Monitoring thread
    std::unique_ptr<std::thread> monitor_thread_;
    std::atomic<bool> monitoring_;
    std::mutex callback_mutex_;

    // Last known content hash for change detection
    std::string last_content_hash_;

    // Callbacks
    std::vector<ClipboardChangeCallback> callbacks_;

    // Internal monitoring loop
    void monitoring_loop();

    // Check for clipboard changes
    bool has_clipboard_changed();

    // Generate content hash for change detection
    std::string generate_content_hash(const ClipboardContent& content);

    // Get clipboard content from GTK
    ClipboardContent get_clipboard_content_internal();

    // GTK signal callback (static wrapper)
    static void on_clipboard_owner_change(GtkClipboard* clipboard, GdkEvent* event, gpointer user_data);

    // Process clipboard change
    void process_clipboard_change();
};

} // namespace gamepad_mapper