#include "clipboard_monitor.h"
#include <gtk/gtk.h>
#include <glib.h>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <cstring>
#include <chrono>
#include <thread>
#include <openssl/md5.h> // For content hashing

namespace gamepad_mapper {

ClipboardMonitor::ClipboardMonitor()
    : clipboard_(nullptr)
    , monitoring_(false) {
}

ClipboardMonitor::~ClipboardMonitor() {
    stop();
}

bool ClipboardMonitor::initialize() {
    // Initialize GTK if not already initialized
    if (!gtk_init_check(nullptr, nullptr)) {
        std::cerr << "Failed to initialize GTK for clipboard monitoring" << std::endl;
        return false;
    }

    // Get the default clipboard
    clipboard_ = gtk_clipboard_get(GDK_SELECTION_CLIPBOARD);
    if (!clipboard_) {
        std::cerr << "Failed to get default clipboard" << std::endl;
        return false;
    }

    std::cout << "Clipboard monitor initialized successfully" << std::endl;
    return true;
}

bool ClipboardMonitor::start() {
    if (monitoring_) {
        return true; // Already running
    }

    if (!clipboard_) {
        std::cerr << "Clipboard monitor not initialized" << std::endl;
        return false;
    }

    monitoring_ = true;

    // Connect to clipboard owner change signal
    g_signal_connect(clipboard_, "owner-change",
                     G_CALLBACK(ClipboardMonitor::on_clipboard_owner_change), this);

    // Start monitoring thread
    monitor_thread_ = std::make_unique<std::thread>(&ClipboardMonitor::monitoring_loop, this);

    std::cout << "Clipboard monitoring started" << std::endl;
    return true;
}

void ClipboardMonitor::stop() {
    if (!monitoring_) {
        return;
    }

    monitoring_ = false;

    // Disconnect signal handler
    if (clipboard_) {
        g_signal_handlers_disconnect_by_func(clipboard_,
            (gpointer)G_CALLBACK(ClipboardMonitor::on_clipboard_owner_change), this);
    }

    // Wait for monitoring thread to finish
    if (monitor_thread_ && monitor_thread_->joinable()) {
        monitor_thread_->join();
    }

    monitor_thread_.reset();
    std::cout << "Clipboard monitoring stopped" << std::endl;
}

ClipboardContent ClipboardMonitor::get_current_content() {
    if (!clipboard_) {
        return ClipboardContent();
    }

    return get_clipboard_content_internal();
}

bool ClipboardMonitor::set_text_content(const std::string& text) {
    if (!clipboard_) {
        return false;
    }

    gtk_clipboard_set_text(clipboard_, text.c_str(), text.length());
    gtk_clipboard_store(clipboard_);
    return true;
}

bool ClipboardMonitor::set_image_content(const std::vector<unsigned char>& image_data,
                                        const std::string& mime_type) {
    if (!clipboard_ || image_data.empty()) {
        return false;
    }

    // For simplicity, we'll just set text content indicating image data
    // In a full implementation, you'd use GdkPixbuf and gtk_clipboard_set_image
    std::string placeholder = "[Image data: " + std::to_string(image_data.size()) + " bytes, " + mime_type + "]";
    return set_text_content(placeholder);
}

bool ClipboardMonitor::clear_clipboard() {
    if (!clipboard_) {
        return false;
    }

    gtk_clipboard_clear(clipboard_);
    return true;
}

void ClipboardMonitor::register_change_callback(ClipboardChangeCallback callback) {
    std::lock_guard<std::mutex> lock(callback_mutex_);
    callbacks_.push_back(callback);
}

bool ClipboardMonitor::is_monitoring() const {
    return monitoring_;
}

void ClipboardMonitor::monitoring_loop() {
    while (monitoring_) {
        if (has_clipboard_changed()) {
            process_clipboard_change();
        }

        // Poll every 500ms
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
}

bool ClipboardMonitor::has_clipboard_changed() {
    if (!clipboard_) {
        return false;
    }

    ClipboardContent current_content = get_clipboard_content_internal();
    std::string current_hash = generate_content_hash(current_content);

    if (current_hash != last_content_hash_) {
        last_content_hash_ = current_hash;
        return true;
    }

    return false;
}

std::string ClipboardMonitor::generate_content_hash(const ClipboardContent& content) {
    std::stringstream ss;

    // Create a simple hash based on content
    ss << static_cast<int>(content.type) << "|"
       << content.text_content << "|"
       << content.mime_type << "|"
       << content.data_size;

    std::string data = ss.str();

    // Use MD5 for hashing
    unsigned char md5_result[MD5_DIGEST_LENGTH];
    MD5(reinterpret_cast<const unsigned char*>(data.c_str()), data.length(), md5_result);

    std::stringstream hash_ss;
    for (int i = 0; i < MD5_DIGEST_LENGTH; ++i) {
        hash_ss << std::hex << std::setw(2) << std::setfill('0')
                << static_cast<int>(md5_result[i]);
    }

    return hash_ss.str();
}

ClipboardContent ClipboardMonitor::get_clipboard_content_internal() {
    ClipboardContent content;

    if (!clipboard_) {
        return content;
    }

    // Check if text is available
    if (gtk_clipboard_wait_is_text_available(clipboard_)) {
        gchar* text = gtk_clipboard_wait_for_text(clipboard_);
        if (text) {
            content.type = ClipboardContentType::TEXT;
            content.text_content = text;
            content.data_size = strlen(text);
            g_free(text);
        }
    }
    // Check if image is available
    else if (gtk_clipboard_wait_is_image_available(clipboard_)) {
        GdkPixbuf* pixbuf = gtk_clipboard_wait_for_image(clipboard_);
        if (pixbuf) {
            content.type = ClipboardContentType::IMAGE;
            content.mime_type = "image/png"; // Assume PNG for simplicity

            // Get image data (simplified - in real implementation you'd save to buffer)
            content.data_size = gdk_pixbuf_get_byte_length(pixbuf);
            content.image_data.resize(content.data_size);
            memcpy(content.image_data.data(), gdk_pixbuf_get_pixels(pixbuf), content.data_size);

            g_object_unref(pixbuf);
        }
    }
    // Check if URIs (files) are available
    else if (gtk_clipboard_wait_is_uris_available(clipboard_)) {
        gchar** uris = gtk_clipboard_wait_for_uris(clipboard_);
        if (uris) {
            content.type = ClipboardContentType::FILES;

            for (int i = 0; uris[i] != nullptr; ++i) {
                content.file_paths.push_back(uris[i]);
            }

            content.data_size = content.file_paths.size();
            g_strfreev(uris);
        }
    }

    return content;
}

void ClipboardMonitor::on_clipboard_owner_change(GtkClipboard* clipboard,
                                                 GdkEvent* event,
                                                 gpointer user_data) {
    ClipboardMonitor* monitor = static_cast<ClipboardMonitor*>(user_data);
    if (monitor) {
        monitor->process_clipboard_change();
    }
}

void ClipboardMonitor::process_clipboard_change() {
    ClipboardContent content = get_current_content();

    std::lock_guard<std::mutex> lock(callback_mutex_);
    for (const auto& callback : callbacks_) {
        try {
            callback(content);
        } catch (const std::exception& e) {
            std::cerr << "Error in clipboard change callback: " << e.what() << std::endl;
        }
    }
}

} // namespace gamepad_mapper