import datetime
import logging
import sys
import urllib3
import requests


from base import BaseExecutor
#发布的时候
#from py_executor.base import BaseExecutor

urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    stream=sys.stdout)


class AtomExecutor(BaseExecutor):
    name = 'Heweather'

    def init(self):
        pass

    def process_item(self, keyword):

        url = f"https://free-api.heweather.net/s6/weather/now?location={keyword}&key=cc33b9a52d6e48de852477798980b76e"
        res = requests.get(url=url, timeout=10, verify=False)
        j_data = res.json()
        j_list = j_data["HeWeather6"]
        for item in j_list:
            data = {}
            data["cid"] = item["basic"]["cid"]
            data["location"] = item["basic"]["location"]
            data["admin_area"] = item["basic"]["admin_area"]
            data["cnty"] = item["basic"]["cnty"]
            data["cloud"] = item["now"]["cloud"]
            data["cond_code"] = item["now"]["cond_code"]
            data["cond_txt"] = item["now"]["cond_txt"]
            self.upload(item)
            self.logger.info("数据上传成功！")


if __name__ == '__main__':
    from cli import invoke_for_debug

    params = {
        "MainKeys": [
            "101010100","101020100","101030100"
        ],
    }

    invoke_for_debug(__file__, params)
