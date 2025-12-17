package {{package_name}}.native;

/**
 * Native interface for {{project_name}}
 *
 * Provides access to native C++ code that uses SpareTools libraries
 * including OpenSSL for cryptographic operations.
 */
public class NativeInterface {

    static {
        System.loadLibrary("native-lib");
    }

    /**
     * Get the OpenSSL version string
     *
     * @return OpenSSL version string
     */
    public native String getOpenSSLVersion();

    /**
     * Encrypt data using native implementation
     *
     * @param data Data to encrypt
     * @param key Encryption key
     * @return Encrypted data
     */
    public native byte[] encryptData(byte[] data, byte[] key);

    /**
     * Decrypt data using native implementation
     *
     * @param encryptedData Data to decrypt
     * @param key Decryption key
     * @return Decrypted data
     */
    public native byte[] decryptData(byte[] encryptedData, byte[] key);

    /**
     * Get device information
     *
     * @return Device information string
     */
    public native String getDeviceInfo();

    /**
     * Utility method to convert byte array to hex string
     *
     * @param bytes Byte array to convert
     * @return Hex string representation
     */
    public static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    /**
     * Utility method to convert hex string to byte array
     *
     * @param hex Hex string to convert
     * @return Byte array
     */
    public static byte[] hexToBytes(String hex) {
        int len = hex.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4)
                    + Character.digit(hex.charAt(i + 1), 16));
        }
        return data;
    }
}