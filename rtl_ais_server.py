import socketserver
import ais
from elasticsearch import Elasticsearch
from datetime import datetime
from collections import OrderedDict
from pprint import pprint

class AISHandler(socketserver.DatagramRequestHandler):
  _messagemap = OrderedDict()
  _es = Elasticsearch()

  def indexDoc(self, doc):
    timestamp = datetime.utcnow()
    dmy = timestamp.strftime('%Y-%m-%d')
    body = doc
    body['curtime'] = timestamp
    print(body)
    if ('x' in body and 'y' in body):
      body['location'] = {'lon': body['x'], 'lat': body['y']}
    self._es.index(index="ais-" + dmy, doc_type="_doc", body=body)
    self._es.update(index='ships-seen',doc_type='_doc',id=body['mmsi'],
                body={ "doc": body, "doc_as_upsert": True })

  def handle(self):
    data = self.rfile.readline()
    while data:
      data = data.strip().decode("utf-8")
      ais_arr = data.split(',')
      num_fragments = int(ais_arr[1])
      fragment_number = int(ais_arr[2])
      sentence_id = ais_arr[3]
      channel = ais_arr[4]
      data_payload = ais_arr[5]
      if num_fragments == 1:
        decoded_message = ais.decode(data_payload,0)
        self.indexDoc(doc=decoded_message)
      elif fragment_number < num_fragments:
        if sentence_id in self._messagemap:
          self._messagemap[sentence_id] = self._messagemap[sentence_id] + data_payload
        else:
          # if we have too many items in queue, we'll force one out
