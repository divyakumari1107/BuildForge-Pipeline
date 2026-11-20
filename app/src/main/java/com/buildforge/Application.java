package com.buildforge;

import java.time.Instant;

public class Application {
    public static void main(String[] args) {
        System.out.println("=================================================");
        System.out.println("  BuildForge Enterprise Microservice is running! ");
        System.out.println("  Version: 1.0.0-RELEASE | Started at: " + Instant.now());
        System.out.println("=================================================");
    }

    public static String getAppStatus() {
        return "UP";
    }

    public static String getAppVersion() {
        return "1.0.0-RELEASE";
    }
}
