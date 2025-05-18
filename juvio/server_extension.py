def _load_jupyter_server_extension(app):
    app.log.info("[juvio] Loading Juvio")
    from juvio.content_manager import create_juvio_contents_manager_class

    original_contents_manager = app.contents_manager_class

    new_cm_class = create_juvio_contents_manager_class(original_contents_manager)
    app.contents_manager_class = new_cm_class
    app.contents_manager = new_cm_class(parent=app, log=app.log)
    app.session_manager.contents_manager = app.contents_manager
    app.web_app.settings["contents_manager"] = app.contents_manager
