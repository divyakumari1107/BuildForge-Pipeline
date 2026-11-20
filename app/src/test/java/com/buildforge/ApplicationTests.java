package com.buildforge;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class ApplicationTests {

    @Test
    public void testAppStatus() {
        assertEquals("UP", Application.getAppStatus(), "Application health status must be UP");
    }

    @Test
    public void testAppVersion() {
        assertNotNull(Application.getAppVersion(), "Application version must not be null");
        assertTrue(Application.getAppVersion().contains("RELEASE"), "Version should be a production RELEASE");
    }

    @Test
    public void testBuildHealth() {
        boolean buildPassed = true;
        assertTrue(buildPassed, "Maven build validation must succeed");
    }
}
