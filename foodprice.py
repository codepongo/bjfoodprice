#coding=utf-8 
import urllib
import urllib2
import sys
import operator 
import HTMLParser
import datetime
import operator 
import getopt
import os
class XiFaDi(object):
    def __init__(self):
        object.__init__(self)
        self.food = {}
        self.food['vegetable'] = 1
        self.food['fruit'] = 2
        self.food['meat'] = 3
        self.food['seafood'] = 4
        self.food['mainfood'] = 5
        

    def feed(self, url):
        req = urllib2.Request(url)
        content = urllib2.urlopen(req)
        html = content.read()
        try:
            html = html.decode('gbk')
        except:
            pass
        price = {}
        class Parser(HTMLParser.HTMLParser):
            def __init__(self):
                self.cur = None
                self.new = False
                self.handle = False
                self.date = None
                HTMLParser.HTMLParser.__init__(self)
            def handle_starttag(self, tag, attrs):
                if tag == 'td':
                    propertys = {}
                    for key,value in attrs:
                        propertys[key] = value
                    if propertys['width'] == '16%' and -1 !=propertys['style'].find('background'):
                        self.new = True
                    elif propertys['width'] == '10%' and -1 !=propertys['style'].find('background'):
                        self.handle = True
                    elif propertys['width'] == '13%' and -1 !=propertys['style'].find('background'):
                        self.handle = True
                    else:
                        pass
            def handle_data(self, data):
                if self.new:
                    price[data] = []
                    if self.cur is not None and self.last is not None:
                        if self.last[-2] != self.cur[-2]:
                            self.date = self.last[-2]
                            raise Exception('finish')
                    self.last = self.cur
                    self.cur = price[data]
                    self.new = False
                if self.handle:
                    self.cur.append(data)
                    self.handle = False
        try:
            p = Parser()
            p.feed(html)
        except Exception, e:
            if str(e) == 'finish':
                return True, price,p.date
            else:
                raise e
        return False, price, p.date
    
    
    def get(self):
        for k in ['vegetable','fruit', 'meat', 'seafood', 'mainfood']:
            mid = self.food[k]
            all = {}
            page = 1 
            while True:
                url = ('http://www.xinfadi.com.cn/price/?mid=%s&page=%s') % (mid, page)
                finish, p, self.date = self.feed(url)
                
                if finish:
                    all.update(p)
                    break
                if len(all) != 0 and all.values()[0][-2] != p.values()[0][-2]:
                    break
                else:
                    all.update(p)
                    page += 1
            p = {}
            for key, value in all.iteritems():
                if len(value) != 0:
                    p[key] = float(value[1])
            self.food[k] = sorted(p.iteritems(), key=operator.itemgetter(1), reverse=False)

    def printone(self, food, output):
        if output == sys.stdout and sys.platform == 'win32':
            print food[0], ':', food[i][1],
        else:
            try:
                output.write(str(food[0].encode('utf-8'))+':'.encode('utf-8')+str(food[1]))
            except:
                output.write(str(food[0])+'='+str(food[1]))


    def show(self, n = 0, cols = True, output = sys.stdout):
        if self.date != None:
            output.write(self.date.encode('utf-8')+os.linesep)
        if n == 0:
            showall = True
        else:
            showall = False
        if cols:
            col = len(self.food.keys())
            if showall:
                n = sorted([len(l) for l in self.food.values()])[col-1]
            for y in range(0, n):
                for x in range(0, col):
                    try:
                        self.printone(self.food.values()[x][y],output)
                    except IndexError:
                        pass
                    output.write(' ')
                output.write(os.linesep)
        else:
            for type,price in self.food.items():
                if showall:
                    n = len(price)
                for i in range(0, n):
                    self.printone(price[i],output)
                    output.write(os.linesep)

class BaLiQiao(object):
    def __init__(self):
        object.__init__(self)
        self.food = {}
        self.food['vegetable'] = 1
        self.food['fruit'] = 2
        self.food['meat'] = 4
        self.food['seafood'] = 8
        self.food['mainfood'] = 16
        self.date = ''
    def snatchFromBJBLQ(self, page_idx, food_type):
        """snatch html page from bjblq.com"""
        d = dict()
        url = 'http://www.bjblq.com/price.aspx'
        post_data = urllib.urlencode(
                {
                    'Page':str(page_idx),
                    'PriceType':str(food_type),
                }
        )
        req = urllib2.Request(url+'?'+post_data)
        try:
            conn = urllib2.urlopen(req)
        except urllib2.URLError,e: 
            print 'URLError:', e
        except urllib2.HTTPError,e:    
            print 'HTTP Error:', e
        result = conn.read()
        return result.split(os.linesep)
    
    def getFoodInfo(self, l):
        """parse html to find the begin line of food information, food page number and food count."""
        key = '最新发布时间：'
        count_key = '共有'
        date_end_key = '</font>'
        prefix_of_count = '<font color=\'red\'>'
        suffix_of_count = '</font>'
        count_per_page = 40
        size = len(l)
        cur = -1
        page = 1
        count = 0
        find_count = False
        date = False
        for i in xrange(size):
            if sys.platform == 'win32':
                pos = l[i].find(key)
            else:
                pos = l[i].find(key)
            if pos != -1:
                date_end_pos = l[i].find(date_end_key)
                date = l[i][date_end_pos-10:date_end_pos]
                year = int(date[date.find('-')-4:date.find('-')])
                date = date[date.find('-')+1:]
                month = int(date[0:date.find('-')])
                date = date[date.find('-')+1:]
                day = int(date)
                date = str(year)+'-'+str(month)+'-'+str(day)
                find_count = True
                cur = i + 21
                continue
            if find_count == False:
                continue
            else:
                if sys.platform == 'win32':
                    pos = l[i].find(count_key)
                else:
                    pos = l[i].find(count_key)
                if pos != -1:
                    s = l[i].strip()
                    s = s[s.find(prefix_of_count)+len(prefix_of_count):s.find(suffix_of_count)]
                    count = int(s)
                    if count % count_per_page != 0:
                        page = count/count_per_page + 1
                    else:
                        page = count/count_per_page
                    break
        return (cur, page, count, date)
    
    def saveFood(self, l, cur, page, count, food_type):
        """save food to a dictionary"""
        d = {}
        if page == 1:
            d = self.parseItems(l, cur, count)
        else:
            for i in xrange(page):
                if i == 0:
                    d.update(self.parseItems(l, cur, 40))
                else:
                    l = self.snatchFromBJBLQ(i+1, food_type)
                    cur, page_tmp, count_tmp, date = self.getFoodInfo(l)
                    d.update(self.parseItems(l, cur, count - 40 * i))
        return d
    
    def parseItems(self, l, cur, count):
        """parse context to get the name and price of every kind of food"""
        d = {}
        for i in xrange(count):
            s = l[cur].strip()
            pos = s.find('>')
            s = s[pos+1:]
            key = s[:s.find('<')]
            cur += 4
            s = l[cur].strip()
            s = l[cur].strip()
            pos = s.find('>')
            s = s[pos+len('&nbsp;')+1:]
            value = s[:s.find('<')-len('&nbsp;')]
            d[key] = float(value)
            cur += 4
        return d

    def get(self):
        for k in self.food.keys():
            html = self.snatchFromBJBLQ(1, self.food[k])
            cur, page, count, self.date = self.getFoodInfo(html)
            d = self.saveFood(html, cur, page, count, self.food[k])
            sorted_d = sorted(d.iteritems(), key=operator.itemgetter(1), reverse=False)
            self.food[k] = sorted_d

    def printone(self, food, output):
        if output == sys.stdout and sys.platform == 'win32':
            print food[0].decode('utf-8')+':'+str(food[1]),
        else:
            output.write(food[0]+':'+str(food[1]))

    def show(self, n = 0, cols = True, output = sys.stdout):
        output.write(self.date+os.linesep)
        if n == 0:
            showall = True
        else:
            showall = False
        if cols:
            col = len(self.food.keys())
            if showall:
                n = sorted([len(l) for l in self.food.values()])[col-1]
            for y in range(0, n):
                for x in range(0, col):
                    try:
                        self.printone(self.food.values()[x][y],output)
                    except IndexError:
                        pass
                    output.write(' ')
                output.write(os.linesep)
        else:
            for k, food in self.food.items():
                if output == sys.stdout and sys.platform == 'win32':
                    print '====='+k.decode('utf8')+'====='
                else:
                    output.write('====='+k+'====='+os.linesep)
                n = len(food)
                for i in xrange(n):
                    self.printone(food[i], output)
                    output.write(os.linesep)
def help():
    print ("""\
USEAGE:
%s [-a|--all] [-h|--help][-m|--multi-column][-o <file>|--output=<file>]
    all     Show all kinds of food
    help    Help
    output  output in <file>
""") % (sys.argv[0])
def main():
    showall = False
    output = sys.stdout
    cols = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "amo:", ["all", "help", "multi-column", "output="])
    except:
        help()
        return 0
    for o, a in opts:
        if o in ('-h', '--help'):
            help()
            return 0
        if o in ('-o', '--output'):
            if sys.platform == 'win32':
                output = open(a, 'wb')
            else:
                output = open(a, 'w')
        if o in ('-a', '--all'):
            showall = True
        if o in ('-m', '--multi-column'):
            cols = True
    if showall:
        output.write('BaLiQiao:') 
        blq = BaLiQiao()
        blq.get()
        blq.show(cols=cols, output=output)
        output.write('XiFaDi:')
        xfd = XiFaDi()
        xfd.get()
        xfd.show(cols=cols, output=output)
    else:
        output.write('BaLiQiao:')
        blq = BaLiQiao()
        blq.get()
        blq.show(n=5, cols=cols, output=output)
        output.write('XiFaDi:')
        xfd = XiFaDi()
        xfd.get()
        xfd.show(n=5, cols=cols, output=output)
    
    
if '__main__' == __name__:
    exit(main())
