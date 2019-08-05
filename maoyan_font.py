import re
import requests
from fontTools.ttLib import TTFont
from lxml import etree


class Maoyan(object):
    def __init__(self):
        self.url = 'https://maoyan.com/board/1'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }


    def get_html(self, url):
        response = requests.get(url, headers=self.headers)
        return response


    def replace_font(self, response):

        base_font = TTFont('./fonts/base.woff')
        # base_font.saveXML('base_font.xml')
        base_dict = {'uniE7F9': '7', 'uniE649': '4', 'uniE41C': '1', 'uniF4E2': '8', 'uniEA4B': '9',
                     'uniEBF3': '3', 'uniED04': '2', 'uniE7D9': '6', 'uniF0AD': '5', 'uniF66A': '0'}
        base_list = base_font.getGlyphOrder()[2:]

        font_file = re.findall(r'vfile\.meituan\.net\/colorstone\/(\w+\.woff)', response)[0]
        font_url = 'http://vfile.meituan.net/colorstone/' + font_file

        new_file = self.get_html(font_url)
        with open('./fonts/' + font_file, 'wb') as f:
            f.write(new_file.content)

        new_font = TTFont('./fonts/' + font_file)
        # new_font.saveXML('new_font.xml')
        new_list = new_font.getGlyphOrder()[2:]


        new_dict = {}
        for name2 in new_list:
            obj2 = new_font['glyf'][name2]
            for name1 in base_list:
                obj1 = base_font['glyf'][name1]
                if obj1 == obj2:
                    new_dict[name2] = base_dict[name1]


        for i in new_list:
            pattern = i.replace('uni', '&#x').lower() + ';'
            response = response.replace(pattern, new_dict[i])
        return response


    def parse_info(self, response):
        tree = etree.HTML(response)
        items = []
        for node in tree.xpath('//dd//div[@class="board-item-content"]'):
            item ={}

            item['film_name'] = node.xpath('./div[@class="movie-item-info"]//a/text()')[0]

            item['today_boxoffice'] = node.xpath('.//p[@class="realtime"]/span/span/text()')[0] + node.xpath(
                './/p[@class="realtime"]//text()[2]')[0].replace('\n', '')

            item['total_boxoffice'] = node.xpath('.//p[@class="total-boxoffice"]/span/span/text()')[0] + node.xpath(
                './/p[@class="total-boxoffice"]//text()[2]')[0].replace('\n', '')

            items.append(item)
        return items


    def start_crawl(self):

        response = self.get_html(self.url).text
        response = self.replace_font(response)
        results = self.parse_info(response)

        for i in results:
            print(i)


if __name__ == '__main__':
    maoyan = Maoyan()
    maoyan.start_crawl()