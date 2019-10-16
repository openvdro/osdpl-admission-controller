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
        resp.content_type = 'application/json'
        resp_body = {'kind': 'AdmissionReview', 'response': {'allowed': True}}

        body = {}
        try:
            body = json.loads(req.stream.read())
            with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   "schemas.json")) as f:
                schema_dict = json.load(f)
            # Validate admission request against schema
            jsonschema.Draft3Validator(schema_dict).validate(body)
        except Exception as e:
            resp_body['response']['allowed'] = False
            resp_body['response']['status'] = {
                'code': 400, 'message': (
                    f'Exception parsing the body of request: {e}.')}
        review_request = body.get('request', {})
        resp_body['response']['uid'] = review_request.get('uid')
        resp_body['apiVersion'] = body.get('apiVersion')
        features = review_request.get('object', {}).get('spec', {}).get(
            'features', {})
        # Validate key manager configuration
        if (review_request.get('kind', {}).get('kind') == 'OpenStackDeployment'
                and 'key-manager' in features.get('services', [])):
            if 'backend' not in features.get('barbican', {}):
                resp_body['response']['allowed'] = False
                resp_body['response']['status'] = {
                    'code': 400, 'message': (
                        "Malformed OpenStackDeployment spec, if key-manager "
                        "is enabled, you need to specify the desired backend.")
                }
        resp.body = json.dumps(resp_body)


def create_api():
    app = falcon.API()
    controller = ControllerResource()
    app.add_route('/validate', controller)
    return app
