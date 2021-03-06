import os
from http import HTTPStatus
from os.path import dirname, basename

from flask import jsonify, request, abort, send_from_directory

from db.access.files import ListFilesRequest, FileMatchFilter, FileSort, FilesDAO
from db.schema import Files
from thumbnail.ffmpeg import extract_frame_tmp
from .blueprint import api
from .helpers import parse_boolean, parse_positive_int, parse_date, parse_enum, get_thumbnails, \
    resolve_video_file_path, Fields, parse_fields, parse_seq, get_config, download_file
from ..model import database, Transform

# Optional file fields to be loaded
FILE_FIELDS = Fields(Files.exif, Files.meta, Files.signature, Files.scenes)
RAY_HEAD_IP=""


def parse_params():
    """Parse and validate request arguments."""
    config = get_config()
    result = ListFilesRequest()
    result.limit = parse_positive_int(request.args, 'limit', 20)
    result.offset = parse_positive_int(request.args, 'offset', 0)
    result.path_query = request.args.get('path', '', type=str).strip()
    result.exif = parse_boolean(request.args, 'exif')
    result.audio = parse_boolean(request.args, 'audio')
    result.min_length = parse_positive_int(request.args, 'min_length')
    result.max_length = parse_positive_int(request.args, 'max_length')
    result.preload = parse_fields(request.args, "include", FILE_FIELDS)
    result.extensions = parse_seq(request.args, "extensions")
    result.date_from = parse_date(request.args, "date_from")
    result.date_to = parse_date(request.args, "date_to")
    result.match_filter = parse_enum(request.args, "matches",
                                     values=FileMatchFilter.values,
                                     default=FileMatchFilter.ALL)
    result.related_distance = config.related_distance
    result.duplicate_distance = config.duplicate_distance
    result.sort = parse_enum(request.args, "sort", values=FileSort.values, default=None)
    return result


def set_ray_head_ip(ipaddr):
    global RAY_HEAD_IP
    RAY_HEAD_IP = ipaddr


def get_ray_head_ip():
    global RAY_HEAD_IP
    return RAY_HEAD_IP


@api.route('/head/<string:ipaddr>')
def launch_head(ipaddr):
    set_ray_head_ip(ipaddr)
    ssh_command = "ssh chenhai@" + ipaddr + " "
    remote_command = "docker exec -i videodeduplication_dedup-app_1 /anaconda/envs/winnow/bin/ray start " \
                    " --head --port=6379 --dashboard-host 0.0.0.0 --num-cpus=7"
    all_command = ssh_command + "'" + remote_command + "'"
    ret = os.popen(all_command)
    return ret.read()


@api.route('/worker/<string:ipaddr>')
def launch_worker(ipaddr):
    ssh_command = "ssh chenhai@" + ipaddr + " "
    get_cpu_num_cmd = "cat /proc/cpuinfo |grep \"cpu cores\" | wc -l"
    remote_cpu_num = os.popen (ssh_command + "'"+get_cpu_num_cmd+"'").read()

    get_mem_size_cmd = "cat /proc/meminfo |grep MemTotal | awk '{print $2}' "
    remote_mem_size = os.popen (ssh_command + get_mem_size_cmd).read()

    if ((int(remote_mem_size)/1024/1024)+1)/2 > int(remote_cpu_num):
        cpu_num = int(remote_cpu_num)-2
    else:
        cpu_num = int(((int(remote_mem_size)/1024/1024)+1)/2)
    cpu_num_command = "--num-cpus=" + str(cpu_num)
    # print(remote_mem_size)
    print (int(((int(remote_mem_size)/1024/1024)+1)/2))

    head_ip_addr = get_ray_head_ip()
    if len(head_ip_addr) != 0:
        remote_command = "docker exec -i videodeduplication_dedup-app_1 /anaconda/envs/winnow/bin/ray start " \
                        " --address='" + head_ip_addr + ":6379'" + " --redis-password='5241590000000000' " + cpu_num_command
                        # " --address='172.17.7.156:6379' --redis-password='5241590000000000' " + cpu_num_command
    else:
        remote_command = "pwd"
    all_command = ssh_command + "'"+remote_command+"'"
    ret = os.popen(all_command)
    return ret.read()


@api.route('/ray_stop/<string:ipaddr>')
def stop_worker(ipaddr):
    command = "ssh chenhai@" + ipaddr + " "
    remote_command = "docker exec -i videodeduplication_dedup-app_1 /anaconda/envs/winnow/bin/ray stop "
    all_command = command + "'"+remote_command+"'"
    # print(all_command)
    os.system(all_command)
    remote_kill_command = "docker exec -i videodeduplication_dedup-app_1 ps -aux |grep ray |awk '{print $2}'| " \
                          "docker exec -i videodeduplication_dedup-app_1 xargs kill -9"
    all_command_kill = command  + remote_kill_command
    ret = os.popen(all_command_kill)
    return ret.read()


@api.route('/clean/<string:ipaddr>')
def clear_node(ipaddr):
    command = "ssh chenhai@" + ipaddr + " "
    remote_command = "docker exec -i videodeduplication_dedup-app_1 sh -c \"rm -rf /project/*_video_dataset_list.txt " \
                "core.* /project/data/test_dataset/* /project/data/representations/*  /project/processing_error.log\" "
    all_command = command + "'" + remote_command + "'"
    ret = os.popen(all_command)
    return ret.read()


@api.route('/launch/<string:startTime>-<string:endTime>')
def launch_task(startTime, endTime):
    command = "ssh chenhai@" + get_ray_head_ip() + " "
    log_file = "/project/data/nohup" + "_"+ startTime + "_" + endTime + ".out"
    remote_command = "docker exec -i videodeduplication_dedup-app_1 /bin/bash -c  \"source activate winnow && nohup python " \
                     "-u ray_extract_features.py " \
                     "-st " + startTime + " " \
                     "-et " + endTime + " > " + log_file + "  2>&1 & \""
    all_command = command + "'" + remote_command + "' &"
    print(all_command)
    os.system(all_command)
    return ""


@api.route('/task_stop/')
def stop_task():
    command = "ssh chenhai@" + get_ray_head_ip() + " "
    remote_kill_command = "docker exec -i videodeduplication_dedup-app_1 ps -aux |grep ray_extract_features.py |" \
                          "docker exec -i videodeduplication_dedup-app_1 xargs kill -9"
    all_command = command + remote_kill_command + " &"
    print(all_command)
    ret = os.popen(all_command)
    return ret.read()


# @api.route('/get_state/', methods=['GET'])
# def get_state():
#     # Fetch state from database
#     query = database.session.query(RayState)
#     raystate = query.get()
#     data = Transform.raystate_dict(raystate)
#     return jsonify(data)
#
#
# @api.route('/set_state/<string:ray_state>')
# def set_state(ray_state):
#     state_list = json.loads()
#     return jsonify(state_list)


@api.route('/files/', methods=['GET'])
def list_files():
    req = parse_params()

    results = FilesDAO.list_files(req, database.session)
    include_flags = {field.key: True for field in req.preload}

    return jsonify({
        'items': [Transform.file_dict(item, **include_flags) for item in results.items],
        'total': results.counts.total,
        'duplicates': results.counts.duplicates,
        'related': results.counts.related,
        'unique': results.counts.unique
    })


@api.route('/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    extra_fields = parse_fields(request.args, "include", FILE_FIELDS)

    # Fetch file from database
    query = database.session.query(Files)
    query = FILE_FIELDS.preload(query, extra_fields)
    file = query.get(file_id)

    # Handle file not found
    if file is None:
        abort(HTTPStatus.NOT_FOUND.value, f"File id not found: {file_id}")

    include_flags = {field.key: True for field in extra_fields}
    data = Transform.file_dict(file, **include_flags)
    data["matches_count"] = FilesDAO.file_matches(file_id, database.session).count()
    return jsonify(data)


@api.route('/files/<int:file_id>/thumbnail', methods=['GET'])
def get_thumbnail(file_id):
    # Get time position
    time = parse_positive_int(request.args, 'time', default=0)

    # Fetch file from database
    query = database.session.query(Files)
    file = query.filter(Files.id == file_id).first()

    # Handle file not found
    if file is None:
        abort(HTTPStatus.NOT_FOUND.value, f"File not found: {file_id}")

    thumbnails_cache = get_thumbnails()
    thumbnail = thumbnails_cache.get(file.file_path, file.sha256, position=time)
    if thumbnail is None:
        if file.file_url is not None:
            thumbnail = extract_frame_tmp(file.file_url , position=time)
            if thumbnail is None:
                abort(HTTPStatus.NOT_FOUND.value, f"Timestamp exceeds video url length: {time}")
            thumbnail = thumbnails_cache.move(file.file_path, file.sha256, position=time, thumbnail=thumbnail)
            print(thumbnail)
            return send_from_directory(dirname(thumbnail), basename(thumbnail))

        video_path = resolve_video_file_path(file.file_path)
        if not os.path.isfile(video_path):
            abort(HTTPStatus.NOT_FOUND.value, f"Video file is missing: {file.file_path}")
        thumbnail = extract_frame_tmp(video_path, position=time)
        if thumbnail is None:
            abort(HTTPStatus.NOT_FOUND.value, f"Timestamp exceeds video length: {time}")
        thumbnail = thumbnails_cache.move(file.file_path, file.sha256, position=time, thumbnail=thumbnail)

    return send_from_directory(dirname(thumbnail), basename(thumbnail))
