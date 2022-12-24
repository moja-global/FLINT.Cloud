from Endpoints.gcbm_endpoints import disturbance, Run, title, classifier, miscellaneous

def endpoints(api):
    api.add_resource(disturbance, "/gcbm/upload/disturbances")
    api.add_resource(title, "/gcbm/create")
    api.add_resource(classifier, "/gcbm/upload/classifies")
    api.add_resource(miscellaneous, "/gcbm/upload/miscellaneous")
    api.add_resource(Run, "/gcbm/run")
