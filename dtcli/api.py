import json
import os
import requests as _requests_impl

# TODO: support pagination

class DynatraceAPIClient:
    def __init__(self, url, token, requests = None):
        self.url_base = url
        self.headers = {"Authorization": f"Api-Token {token}"}
        self.requests = requests if requests is not None else _requests_impl

    @classmethod
    def from_dev_tenant(cls, tenant, token):
        tenant_url = f"https://{tenant}.dev.dynatracelabs.com"
        return cls(tenant_url, token)

    @classmethod
    def from_tenant_url(cls, _tenant_url, token):
        tenant_url = f"{_tenant_url}"
        return cls(tenant_url, token)

    def acquire_extension_alert(self, alert_id: str):
        r = self.requests.get(self.url_base + f"/api/config/v1/anomalyDetection/metricEvents/" + alert_id, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def acquire_monitoring_configurations(self, fqdn: str):
        r = self.requests.get(self.url_base + f"/api/v2/extensions/{fqdn}/monitoringConfigurations", headers=self.headers)
        r.raise_for_status()
        return r.json()["items"]

    def acquire_environment_configuration(self, fqdn: str):
        # TODO: check the url if that 100% it
        r = self.requests.get(self.url_base + f"/api/v2/extensions/{fqdn}/environmentConfiguration", headers=self.headers)

        if r.status_code == 404:
            return

        r.raise_for_status()
        return r.json()

    def acquire_extensions(self):
        # TODO: check the url if that 100% it
        r = self.requests.get(self.url_base + f"/api/v2/extensions", headers=self.headers)
        r.raise_for_status()
        return r.json()["extensions"]

    def acquire_extension_versions(self, fqdn: str):
        # TODO: check the url if that 100% it
        r = self.requests.get(self.url_base + f"/api/v2/extensions/{fqdn}", headers=self.headers)

        r.raise_for_status()
        return r.json()["extensions"]

    def delete_monitoring_configuration(self, fqdn: str, configuration_id: str):
        r = self.requests.delete(self.url_base + f"/api/v2/extensions/{fqdn}/monitoringConfigurations/{configuration_id}", headers=self.headers)
        try:
            r.raise_for_status()
        except:
            err = ""
            try:
                err = r.json()
            except:
                pass

            print(err)
            raise

    def delete_environment_configuration(self, fqdn: str):
        r = self.requests.delete(self.url_base + f"/api/v2/extensions/{fqdn}/environmentConfiguration", headers=self.headers)
        err = r.json()
        try:
            r.raise_for_status()
        except:
            print(err)
            if r.code != 404:
                raise

    def delete_extension(self, fqdn: str, version: str):
        r = self.requests.delete(self.url_base + f"/api/v2/extensions/{fqdn}/{version}", headers=self.headers)
        err = r.json()
        try:
            r.raise_for_status()
        except:
            print(err)
            if r.code != 404:
                raise

    def get_schema_target_version(self, target_version: str):
        """Get version number from tenant. If version doesn't exist return list of available versions."""
        versions = self.requests.get(self.url_base + "/api/v2/extensions/schemas", headers=self.headers).json().get("versions", [])

        if target_version == "latest":
            return versions[-1]

        matches = [v for v in versions if v.startswith(target_version)]
        if matches:
            return matches[0]

        print(f"Target version {target_version} does not exist. \nAvailable versions: {versions}")
        raise SystemExit

    def download_schemas(self, target_version: str, download_dir: str):
        """Downloads schemas from choosen version"""

        version = self.get_schema_target_version(target_version)

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            print("Directory for schemas created")

        print(f"Downloading schemas for version {version}")

        files = self.requests.get(self.url_base + f"/api/v2/extensions/schemas/{version}", headers=self.headers).json().get("files", [])
        for file in files:
            schema = self.requests.get(self.url_base + f"/api/v2/extensions/schemas/{version}/{file}", headers=self.headers).json()
            with open(file=f"{download_dir}/{file}", mode="w") as f:
                json.dump(schema, f, indent=2)

        print("Finished")

        return 0

    def point_environment_configuration_to(self, fqdn: str, version: str):
        r = self.requests.put(self.url_base + f"/api/v2/extensions/{fqdn}/environmentConfiguration", headers=self.headers, json={"version": version})
        err = r.json()
        try:
            r.raise_for_status()
        except:
            print(err)
            raise
