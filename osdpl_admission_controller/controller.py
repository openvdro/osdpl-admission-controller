# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

import falcon
import jsonschema


class ControllerResource(object):
    def on_post(self, req, resp):
        try:
            body = json.loads(req.stream.read())
        except Exception:
            raise falcon.HTTPBadRequest(
                'Missing HTTP POST body to validate.')
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               "schemas.json")) as f:
            schema_dict = json.load(f)
        # Validate admission request against schema
        jsonschema.Draft3Validator(schema_dict).is_valid(body)
        review_request = body.get('request', {})
        if not review_request:
            # Nothing to validate
            return
        if review_request.get('kind', {}).get('kind') != 'OpenStackDeployment':
            # We don't handle any other types of objects
            return

        features = review_request.get('object', {}).get('spec', {}).get(
            'features', {})
        # Validate key manager configuration
        if 'key-manager' in features.get('services', []):
            if 'backend' not in features.get('barbican', {}):
                raise falcon.HTTPBadRequest(
                    "Malformed OpenStackDeployment spec",
                    "If key-manager is enabled, you need to specify the "
                    "desired backend.")


def create_api():
    app = falcon.API()
    controller = ControllerResource()
    app.add_route('/validate', controller)
    return app
