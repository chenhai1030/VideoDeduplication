import requests
import os
import csv
import cv2
import ray
from ray.services import get_node_ip_address
from functools import reduce

# from apscheduler.schedulers.background import BackgroundScheduler

import logging
import sys
import click
import time

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

file_handler = logging.FileHandler('extract_features.log')
file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(file_handler)

ray.init(address="0.0.0.0:6379")


@click.command()
@click.option(
    '--config', '-cp',
    help='path to the project config file',
    default=os.environ.get('WINNOW_CONFIG'))
# @click.option(
#     '--list-of-files', '-lof',
#     help='path to txt with a list of files for processing - overrides source folder from the config file',
#     default="")

@click.option(
    '--frame-sampling', '-fs',
    help='Sets the sampling strategy (values from 1 to 10 - eg sample one frame every X seconds) - overrides frame'
         'sampling from the config file',
    default="")
@click.option(
    '--save-frames', '-sf',
    help='Whether to save the frames sampled from the videos - overrides save_frames on the config file',
    default=False, is_flag=True)
def main(config, frame_sampling, save_frames):
    # scheduler = BackgroundScheduler()
    config = resolve_config(
        config_path=config,
        frame_sampling=frame_sampling,
        save_frames=save_frames)

    video_links = []
    result_ids = []
    with open('/project/data/video_path.csv', 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            # print(row)
            video_links.extend(row)

        for link in video_links:
            duration = get_video_duration(link)
            if duration < 240:
                if not is_video_exist_in_db(config, link.split('/')[-1]):
                    while True:
                        # resource = ray.available_resources()
                        print(ray.available_resources())
                        if 'CPU' in list(ray.available_resources()):
                            task_id = extract_features.remote(config, link)
                            result_ids.append(task_id)
                            break
                        time.sleep(0.5)

    # print(len(video_links))
    # for link in video_links:
    #     if not is_video_exist_in_db(config, link.split('/')[-1]):
    #         extract_features.remote(config, link)
    #     time.sleep(1)
    print("task dis done!")

    while len(result_ids):
        done_id, result_ids = ray.wait(result_ids)
        time.sleep(10)

    print("All task Done!!")
    # scheduler.add_job(download_video_series(get_video_links), 'interval', seconds=3000)
    #
    # scheduler.add_job(scanVideos.remote(config), 'interval', seconds=10)


def check_unhandled_video(config):
    reps = ReprStorage(os.path.join(config.repr.directory))
    reprkey = reprkey_resolver(config)

    videos = scan_videos(config.sources.root, '**', extensions=config.sources.extensions)
    remaining_videos_path = [path for path in videos if not reps.frame_level.exists(reprkey(path))]
    logging.info('There are {} videos unhandled'.format(len(remaining_videos_path)))

    VIDEOS_UNHANDLED_LIST = create_video_list(remaining_videos_path, config.proc.video_list_filename)
    if len(remaining_videos_path) > 0:
        model_path = default_model_path(config.proc.pretrained_model_local_path)
        extractor = IntermediateCnnExtractor(video_src=VIDEOS_UNHANDLED_LIST, reprs=reps, reprkey=reprkey,
                                             frame_sampling=config.proc.frame_sampling,
                                             save_frames=config.proc.save_frames,
                                             model=(load_featurizer(model_path)))
        # Starts Extracting Frame Level Features
        extractor.start(batch_size=16, cores=4)

    Convert(config)


def Convert(config):
    reps = ReprStorage(os.path.join(config.repr.directory))
    print('Converting Frame by Frame representations to Video Representations')
    converter = FrameToVideoRepresentation(reps)
    converter.start()

    print('Extracting Signatures from Video representations')
    sm = SimilarityModel()
    vid_level_iterator = bulk_read(reps.video_level)

    assert len(vid_level_iterator) > 0, 'No Signatures left to be processed'

    signatures = sm.predict(vid_level_iterator)  # Get {ReprKey => signature} dict

    logging.info('Saving Video Signatures on :{}'.format(reps.signature.directory))
    if config.database.use:
        # Convert dict to list of (path, sha256, signature) tuples
        # entries = [(key.path, key.hash, sig) for key, sig in signatures.items()]
        ## use link instead of path
        entries = [(key.path, key.hash, sig) for key, sig in signatures.items()]

        # Connect to database
        database = Database(uri=config.database.uri)
        database.create_tables()

        # Save signatures
        result_storage = DBResultStorage(database)
        result_storage.add_signatures(entries)

    if config.save_files:
        bulk_write(reps.signature, signatures)


@ray.remote(num_cpus=1, max_calls=1)
def extract_features(config, link):
    download_video(link)
    reps = ReprStorage(os.path.join(config.repr.directory))
    reprkey = reprkey_resolver(config)

    # link = ray.get(link_id)
    file_name = link.split('/')[-1]
    if not reps.frame_level.exists(reprkey(os.path.join(config.sources.root, file_name))):
        VIDEOS_LIST = create_video_list([os.path.join(config.sources.root, file_name)],
                                        str(os.getpid()) + "_" + config.proc.video_list_filename)
        # logging.info('Processed video List saved on :{}'.format(VIDEOS_LIST))
        # Instantiates the extractor
        model_path = default_model_path(config.proc.pretrained_model_local_path)
        # model_pid_path = "/project/winnow/feature_extraction/pretrained_models/" + str(os.getpid()) + "_" + model_path.split('/')[-1]
        # os.system('cp ' + model_path + " " + model_pid_path)

        extractor = IntermediateCnnExtractor(video_src=VIDEOS_LIST, reprs=reps, reprkey=reprkey,
                                             frame_sampling=config.proc.frame_sampling,
                                             save_frames=config.proc.save_frames,
                                             model=(load_featurizer(model_path)))
        # Starts Extracting Frame Level Features
        extractor.start(batch_size=16, cores=4)

        remove_file(VIDEOS_LIST)
        remove_file("/project/data/test_dataset/" + file_name)
        # os.remove(VIDEOS_LIST)
        Convert(config)


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
                pass
    return True


@ray.remote
def f():
    time.sleep(0.01)
    return ray.services.get_node_ip_address()


def get_video_links():
    video_links = []
    with open('/project/data/video_path.csv', 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            # print(row)
            video_links.extend(row)

    # 删除大于240s的长视频
    for link in video_links:
        print(link)
        # file_name = link.split('/')[-1]

        duration = get_video_duration(link)
        if duration > 240:
            video_links.remove(link)

    return video_links


def get_video_duration(filename):
    cap = cv2.VideoCapture(filename)
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        return duration
    return -1


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


# @ray.remote
def download_video(link):
    file_name = link.split('/')[-1]
    # print("Downloading file:%s" % file_name)
    r = requests.get(link, stream=True)

    file_path = "/project/data/test_dataset/"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    # download started
    with open(file_path + file_name, 'wb') as file:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)
        if os.path.exists(file_path + file_name):
            print("%s downloaded!\n" % file_name)
            return link
    return None


if __name__ == "__main__":
    set_notes = set(ray.get([f.remote() for _ in range(1000)]))
    print(set_notes)
    main()
