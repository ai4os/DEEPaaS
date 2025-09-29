#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import json
import sys
import requests


def get_openapi_spec(base_url):
    """Retrieve the OpenAPI spec from the given base URL."""
    response = requests.get(f"{base_url}/swagger.json", timeout=5)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()


def compare_endpoints(old_spec, new_spec, model_name):
    """Compare endpoints in both OpenAPI specs.

    This method ignoring methods that have been removed.
    """
    old_paths = set(old_spec["paths"].keys())
    new_paths = set(new_spec["paths"].keys())

    removed_paths = [f"/v2/models/{model_name}/train"]
    for path in removed_paths:
        old_paths.discard(path)

    # Find paths that are in new but not in old
    missing_in_old = new_paths - old_paths

    if missing_in_old:
        print("The following endpoints are missing in the old API:")
        for path in missing_in_old:
            print(f" - {path}")

    # Check if all old paths (except removed) are in the new API
    missing_in_new = old_paths - new_paths

    if missing_in_new:
        print("The following endpoints are missing in the new API:")
        for path in missing_in_new:
            print(f" - {path}")

    return old_paths.intersection(new_paths)


def test_endpoint(old_url, new_url, method, endpoint, debug=False):
    """Test both endpoints and check if responses are equivalent."""
    old_response = requests.request(method, old_url + endpoint)
    new_response = requests.request(method, new_url + endpoint)

    # If both return 405 Method Not Allowed, that's expected for
    # some method/endpoint combinations
    if old_response.status_code == 405 and new_response.status_code == 405:
        return True

    if old_response.status_code != new_response.status_code:
        error_msg = (
            f"Status code mismatch for {method} {endpoint}: "
            f"Old: {old_response.status_code}, New: {new_response.status_code}"
        )
        if debug:
            try:
                old_body = old_response.json()
                new_body = new_response.json()
                error_msg += f"\nOld response: {json.dumps(old_body, indent=2)}"
                error_msg += f"\nNew response: {json.dumps(new_body, indent=2)}"
            except ValueError:
                old_text = (
                    old_response.text[:500] + "..."
                    if len(old_response.text) > 500
                    else old_response.text
                )
                new_text = (
                    new_response.text[:500] + "..."
                    if len(new_response.text) > 500
                    else new_response.text
                )
                error_msg += f"\nOld response: {old_text}"
                error_msg += f"\nNew response: {new_text}"

        raise AssertionError(error_msg)

    # Only compare JSON responses if status code indicates success
    if 200 <= old_response.status_code < 300:
        try:
            old_data = old_response.json()
            new_data = new_response.json()

            if old_data != new_data:
                error_msg = f"Response mismatch for {method} {endpoint}"
                if debug:
                    error_msg += f"\nOld response: {json.dumps(old_data, indent=2)}"
                    error_msg += f"\nNew response: {json.dumps(new_data, indent=2)}"

                    # Find differences in keys
                    old_keys = set(
                        old_data.keys()
                        if isinstance(old_data, dict)
                        else range(len(old_data))
                    )
                    new_keys = set(
                        new_data.keys()
                        if isinstance(new_data, dict)
                        else range(len(new_data))
                    )

                    if old_keys != new_keys:
                        only_in_old = old_keys - new_keys
                        only_in_new = new_keys - old_keys

                        if only_in_old:
                            error_msg += (
                                f"\nKeys only in old response: {sorted(only_in_old)}"
                            )
                        if only_in_new:
                            error_msg += (
                                f"\nKeys only in new response: {sorted(only_in_new)}"
                            )

                    # Show differing values for common keys
                    if isinstance(old_data, dict) and isinstance(new_data, dict):
                        common_keys = old_keys.intersection(new_keys)
                        different_values = {
                            k: (old_data[k], new_data[k])
                            for k in common_keys
                            if old_data[k] != new_data[k]
                        }

                        if different_values:
                            error_msg += "\nDiffering values for common keys:"
                            for k, (old_val, new_val) in different_values.items():
                                error_msg += f"\n  {k}:"
                                error_msg += f"\n    Old: {old_val}"
                                error_msg += f"\n    New: {new_val}"

                raise AssertionError(error_msg)
        except ValueError as e:
            if debug:
                raise AssertionError(
                    f"JSON parsing failed: {e}\nOld: {old_response.text}"
                    f"\nNew: {new_response.text}"
                )
            else:
                raise AssertionError(f"JSON parsing failed: {e}")

    return True


def run_tests(old_api_url, new_api_url, model_name, debug=False):
    """Run all tests and return results."""
    test_results = {"passed": 0, "failed": 0, "errors": []}

    # Retrieve OpenAPI specifications
    try:
        old_openapi_spec = get_openapi_spec(old_api_url)
        new_openapi_spec = get_openapi_spec(new_api_url)
    except requests.exceptions.RequestException as e:
        test_results["errors"].append(f"Failed to retrieve OpenAPI specs: {e}")
        return test_results

    # Compare endpoints and get common paths
    common_paths = compare_endpoints(old_openapi_spec, new_openapi_spec, model_name)

    # Testing the endpoints
    for endpoint in common_paths:
        # We will loop through all HTTP methods available in the old API
        for method in ["GET", "POST", "PUT", "DELETE"]:
            try:
                test_endpoint(old_api_url, new_api_url, method, endpoint, debug)
                print(f"\033[92mTest passed for {method}\033[0m {endpoint}")
                test_results["passed"] += 1
            except Exception as e:
                print(f"\033[91mTest failed for {method}\033[0m {endpoint}")
                test_results["failed"] += 1
                test_results["errors"].append(f"{method} {endpoint}: {str(e)}")
                if debug:
                    print(f"  Error details: {str(e)}")

    return test_results


# For pytest integration
def test_api_endpoints(old_api_url, new_api_url, model_name, debug=False):
    """Pytest-compatible test function."""
    import pytest

    # Retrieve OpenAPI specifications
    old_openapi_spec = get_openapi_spec(old_api_url)
    new_openapi_spec = get_openapi_spec(new_api_url)

    # Compare endpoints and get common paths
    common_paths = compare_endpoints(old_openapi_spec, new_openapi_spec, model_name)

    # Testing the endpoints
    for endpoint in common_paths:
        # We will loop through all HTTP methods available in the old API
        for method in ["GET", "POST", "PUT", "DELETE"]:
            try:
                assert test_endpoint(
                    old_api_url, new_api_url, method, endpoint, debug
                )  # nosec
            except AssertionError as e:
                pytest.fail(str(e))


def main():
    """Main function to test the API endpoints."""
    parser = argparse.ArgumentParser(
        description="DEEPaaS API v2 to v3 migration test script"
    )
    parser.add_argument(
        "--old-api-base-url",
        default="http://127.0.0.1:5000",
        help="Base URL of the old API",
    )
    parser.add_argument(
        "--new-api-base-url",
        default="http://127.0.0.1:5001",
        help="Base URL of the new API",
    )
    parser.add_argument(
        "--model-name",
        default="demo_app",
        help="Name of the model to test. To make testing easier, you should provide "
        "the name of the model you want to test.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show detailed debug information for failed tests",
    )

    args = parser.parse_args()

    results = run_tests(
        args.old_api_base_url, args.new_api_base_url, args.model_name, args.debug
    )

    # Print summary
    print("\nTest Summary:")
    print(f"\tPassed: \033[92m{results['passed']}\033[0m")
    print(f"\tFailed: \033[91m{results['failed']}\033[0m")

    if results["failed"] > 0 and args.debug:
        print("\nDetailed Errors:")
        for i, error in enumerate(results["errors"], 1):
            print(f"\n{i}. {error}")

    # Return non-zero exit code if any tests failed
    if results["failed"] > 0:
        sys.exit(1)


# Pytest integration functions
def pytest_addoption(parser):
    """Add command line options to pytest."""
    parser.addoption(
        "--old-api-base-url",
        default="http://127.0.0.1:5000",
        help="Base URL of the old API",
    )
    parser.addoption(
        "--new-api-base-url",
        default="http://127.0.0.1:5001",
        help="Base URL of the new API",
    )
    parser.addoption(
        "--model-name", default="demo_app", help="Name of the model to test"
    )
    parser.addoption(
        "--debug",
        action="store_true",
        help="Show detailed debug information for failed tests",
    )


def pytest_generate_tests(metafunc):
    """Generate test configurations."""
    if {"old_api_url", "new_api_url", "model_name", "debug"}.intersection(
        metafunc.fixturenames
    ):
        old_api_url = metafunc.config.getoption("old_api_base_url")
        new_api_url = metafunc.config.getoption("new_api_base_url")
        model_name = metafunc.config.getoption("model_name")
        debug = metafunc.config.getoption("debug")

        params = {}
        if "old_api_url" in metafunc.fixturenames:
            params["old_api_url"] = [old_api_url]
        if "new_api_url" in metafunc.fixturenames:
            params["new_api_url"] = [new_api_url]
        if "model_name" in metafunc.fixturenames:
            params["model_name"] = [model_name]
        if "debug" in metafunc.fixturenames:
            params["debug"] = [debug]

        metafunc.parametrize(",".join(params.keys()), list(zip(*params.values())))


if __name__ == "__main__":
    main()
else:
    # When imported as a module, provide the necessary pytest hooks and test functions
    __all__ = ["test_api_endpoints", "pytest_addoption", "pytest_generate_tests"]
