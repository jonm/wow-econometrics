import logging
import gzip
import tempfile

import avro.schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter
import boto
from boto.s3.key import Key
import ijson

def convert_object(auc):
    out = {}
    for f in ['rand', 'bid', 'seed', 'context', 'owner', 'buyout',
              'quantity', 'modifiers']:
        if f in auc: out[f] = auc[f]

    remaps = { "auc" : "auction_id", "ownerRealm" : "owner_realm",
               "timeLeft" : "time_left", "item" : "item_id",
               "petQualityId" : "pet_quality_id",
               "petBreedId" : "pet_breed_id",
               "petSpeciesId" : "pet_species_id",
               "petLevel" : "pet_level" }
    for k1,k2 in remaps.iteritems():
        if k1 in auc: out[k2] = auc[k1]
        
    if 'bonusLists' in auc:
        out['bonus_lists'] = \
          map(lambda bl: bl['bonusListId'], auc['bonusLists'])

    known_keys = out.keys() + remaps.keys() + ['bonusLists']
    for k in auc.keys():
        if k not in known_keys:
            logging.warn("Detected unused key %s" % (k,))
        
    return out

def convert_file(in_f, out_f, schema_filename="auctions.avsc"):
    schema = avro.schema.parse(open(schema_filename, "rb").read())

    writer = DataFileWriter(out_f, DatumWriter(), schema)

    for auc in ijson.items(in_f, 'auctions.item'):
        writer.append(convert_object(auc))

def convert_s3_obj(src_bucket, src_key, dst_bucket, dst_key=None):
    if dst_key is None: dst_key = src_key
    conn = boto.connect_s3()

    try:
        b_out = conn.get_bucket(dst_bucket)
    except boto.exception.S3ResponseError:
        b_out = conn.create_bucket(dst_bucket)

    b_in = conn.get_bucket(src_bucket)
        
    local_in_f = tempfile.TemporaryFile()
    k_in = Key(b_in)
    k_in.key = src_key
    print "Downloading ", k_in.key, "...",
    k_in.get_contents_to_file(local_in_f)
    print "done."
    local_in_f.seek(0)
    
    local_out_f = tempfile.TemporaryFile()
    print "Converting to Avro...",
    convert_file(gzip.GzipFile(mode="rb",fileobj=local_in_f), local_out_f)
    local_in_f.close()
    print "done."
    local_out_f.seek(0)

    k_out = Key(b_out)
    k_out.key = dst_key
    print "Uploading Avro to", k_out.key, "...",
    k_out.set_contents_from_file(local_out_f)
    print "done."
    local_out_f.close()
    
