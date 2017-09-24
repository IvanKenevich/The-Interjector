import requests
from bs4 import BeautifulSoup


def make_soup(url):
    return BeautifulSoup(s.get(url, timeout=None).text, 'html.parser')


def make_json(url):
    return s.get(url, timeout=None).json()


def search_thread_for_linux(thread):
    soup = make_soup("https://2ch.hk/" + BOARD_NAME + "/res/" + thread["num"] + ".html")

    messages = soup.find_all("blockquote")

    matching_messages = []
    # TODO: What if quote AND message contain the word?
    for message in messages:
        if text_matches(message.text):  # if it's somewhere in the message
            # (including quotes from previous messages)
            quotes = message.find_all("span", attrs={"class": "unkfunc"})
            if len(quotes) > 0:  # if there are any quotes in the message
                for quote in quotes:
                    if text_matches(quote.text):  # check every quote
                        break
                else:  # if not in any of the quotes, must be in the message itself
                    matching_messages.append(message["id"][1:])
            else:  # if there are no quotes, the word is in the message
                matching_messages.append(message["id"][1:])

    return matching_messages


def text_matches(text):
    w1 = "линукс"
    w2 = "linux"
    wn1 = "gnu/linux"
    wn2 = "gnu-linux"
    if (w1 in text or w2 in text) and wn1 not in text and wn2 not in text:
        return True
    else:
        return False


with requests.session() as s:
    BOARD_NAME = "s"

    image_id = make_json("https://2ch.hk/api/captcha/2chaptcha/id?board=" + BOARD_NAME + "&thread=" + "161694010")["id"]
    image_address = "https://2ch.hk/api/captcha/2chaptcha/image/" + image_id

    captcha_value = input(image_address+"\nEnter value from the captcha above: ")

    print(s.post("https://2ch.hk/makaba/posting.fcgi?json=1",data={"task":"post","board":"b",
                                                             "thread":"161694010",
                                                             "captcha_type":"2chaptcha",
                                                             "comment":"test-roll",
                                                             "2chaptcha_id":str(image_id),
                                                             "2chaptcha_value":str(captcha_value)}).json()["Error"])
    # thread_catalog = make_json("https://2ch.hk/" + BOARD_NAME + "/threads.json")["threads"]
    # print("There are currently", len(thread_catalog), "threads on /" + BOARD_NAME)
    # i = 0
    # for t in thread_catalog:
    #     print("=== SEARCHING THROUGH THREAD " + str(i + 1) + "/" + str(len(thread_catalog)) + " ===")
    #     message_numbers = search_thread_for_linux(t)
    #     for message_number in message_numbers:
    #         print("https://2ch.hk/" + BOARD_NAME + "/res/" + t["num"] + ".html#" + message_number)
    #         image_id = make_json("https://2ch.hk/api/captcha/2chaptcha/id?board=" + BOARD_NAME + "&thread=" + t["num"])["id"]
    #         image_address = "https://2ch.hk/api/captcha/2chaptcha/image/" + image_id
    #     i += 1

s.close()
