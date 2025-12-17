#include <jni.h>
#include <string>
#include <android/log.h>

#define LOG_TAG "ClipHistNative"
#define LOGD(...) __android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, __VA_ARGS__)

extern "C" JNIEXPORT jstring JNICALL
Java_com_sparesparrow_cliphist_ClipHistNative_getVersion(
        JNIEnv* env,
        jobject /* this */) {
    std::string version = "ClipHist v1.0.0";
    LOGD("Native library version: %s", version.c_str());
    return env->NewStringUTF(version.c_str());
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_sparesparrow_cliphist_ClipHistNative_encryptData(
        JNIEnv* env,
        jobject /* this */,
        jstring data,
        jstring key) {
    // Placeholder for encryption logic
    // In production, this would integrate with SQLCipher or other encryption
    LOGD("Encrypting data with native code");
    return JNI_TRUE;
}