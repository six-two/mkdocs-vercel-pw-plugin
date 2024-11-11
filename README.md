# MkDocs Vercel Password Protection Plugin

This plugin allows you to password protect your site if it is deployed by [Vercel](https://vercel.com).
It works by overwriting your `vercel.json`'s `routes` attribute so that your deployment can only be accessed with the correct cookie.
If users without the cookie try to visit your site they are shown a `Deployment not found` decoy page by default.
By visiting the decoy page with the password in the URL hash, you can set the correct cookie and access the site.

More detailed information can be found in my [mkdocs-vercel-basic-auth-example](https://github.com/six-two/mkdocs-vercel-basic-auth-example) repository in the `cookie` and `cookie-killswitch` folders.

## Demo

This plugin has a corresponding demo page, which is hosted by Vercel.
If you try to access it normally, it should not work and you should see `Deployment not found`: <https://mkdocs-vercel-pw-plugin.vercel.app/>

If you access it with the correct password, it should be accessible: <https://mkdocs-vercel-pw-plugin.vercel.app/#Täßt😀Emoji>
Your credentials are stored, so if you visit <https://mkdocs-vercel-pw-plugin.vercel.app/> afterwards you should still be logged in.

You will stay logged in until the cookie expires (after about a year), you delete your cookies or you log out.
After any of these cases <https://mkdocs-vercel-pw-plugin.vercel.app/> should show you the default `Deployment not found` page again.

## Usage

Prerequesites:
You have created a `vercel.json` file and it does not have any existing `routes`.

Install the package via pip:
```bash
pip install mkdocs-vercel-pw-plugin
```

Then add the plugin to your `mkdocs.yml`:
```yaml
plugins:
- search
- vercel_pw:
    cookie_name: JSESSIONID
    password: Täßt😀Emoji
    restrict_to_domain: mkdocs-vercel-pw-plugin.vercel.app
    vercel_json_path: ../vercel.json
```

Optional:
You can link to `/logout.html`.

You need to run a successful build (`mkdocs build` or `mkdocs serve`) after changing the config before pushing your changes to Vercel.
This is because the `vercel.json` is only updated after a build is performed.

### Password in environment variable

If you want to obscure the password a little bit, you can use an [environment variable](https://www.mkdocs.org/user-guide/configuration/#environment-variables) instead of the plain password in the `mkdocs.yml`:

```yaml
plugins:
- search
- vercel_pw:
    cookie_name: JSESSIONID
    password: !ENV MKDOCS_VERCEL_PW_DEMO_APP
    restrict_to_domain: mkdocs-vercel-pw-plugin.vercel.app
    vercel_json_path: ../vercel.json
```

You can the set and export the environment variable or pass it directly to mkdocs:
```bash
MKDOCS_VERCEL_PW_DEMO_APP=Täßt😀Emoji mkdocs serve
```

In this case, anyone with access to the source code can still access your site using the value in the `vercel.json` file, and they can also hex-decode that value to get your original password.
If you use an environment variable, you also need to set it in the CI/CD pipeline, otherwise this plugin will abort the build, since the missing `password` parameter is not set.

But I am not sure if you need the same password there, since I would guess that the `vercel.json` file is fully read and processed, before its values like `buildCommand` are executed. Thus any modifications that the plugin does should theoretically not affect the deployed site. But I havent tested that.

## Customization

By default the "login" page mimics the Vercel deployment not found page.
This serves as a small security by obscurity measure.
Of course you can also provide your own `docs/deployment_not_found.html` that instead shows a login form or something like that.

## Notable changes

### Head

- Perform basic sanity checks on password.


### Version 0.1.0

- Use hex encoding instead of base64.
    The issue is that vercel's header matching is case insensitive, which makes password brute forcing much easier.
    For example if the password was `aa` (`YWE=`), the password `c` (`YwE=`) would also be accepted.
    The new encoding should also accept Unicode characters like Umlauts, emojis, etc.
    But I would recommend sticking to ASCII, since Unicode is tricky and I am not sure if JavaScript and Python handle encoding exactly the same.

### Version 0.0.2

- Hide the `Plugin 'vercel_pw' was specified multiple times` warning
