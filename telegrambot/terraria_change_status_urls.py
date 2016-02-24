def do_GET(self):
    if "?" in self.path:
        host = self.path.split("?")[1]
        self.path = self.path.split("?")[0]
    else:
        host = None
    if self.path == self.server.webhook_path+"/server_on":
        self.logger.info("Terraria Server On (%s) (%s) ( via weburl)" % (host, self.headers['X-Forwarded-For'] ))
        self.server.update_queue.put("/terraria_on %s %s" % (host, self.headers['X-Forwarded-For'] ))
    elif self.path == self.server.webhook_path+"/server_off":
        self.logger.info("Terraria Server Off (%s) ( via weburl)" % (host))
        self.server.update_queue.put("/terraria_off %s" % (host))
    self.send_response(200)
    self.end_headers()