teedoc-plugin-assets
====


Add css and js items(/files) to pages or other custom items to pages


`site_config.json`:

```json
{
    "route": {
            "assets": {
                "/static/": "static",
            },
        },
    "plugins": {
        "teedoc-plugin-assets":{
            "from": "pypi",
            "config": {
                "header_items": [
                    "/static/css/custom.css",
                    "<meta name=\"plugin-assets\" content=\"example meta item\">"
                ],
                "footer_items": [
                    "/static/css/custom.js"
                ],
                "env":{
                    "main_color": "#000000"
                }
            }
        },
    }
}
```

`custom.css`:

```css
a {
    color: ${main_color}
}
```




