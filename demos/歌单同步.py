from pyncm.__main__ import parse_args,logger
from pyncm import GetCurrentSession,SetCurrentSession,LoadSessionFromString
from pyncm.utils.helper import UserHelper
args, _ = parse_args()
logger.info("读取登录信息 : %s" % args.load)
SetCurrentSession(LoadSessionFromString(open(args.load).read()))
logger.info("用户 : %s" % UserHelper(GetCurrentSession().uid).UserName)