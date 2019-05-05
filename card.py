from lxml import html
from requests import get

def getcategory(name):
    cat=get('http://yugioh.wikia.com/api.php?action=query&prop=categories&cllimit=500&format=json&titles='+name).json()
    return cat

def getpage(query):
    result=get('http://yugioh.wikia.com/api/v1/Search/List?limit=10&namespaces=0&query='+query).json()
    name=[x['title'] for x in result['items']]
    while name!=[]:
        cat=str(getcategory(name[0]))
        if 'Category:Tokens' not in cat:
            if any(x in cat for x in ('Category:OCG cards','Category:TCG cards')):
                break
        del name[0]
    if name!=[]:
        return name[0]
    else:
        raise ValueError

def ismonster(tree):
    if tree.xpath('//tr[th[a[@href="/wiki/Card_type"]]]/td/a/text()')[0]=='Monster':
        return True
    else:
        return False

def getattribute(tree):
    attribute=tree.xpath('//tr[th[a[@href="/wiki/Attribute"]]]/td/a/text()')
    attribute=''.join(attribute)
    return attribute

def gettypes(tree):
    types=tree.xpath('//tr[th[a[@href="/wiki/Type"]]]/td/a/text()')
    types='/'.join(types)
    return types

def getatk(tree):
    atk=tree.xpath('//tr[th[a[@href="/wiki/ATK"]]]/td/a/text()')
    stat=tree.xpath('//th[a[@href="/wiki/ATK"]]/a/text()')[1]
    if stat=='LINK':
        sign='-'
    else:
        sign='/'
    atk='ATK/'+atk[0]+' '+stat+sign+atk[1]
    return atk

def getlevel(tree):
    level=tree.xpath('//tr[th[a[@href="/wiki/Level"]]]/td/a/text()|//tr[th[a[@href="/wiki/Rank"]]]/td/a/text()')
    if level!=[]:
        stat=tree.xpath('//th[a[@href="/wiki/Level"]]/a/text()|//th[a[@href="/wiki/Rank"]]/a/text()')
        level=stat[0]+' '+level[0]
        level+='|'
    else:
        level=''
    return level

def getscale(tree):
    scale=tree.xpath('//tr[th[a[@href="/wiki/Pendulum_Scale"]]]/td/a/text()')
    if scale==[]:
        scale=''
    else:
        scale='\nPendulum Scale: '+scale[0]
    return scale

def getarrows(tree):
    arrows=tree.xpath('//tr[th[a[@href="/wiki/Link_Arrow"]]]/td/a/text()')
    if arrows==[]:
        arrows=''
    else:
        arrows='\nLink Arrows: '+', '.join(arrows)
    return arrows

def getproperty(tree):
    prop=tree.xpath('//tr[th[a[@href="/wiki/Property"]]]/td/a/text()')[0]
    card=tree.xpath('//tr[th[a[@href="/wiki/Card_type"]]]/td/a/text()')[0]
    prop+=' '+card
    return prop

def getcard(query):
    page=get('http://yugioh.wikia.com/wiki/'+getpage(query))
    tree=html.fromstring(page.content)
    name=tree.xpath('(//th[@class="cardtable-header"])[1]/text()')[0]
    effect=tree.xpath('(//td[@class="navbox-list"])[1]//text()|(//td[@class="navbox-list"])[1]//br')
    pendeffect=tree.xpath('(//td[@class="navbox-list"])[1]/dl[1]/dd//text()|(//td[@class="navbox-list"])[1]/dl[1]/dd//br')
    moneffect=tree.xpath('(//td[@class="navbox-list"])[1]/dl[2]/dd//text()|(//td[@class="navbox-list"])[1]/dl[2]/dd//br')
    for i in range(len(effect)):
        if not isinstance(effect[i],str):
            effect[i]='\n'
    for i in range(len(pendeffect)):
        if not isinstance(pendeffect[i],str):
            pendeffect[i]='\n'
    for i in range(len(moneffect)):
        if not isinstance(moneffect[i],str):
            moneffect[i]='\n'
    effect=''.join(effect)[1:]
    pendeffect=''.join(pendeffect)[1:]
    moneffect=''.join(moneffect)[1:]
    if moneffect!='':
        effect='Pendulum Effect:\n'+pendeffect+'Monster Effect:\n'+moneffect
    if ismonster(tree):
        text=getlevel(tree)+getattribute(tree)+'|'+gettypes(tree)+'\n'+getatk(tree)+getscale(tree)+getarrows(tree)
    else:
        text=getproperty(tree)
    text+='\n\nCard descriptions:'+'\n'+effect
    text=name+'\n\n'+text
    return text

def getpic(url):
    page=get(url)
    tree=html.fromstring(page.content)
    pic=tree.xpath('//td[@class="cardtable-cardimage"]/a/@href')[0].split('/revision/latest')[0]
    return pic

def getcardname(url):
    page=get(url)
    tree=html.fromstring(page.content)
    name=tree.xpath('(//th[@class="cardtable-header"])[1]/text()')[0]
    return name
