import binascii
import json
import os
import shutil
from typing import Optional
# pip install mkdocs
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.config import base, config_options as c
from mkdocs.exceptions import PluginError

TERRIBLE_PASSWORDS = [
    # Source: https://en.wikipedia.org/wiki/List_of_the_most_common_passwords
    "123456",
	"123456789",
 	"qwerty",
 	"password",
 	"12345678",
 	"111111",
 	"123123",
 	"1234567890",
 	"1234567",
 	"qwerty123",
 	"000000",
 	"1q2w3e",
 	"aa12345678",
 	"abc123",
 	"password1",
 	"qwertyuiop",
 	"123321",
 	"password123"
    # Trivial passwords
    "admin",
    "vercel",
    "mkdocs"
]


def generate_vercel_json_routes(cookie_name: str, cookie_value: str, restrict_to_domain: Optional[str] = None) -> list[dict]:
    routes: list[dict] = []
    if restrict_to_domain:
        # Deployment called via a secundary domain name (like the deployment or branch name) -> reject all requests
        routes.append({
            "src": "/.*",
            "missing": [{
                "type": "header",
                "key": "host",
                "value": restrict_to_domain,
            }],
            "dest": "/deployment_forbidden.html",
            "status": 403,
        })

    # Reject all requests without the correct cookie
    routes.append({
        "src": "/.*",
        "missing": [{
            "type": "header",
            "key": "cookie",
            "value": f".*{cookie_name}={cookie_value}.*"
        }],
        "dest": "/deployment_not_found.html",
        "status": 404
    })

    return routes


class MyConfig(base.Config):
    cookie_name = c.Type(str, default="ID")
    password = c.Type(str)
    restrict_to_domain = c.Optional(c.Type(str))
    vercel_json_path = c.Type(str, default="../vercel.json")


class VercelJsonModifierPlugin(BasePlugin[MyConfig]):
    supports_multiple_instances = True

    def on_config(self, config):
        path = os.path.join(config['docs_dir'], self.config['vercel_json_path'])
        if not os.path.exists(path):
            raise PluginError(f"File referenced by 'vercel_json_path' does not exist: {path}")
        
        # Do sanity checking on the password
        if len(self.config.password) < 6:
            raise PluginError(f"Password needs to be at least 6 characters long")
        if self.config.password.lower() in TERRIBLE_PASSWORDS:
            raise PluginError(f"That is a really terrible password, because it is very common. If I had to guess it, it would take only a couple of seconds. Please generate a strong and random password.")
        if self.config.password.startswith("ENV "):
            get_plugin_logger(__name__).warning("Your password starts with 'ENV '. Did you mean '!ENV ', which is used to expand an environment variable?")

        return config

    def on_post_build(self, config):
        self.perform_all_actions(config)

    def perform_all_actions(self, config):
        try:
            self.modify_vercel_json(config)

            if self.config['restrict_to_domain']:
                self.copy_html_file_if_it_does_not_exist(config, "deployment_forbidden.html")

            self.copy_html_file_if_it_does_not_exist_and_replace_cookie_name(config, "deployment_not_found.html")

            self.copy_html_file_if_it_does_not_exist_and_replace_cookie_name(config, "logout.html")
        except Exception as e:
            raise PluginError(f"Error modifying vercel.json or copying HTML files: {e}")

    def modify_vercel_json(self, config):
        path = os.path.join(config['docs_dir'], self.config['vercel_json_path'])

        # Load the vercel.json file
        with open(path, 'r') as file:
            vercel_json = json.load(file)

        # Modify the routes attribute
        cookie_name = self.config['cookie_name']
        cookie_value = binascii.hexlify(self.config['password'].encode()).decode()
        restrict_to_domain = self.config['restrict_to_domain']
        vercel_json['routes'] = generate_vercel_json_routes(cookie_name, cookie_value, restrict_to_domain)

        # Save the changes
        with open(path, 'w') as file:
            json.dump(vercel_json, file, indent=4)

    def copy_html_file_if_it_does_not_exist_and_replace_cookie_name(self, config, relative_path: str):
        self.copy_html_file_if_it_does_not_exist(config, relative_path)
        self.replace_in_file(config, relative_path, "{{COOKIE_NAME}}", self.config['cookie_name'])


    def copy_html_file_if_it_does_not_exist(self, config, relative_path: str):
        to_file = os.path.join(config['site_dir'], relative_path)
        if not os.path.exists(to_file):
            # Create parent directory
            os.makedirs(os.path.dirname(to_file), exist_ok=True)

            # Copy file
            from_file = os.path.join(os.path.dirname(__file__), relative_path)
            shutil.copy(from_file, to_file)

    def replace_in_file(self, config, relative_path: str, search_for: str, replace_with: str):
        path = os.path.join(config['site_dir'], relative_path)
        with open(path) as f:
            contents = f.read()

        contents = contents.replace(search_for, replace_with)
        with open(path, "w") as f:
            f.write(contents)

