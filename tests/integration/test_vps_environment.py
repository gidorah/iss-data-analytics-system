"""
Integration test for VPS environment validation
Task 2.1.5: Automated test to verify VPS meets all technical requirements
Requirements: T002-FR02, T002-NR02
"""

import platform
import shutil
import subprocess

import psutil
import pytest
import requests


class TestVPSEnvironment:
    """Integration tests for VPS environment validation according to T002 requirements"""

    def test_cpu_requirements(self):
        """Verify CPU meets minimum requirements (≥2 cores)"""
        cpu_count = psutil.cpu_count(logical=True)
        assert cpu_count >= 2, f"CPU cores {cpu_count} < minimum required 2 cores"

        # Additional validation: physical cores
        physical_cores = psutil.cpu_count(logical=False)
        assert physical_cores >= 1, f"Physical cores {physical_cores} < minimum 1"

        print(
            f"✅ CPU validation passed: {cpu_count} logical cores, {physical_cores} physical cores"
        )

    def test_memory_requirements(self):
        """Verify RAM meets minimum requirements (≥4GB)"""
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)  # Convert bytes to GB

        assert memory_gb >= 4.0, f"RAM {memory_gb:.2f}GB < minimum required 4GB"

        # Additional validation: available memory
        available_gb = memory.available / (1024**3)
        assert available_gb >= 1.0, f"Available RAM {available_gb:.2f}GB < minimum 1GB"

        print(
            f"✅ Memory validation passed: {memory_gb:.2f}GB total, {available_gb:.2f}GB available"
        )

    def test_disk_requirements(self):
        """Verify disk space meets minimum requirements (≥50GB available)"""
        disk_usage = psutil.disk_usage("/")
        disk_free_gb = disk_usage.free / (1024**3)  # Convert bytes to GB
        disk_total_gb = disk_usage.total / (1024**3)

        assert disk_free_gb >= 50.0, (
            f"Free disk space {disk_free_gb:.2f}GB < minimum required 50GB"
        )

        print(
            f"✅ Disk validation passed: {disk_free_gb:.2f}GB free of {disk_total_gb:.2f}GB total"
        )

    def test_docker_installation(self):
        """Verify Docker is installed and meets version requirements (≥20.x)"""
        docker_path = shutil.which("docker")
        assert docker_path is not None, "Docker not found in PATH"

        # Check Docker version
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )
            assert result.returncode == 0, (
                f"Docker version check failed: {result.stderr}"
            )

            version_output = result.stdout.strip()
            # Extract version number (format: Docker version 20.10.x, build ...)
            version_parts = version_output.split()
            version_str = version_parts[2].rstrip(",")
            major_version = int(version_str.split(".")[0])

            assert major_version >= 20, (
                f"Docker version {version_str} < minimum required 20.x"
            )

            print(f"✅ Docker validation passed: {version_output}")

        except subprocess.TimeoutExpired:
            pytest.fail("Docker version check timed out")
        except (subprocess.CalledProcessError, IndexError, ValueError) as e:
            pytest.fail(f"Docker version validation failed: {e}")

    def test_docker_daemon_running(self):
        """Verify Docker daemon is running and accessible"""
        try:
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, timeout=15
            )
            assert result.returncode == 0, (
                f"Docker daemon not accessible: {result.stderr}"
            )

            # Check for key indicators that Docker is properly running
            output = result.stdout.lower()
            assert "containers:" in output, (
                "Docker daemon output missing container information"
            )
            assert "images:" in output, "Docker daemon output missing image information"

            print(
                "✅ Docker daemon validation passed: Docker daemon is running and accessible"
            )

        except subprocess.TimeoutExpired:
            pytest.fail("Docker daemon check timed out")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Docker daemon check failed: {e}")

    def test_network_outbound_https(self):
        """Verify outbound HTTPS connectivity to required services"""
        test_endpoints = {
            "GitHub API": "https://api.github.com",
            "Let's Encrypt": "https://acme-v02.api.letsencrypt.org",
            "Docker Registry": "https://registry-1.docker.io",
        }

        for service_name, url in test_endpoints.items():
            try:
                response = requests.head(url, timeout=10, allow_redirects=True)
                assert response.status_code in [200, 301, 302, 404], (
                    f"{service_name} ({url}) returned status {response.status_code}"
                )

                print(
                    f"✅ Network connectivity to {service_name}: HTTP {response.status_code}"
                )

            except requests.exceptions.Timeout:
                pytest.fail(f"Network timeout connecting to {service_name} ({url})")
            except requests.exceptions.ConnectionError:
                pytest.fail(f"Network connection failed to {service_name} ({url})")
            except Exception as e:
                pytest.fail(f"Network test failed for {service_name} ({url}): {e}")

    def test_dns_resolution(self):
        """Verify DNS resolution for critical services"""
        import socket

        critical_domains = [
            "api.github.com",
            "acme-v02.api.letsencrypt.org",
            "registry-1.docker.io",
        ]

        for domain in critical_domains:
            try:
                socket.gethostbyname(domain)
                print(f"✅ DNS resolution successful for {domain}")
            except socket.gaierror as e:
                pytest.fail(f"DNS resolution failed for {domain}: {e}")

    def test_container_execution_capability(self):
        """Verify Docker can pull and run containers successfully"""
        test_image = "hello-world:latest"

        try:
            # Pull test image
            pull_result = subprocess.run(
                ["docker", "pull", test_image],
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert pull_result.returncode == 0, (
                f"Docker pull failed: {pull_result.stderr}"
            )

            # Run test container
            run_result = subprocess.run(
                ["docker", "run", "--rm", test_image],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert run_result.returncode == 0, f"Docker run failed: {run_result.stderr}"
            assert "Hello from Docker!" in run_result.stdout, (
                "Expected Docker output not found"
            )

            print("✅ Container execution capability validated")

        except subprocess.TimeoutExpired:
            pytest.fail("Container execution test timed out")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Container execution test failed: {e}")

    def test_system_architecture_compatibility(self):
        """Verify system architecture is compatible with deployment requirements"""
        arch = platform.machine().lower()
        compatible_archs = ["x86_64", "amd64", "aarch64", "arm64"]

        assert arch in compatible_archs, (
            f"System architecture {arch} not in compatible list: {compatible_archs}"
        )

        print(f"✅ Architecture compatibility validated: {arch}")

    def test_environment_summary(self):
        """Provide comprehensive environment summary"""
        summary = {
            "CPU Cores": psutil.cpu_count(logical=True),
            "Physical Cores": psutil.cpu_count(logical=False),
            "RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
            "Available RAM (GB)": round(
                psutil.virtual_memory().available / (1024**3), 2
            ),
            "Free Disk (GB)": round(psutil.disk_usage("/").free / (1024**3), 2),
            "Total Disk (GB)": round(psutil.disk_usage("/").total / (1024**3), 2),
            "Architecture": platform.machine(),
            "Platform": platform.system(),
            "Python Version": platform.python_version(),
        }

        print("\n" + "=" * 50)
        print("VPS ENVIRONMENT VALIDATION SUMMARY")
        print("=" * 50)
        for key, value in summary.items():
            print(f"{key:20}: {value}")
        print("=" * 50)

        # All values should pass minimum requirements
        assert summary["CPU Cores"] >= 2
        assert summary["RAM (GB)"] >= 4.0
        assert summary["Free Disk (GB)"] >= 50.0

        print("✅ All VPS environment requirements validated successfully")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])
