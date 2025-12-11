#!/usr/bin/env python3
"""
CrewAI Component Services Setup Script

This script initializes the CrewAI component services:
1. Removes old ChromaDB files (if exists)
2. Starts Docker services
3. Waits for services to be healthy
4. Triggers component indexing from crewai_components/

Usage:
    python setup.py [--force-reindex]

Options:
    --force-reindex    Force reindex even if ChromaDB already exists
"""

import os
import sys
import time
import shutil
import requests
import subprocess
from pathlib import Path


class SetupManager:
    """Manages setup and initialization of CrewAI services"""

    def __init__(self, force_reindex: bool = False):
        self.force_reindex = force_reindex
        self.chromadb_path = Path("component-index/data/chromadb")
        self.generator_url = "http://localhost:8085"
        self.index_url = "http://localhost:8086"

    def print_step(self, step: str, emoji: str = "🔧"):
        """Print a setup step"""
        print(f"\n{emoji} {step}")
        print("=" * 80)

    def cleanup_chromadb(self):
        """Remove ChromaDB files to force fresh indexing"""
        self.print_step("Cleaning up ChromaDB files", "🧹")

        if self.chromadb_path.exists():
            print(f"Removing: {self.chromadb_path}")
            shutil.rmtree(self.chromadb_path)
            print("✅ ChromaDB files removed")
        else:
            print("ℹ️  No existing ChromaDB found (clean state)")

    def start_services(self):
        """Start Docker services"""
        self.print_step("Starting Docker services", "🐳")

        # Stop any existing services
        print("Stopping existing services...")
        subprocess.run(["docker-compose", "down"], check=False)

        # Build and start services
        print("\nBuilding and starting services...")
        result = subprocess.run(
            ["docker-compose", "up", "-d", "--build"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Failed to start services:\n{result.stderr}")
            sys.exit(1)

        print("✅ Services started")

    def wait_for_health(self, service_name: str, url: str, max_retries: int = 30):
        """Wait for service to be healthy"""
        print(f"\nWaiting for {service_name} to be healthy...")

        for i in range(max_retries):
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {service_name} is healthy")
                    return True
            except Exception:
                pass

            print(f"  Retry {i+1}/{max_retries}...", end="\r")
            time.sleep(2)

        print(f"\n❌ {service_name} failed to become healthy")
        return False

    def wait_for_services(self):
        """Wait for all services to be healthy"""
        self.print_step("Waiting for services to be ready", "⏳")

        # Wait for component-index service
        if not self.wait_for_health(
            "Component Index",
            f"{self.index_url}/api/crewai/component-index/health"
        ):
            sys.exit(1)

        # Wait for component-generator service
        if not self.wait_for_health(
            "Component Generator",
            f"{self.generator_url}/api/crewai/component-generator/health"
        ):
            sys.exit(1)

        print("\n✅ All services ready")

    def trigger_indexing(self):
        """Trigger component indexing"""
        self.print_step("Indexing components from crewai_components/", "📚")

        try:
            response = requests.post(
                f"{self.index_url}/api/crewai/component-index/patterns/index",
                json={"force_reindex": True},
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Indexed {data.get('tools_indexed', 0)} tools")
                print(f"   Platform: {data.get('platform', 'N/A')}")
            else:
                print(f"❌ Indexing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                sys.exit(1)

        except Exception as e:
            print(f"❌ Indexing failed: {str(e)}")
            sys.exit(1)

    def verify_setup(self):
        """Verify setup by checking stats"""
        self.print_step("Verifying setup", "✅")

        try:
            # Check pattern stats
            response = requests.get(
                f"{self.index_url}/api/crewai/component-index/patterns/stats",
                timeout=10
            )

            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Pattern engine stats:")
                print(f"   Total tools: {stats.get('total_tools', 0)}")
                print(f"   Has embeddings: {stats.get('has_embeddings', False)}")

            # Check health endpoint
            response = requests.get(
                f"{self.index_url}/api/crewai/component-index/health",
                timeout=10
            )

            if response.status_code == 200:
                health = response.json()
                print(f"\n✅ Service health:")
                print(f"   Status: {health.get('status', 'unknown')}")
                print(f"   Version: {health.get('version', 'unknown')}")

        except Exception as e:
            print(f"⚠️  Verification failed: {str(e)}")

    def run(self):
        """Run complete setup process"""
        print("\n" + "=" * 80)
        print("  CrewAI Component Services - Setup & Initialization")
        print("=" * 80)

        # Step 1: Cleanup ChromaDB
        if self.force_reindex:
            self.cleanup_chromadb()

        # Step 2: Start services
        self.start_services()

        # Step 3: Wait for services
        self.wait_for_services()

        # Step 4: Trigger indexing
        self.trigger_indexing()

        # Step 5: Verify
        self.verify_setup()

        # Success
        print("\n" + "=" * 80)
        print("  ✅ Setup complete!")
        print("=" * 80)
        print("\n📍 Services running at:")
        print(f"   - Component Generator: {self.generator_url}/api/crewai/component-generator/health")
        print(f"   - Component Index:     {self.index_url}/api/crewai/component-index/health")
        print("\n📖 Next steps:")
        print("   - Run tests: python test_all_endpoints.py")
        print("   - View logs: docker-compose logs -f")
        print("   - Stop services: docker-compose down")
        print("\n")


if __name__ == "__main__":
    force_reindex = "--force-reindex" in sys.argv

    manager = SetupManager(force_reindex=force_reindex)
    manager.run()
