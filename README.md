# vercel-pw-protection

This plugin overwrites your `vercel.json`'s `routes` attribute so that your deployment is password protected.

Login on demo: https://mkdocs-vercel-pw-plugin.vercel.app/#Monkey123!

This plugin is an implementation of the cookie method from `https://github.com/six-two/mkdocs-vercel-basic-auth-example`.

Prerequesites:
You have created a `vercel.json` file and it does not have any existing `routes`.

## Usage

Install the package via pip:
```bash
pip install mkdocs-vercel-pw-plugin
```

Then add the plugin to your `mkdocs.yml`:
```yaml
plugins:
- vercel_pw:
    cookie_name: JSESSIONID
    password: Monkey123!
    restrict_to_domain: mkdocs-pw-protection.vercel.app
    vercel_json_path: ../vercel.json
```

Optional:
You can link to `/logout.html`.

You need to run a successful build (`mkdocs build` or `mkdocs serve`) after changing the config before pushing your changes to Vercel.
This is because the `vercel.json` is only updated after a build is performed.

## Customization

By default the "login" page mimics the Vercel deployment not found page.
This serves as a small security by obscurity measure.
Of course you can also provide your own `docs/deployment_not_found.html` that instead shows a login form or something like that.

## Notable changes

### Version HEAD

- Use hex encoding instead of base64.
    The issue is that vercel's header matching is case insensitive, which makes password brute forcing much easier.
    For example if the password was `aa` (`YWE=`), the password `c` (`YwE=`) would also be accepted.

### Version 0.0.2

- Hide the `Plugin 'vercel_pw' was specified multiple times` warning
