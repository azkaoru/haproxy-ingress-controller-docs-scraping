# coding: utf-8
__author__ = 'kwatanabe'

import os
import urllib.request
import urllib.parse
import urllib.error

import yaml
#import urllib2
from lxml import html
import json

class HttpClient(object):

     def __init__(self,proxyUrl):
        if proxyUrl == None:
            pass
        else:
            proxy = {'https': proxyUrl}
            # プロキシハンドラを作成
            proxy_handler = urllib.request.ProxyHandler(proxy)
            # オープナーを作成
            opener = urllib.request.build_opener(proxy_handler)
            # グローバルオープナーを設定
            urllib.request.install_opener(opener)

     def get(self,url):
        request = urllib.request.Request(url)
        request.add_header('User-Agent','curl/7.29.0')
        return urllib.request.urlopen(request)

     def get_honyaku_deepl(self,apikey,text,DEEPL_API_URL= "https://api-free.deepl.com/v2/translate",T_LANG="JA"):
        api_params = {
            "auth_key": apikey,
            "text": text,
            "source_lang": "EN",
            "target_lang": T_LANG,
        }
        # URL エンコード
        encoded_data = urllib.parse.urlencode(api_params).encode('utf-8')
        # リクエストの作成
        request = urllib.request.Request(DEEPL_API_URL, data=encoded_data, method='POST')
        # リクエストの送信とレスポンスの取得
        try:
            with urllib.request.urlopen(request) as response:
                response_data = response.read().decode('utf-8')
                result = json.loads(response_data)
                # 翻訳結果の表示
                #print("翻訳結果:", result['translations'][0]['text'])
                return result['translations'][0]['text']
        except urllib.error.HTTPError as e:
            print("HTTPエラー:", e.code, e.reason)
            return None
        except urllib.error.URLError as e:
            print("URLエラー:", e.reason)
            return None


class JRNoteParser(object):
    """JRNoteParser class

    """

    def __init__(self,cache):
        self.cache =cache
        self.httpclient= HttpClient(cache.data['setting']['https.proxy'])
        self.deepl_enable = cache.data['setting']['deepl_enable']
        if self.deepl_enable:
            self.deepl_apikey = cache.data['setting']['deepl_apikey']

    def parse(self,APPEND_KEY="_scraping"):
        content = self.httpclient.get(self.cache.data['setting']['scraping_url'])
        data = content.read()
        for item in self.cache.data['jrnote']:
            #print item
            #print "method:" + str(item)+APPEND_KEY
            search_con= self.cache.data[str(item)+APPEND_KEY]
            settings= self.cache.data['setting']
            if search_con ==None:
                raise Exception("yaml parse err: not found:"+str(item)+APPEND_KEY)
            try:
                getattr(self, str(item)+APPEND_KEY)(data,search_con)
            except Exception as e:
                self.default_scraping(data,search_con)
            #self.scrape_jrnote(content,search_con)

    def normalize_text(self,s):
        return (
            s.replace('\u00a0', ' ')
             .replace('\u200b', '')   # ゼロ幅スペース対策
             .strip()
        )

    def default_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        content = self.httpclient.get(scrape_con['url'])
        data = content.read()
        elem = html.fromstring(data)
        section_elm = elem.xpath("//h1")[0]
        # 配下のすべてのテキストを取得
        all_text = section_elm.xpath('.//text()')
        # リストで取得されるため、結合する場合
        major_tilte = ' '.join(all_text)
        parent_title = section_elm.xpath('preceding-sibling::*[1]')[0].text

        first_bodys = section_elm.getparent().xpath('./../main/*')
        previous_first_join_body = None
        first_join_body = ""
        for first_body in first_bodys:

            first_body_all_text = first_body.xpath(
                    './/text()['
                    'not(ancestor::script)'
                    ' and (not(ancestor::select) or ancestor::option[@selected])'
                    ' and not(ancestor::div[contains(concat(" ", normalize-space(@class), " "), " language-id ")])'
                    ']'
                )
            if first_join_body != "":
                    previous_first_join_body = first_join_body
            first_join_body = ' '.join(first_body_all_text)
            if previous_first_join_body != None and first_join_body == previous_first_join_body:
                continue

            if self.deepl_enable :
                translated = self.httpclient.get_honyaku_deepl(self.deepl_apikey,first_join_body)
                if translated is not None:
                    first_join_body = translated
            print  (parent_title ,",", major_tilte + ",", "NONE,", "\"", first_join_body.strip().replace('\n','').replace(",", u"、"), "\"")

        componet_elms = section_elm.xpath(scrape_con['componet'])
        for item in componet_elms:
            # 配下のすべてのテキストを取得
            #all_text = item.xpath('.//text()')
            all_text = item.text
            # リストで取得されるため、結合する場合
            texts = [self.normalize_text(t) for t in all_text]
            minor_title = ' '.join(texts)

            body_all_text = ""
            desc_all_text = ""
            join_body = ""
            previous_join_body = None
            bodys = item.xpath('./following-sibling::*')
            for body in bodys:
                body_all_text = body.xpath(
                    './/text()['
                    'not(ancestor::script)'
                    ' and (not(ancestor::select) or ancestor::option[@selected])'
                    ' and not(ancestor::div[contains(concat(" ", normalize-space(@class), " "), " language-id ")])'
                    ']'
                )
                #body_all_text = body.xpath('.//text()[not(ancestor::script) and (not(ancestor::select) or ancestor::option[@selected])]')
                if join_body != "":
                    previous_join_body = join_body
                join_body = ' '.join(body_all_text)
                if previous_join_body != None and join_body == previous_join_body:
                    continue
                if self.deepl_enable:
                    translated = self.httpclient.get_honyaku_deepl(self.deepl_apikey,join_body)
                    if translated is not None:
                        join_body = translated
                print (parent_title ,",", major_tilte + ",", minor_title + ",", "\"",  join_body.strip().replace( '\n', '').replace(",", u"、"), "\"")

    def communityConfigurationTcpCrd_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationDefaultsCRD_scraping(data,scrape_con,DEF_ITEM)

    def communityConfigurationStartupArgs_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationIngressAnnotations_scraping(data,scrape_con,DEF_ITEM)

    def communityConfigurationServiceAnnotations_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationIngressAnnotations_scraping(data,scrape_con,DEF_ITEM)

    def communityConfigurationIngressAnnotations_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        content = self.httpclient.get(scrape_con['url'])
        data = content.read()
        elem = html.fromstring(data)
        section_elm = elem.xpath("//h1")[0]
        # 配下のすべてのテキストを取得
        all_text = section_elm.xpath('.//text()')
        # リストで取得されるため、結合する場合
        major_tilte = ' '.join(all_text)
        parent_title = section_elm.xpath('preceding-sibling::*[1]')[0].text
        h1_parent_brothers = section_elm.xpath('./../following-sibling::*')
        for h1_parent_brother in h1_parent_brothers:
            if h1_parent_brother.tag == "h1" or h1_parent_brother.tag == "h2": 
                 break
            print (parent_title ,",", major_tilte + ",", "NONE", "\"",  ' '.join( h1_parent_brother.xpath('.//text()[not(ancestor::script) and (not(ancestor::select) or ancestor::option[@selected])]')).strip().replace( '\n', '').replace(",", u"、"), "\"") 

        h2_elms = section_elm.xpath(scrape_con['componet'])
        for h2_elm in h2_elms:
            # h2のテキストを取得
            minor_title = h2_elm.xpath('.//text()')[0]
            body_all_text = ""
            join_body = ""
            bodys = h2_elm.xpath('./following-sibling::*')
            for body in bodys:
                if body.tag == "h2": 
                     break
                body_all_texts = body.xpath('.//text()')
                all_body = ' '.join(body_all_texts)
                join_body += all_body
            #     if self.deepl_enable:
            #         translated = self.httpclient.get_honyaku_deepl(self.deepl_apikey,join_body)
            #         if translated is not None:
            #             join_body = translated
            print (parent_title ,",", major_tilte + ",", minor_title + ",", "\"",  join_body.strip().replace( '\n', '').replace(",", u"、"), "\"")

    def enterpriseConfigurationTcpCrd_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationDefaultsCRD_scraping(data,scrape_con,DEF_ITEM)

    def enterpriseConfigurationStartupArgs_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationIngressAnnotations_scraping(data,scrape_con,DEF_ITEM)

    def enterpriseConfigurationServiceAnnotations_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationIngressAnnotations_scraping(data,scrape_con,DEF_ITEM)

    def enterpriseConfigurationIngressAnnotations_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationIngressAnnotations_scraping(data,scrape_con,DEF_ITEM)
    
    def communityConfigurationGlobalCRD_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationDefaultsCRD_scraping(data,scrape_con,DEF_ITEM)

    def communityConfigurationBackendCRD_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationDefaultsCRD_scraping(data,scrape_con,DEF_ITEM)

    def enterpriseConfigurationGlobalCRD_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationDefaultsCRD_scraping(data,scrape_con,DEF_ITEM)

    def enterpriseConfigurationBackendCRD_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationDefaultsCRD_scraping(data,scrape_con,DEF_ITEM)


    def enterpriseConfigurationDefaultsCRD_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        self.communityConfigurationDefaultsCRD_scraping(data,scrape_con,DEF_ITEM)

    def communityConfigurationDefaultsCRD_scraping(self,data,scrape_con,DEF_ITEM="defaultscraping"):
        content = self.httpclient.get(scrape_con['url'])
        data = content.read()
        elem = html.fromstring(data)
        section_elm = elem.xpath("//h1")[0]
        # 配下のすべてのテキストを取得
        all_text = section_elm.xpath('.//text()')
        # リストで取得されるため、結合する場合
        major_tilte = ' '.join(all_text)
        parent_title = section_elm.xpath('preceding-sibling::*[1]')[0].text
        componet_elms = section_elm.xpath(scrape_con['componet'])
        for item in componet_elms:
            #if item.text == "Defaults config" and item.getattr("id") != "defaults-config-enterprise-defaults-version-v3-0":
            #    continue
            # 配下のすべてのテキストを取得
            all_text = item.text
            # リストで取得されるため、結合する場合
            minor_title = ' '.join(all_text)
            body_all_text = ""
            desc_all_text = ""
            bodys = item.xpath('./following-sibling::*')
            for body in bodys:
                if body.tag == "h2": 
                    break
                body_all_text = body.xpath('.//text()[not(ancestor::script) and (not(ancestor::select) or ancestor::option[@selected])]')
                join_body = ' '.join(body_all_text)
                if self.deepl_enable:
                    translated = self.httpclient.get_honyaku_deepl(self.deepl_apikey,join_body)
                    if translated is not None:
                        join_body = translated
                print (parent_title ,",", major_tilte + ",", minor_title.strip().replace( '\n', ''), "\"",  join_body.strip().replace( '\n', '').replace(",", u"、"), "\"")
  
class JRNoteYAMLCache(object):
    """JRNoteYAMLCache for Yaml Configration

    """
    def __init__(self,DEFAULT_TARGET="../jrnote.yml"):
        self.cache = {}
        base = os.path.dirname(os.path.abspath(__file__))
        self.target =os.path.normpath(os.path.join(base, DEFAULT_TARGET))
        self.data = self._load(self.target)

    def _load(self,target):
        f = open(target,"r")
        #data = yaml.load(f)
        data = yaml.load(f, Loader=yaml.SafeLoader)
        f.close()
        return data


def main():
    JRNoteParser(JRNoteYAMLCache()).parse()

if __name__ == '__main__':
    main()



