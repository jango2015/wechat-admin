# coding=utf8

import settings
from flask import request, Flask

from flask.ext.sqlalchemy import SQLAlchemy

from wechat_sdk import WechatBasic
from kits.menu import WechatMenuAdapter


app = Flask(__name__)
db_str = 'mysql://%s:%s@%s:%s/%s' % (
    settings.db_username,
    settings.db_password,
    settings.db_hostname,
    settings.db_port,
    settings.db_name)

db_binds = {
    settings.db_name: db_str,
}

app.config['TOKEN'] = settings.token
app.config['SQLALCHEMY_DATABASE_URI'] = db_str
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_BINDS'] = db_binds

db = SQLAlchemy(app)

@app.route('/', methods=['POST', 'GET'])
def index():
    token = app.config['TOKEN']
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')

    # 实例化 wechat
    wechat = WechatBasic(token=token)

    if not wechat.check_signature(
        signature=signature,
        timestamp=timestamp,
        nonce=nonce):
        return 'fail'

    # 对签名进行校验
    echostr = request.args.get('echostr')
    if echostr:
        return echostr

    wechat.parse_data(request.data)
    message = wechat.get_message()
    if message.type == 'text':
        response = wechat.response_text(settings.auto_replay_text)
    elif message.type == 'image':
        response = wechat.response_text(u'图片')
    else:
        response = wechat.response_text(u'未知')
    return response


@app.route('/menus', methods=['GET'])
def get_menus():
    menus = WechatMenuAdapter.get_menus()
    return menus

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=19015, debug=True)
