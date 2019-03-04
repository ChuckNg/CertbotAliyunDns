Aliyun DNS Authenticator plugin for Certbot
===============================================
This plugin design for user using Certbot to create free Let's Encrypt license
on Aliyun and using Aliyun DNS for authentication challenge. This plugin only
for personal study and internal usage.

Overall coding style based on certbot-dns-google, thanks to contributors of
this project.

Installation
------------
    pip install -e $CWD

Execution
---------
.. code-block:: bash

    $ certbot certonly --certbot-dns-aliyun:dns-aliyun-propagation-seconds 10  \
                       --certbot-dns-aliyun:dns-aliyun-credentials $PATH_TO_CREDENTIALS/aliyun.json \
                       -d "$YOUR_DOMAIN"

Reference
---------
1. certbot-dns-google, https://github.com/certbot/certbot/tree/master/certbot-dns-google
2. Certbot - Developer Guide, https://certbot.eff.org/docs/contributing.html#writing-your-own-plugin
3. Certbot - API Documentation -certbot.plugins.dns_common, https://certbot.eff.org/docs/api/plugins/dns_common.html
