import urllib.request
import urllib.error
import json
import time
import sys

BASE_URL = "http://localhost:8090"

def log_test(name, passed, details=""):
    symbol = "[PASS]" if passed else "[FAIL]"
    print(f"{symbol} {name}")
    if details:
        print(f"       -> {details}")

def test_nginx_dashboard():
    try:
        req = urllib.request.Request(f"{BASE_URL}/")
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read().decode("utf-8")
            passed = resp.status == 200 and "BuildForge" in content
            log_test("Nginx Static Dashboard (Port 8090)", passed, f"Status: {resp.status}, Title detected: {'BuildForge' in content}")
            return passed
    except Exception as e:
        log_test("Nginx Static Dashboard (Port 8090)", False, str(e))
        return False

def test_health_probe():
    try:
        req = urllib.request.Request(f"{BASE_URL}/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            passed = resp.status == 200 and data.get("status") == "UP"
            log_test("Service Health Probe (/health)", passed, f"Status: {data.get('status')}, Runtime: {data.get('runtime')}")
            return passed
    except Exception as e:
        log_test("Service Health Probe (/health)", False, str(e))
        return False

def test_pipeline_history():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/pipeline/history")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            builds = data.get("builds", [])
            passed = resp.status == 200 and len(builds) > 0
            log_test("Pipeline Build History API (/api/pipeline/history)", passed, f"Total builds returned: {len(builds)}, Latest Build: #{builds[0].get('build_number')}")
            return passed
    except Exception as e:
        log_test("Pipeline Build History API (/api/pipeline/history)", False, str(e))
        return False

def test_pipeline_trigger():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/pipeline/run", method="POST")
        req.add_header("Content-Type", "application/json")
        payload = json.dumps({"trigger_by": "Automated Integration Test Runner"}).encode("utf-8")
        with urllib.request.urlopen(req, data=payload, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            build = data.get("build", {})
            passed = resp.status == 201 and build.get("status") == "SUCCESS"
            stages_count = len(build.get("stages", []))
            log_test("Pipeline Execution Trigger (/api/pipeline/run)", passed, f"Triggered Build #{build.get('build_number')}, Stages Completed: {stages_count}/6")
            return passed
    except Exception as e:
        log_test("Pipeline Execution Trigger (/api/pipeline/run)", False, str(e))
        return False

def test_puppet_compliance():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/puppet/compliance")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rate = data.get("compliance_rate")
            resources = data.get("resources", [])
            passed = resp.status == 200 and rate == "100%" and len(resources) > 0
            log_test("Puppet Configuration Compliance API (/api/puppet/compliance)", passed, f"Compliance Rate: {rate}, Managed Resources: {len(resources)}")
            return passed
    except Exception as e:
        log_test("Puppet Configuration Compliance API (/api/puppet/compliance)", False, str(e))
        return False

def test_artifacts():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/artifacts")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            artifacts = data.get("artifacts", [])
            passed = resp.status == 200 and len(artifacts) >= 2
            log_test("Artifact Registry Verification (/api/artifacts)", passed, f"Found {len(artifacts)} published artifacts (Maven JAR + Docker Image)")
            return passed
    except Exception as e:
        log_test("Artifact Registry Verification (/api/artifacts)", False, str(e))
        return False

def main():
    print("=" * 70)
    print("BuildForge Enterprise CI/CD Pipeline - Automated Test Suite")
    print("Target Ingress: " + BASE_URL)
    print("=" * 70)
    
    tests = [
        test_nginx_dashboard,
        test_health_probe,
        test_pipeline_history,
        test_pipeline_trigger,
        test_puppet_compliance,
        test_artifacts
    ]
    
    results = [t() for t in tests]
    passed_count = sum(results)
    total_count = len(results)
    
    print("=" * 70)
    print(f"Summary: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.1f}%)")
    print("=" * 70)
    
    if passed_count == total_count:
        print("[SUCCESS] All BuildForge CI/CD pipeline tests passed successfully!")
        sys.exit(0)
    else:
        print("[ERROR] Some tests failed. Please inspect container logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
