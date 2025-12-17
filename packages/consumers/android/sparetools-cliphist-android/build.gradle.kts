// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id("com.android.application") version "8.2.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
    id("com.android.library") version "8.2.2" apply false
    id("androidx.navigation.safeargs.kotlin") version "2.7.6" apply false
    id("dagger.hilt.android.plugin") version "2.48" apply false
    id("kotlin-kapt") version "1.9.22" apply false
    id("kotlin-parcelize") apply false
}

task<Delete>("clean") {
    delete(rootProject.buildDir)
}