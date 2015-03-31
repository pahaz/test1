import wsgiref.validate
from router import Router
from request import Request
import controller
import config


router = Router()
router.add_route('/home', controller.home_controller)
router.add_route('/messages', controller.messages_controller)
router.add_route('/upload', controller.upload_controller)
router.add_route(config.STATIC_BASE_URI, controller.static_controller)


@wsgiref.validate.validator
def application(environ, start_response):
    request = Request(environ)
    route_callback = router.resolve(request.URI_PATH)
    response = route_callback(request)
    start_response(response.status, response.headers)
    return [response.body]
