from logging import StreamHandler
import requests

class ITKSnapHandler(StreamHandler):

    def __init__(self, server_url, ticket_id):
        super(ITKSnapHandler, self).__init__()
        self.server_url = server_url
        self.ticket_id = ticket_id


    def emit(self, info):
        log_url = "{0}/api/pro/tickets/{1}/info".format(self.server_url, self.ticket_id)
        r = requests.post(log_url, data={"message": info.split(',')[-1][2:-2]})

