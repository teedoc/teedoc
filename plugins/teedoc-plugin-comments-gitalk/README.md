teedoc-plugin-comments-gitalk
====


[gitalk](https://github.com/gitalk/gitalk) comment support for [teedoc](https://github.com/Neutree/teedoc)

Create [applications](https://github.com/settings/applications/new) first, callback url set page that have gitalk(default doc and blog pages),`https://teedoc.github.io/get_started/zh/` for example.

config example:
```json
"teedoc-plugin-comments-gitalk": {
            "from": "pypi",
            "config": {
                "classes": [
                    "type_doc",
                    "type_blog"
                ],
                "env": {
                    "clientID": "*****",
                    "clientSecret": "********",
                    "repo": "teedoc.github.io",
                    "owner": "teedoc",
                    "admin": ["Neutree"]
                }
            }
        }
```

admin can directly comment, it will automatically create issue
and you can create issue manually for one page, and then set issue number in markdown metadata:
```markdown
---
title: *****
gitalk-number: 2
---
```

or create label for issue, need `Gitalk` and one other lable like `Demo`, like [official issue](https://github.com/gitalk/gitalk/issues/1), and set id for page
```markdown
---
title: *****
id: Demo
---
```
or
```markdown
---
title: *****
gitalk-id: Demo
---
```
