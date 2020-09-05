import handlers
from datetime import timedelta
from babel.dates import format_timedelta
import dataset
import datetime
import out
import random
import common

modname = "vim tips"
tipdb = dataset.connect('sqlite:///dat/tips.db')
tipslist = tipdb.load_table('tips')

TIP_TYPES = {
    'text': 0,
    'snippet': 1,
}


def format_tip(tip):
    text = ['']

    if tip['tiptype'] == TIP_TYPES['snippet']:
        text[0] += '{}:'.format(tip['snippet_desc'])
        text.append('    {}'.format(tip['snippet']))
    elif tip['tiptype'] == TIP_TYPES['text']:
        text[0] += '{}'.format(tip['text'])

    text.append('[{}]'.format(tip['id']))

    if not tip["date"] == None and not tip["date"] == 0:
        # format added date nice (e.g. "added 5m ago")
        last_fed_unix = int(tip["date"])
        last_fed_date = datetime.datetime.fromtimestamp(last_fed_unix)
        since = datetime.datetime.now() - last_fed_date
        since_delta_fmt = format_timedelta(since, locale="en_US")
        text[-1] += f' added {since_delta_fmt} ago'

    author = tip['author_username']
    if not author == None:
        text[-1] += ' ({}) '.format(common.nohighlight(author))

    return text


async def random_tip(self, ch, src, msg, args, opts):
    """
    :name: tip
    :hook: cmd
    :help: show a random vim tip or search for a tip
    :args: @query:str
    """
    msg = msg.strip()
    if len(msg) < 1:
        # get a random tip
        tip = random.choice(list(tipslist.find()))
    else:
        # search for tips
        try:
            text_tips = [i for i in tipslist.find(text={'like':f"%{msg}%"})]
            snippet_d = [i for i in tipslist.find(snippet_desc={'like':f"%{msg}%"})]
            snippets  = [i for i in tipslist.find(snippet={'like':f"%{msg}%"})]

            possible_tips = []
            if len(text_tips) > 0:
                possible_tips.append([i for i in text_tips])
            if len(snippets) > 0:
                possible_tips.append([i for i in snippets])
            if len(snippet_d) > 0:
                possible_tips.append([i for i in snippet_d])

            tip = random.choice(possible_tips)[0]
        except IndexError:
            await out.msg(self, modname, ch, ['no tips found.'])
            return

    # print all lines of tip at once
    for msg in format_tip(tip):
        await out.msg(self, "", ch, [msg])



async def submit_text_tip(self, ch, src, msg, args, opts):
    """
    :hook: cmd
    :name: addtip-text
    :help: add a random vim tip (requires +v)
    :args: text:str
    :require_vop:
    """
    data = dict(date=datetime.datetime.now().timestamp(),
        author_nick=src, author_account=self.users[src]['account'],
        author_username=self.users[src]['username'],
        tiptype=TIP_TYPES['text'], text=msg)
    tipslist.insert(data)
    await out.msg(self, modname, ch, ['added text tip'])


async def delete_tip(self, ch, src, msg, args, opts):
    """
    :hook: cmd
    :name: rmtip
    :help: delete a tip by id (requires +h)
    :args: id:int
    :require_hop:
    """
    try:
        tipid = int(msg.split()[0].strip())
    except:
        await out.msg(self, modname, ch, ['invalid tip id.'])
        return

    target = tipslist.find_one(id=tipid)
    if not target == None:
        tipslist.delete(id=tipid)
        await out.msg(self, modname, ch, [f'removed tip {tipid} (was "{target}")'])
    else:
        await out.msg(self, modname, ch, [f'no such tip with id "{tipid}"'])


async def init(self):
    handlers.register(self, modname, random_tip)
    handlers.register(self, modname, submit_text_tip)
    handlers.register(self, modname, delete_tip)
