from namizun_core import database
from random import uniform, randint
from time import sleep
from namizun_core.monitor import get_network_io
from namizun_core.udp import multi_udp_uploader
from datetime import datetime
from pytz import timezone
from namizun_core.ip import cache_ip_ports_from_database


def get_network_usage():
    upload, download = get_network_io()
    limitation = int(uniform(database.get_cache_parameter('coefficient_limitation') * 0.7,
                             database.get_cache_parameter('coefficient_limitation') * 1.3))
    difference = download * limitation - upload
    if difference < 1000000000:
        return 0
    return difference


def get_uploader_count_base_timeline():
    time_in_iran = int(datetime.now(timezone("Asia/Tehran")).strftime("%H"))
    default_uploader_count = database.get_cache_parameter('coefficient_uploader_threads_count') * 10
    maximum_allowed_coefficient = [2, 1.6, 1, 0.6, 0.2, 0.1, 0.6, 1, 1.2, 1.3, 1.4, 1.5,
                                   1.3, 1.4, 1.6, 1.5, 1.3, 1.5, 1.7, 1.8, 2, 1.3, 1.5, 1.8]
    minimum_allowed_coefficient = [1.6, 1, 0.6, 0.2, 0, 0, 0.2, 0.8, 1, 1.1, 1.2, 1.3,
                                   1.1, 1.2, 1.5, 1.4, 1.2, 1.4, 1.5, 1.6, 1.8, 1, 1.2, 1.5]
    return int(uniform(minimum_allowed_coefficient[time_in_iran] * default_uploader_count,
                       maximum_allowed_coefficient[time_in_iran] * default_uploader_count))


while True:
    database.set_parameters_to_cache()
    if database.get_cache_parameter('fake_udp_uploader_running'):
        cache_ip_ports_from_database()
        total_uploader = remain_uploader = get_uploader_count_base_timeline()
        total_upload_size = remain_upload_size = get_network_usage()
        while remain_uploader >= 0 and remain_upload_size > 0.1 * total_upload_size:
            uploader_count, upload_size_for_each_ip = multi_udp_uploader(0.3 * total_upload_size, total_uploader)
            remain_uploader -= uploader_count
            remain_upload_size -= uploader_count * upload_size_for_each_ip
    sleep(randint(5, 30))
