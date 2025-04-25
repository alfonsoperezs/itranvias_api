from . import _queryitr_adapter
from .models import Stop, Line, Bus


def get_stop_buses(stop_id: int) -> dict[int, list[Bus]]:
    """
    Fetch information about a stop, including real-time info about buses

    :param stop_id: The id of the stop to consult

    :return: A dictionary with keys the line ids that go trough that stop, each having a list of `Bus`es
    """

    response = _queryitr_adapter.get(func=0, dato=stop_id)
    data = response.data

    lines = {}
    for line in data["buses"].get("lineas", []):
        buses = []
        for bus in line["buses"]:
            buses.append(
                Bus(
                    id=bus["bus"],
                    time=bus["tiempo"],
                    distance=bus["distancia"],
                    state=bus["estado"],
                    last_stop=Stop(bus["ult_parada"]),
                )
            )

        lines[line["linea"]] = buses

    return lines

def get_all_stops() -> list[Stop]:
    """
    Get information of all stops

    :return: A stop list with all the existing stops
    """
    response = _queryitr_adapter.get(func=7, dato="20160101T000000_gl_0_20160101T000000")
    data = response.data
    stops = []
    for stop in data["iTranvias"]["actualizacion"]["paradas"]:
        stops.append(_parse_stop(stop,data))
    return stops

def get_stop_by_id(stop_id: int) -> Stop | None:
    """
    Get information of about a stop

    :param stop_id: The id of the stop to consult

    :return: The information of the stop
    """
    response = _queryitr_adapter.get(func=7, dato="20160101T000000_gl_0_20160101T000000")
    data = response.data
    stop = next((s for s in data["iTranvias"]["actualizacion"]["paradas"] if s["id"] == stop_id), None)
    if stop == None:
        return None
    return _parse_stop(stop, data)

def _parse_stop(stop, data) -> Stop:
    lines = []
    for line_id in stop["enlaces"]:
        line = next((l for l in data["iTranvias"]["actualizacion"]["lineas"] if l["id"] == line_id), None)
        lines.append(Line(
            id=line_id,
            name=line["lin_comer"],
            color=line["color"],
            origin=Stop(name=line["nombre_orig"]),
            destination=Stop(name=line["nombre_dest"]),
        ))
    return Stop(
        id=stop["id"],
        name=stop["nombre"],
        connections=lines,
        long=stop["posx"],
        lat=stop["posy"],
    )

def get_stop_by_keywords(keywords: str) -> list[Stop]:
    """
    Get stops whose name match with the given keywords

    :param keywords: A string with the keywords to search

    :return: A list with stops that matches with the keywords
    """
    keywords_list = keywords.lower().split(" ")
    stops = get_all_stops()
    return [stop for stop in stops if all(keyword in stop.name.lower() for keyword in keywords_list)]