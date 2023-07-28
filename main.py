from pprint import pprint as pp
import json
import configparser
import requests

GLOBAL_LOG = False

config = configparser.ConfigParser()
config.read("config.ini")
PAT = config["miro-api"]["PAT"]
BOARD_ID = config["miro-api"]["board_id"]
GLOBAL_URL = "https://api.miro.com/v2"


def _header(bearer_token=PAT):
    """generate header for requests"""
    return {
        "Accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {bearer_token}",
    }


def _requests_get(url, timeout=10):
    """requests GET wrapper with header
    returns: response object"""
    return requests.get(url, headers=_header(), timeout=timeout)


def _requests_post(url, payload=r"{}", timeout=10):
    """requests POST wrapper with header
    returns: response object"""
    return requests.post(url, json=payload, headers=_header(), timeout=timeout)


def auth_test():
    """test oauth pat via miro api"""
    url = "https://api.miro.com/v1/oauth-token"
    # response = requests.get(url, headers=header(), timeout=10)
    response = _requests_get(url)

    print(response.text)


def get_board_items(board_id):
    """get items from board"""
    url = f"{GLOBAL_URL}/boards/{board_id}/items"
    response = _requests_get(url)
    print_log(response.text)
    result = response.json().get("data")
    # print_log(result)
    return result


def get_board_connectors(board_id):
    """get connectors from board"""
    url = f"{GLOBAL_URL}/boards/{board_id}/connectors"
    response = _requests_get(url)
    print_log(response.text)
    result = response.json().get("data")
    # print_log(result)
    return result


def print_log(message):
    """print scalar logs or json payloads"""
    if GLOBAL_LOG and message is not None:
        print()
        if isinstance(message, str):
            if message[0:1] == "{":
                print(message)
            else:
                print(message[0:100])
        else:
            print(json.dumps(message))


def get_board_item(board_id, item_id):
    """get specific item via its item_id from board"""
    url = f"{GLOBAL_URL}/boards/{board_id}/items/{item_id}"
    response = _requests_get(url)
    print_log(response.text)
    result = response.json().get("data")
    # print_log(result)
    return result


def _clean_str(string: str) -> str:
    """replace html paragraph tags in a string"""
    return string.replace("<p>", "").replace("</p>", "")


def make_trivial_graph(board_id, connectors):
    """go through a list of connectors, extracting the captions
    of the starting and end node with the connecror caption to a edge list"""
    # FIXME refactor better
    gi = lambda i: get_board_item(item_id=i, board_id=board_id)["content"]
    ct = lambda s: _clean_str(s)
    extr = lambda d: [
        ct(gi(d["startItem"]["id"])),
        [ct(c["content"]) for c in d["captions"]],
        ct(gi(d["endItem"]["id"])),
    ]
    return [extr(conn) for conn in connectors]


def make_sticky(board_id, caption="test", x_pos=0, y_pos=0):
    """create a sticky with a left&top aligned
    caption and x + y position on the board
    standard geomatry is: {'height': 228.0, 'width': 350.0}

    returns: a tuple with the id + a dict with id, position and geometry attributes of the sticky created
    see: https://developers.miro.com/reference/create-sticky-note-item"""
    url = f"https://api.miro.com/v2/boards/{board_id}/sticky_notes"

    payload = {
        "data": {"shape": "rectangle", "content": f"{caption}"},
        "style": {"textAlign": "left", "textAlignVertical": "top"},
        "position": {"x": f"{x_pos}", "y": f"{y_pos}"},
        # "parent": {"id": "frame_id"},
    }

    response = _requests_post(url, payload=payload)

    print_log(response.text)

    properties = {
        k: v for k, v in response.json().items() if k in ("id", "geometry", "position")
    }

    return (properties["id"], properties)


def connect_objects(board_id, from_item, to_item, caption="test", font_size=25):
    """connect two items via an elbowed connector with a caption
    of font-size 50 and strode width of 5
    see: https://developers.miro.com/reference/create-connector"""
    url = f"https://api.miro.com/v2/boards/{board_id}/connectors"

    payload = {
        "startItem": {"snapTo": "auto", "id": f"{from_item}"},
        "endItem": {"snapTo": "auto", "id": f"{to_item}"},
        "captions": [{"content": f"{caption}", "textAlignVertical": "middle"}],
        "style": {
            "fontSize": f"{font_size}",
            "textOrientation": "horizontal",
            "strokeWidth": "5",
        },
        "shape": "elbowed",
    }

    response = _requests_post(url, payload=payload)

    print_log(response.text)


def tgf_demo():
    """make a trivial graph file node - edge - node list from a board
    TODO: figure out how to sort an edge list for better vizzing: https://stackoverflow.com/questions/35608832/sorting-lists-of-edges-in-python
    """
    conns = get_board_connectors(board_id="uXjVM2vb9AQ=")
    # pp(items)
    conns = make_trivial_graph(connectors=conns, board_id="uXjVM2vb9AQ=")
    pp(conns)


def stickies_demo():
    """create some stickies and then connect them"""
    id1, _ = make_sticky(board_id=BOARD_ID, caption="A", x_pos=0)
    id2, _ = make_sticky(board_id=BOARD_ID, caption="B", x_pos=700, y_pos=300)
    id3, _ = make_sticky(board_id=BOARD_ID, caption="C", x_pos=700, y_pos=-300)
    connect_objects(
        board_id=BOARD_ID, from_item=id1, to_item=id2, caption="points\ntowards"
    )
    connect_objects(
        board_id=BOARD_ID, from_item=id1, to_item=id3, caption="points\ntowards"
    )
    # make_sticky(board_id=BOARD_ID, caption="xxyyzz2", x_pos=50)
    # make_sticky(board_id=BOARD_ID, caption="xxyyzz3", x_pos=100)


def main():
    """main function"""
    auth_test()
    tgf_demo()
    stickies_demo()


if __name__ == "__main__":
    main()
