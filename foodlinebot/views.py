from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    PostbackTemplateAction
)

from .scraper import IFoodie

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):

    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件

                if event.message.text == "哈囉":

                    message = TemplateSendMessage(
                        alt_text='Buttons template',
                        template=ButtonsTemplate(
                            title='Menu',
                            text='請選擇地區',
                            actions=[
                                PostbackTemplateAction(
                                    label='台北市',
                                    text='台北市',
                                    data='area=台北市'
                                ),
                                PostbackTemplateAction(
                                    label='台中市',
                                    text='台中市',
                                    data='area=台中市'
                                ),
                                PostbackTemplateAction(
                                    label='高雄市',
                                    text='高雄市',
                                    data='area=高雄市'
                                )
                            ]
                        )
                    )

                    line_bot_api.reply_message(  # 回復按鈕樣板訊息
                        event.reply_token,
                        message
                    )

                else:

                    # 資料初始化
                    food = IFoodie(event.message.text, "火鍋", "2")

                    line_bot_api.reply_message(  # 回復訊息文字
                        event.reply_token,
                        # 爬取該地區正在營業且600元以內的前五名最高人氣火鍋店
                        TextSendMessage(text=food.scrape())
                    )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
