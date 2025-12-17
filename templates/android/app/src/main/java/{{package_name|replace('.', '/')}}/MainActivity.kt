package {{package_name}}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import {{package_name}}.native.NativeInterface
import kotlinx.coroutines.*

class MainActivity : ComponentActivity() {

    private val nativeInterface = NativeInterface()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            {{class_name}}Theme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen(nativeInterface)
                }
            }
        }
    }
}

@Composable
fun MainScreen(nativeInterface: NativeInterface) {
    var opensslVersion by remember { mutableStateOf("Loading...") }
    var deviceInfo by remember { mutableStateOf("Loading...") }
    var testResult by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        // Load native information
        withContext(Dispatchers.IO) {
            opensslVersion = nativeInterface.getOpenSSLVersion()
            deviceInfo = nativeInterface.getDeviceInfo()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "{{project_name}}",
            style = MaterialTheme.typography.headlineMedium
        )

        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text("OpenSSL Version:", style = MaterialTheme.typography.titleMedium)
                Text(opensslVersion, style = MaterialTheme.typography.bodyMedium)

                Spacer(modifier = Modifier.height(8.dp))

                Text("Device Info:", style = MaterialTheme.typography.titleMedium)
                Text(deviceInfo, style = MaterialTheme.typography.bodyMedium)
            }
        }

        Button(
            onClick = {
                isLoading = true
                CoroutineScope(Dispatchers.IO).launch {
                    val result = testEncryption(nativeInterface)
                    withContext(Dispatchers.Main) {
                        testResult = result
                        isLoading = false
                    }
                }
            },
            enabled = !isLoading,
            modifier = Modifier.fillMaxWidth()
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    strokeWidth = 2.dp
                )
            } else {
                Text("Test Encryption")
            }
        }

        if (testResult.isNotEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = if (testResult.contains("SUCCESS"))
                        MaterialTheme.colorScheme.primaryContainer
                    else
                        MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Text(
                    text = testResult,
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

private suspend fun testEncryption(nativeInterface: NativeInterface): String {
    return withContext(Dispatchers.IO) {
        try {
            val testData = "Hello, {{project_name}}!".toByteArray()
            val key = "secretkey123".toByteArray()

            // Encrypt
            val encrypted = nativeInterface.encryptData(testData, key)

            // Decrypt
            val decrypted = nativeInterface.decryptData(encrypted, key)

            // Verify
            val success = testData.contentEquals(decrypted)

            if (success) {
                "SUCCESS: Encryption/decryption test passed\n" +
                "Original: ${String(testData)}\n" +
                "Encrypted: ${NativeInterface.bytesToHex(encrypted)}\n" +
                "Decrypted: ${String(decrypted)}"
            } else {
                "FAILED: Encryption/decryption test failed"
            }
        } catch (e: Exception) {
            "ERROR: ${e.message}"
        }
    }
}

@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    {{class_name}}Theme {
        MainScreen(NativeInterface())
    }
}