base_fixtures_folder_path = 'tests.fixtures'

pytest_plugins = [
    f"{base_fixtures_folder_path}.login_endpoint_fixtures",
    f"{base_fixtures_folder_path}.refresh_endpoint_fixtures",
f"{base_fixtures_folder_path}.register_endpoint_fixtures",
]

