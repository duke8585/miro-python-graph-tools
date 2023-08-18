from pprint import pprint as pp
import json
import configparser
import requests
import networkx as nx
import matplotlib.pyplot as plt

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


def get_board_items(board_id, limit=50):  # NOTE 50 is the official limit
    """get items from board"""
    url = f"{GLOBAL_URL}/boards/{board_id}/items?limit={limit}"
    response = _requests_get(url)
    print_log(response.text)
    result = response.json().get("data")
    # pp(response.text)
    # print_log(result)
    return result


def get_board_connectors(board_id, limit=50):  # NOTE 50 is the official limit
    """get connectors from board"""
    url = f"{GLOBAL_URL}/boards/{board_id}/connectors?limit={limit}"
    response = _requests_get(url)
    print_log(response.text)
    result = response.json().get("data")
    # print_log(result)
    # pp(response.text)
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


def get_board_item(board_id, item_id) -> dict:
    """get specific item via its item_id from board"""
    url = f"{GLOBAL_URL}/boards/{board_id}/items/{item_id}"
    response = _requests_get(url)
    print_log(response.text)
    result = response.json().get("data")
    # print_log(result)
    return result


def _get_item_caption(board_id: str, item_id: str) -> str:
    return get_board_item(item_id=item_id, board_id=board_id)["content"]


def _clean_str(string: str) -> str:
    """replace html paragraph tags in a string"""
    return string.replace("<p>", "").replace("</p>", "")


def _get_connector_captions(connector):
    """try to get captions from a connector and ", "-join them if multiple, if empty return empty string"""
    if connector.get("captions"):
        return _clean_str(", ".join(c["content"] for c in connector.get("captions")))
    else:
        return ""


def _extract_connector(board_id, connector: dict):
    """take a connector object
    for start (from) and end (to): retrieve its caption via its id and clean it up
    for the connector, if multiple caption, join them and clean them up
    return: a list with captions of start (from), connector and end (to) item"""
    from_id = connector["startItem"]["id"]
    from_caption = _clean_str(_get_item_caption(board_id, from_id))
    connector_caption_merged = _get_connector_captions(connector)
    to_id = connector["endItem"]["id"]
    to_caption = _clean_str(_get_item_caption(board_id, to_id))
    return [from_caption, connector_caption_merged, to_caption]


def make_trivial_graph(board_id, connectors) -> list[list]:
    """iterate through connectors and build adjacency list from its nodes and caption (edge)"""
    adjacency_list = []

    for edge in connectors:
        adjacency_list.append(_extract_connector(board_id, edge))

    return adjacency_list


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


def get_tgf_from_board_demo():
    """make a trivial graph file node - edge - node list from a board
    TODO: figure out how to sort an edge list for better vizzing: https://stackoverflow.com/questions/35608832/sorting-lists-of-edges-in-python
    """
    conns = get_board_connectors(board_id="uXjVM2vb9AQ=")
    # pp(items)
    conns = make_trivial_graph(board_id="uXjVM2vb9AQ=", connectors=conns)
    pp(conns)


def create_manual_graph_demo():
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


def _edge_list_from_tgf(tgf: list[list]) -> list[list]:
    edge_list = [
        [edge[0], edge[2]] for edge in tgf
    ]  # NOTE a simple from_node - to_node
    return edge_list


def get_node_positions(tgf: list[list], scale=2000, draw_local=True):
    """topologically sort an edge list, then use a multipartitie layout to determine their x and y positions inside a scale

    see https://networkx.org/documentation/stable/auto_examples/graph/plot_dag_layout.html
    """
    import networkx as nx

    edge_list = _edge_list_from_tgf(tgf)

    if draw_local:  # NOTE for local debugging
        fig = plt.figure(figsize=(12, 12))
        ax = plt.subplot(111)
        ax.set_title("Graph - Shapes", fontsize=10)

    # define a graph
    G = nx.DiGraph()
    G.add_edges_from(edge_list)

    for layer, nodes in enumerate(nx.topological_generations(G)):
        # `multipartite_layout` expects the layer as a node attribute, so add the
        # numeric layer value as a node attribute
        for node in nodes:
            G.nodes[node]["layer"] = layer

    # Compute the multipartite_layout using the "layer" node attribute
    pos = nx.multipartite_layout(G, subset_key="layer", scale=scale)
    # pp(pos)

    if draw_local:
        # draw graph
        nx.draw_networkx(G, pos=pos, ax=ax, node_size=1000, font_size=12)
        plt.tight_layout()
        plt.savefig("Graph.png", format="PNG")

    return pos


def create_stickies_graph_tgf(edges, node_pos):
    """take a tgf edge list of lists adn the node positions to build a graph

    * take the node_positions and create stickies
    * store the according object_id after every api call in a lookup
    * make connectors, using the edges tgf and the lookup

    mostly using:
    id1, _ = make_sticky(board_id=BOARD_ID, caption="A", x_pos=0)
    connect_objects(
        board_id=BOARD_ID, from_item=id1, to_item=id2, caption="points\ntowards")
    """

    print_log("creating nodes")
    nodes_lookup = {}  # NOTE caption : miro_id lookup for edges
    for caption, pos in node_pos.items():
        x_pos = pos[0]
        y_pos = pos[1]
        object_id, _ = make_sticky(
            board_id=BOARD_ID, caption=caption, x_pos=x_pos, y_pos=y_pos
        )
        nodes_lookup.update({caption: object_id})

    print_log("creating edges")
    for edge in edges:
        node_from = edge[0]
        edge_caption = edge[1]
        node_to = edge[2]
        id_from = nodes_lookup[node_from]
        id_to = nodes_lookup[node_to]
        connect_objects(
            board_id=BOARD_ID,
            from_item=id_from,
            to_item=id_to,
            caption=edge_caption if len(edge_caption) > 0 else "TBD",
        )


def main():
    """main function"""

    # auth_test()
    # get_tgf_from_board_demo()
    # create_manual_graph_demo()

    tgf = [
        ["App_1", "", "collect_traces"],
        ["App_2", "", "collect_traces"],
        ["App_3", "", "collect_traces"],
        ["App_4", "", "collect_traces"],
        ["App_5", "", "collect_traces"],
        ["collect_traces", "", "<em>optional layer, needed?!</em>"],
        ["<em>optional layer, needed?!</em>", "", "lbd"],
        ["lbd", "", "update"],
        ["update", "", "leadouts"],
        ["update", "", "leadins"],
        ["update", "", "earnings_cpc"],
        ["update", "", "earnings_cpo"],
        ["ext tables", "", "earnings_cpo"],
        ["ext tables", "", "earnings_cpc"],
        ["App_6", "", "prepare_traces"],
        ["App_7", "", "prepare_traces"],
        ["App_8", "", "prepare_traces"],
        ["prepare_traces", "", "isg"],
        ["isg", "", "collect_traces"],
        ["update", "", "earnings_cpc"],
    ]
    node_positions = get_node_positions(tgf)
    create_stickies_graph_tgf(tgf, node_positions)


if __name__ == "__main__":
    main()
