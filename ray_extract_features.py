import requests
import os
import csv
import cv2
import ray
from ray.services import get_node_ip_address
from functools import reduce
import queue, threading

import logging
import sys
import click
import time
import lmdb
import json

from db import Database
from winnow.feature_extraction import IntermediateCnnExtractor, FrameToVideoRepresentation, SimilarityModel, \
    load_featurizer
from winnow.feature_extraction.model import default_model_path
from winnow.storage.db_result_storage import DBResultStorage
from winnow.storage.repr_storage import ReprStorage
from winnow.storage.repr_utils import bulk_read, bulk_write
from winnow.utils import scan_videos, create_video_list, scan_videos_from_txt, \
    resolve_config, reprkey_resolver

from sqlalchemy.orm import joinedload
from db.schema import (
    Files,
)

logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("winnow").setLevel(logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('test.log')
logger.addHandler(file_handler)

ray.init(address="0.0.0.0:6379")
head_ip = "172.17.12.189"

@click.command()
@click.option(
    '--config', '-cp',
    help='path to the project config file',
    default=os.environ.get('WINNOW_CONFIG'))
@click.option(
    '--list-of-files', '-lof',
    help='path to txt with a list of files for processing - overrides source folder from the config file',
    default='/project/data/video_path.csv')
@click.option(
    '--frame-sampling', '-fs',
    help='Sets the sampling strategy (values from 1 to 10 - eg sample one frame every X seconds) - overrides frame'
         'sampling from the config file',
    default="")
@click.option(
    '--save-frames', '-sf',
    help='Whether to save the frames sampled from the videos - overrides save_frames on the config file',
    default=False, is_flag=True)
@click.option(
    '--start-time', '-st',
    help='Start time  fetch the videos from linda',
    default=int(time.time())
)
@click.option(
    '--end-time', '-et',
    help='End time  fetch the videos from linda',
    default=int(time.time())+600
)
def main(config, list_of_files, frame_sampling, save_frames, start_time, end_time):
    Linda_interface = "http://172.17.26.95:8086/status/linda_orange_material_info?"
    nodes = set(ray.get([f.remote() for _ in range(1000)]))
    nodes |= set(ray.get([f.remote() for _ in range(1000)]))
    logging.info(nodes)

    config = resolve_config(
        config_path=config,
        frame_sampling=frame_sampling,
        save_frames=save_frames)

    startTime = start_time
    result_ids = []
    prepare_to_end = False
    while end_time - startTime > 0:
        if startTime >= (time.time()):
            startTime = start_time
            time.sleep(5)
        linda_request_url = Linda_interface + "starttime=" + str(startTime) + "&&" + "endtime=" + str((startTime+600))
        startTime += 600
        if startTime >= end_time:
            prepare_to_end = True
        print(linda_request_url)
        r = requests.get(linda_request_url)
        rsp = json.loads(r.text)
        if rsp['result'] == "success" and range(len(rsp['data']) > 0):
            linda_list = [rsp['data'][i]['file_path'] for i in range(len(rsp['data']))]
            linda_list_temp = linda_list.copy()
            # create_video_list(linda_list, list_of_files)
            record_video_list(linda_request_url, linda_list_temp)

            # with open(list_of_files, 'r') as file:
            #     reader = csv.reader(file)
            for idx, value in enumerate(linda_list_temp):
                link = value
                is_in_db = is_video_exist_in_db(config, link.split('/')[-1])
                if not is_in_db:
                    # duration = get_video_duration(link)
                    # if duration < 240:
                    while True:
                        try:
                            # logging.info(ray.available_resources())
                            resources = list(ray.available_resources())
                            if 'CPU' in resources:
                                if prepare_to_end:
                                    task_id = extract_features.remote(config, link)
                                    result_ids.append(task_id)
                                else:
                                    extract_features.remote(config, link)
                                break
                        except Exception as e:
                            print(e)
                        time.sleep(0.2)

            for nodeIP in nodes:
                node_id = f"node:{nodeIP}"
                Convert.options(resources={node_id: 0.01})
                # Convert.remote(config)
                ray.get(Convert.remote(config))

    logging.info("task dis done!")

    count = 0
    while len(result_ids) and count < 100:
        done_id, result_ids = ray.wait(result_ids)
        count += 1
        time.sleep(2)

    collect_files(nodes)
    merge_files(nodes)
    os.popen('python /project/generate_matches.py')
    logging.info("All task Done!!")


def collect_files(nodes):
    global head_ip
    if not os.path.exists("/project/data/rsync_path"):
        os.makedirs("/project/data/rsync_path")
    for node in nodes:
        if node != head_ip:
            command = "rsync -avz --password-file=/etc/rsyncd.passwd chenhai@" + node + \
                      "::video /project/data/rsync_path/" + node
            ret = os.popen(command)
            logging.info(ret.read())


def merge_files(nodes):
    global head_ip
    for node in nodes:
        if node != head_ip:
            src_path = "/project/data/rsync_path/" + node
            if os.path.exists(src_path):
                # vid_level_cmd = "cp -rf " + src_path + "/" + "representations/video_level/*.npy " + \
                #                 "/project/data/representations/video_level/"
                # os.system(vid_level_cmd)
                vid_sig_cmd = "cp -rf " + src_path + "/" + "representations/video_signatures/*.npy " + \
                              "/project/data/representations/video_signatures/"
                os.system(vid_sig_cmd)
                ## video_level
                src_vid_lev_lmdb = src_path + "/" + "representations/video_level/store.lmdb"
                dst_vid_lev_lmdb = "/project/data/representations/video_level/store.lmdb"
                ret_vid_lev_lmdb = "/project/data/representations/video_level/ret.lmdb"
                merge_lmdb(src_vid_lev_lmdb, dst_vid_lev_lmdb, ret_vid_lev_lmdb)
                os.system("rm -rf /project/data/representations/video_level/store.lmdb")
                os.system("mv /project/data/representations/video_level/ret.lmdb "
                          "/project/data/representations/video_level/store.lmdb")
                ## video_signatures
                src_vid_sig_lmdb = src_path + "/" + "representations/video_signatures/store.lmdb"
                dst_vid_sig_lmdb = "/project/data/representations/video_signatures/store.lmdb"
                ret_vid_sig_lmdb = "/project/data/representations/video_signatures/ret.lmdb"
                merge_lmdb(src_vid_sig_lmdb, dst_vid_sig_lmdb, ret_vid_sig_lmdb)
                os.system("rm -rf /project/data/representations/video_signatures/store.lmdb")
                os.system("mv /project/data/representations/video_signatures/ret.lmdb "
                          "/project/data/representations/video_signatures/store.lmdb")
                # del after work done!
                os.system("rm -rf " + src_path)


def merge_lmdb(lmdb1, lmdb2, result_lmdb):
    logging.info('Merge start!')
    env_1 = lmdb.open(lmdb1)
    env_2 = lmdb.open(lmdb2)

    txn_1 = env_1.begin()
    txn_2 = env_2.begin()

    database_1 = txn_1.cursor()
    database_2 = txn_2.cursor()

    env_3 = lmdb.open(result_lmdb, map_size=int(1e12))
    txn_3 = env_3.begin(write=True)

    count = 0
    for (key, value) in database_1:
        txn_3.put(key, value)
        count += 1
        if count % 1000 == 0:
            txn_3.commit()
            count = 0
            txn_3 = env_3.begin(write=True)

    if count % 1000 != 0:
        txn_3.commit()
        count = 0
        txn_3 = env_3.begin(write=True)

    for (key, value) in database_2:
        txn_3.put(key, value)
        if count % 1000 == 0:
            txn_3.commit()
            count = 0
            txn_3 = env_3.begin(write=True)

    if count % 1000 != 0:
        txn_3.commit()
        count = 0
        txn_3 = env_3.begin(write=True)

    env_1.close()
    env_2.close()
    env_3.close()

    logging.info('Merge success!')


@ray.remote(num_cpus=1, max_calls=1)
def Convert(config):
    reps = ReprStorage(os.path.join(config.repr.directory))
    logging.info('Converting Frame by Frame representations to Video Representations')
    converter = FrameToVideoRepresentation(reps)
    converter.start()

    logging.info('Extracting Signatures from Video representations')
    sm = SimilarityModel()
    vid_level_iterator = bulk_read(reps.video_level)

    # assert len(vid_level_iterator) > 0, 'No Signatures left to be processed'
    if len(vid_level_iterator) > 0:
        signatures = sm.predict(vid_level_iterator)  # Get {ReprKey => signature} dict

        os.system("rm -rf /project/data/representations/video_level/*.npy")
        os.system("rm -rf /project/data/representations/frame_level/*.npy")

        logging.info('Saving Video Signatures on :{}'.format(reps.signature.directory))
        if config.database.use:
            # Convert dict to list of (path, sha256, signature) tuples
            # entries = [(key.path, key.hash, sig) for key, sig in signatures.items()]
            ## use link instead of path
            entries = [(key.path, key.hash, key.url, sig) for key, sig in signatures.items()]

            # Connect to database
            database = Database(uri=config.database.uri)
            database.create_tables()

            # Save signatures
            result_storage = DBResultStorage(database)
            result_storage.add_signatures(entries)

        if config.save_files:
            bulk_write(reps.signature, signatures)



@ray.remote(max_calls=1)
def extract_features(config, link):
    download_video(link)
    reps = ReprStorage(os.path.join(config.repr.directory))
    reprkey = reprkey_resolver(config)

    file_name = link.split('/')[-1]
    if not reps.frame_level.exists(reprkey(os.path.join(config.sources.root, file_name))):
        #VIDEOS_LIST = create_video_list([os.path.join(config.sources.root, file_name)],
        #                                str(os.getpid()) + "_" + config.proc.video_list_filename)
        VIDEOS_LIST = create_video_list([link],
                                        str(os.getpid()) + "_" + config.proc.video_list_filename)
        # logging.info('Processed video List saved on :{}'.format(VIDEOS_LIST))
        # Instantiates the extractor
        model_path = default_model_path(config.proc.pretrained_model_local_path)

        extractor = IntermediateCnnExtractor(video_src=VIDEOS_LIST, reprs=reps, reprkey=reprkey,
                                             frame_sampling=config.proc.frame_sampling,
                                             save_frames=config.proc.save_frames,
                                             model=(load_featurizer(model_path)))
        # Starts Extracting Frame Level Features
        extractor.start(batch_size=8, cores=4)

        remove_file(VIDEOS_LIST)
        remove_file("/project/data/test_dataset/" + file_name)
        os.system("rm -rf /project/core.*")


def is_video_exist_in_db(config, file):
    if config.database.use:
        database = Database(uri=config.database.uri)
        with database.session_scope() as session:
            try:
                query = session.query(Files).options(joinedload(Files.signature))
                file = query.filter(Files.file_path == file).one_or_none()
                if file is None:
                    return False
            except Exception as e:
                print("db is null")
                return False
    return True


@ray.remote
def f():
    time.sleep(0.01)
    return ray.services.get_node_ip_address()


def get_video_duration(link):
    cap = cv2.VideoCapture(link)
    duration = -1
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        cap.release()
    return duration


def ip_into_int(ip):
    return reduce(lambda x, y: (x << 8) + y, map(int, ip.split('.')))


def is_internal_ip(ip):
    ip = ip_into_int(ip)
    net_a = ip_into_int('10.255.255.255') >> 24
    net_b = ip_into_int('172.31.255.255') >> 20
    net_c = ip_into_int('192.168.255.255') >> 16
    return ip >> 24 == net_a or ip >> 20 == net_b or ip >> 16 == net_c


def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def record_video_list(url, list):
    file_path = "/project/data/record.txt"
    need_record = True
    with open(file_path, 'r') as file:
        for line in file.readlines():
            if line.rstrip() == url:
                need_record = False

    with open(file_path, 'a+') as file:
        if need_record:
            file.write(url)
            file.write('\r\n')
            for list_video in list:
                file.write(list_video)
                file.write('\r\n')


# 15s > 5s-15s video
def check_duration_and_download(link, file_path):
    is_video_rewrite = False
    cap = cv2.VideoCapture(link)

    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        print("file:" + link + ", duration:" + str(duration))
        if duration > 15:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            end_time = 15
            cap.set(cv2.CAP_PROP_POS_MSEC, 5*1000)
            out = cv2.VideoWriter(file_path, fourcc, cap.get(5), (int(cap.get(3)), int(cap.get(4))))
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    is_video_rewrite = True
                    if cap.get(cv2.CAP_PROP_POS_MSEC) >= end_time*1000:
                        break
                    out.write(frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break
            out.release()
    else:
        return is_video_rewrite

    cap.release()
    return is_video_rewrite


def download_video(link):
    file_name = link.split('/')[-1]
    file_path = "/project/data/test_dataset/"
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    if os.path.exists(file_path + file_name):
        return None
    # duration = get_video_duration(link)
    if not check_duration_and_download(link, file_path + file_name):
        r = requests.get(link, stream=True)
        # download started
        with open(file_path + file_name, 'wb') as file:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)
            if os.path.exists(file_path + file_name):
                logging.info("%s downloaded!\n" % file_name)
                return link
    else:
        return link
    return None


if __name__ == "__main__":
    main()
