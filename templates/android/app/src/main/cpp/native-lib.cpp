#include <jni.h>
#include <string>
#include <vector>
#include <android/log.h>

#include <openssl/ssl.h>
#include <openssl/err.h>

#define LOG_TAG "{{project_name}}"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

extern "C" {

JNIEXPORT jstring JNICALL
Java_{{package_name|replace('_', '_1')|replace('.', '_')}}native_NativeInterface_getOpenSSLVersion(
    JNIEnv* env, jobject /* this */) {
    try {
        const char* version = OpenSSL_version(OPENSSL_VERSION);
        LOGI("OpenSSL version: %s", version);
        return env->NewStringUTF(version);
    } catch (const std::exception& e) {
        LOGE("Error getting OpenSSL version: %s", e.what());
        return env->NewStringUTF("Error getting OpenSSL version");
    }
}

JNIEXPORT jbyteArray JNICALL
Java_{{package_name|replace('_', '_1')|replace('.', '_')}}native_NativeInterface_encryptData(
    JNIEnv* env, jobject /* this */, jbyteArray data, jbyteArray key) {

    try {
        // Get data from Java
        jsize data_len = env->GetArrayLength(data);
        jbyte* data_bytes = env->GetByteArrayElements(data, nullptr);

        jsize key_len = env->GetArrayLength(key);
        jbyte* key_bytes = env->GetByteArrayElements(key, nullptr);

        // Simple XOR encryption for demonstration
        // In real code, use proper encryption algorithms
        std::vector<jbyte> encrypted_data(data_len);
        for (jsize i = 0; i < data_len; ++i) {
            encrypted_data[i] = data_bytes[i] ^ key_bytes[i % key_len];
        }

        // Release Java arrays
        env->ReleaseByteArrayElements(data, data_bytes, JNI_ABORT);
        env->ReleaseByteArrayElements(key, key_bytes, JNI_ABORT);

        // Create result array
        jbyteArray result = env->NewByteArray(data_len);
        env->SetByteArrayRegion(result, 0, data_len, encrypted_data.data());

        LOGI("Data encrypted successfully, length: %d", data_len);
        return result;

    } catch (const std::exception& e) {
        LOGE("Error encrypting data: %s", e.what());

        // Release arrays in case of error
        if (data) env->ReleaseByteArrayElements(data,
            env->GetByteArrayElements(data, nullptr), JNI_ABORT);
        if (key) env->ReleaseByteArrayElements(key,
            env->GetByteArrayElements(key, nullptr), JNI_ABORT);

        return nullptr;
    }
}

JNIEXPORT jbyteArray JNICALL
Java_{{package_name|replace('_', '_1')|replace('.', '_')}}native_NativeInterface_decryptData(
    JNIEnv* env, jobject /* this */, jbyteArray encrypted_data, jbyteArray key) {

    try {
        // Get data from Java
        jsize data_len = env->GetArrayLength(encrypted_data);
        jbyte* data_bytes = env->GetByteArrayElements(encrypted_data, nullptr);

        jsize key_len = env->GetArrayLength(key);
        jbyte* key_bytes = env->GetByteArrayElements(key, nullptr);

        // XOR decryption (same as encryption for XOR)
        std::vector<jbyte> decrypted_data(data_len);
        for (jsize i = 0; i < data_len; ++i) {
            decrypted_data[i] = data_bytes[i] ^ key_bytes[i % key_len];
        }

        // Release Java arrays
        env->ReleaseByteArrayElements(encrypted_data, data_bytes, JNI_ABORT);
        env->ReleaseByteArrayElements(key, key_bytes, JNI_ABORT);

        // Create result array
        jbyteArray result = env->NewByteArray(data_len);
        env->SetByteArrayRegion(result, 0, data_len, decrypted_data.data());

        LOGI("Data decrypted successfully, length: %d", data_len);
        return result;

    } catch (const std::exception& e) {
        LOGE("Error decrypting data: %s", e.what());

        // Release arrays in case of error
        if (encrypted_data) env->ReleaseByteArrayElements(encrypted_data,
            env->GetByteArrayElements(encrypted_data, nullptr), JNI_ABORT);
        if (key) env->ReleaseByteArrayElements(key,
            env->GetByteArrayElements(key, nullptr), JNI_ABORT);

        return nullptr;
    }
}

JNIEXPORT jstring JNICALL
Java_{{package_name|replace('_', '_1')|replace('.', '_')}}native_NativeInterface_getDeviceInfo(
    JNIEnv* env, jobject /* this */) {

    try {
        // Get device information using Android APIs would go here
        // For now, return a simple string
        std::string device_info = "Android Device - OpenSSL: " +
            std::string(OpenSSL_version(OPENSSL_VERSION));

        LOGI("Device info requested: %s", device_info.c_str());
        return env->NewStringUTF(device_info.c_str());

    } catch (const std::exception& e) {
        LOGE("Error getting device info: %s", e.what());
        return env->NewStringUTF("Error getting device info");
    }
}

} // extern "C"