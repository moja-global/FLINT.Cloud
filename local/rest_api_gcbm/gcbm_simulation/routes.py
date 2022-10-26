from .views import Gcbm, GbcmUpload, Config, GcbmRun, DownloadGcbmResult

def initialize_routes(api):
    api.add_resource(Gcbm, '/gcbm/new')
    api.add_resource(GbcmUpload, '/gcbm/upload/?category=category')
    api.add_resource(GcbmRun, '/dynamic')
    api.add_resource(Config, '/config')
    api.add_resource(DownloadGcbmResult, '/gcbm/download')

