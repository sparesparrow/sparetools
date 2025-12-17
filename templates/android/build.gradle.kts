// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id("com.android.application") version "8.1.4" apply false
    id("org.jetbrains.kotlin.android") version "1.9.10" apply false
    id("com.android.library") version "8.1.4" apply false
    id("com.diffplug.spotless") version "6.20.0" apply false
    id("io.gitlab.arturbosch.detekt") version "1.23.1" apply false
    id("com.ncorti.ktfmt.gradle") version "0.17.0" apply false
}

task<Delete>("clean") {
    delete(rootProject.buildDir)
}