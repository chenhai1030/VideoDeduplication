import requests
import os
import csv
import cv2
import ray
from ray.services import get_node_ip_address
from functools import reduce
import schedule
import struct

import logging
import sys
import click
import time
import lmdb
import json
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

from db import Database
from winnow.feature_extraction import IntermediateCnnExtractor, FrameToVideoRepresentation, SimilarityModel, \
    load_featurizer
from winnow.feature_extraction.model import default_model_path
from winnow.storage.db_result_storage import DBResultStorage
from winnow.storage.repr_storage import ReprStorage
from winnow.storage.repr_utils import bulk_read, bulk_write
from winnow.utils import scan_videos, create_video_list, scan_videos_from_txt, \
    resolve_config, reprkey_resolver
from winnow.utils import extract_additional_info, extract_scenes, filter_results, uniq, \
    get_brightness_estimation



from sqlalchemy.orm import joinedload
from db.schema import (
    Files,
)

logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("winnow").setLevel(logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# file_handler = logging.FileHandler('test.log')
# logger.addHandler(file_handler)

ray.init(address="0.0.0.0:6379")
head_ip = "172.17.12.189"

LOCAL_TEST = False


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
    nodes = get_ray_nodes()
    print(nodes)

    config = resolve_config(
        config_path=config,
        frame_sampling=frame_sampling,
        save_frames=save_frames)

    if LOCAL_TEST:
        local_test(config)
        os.popen('python /project/generate_matches.py')
        return

    schedule.every(3600).seconds.do(find_matchs, config)
    schedule.every(900).seconds.do(check_convert, config)

    startTime = start_time
    result_ids = []
    prepare_to_end = False
    while end_time - startTime > 0:
        cur_time = int(time.time())
        if startTime >= cur_time:
            startTime = start_time
            time.sleep(5)
        linda_request_url = Linda_interface + "starttime=" + str(startTime) + "&&" + "endtime=" + str((startTime+600))
        startTime += 600
        if startTime >= end_time:
            prepare_to_end = True
        print(linda_request_url)
        print("cur_time: " + str(cur_time))
        r = requests.get(linda_request_url)
        rsp = json.loads(r.text)
        if rsp['result'] == "success" and range(len(rsp['data']) > 0):
            need_convert = False
            linda_list = [rsp['data'][i]['file_path'] for i in range(len(rsp['data']))]
            linda_list_temp = linda_list.copy()

            record_video_list(linda_request_url, linda_list_temp)

            for idx, value in enumerate(linda_list_temp):
                link = value
                is_in_db = is_video_exist_in_db(config, link.split('/')[-1])
                if not is_in_db:
                    need_convert = True
                    while True:
                        try:
                            if int(ray.available_resources().get("CPU", 0)) > 1:
                                if prepare_to_end:
                                    task_id = extract_features.remote(config, link)
                                    result_ids.append(task_id)
                                else:
                                    extract_features.remote(config, link)

                                break
                        except Exception as e:
                            print(e)
                        time.sleep(2)


            # cur_time = int(time.time())
            # if (cur_time - task_start_time > 0) and \
            #         (cur_time - task_start_time) / 3600 > time_count:
            #     time_count += 1
            #     print("Num: " + str(time_count) + " generate matches by TIME!")
            #     find_matchs(config)
            #     print("Num: " + str(time_count) + " generate matches by TIME! Done!")

    print("task dis done!")

    count = 0
    while len(result_ids) and count < 100:
        print("result_ids:" + str(len(result_ids)) )
        done_id, result_ids = ray.wait(result_ids)
        count += 1
        time.sleep(2)

    if need_convert:
        check_convert(config)

    find_matchs(config)
    print("All task Done!!")


def check_convert(config):
    for nodeIP in get_ray_nodes():
        node_id = f"node:{nodeIP}"
        Convert.options(resources={node_id: 1.0})
        ray.get(Convert.remote(config))


@ray.remote(max_calls=1)
def Convert(config):
    reps = ReprStorage(os.path.join(config.repr.directory))
    print('Extracting Signatures from Video representations')
    sm = SimilarityModel()
    vid_level_iterator = bulk_read(reps.video_level)

    if len(vid_level_iterator) > 0:
        signatures = sm.predict(vid_level_iterator)  # Get {ReprKey => signature} dict

        logging.info('Saving Video Signatures on :{}'.format(reps.signature.directory))
        if config.database.use:
            # Convert dict to list of (path, sha256, signature) tuples
            # entries = [(key.path, key.hash, sig) for key, sig in signatures.items()]
            ## use link instead of path
            entries = [(key.path, key.hash, key.url, sig) for key, sig in signatures.items()]

            # Connect to database
            database = Database(uri=config.database.uri)
            database.create_tables()

            try:
                # Save signatures
                result_storage = DBResultStorage(database)
                result_storage.add_signatures(entries)
            except Exception as e:
                print(e)

        # if config.save_files:
        #     bulk_write(reps.signature, signatures)


@ray.remote(max_calls=1, num_cpus=2)
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
        extractor.start(batch_size=16, cores=4)

        print('Converting Frame by Frame representations to Video Representations')
        converter = FrameToVideoRepresentation(reps)
        converter.start()

        remove_file(VIDEOS_LIST)
        remove_file("/project/data/test_dataset/" + file_name)
        remove_file("/project/data/representations/frame_level/" + file_name + ".npy")
        os.system("rm -rf /project/core.*")


def db_test(config):
    database = Database(uri=config.database.uri)
    with database.session_scope() as session:
        query = session.query(Files).options(joinedload(Files.signature))
        files = query.filter().all()

        paths = np.array([file.file_path for file in files])
        hashes = np.array([file.sha256 for file in files])
        # video_signatures = np.array([file.signature.signature for file in files])
        for file in files:
            if file.signature is not None:
                if file.file_path == "v127550211.mp4":
                    with open("test.txt", "wb+") as f:
                        f.write(file.signature.signature)
                        f.seek(0)
                    # f = open('test.txt', 'rb+')
                        str = f.read()
                        len_s = len(str)
                        data = struct.unpack(('%df' % (len_s / 4)), str)
                        print(data)
                    # f.close()
            else:
                print(file.file_path)
            return


def find_matchs(config):
    # reps = ReprStorage(config.repr.directory)

    # Get mapping (path,hash) => sig.
    # print('Extracting Video Signatures')

    # # signature_iterator = bulk_read_lmdb(reps.signature)
    # signature_iterator = bulk_read(reps.signature)
    # repr_keys, video_signatures = zip(*signature_iterator.items())
    # paths = np.array([key.path for key in repr_keys])
    # hashes = np.array([key.hash for key in repr_keys])
    # video_signatures = np.array(video_signatures)

    print('Reading Video Signatures')
    database = Database(uri=config.database.uri)
    with database.session_scope() as session:
        query = session.query(Files).options(joinedload(Files.signature))
        files = query.filter().all()
        paths = np.array([file.file_path for file in files])
        hashes = np.array([file.sha256 for file in files])
        video_signatures = []
        for file in files:
            if file.signature is not None:
                with open("/tmp/test.txt", "wb+") as f:
                    f.write(file.signature.signature)
                    f.seek(0)
                    # f = open('test.txt', 'rb+')
                    str = f.read()
                    len_s = len(str)
                    data = struct.unpack(('%df' % (len_s / 4)), str)
                    video_signatures.append(data)
        video_signatures = np.array(video_signatures)

    print('Finding Matches...')
    # Handles small tests for which number of videos <  number of neighbors
    t0 = time.time()
    neighbors = min(20, video_signatures.shape[0])
    nn = NearestNeighbors(n_neighbors=neighbors, metric='euclidean', algorithm='kd_tree')
    nn.fit(video_signatures)
    distances, indices = nn.kneighbors(video_signatures)
    print('{} seconds spent finding matches '.format(time.time() - t0))
    results, results_distances = filter_results(config.proc.match_distance, distances, indices)

    ss = sorted(zip(results, results_distances), key=lambda x: len(x[0]), reverse=True)
    results_sorted = [x[0] for x in ss]
    results_sorted_distance = [x[1] for x in ss]

    q = []
    m = []
    distance = []

    print('Generating Report')
    for i,r in enumerate(results_sorted):
        for j,matches in enumerate(r):
            if j == 0:
                qq = matches
            q.append(qq)
            m.append(matches)
            distance.append(results_sorted_distance[i][j])

    match_df = pd.DataFrame({"query":q,"match":m,"distance":distance})
    match_df['query_video'] = paths[match_df['query']]
    match_df['query_sha256'] = hashes[match_df['query']]
    match_df['match_video'] = paths[match_df['match']]
    match_df['match_sha256'] = hashes[match_df['match']]
    match_df['self_match'] = match_df['query_video'] == match_df['match_video']
    # Remove self matches
    match_df = match_df.loc[~match_df['self_match'], :]
    # Creates unique index from query, match
    match_df['unique_index'] = match_df.apply(uniq, axis=1)
    # Removes duplicated entries (eg if A matches B, we don't need B matches A)
    match_df = match_df.drop_duplicates(subset=['unique_index'])

    # if config.proc.filter_dark_videos:
    #
    #     print('Filtering dark and/or short videos')
    #
    #     # Get original files for which we have both frames and frame-level features
    #     repr_keys = list(set(reps.video_level.list()))
    #     paths = [key.path for key in repr_keys]
    #     hashes = [key.hash for key in repr_keys]
    #
    #     print('Extracting additional information from video files')
    #     brightness_estimation = np.array([get_brightness_estimation(reps, key) for key in tqdm(repr_keys)])
    #     print(brightness_estimation.shape)
    #     metadata_df = pd.DataFrame({"fn": paths,
    #                                 "sha256": hashes,
    #                                 "gray_max":brightness_estimation.reshape(brightness_estimation.shape[0])})
    #
    #     # Flag videos to be discarded
    #
    #     metadata_df['video_dark_flag'] = metadata_df.gray_max < config.proc.filter_dark_videos_thr
    #
    #     print('Videos discarded because of darkness:{}'.format(metadata_df['video_dark_flag'].sum()))
    #
    #     metadata_df['flagged'] = metadata_df['video_dark_flag']
    #
    #     # Discard videos
    #     discarded_videos = metadata_df.loc[metadata_df['flagged'], :][['fn', 'sha256']]
    #     discarded_videos = set(tuple(row) for row in discarded_videos.to_numpy())
    #
    #     # Function to check if the (path,hash) row is in the discarded set
    #     def is_discarded(row):
    #         return tuple(row) in discarded_videos
    #
    #     msk_1 = match_df[['query_video', 'query_sha256']].apply(is_discarded, axis=1)
    #     msk_2 = match_df[['match_video', 'match_sha256']].apply(is_discarded, axis=1)
    #     discard_msk = msk_1 | msk_2
    #
    #     match_df = match_df.loc[~discard_msk, :]
    if config.database.use:
        # Connect to database and ensure schema
        database = Database(uri=config.database.uri)
        database.create_tables()

        # Save metadata
        result_storage = DBResultStorage(database)

        # if metadata_df is not None:
        #     metadata_entries = metadata_df[['fn', 'sha256']]
        #     metadata_entries['metadata'] = metadata_df.drop(columns=['fn', 'sha256']).to_dict('records')
        #     result_storage.add_metadata(metadata_entries.to_numpy())

        # Save matches
        match_columns = ['query_video', 'query_sha256', 'match_video', 'match_sha256', 'distance']

        result_storage.add_matches(match_df[match_columns].to_numpy())


def collect_nodes_files(nodes):
    collect_files(nodes)
    merge_files(nodes)
    clean_files()


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


def num_alive_nodes():
    n = 0
    for node in ray.nodes():
        if node["Alive"]:
            n += 1
    return n


def get_ray_nodes():
    node_list = []
    for node in ray.nodes():
        node_list.append(node['NodeManagerAddress'])
    return node_list


def get_video_duration(link):
    cap = cv2.VideoCapture(link)
    duration = -1
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        cap.release()
    return duration


def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def record_video_list(url, list):
    file_path = "/project/data/record.txt"
    if not os.path.exists(file_path):
        record_file = open(file_path, 'w')
        record_file.close()
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


def check_duration_and_cut(file_path):
    cap = cv2.VideoCapture(file_path)
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        w = int(cap.get(3))
        h = int(cap.get(4))
        print("file:" + file_path + ", duration:" + str(duration))
        if int(duration) >= 20:
            file_tmp =  "/project/data/test_dataset/tmp.mp4"

            end_time = 20
            cap.set(cv2.CAP_PROP_POS_MSEC, 0)
            out = cv2.VideoWriter(file_tmp, cv2.VideoWriter_fourcc(*'mp4v'), rate, (w, h))
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    if cap.get(cv2.CAP_PROP_POS_MSEC) >= end_time*1000:
                        break
                    out.write(frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break
            out.release()
            if os.path.exists(file_tmp):
                remove_file(file_path)
                cmd = "mv " + file_tmp + " " + file_path
                os.popen(cmd)

                count = 0
                while not os.path.exists(file_path) and count < 10:
                    time.sleep(0.3)
                    count += 1
                    print("not exist!")


# 20s > 0s-20s video
def check_duration_and_download(link, file_path):
    is_video_rewrite = False
    cap = cv2.VideoCapture(link)

    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = int(frame_num / rate)
        print("file:" + link + ", duration:" + str(duration))
        if 20 <= duration <= 60:
            start_pos = 0
        elif 60 < duration - 20 <= 180:
            start_pos = 61
        elif duration - 20 > 180:
            start_pos = 181
        else:
            start_pos = 0

        end_pos = start_pos + 20
        cap.set(cv2.CAP_PROP_POS_MSEC, start_pos*1000)
        out = cv2.VideoWriter(file_path, cv2.VideoWriter_fourcc(*'mp4v'), rate, (int(cap.get(3)), int(cap.get(4))))
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                if cap.get(cv2.CAP_PROP_POS_MSEC) >= end_pos*1000:
                    is_video_rewrite = True
                    break
                out.write(frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        out.release()
        # check if the file size less then 2M
        if is_video_rewrite and os.path.getsize(file_path) < 2097152:
            is_video_rewrite = False
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
        if LOCAL_TEST:
            check_duration_and_cut(file_path + file_name)
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
                print("%s downloaded!\n" % file_name)
                return link
    else:
        return link
    return None


def local_test(config):
    reps = ReprStorage(os.path.join(config.repr.directory))
    reprkey = reprkey_resolver(config)
    videos = scan_videos(config.sources.root, '**', extensions=config.sources.extensions)

    print('Number of files found: {}'.format(len(videos)))

    remaining_videos_path = ["/project/" + path for path in videos if not reps.frame_level.exists(reprkey(path))]

    print('There are {} videos left'.format(len(remaining_videos_path)))

    VIDEOS_LIST = create_video_list(remaining_videos_path, config.proc.video_list_filename)
    video_list = []
    with open(VIDEOS_LIST, 'r', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            video_list.append(row)

    result_ids = []
    for idx, value in enumerate(video_list):
        link = value[0]
        is_in_db = is_video_exist_in_db(config, link.split('/')[-1])
        if not is_in_db:
            while True:
                try:
                    if int(ray.available_resources().get("CPU", 0)) > 0:
                        task_id = extract_features.remote(config, link)
                        result_ids.append(task_id)
                        break
                except Exception as e:
                    print(e)
                time.sleep(1)

    count = 0
    while len(result_ids) and count < 2000:
        done_id, result_ids = ray.wait(result_ids)
        count += 1
        time.sleep(2)

    for nodeIP in get_ray_nodes():
        node_id = f"node:{nodeIP}"
        Convert.options(resources={node_id: 1.0})
        ray.get(Convert.remote(config))


def clean_files():
    os.popen("rm -rf /project/data/representations/video_level/*.npy")
    os.popen("rm -rf /project/data/representations/frame_level/*.npy")


def collect_files(nodes):
    global head_ip
    if not os.path.exists("/project/data/rsync_path"):
        os.makedirs("/project/data/rsync_path")
    for node in nodes:
        if node != head_ip:
            command = "rsync -avz --password-file=/etc/rsyncd.passwd chenhai@" + node + \
                      "::video /project/data/rsync_path/" + node
            ret = os.popen(command)
            print(ret.read())


if __name__ == "__main__":
    main()
